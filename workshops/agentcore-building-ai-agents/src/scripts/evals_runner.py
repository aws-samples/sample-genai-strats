# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = [
#     "boto3>=1.42.94",
# ]
# ///
"""
Simulates customer conversations with the agent running on AgentCore Runtime, then runs an
AgentCore Evaluations batch evaluation over them.

Conversations are picked at random from evals_conversations.json. Some ask for things the agent
can do, others for things it can't, so evaluation results show a mix of good and poor scores.
"""
import json
import os
import random
import shutil
import subprocess
import sys
import textwrap
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.config import Config

AGENT_RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]
REGION = AGENT_RUNTIME_ARN.split(":")[3]
RUNTIME_ID = AGENT_RUNTIME_ARN.split("/")[-1]  # <runtime-name>-<suffix>
RUNTIME_NAME = RUNTIME_ID.rsplit("-", 1)[0]
# Runtime log group has the OTEL event records (prompts, responses), aws/spans has the spans
LOG_GROUPS = [f"/aws/bedrock-agentcore/runtimes/{RUNTIME_ID}-DEFAULT", "aws/spans"]
# Batch evaluation names must match [a-zA-Z][a-zA-Z0-9_]{0,47}
BATCH_NAME_PREFIX = f"{RUNTIME_NAME[:34]}_batch_"

INJECTION_SECONDS = 180
THREADS = 5
TRACES_TIMEOUT_SECONDS = 180
TRACES_POLL_INTERVAL_SECONDS = 15
EVALUATION_TIMEOUT_SECONDS = 600
POLL_INTERVAL_SECONDS = 15

# Built-in evaluators, ordered by how much they tell us about this customer support agent.
# A batch evaluation accepts up to 10 evaluators.
EVALUATORS = [
    "Builtin.GoalSuccessRate",        # SESSION   - did the customer get what they came for
    "Builtin.Helpfulness",            # TRACE     - how useful the response is to the customer
    "Builtin.ToolSelectionAccuracy",  # TOOL_CALL - picked the right tool for the request
    "Builtin.Faithfulness",           # TRACE     - response is supported by tool/KB results
    "Builtin.InstructionFollowing",   # TRACE     - follows the system prompt (e.g. plain text, no markdown)
    "Builtin.ToolParameterAccuracy",  # TOOL_CALL - extracted tool parameters correctly
    "Builtin.Refusal",                # TRACE     - declined or evaded the request
    "Builtin.Harmfulness",            # TRACE     - safety baseline
    "Builtin.ResponseRelevance",      # TRACE     - addresses the question asked
    "Builtin.Correctness",            # TRACE     - factual accuracy
]

CONVERSATIONS = json.loads((Path(__file__).parent / "evals_conversations.json").read_text())
REPORT_PATH = Path(__file__).resolve().parents[2] / "tmp" / "evals_results.txt"

agentcore = boto3.client("bedrock-agentcore", region_name=REGION, config=Config(read_timeout=120))
logs = boto3.client("logs", region_name=REGION)


def fmt_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# --- Injection ---------------------------------------------------------------

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.sessions_done = 0
        self.sessions_active = 0
        self.turns = 0
        self.errors = 0
        self.session_turns = {}  # session ID -> number of completed turns


class ConversationPool:
    """Hands out conversations in random order, reshuffling once all have been used."""

    def __init__(self, conversations):
        self.lock = threading.Lock()
        self.conversations = conversations
        self.queue = []

    def next(self):
        with self.lock:
            if not self.queue:
                self.queue = random.sample(self.conversations, len(self.conversations))
            return self.queue.pop()


def invoke_agent(session_id: str, prompt: str):
    response = agentcore.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": prompt}),
        contentType="application/json",
    )
    # Read the whole streamed response - we only need the agent to finish the turn
    response["response"].read()


def worker(deadline: float, pool: ConversationPool, stats: Stats):
    while time.time() < deadline:
        conversation = pool.next()
        # Each conversation is a separate runtime session. Session IDs must be at least 33 characters.
        session_id = f"evals-runner-{uuid.uuid4()}"
        with stats.lock:
            stats.sessions_active += 1

        completed_turns = 0
        for prompt in conversation["prompts"]:
            try:
                invoke_agent(session_id, prompt)
                completed_turns += 1
                with stats.lock:
                    stats.turns += 1
            except Exception:
                with stats.lock:
                    stats.errors += 1
                break

        with stats.lock:
            stats.sessions_active -= 1
            stats.sessions_done += 1
            if completed_turns:
                stats.session_turns[session_id] = completed_turns


def inject_conversations() -> dict[str, int]:
    print(f"Simulating customer conversations for {fmt_duration(INJECTION_SECONDS)} with {THREADS} concurrent sessions...")
    stats = Stats()
    pool = ConversationPool(CONVERSATIONS)
    start = time.time()
    deadline = start + INJECTION_SECONDS

    threads = [threading.Thread(target=worker, args=(deadline, pool, stats), daemon=True) for _ in range(THREADS)]
    for t in threads:
        t.start()

    while any(t.is_alive() for t in threads):
        now = time.time()
        with stats.lock:
            line = (
                f"[{fmt_duration(now - start)} elapsed | {fmt_duration(deadline - now)} left] "
                f"sessions: {stats.sessions_done} done, {stats.sessions_active} active | "
                f"requests: {stats.turns} ({stats.turns / (now - start):.2f}/s) | errors: {stats.errors}"
            )
        if now >= deadline:
            line += " | finishing active sessions..."
        print(f"\r{line:<130}", end="", flush=True)
        time.sleep(1)

    print(f"\nDone. Simulated {len(stats.session_turns)} conversations ({stats.turns} requests, {stats.errors} errors).")
    return stats.session_turns


# --- Waiting for traces ------------------------------------------------------

def run_logs_query(query: str, since: datetime) -> list[dict]:
    """Runs a CloudWatch Logs Insights query over the agent's log groups, from `since` until now."""
    query_id = logs.start_query(
        logGroupNames=LOG_GROUPS,
        startTime=int(since.timestamp()),
        endTime=int(datetime.now(timezone.utc).timestamp()),
        queryString=query,
    )["queryId"]
    while True:
        response = logs.get_query_results(queryId=query_id)
        if response["status"] not in ("Scheduled", "Running"):
            return [{field["field"]: field["value"] for field in row} for row in response["results"]]
        time.sleep(1)


def complete_sessions(session_turns: dict[str, int], since: datetime) -> set[str]:
    """
    Returns the sessions whose traces are fully visible in CloudWatch: one invoke_agent span per
    turn, and an OTEL event record (prompts, responses, tool calls) for every agent span.
    """
    rows = run_logs_query(
        "fields @log, attributes.session.id as sessionId, spanId, name"
        ' | filter scope.name = "strands.telemetry.tracer"'
        f" | filter attributes.session.id in {json.dumps(list(session_turns))}"
        " | limit 10000",
        since,
    )
    spans = {}    # session ID -> {span ID: span name}, from aws/spans
    records = {}  # session ID -> {span IDs that have event records}, from the runtime log group
    for row in rows:
        if row["@log"].endswith(":aws/spans"):
            spans.setdefault(row["sessionId"], {})[row["spanId"]] = row.get("name", "")
        else:
            records.setdefault(row["sessionId"], set()).add(row["spanId"])

    complete = set()
    for session_id, turns in session_turns.items():
        session_spans = spans.get(session_id, {})
        invocations = sum(1 for name in session_spans.values() if name.startswith("invoke_agent"))
        if invocations >= turns and session_spans.keys() <= records.get(session_id, set()):
            complete.add(session_id)
    return complete


def wait_for_traces(session_turns: dict[str, int], since: datetime):
    # Spans and event records take a few minutes to become queryable in CloudWatch.
    # Batch evaluation needs all of them, so wait until every conversation is complete.
    print("\nWaiting for the conversations' traces to become available in CloudWatch (typically 2-3 minutes)...")
    start = time.time()
    next_probe = start
    complete = 0
    while True:
        now = time.time()
        # Probe CloudWatch on the poll interval, but refresh the progress line every second
        if now >= next_probe:
            complete = len(complete_sessions(session_turns, since))
            next_probe = time.time() + TRACES_POLL_INTERVAL_SECONDS
            if complete == len(session_turns):
                print(
                    f"\r  [{fmt_duration(time.time() - start)}] "
                    f"All {complete} conversations have complete traces.{'':<30}"
                )
                return
        if now - start >= TRACES_TIMEOUT_SECONDS:
            print(
                f"\n  ⚠️ Not all traces are available after {TRACES_TIMEOUT_SECONDS // 60} minutes. Continuing anyway, "
                "batch evaluation will evaluate the incomplete conversations again."
            )
            return
        print(
            f"\r  [{fmt_duration(now - start)}] "
            f"{complete} of {len(session_turns)} conversations have complete traces "
            f"(next check in {max(0, round(next_probe - now))}s)  ",
            end="", flush=True,
        )
        time.sleep(1)


# --- Batch evaluation --------------------------------------------------------

def start_batch_evaluation(session_ids: list[str], since: datetime) -> str:
    response = agentcore.start_batch_evaluation(
        batchEvaluationName=f"{BATCH_NAME_PREFIX}{time.strftime('%H%M%S')}",
        evaluators=[{"evaluatorId": evaluator} for evaluator in EVALUATORS],
        dataSourceConfig={
            "cloudWatchLogs": {
                # Agents on AgentCore Runtime report their OTEL service name as <runtime-name>.<endpoint-name>
                "serviceNames": [f"{RUNTIME_NAME}.DEFAULT"],
                "logGroupNames": LOG_GROUPS,
                "filterConfig": {
                    "sessionIds": session_ids,
                    # Without a time range, the evaluation searches the last 7 days of logs
                    "timeRange": {"startTime": since, "endTime": datetime.now(timezone.utc)},
                },
            }
        },
    )
    return response["batchEvaluationId"]


def read_results(batch: dict) -> list[dict]:
    """Reads a batch evaluation's results (one record per score or error) from CloudWatch Logs."""
    output = batch["outputConfig"]["cloudWatchConfig"]
    results = []
    kwargs = {"logGroupName": output["logGroupName"], "logStreamName": output["logStreamName"], "startFromHead": True}
    while True:
        response = logs.get_log_events(**kwargs)
        results += [json.loads(event["message"]) for event in response["events"]]
        if response["nextForwardToken"] == kwargs.get("nextToken"):
            return results
        kwargs["nextToken"] = response["nextForwardToken"]


def add_scores(scores: dict, batch: dict) -> set[str]:
    """Adds a batch evaluation's scores to `scores`, and returns the sessions that had evaluation errors."""
    failed = set()
    for result in read_results(batch):
        attributes = result.get("attributes", {})
        if "error.type" in attributes:
            failed.add(attributes.get("session.id"))
        else:
            # A retried session is scored again, so keep one score per evaluator and scored item
            key = (attributes.get("session.id"), attributes.get("gen_ai.evaluation.name"),
                   result.get("traceId"), result.get("spanId"))
            scores[key] = result
    return failed


def latest_run_scores() -> dict | None:
    """Collects the scores of the batch evaluations started by the most recent run of this script."""
    batches = []
    kwargs = {}
    while True:
        response = agentcore.list_batch_evaluations(**kwargs)
        batches += [b for b in response["batchEvaluations"] if b["batchEvaluationName"].startswith(BATCH_NAME_PREFIX)]
        if "nextToken" not in response:
            break
        kwargs["nextToken"] = response["nextToken"]
    if not batches:
        return None

    # A run retries for at most EVALUATION_TIMEOUT_SECONDS, so its batches are that close to the latest one
    batches.sort(key=lambda b: b["createdAt"])
    run_start = batches[-1]["createdAt"] - timedelta(seconds=EVALUATION_TIMEOUT_SECONDS)
    scores = {}
    for summary in batches:
        if summary["createdAt"] >= run_start:
            add_scores(scores, agentcore.get_batch_evaluation(batchEvaluationId=summary["batchEvaluationId"]))
    return scores


def run_batch_evaluations(session_ids: list[str], since: datetime) -> dict | None:
    """Evaluates the sessions, retrying incomplete ones. Returns the scores, keyed by what was scored."""
    start = time.time()
    deadline = start + EVALUATION_TIMEOUT_SECONDS
    pending = session_ids
    scores = {}

    while time.time() < deadline:
        batch_id = start_batch_evaluation(pending, since)
        print(f"\nStarted batch evaluation {batch_id} for {len(pending)} sessions with {len(EVALUATORS)} evaluators")

        status, evaluated = "PENDING", 0
        next_probe = time.time() + POLL_INTERVAL_SECONDS
        while True:
            now = time.time()
            # Check the batch status on the poll interval, but refresh the progress line every second
            if now >= next_probe:
                batch = agentcore.get_batch_evaluation(batchEvaluationId=batch_id)
                status = batch["status"]
                evaluated = batch.get("evaluationResults", {}).get("numberOfSessionsCompleted", 0)
                next_probe = time.time() + POLL_INTERVAL_SECONDS
            line = f"\r  [{fmt_duration(now - start)}] {status}: {evaluated} of {len(pending)} sessions evaluated"
            if status not in ("PENDING", "IN_PROGRESS") or now >= deadline:
                print(f"{line}{'':<30}")
                break
            print(f"{line} (next check in {max(0, round(next_probe - now))}s)  ", end="", flush=True)
            time.sleep(1)

        if status not in ("COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"):
            return None

        failed = add_scores(scores, batch)
        if status == "COMPLETED":
            return scores

        # Spans and logs take a few minutes to become queryable in CloudWatch, so the most
        # recent sessions may not be complete yet. Evaluate those again.
        pending = sorted(failed & set(pending)) or pending
        print(f"  {len(pending)} sessions don't have complete trace data in CloudWatch yet, evaluating them again...")

    return None


def explanation(attributes: dict) -> str:
    return textwrap.fill(attributes["gen_ai.evaluation.explanation"], width=110,
                         initial_indent="    ", subsequent_indent="    ")


def scorecard_lines(scores: dict) -> list[str]:
    by_evaluator = {}
    for result in scores.values():
        attributes = result["attributes"]
        by_evaluator.setdefault(attributes["gen_ai.evaluation.name"], []).append(attributes["gen_ai.evaluation.score.value"])

    lines = [f"  {'Evaluator':<24}{'Average':>8}{'Scores':>8}"]
    for evaluator in EVALUATORS:
        values = by_evaluator.get(evaluator, [])
        if values:
            lines.append(f"  {evaluator.removeprefix('Builtin.'):<24}{sum(values) / len(values):>8.2f}{len(values):>8}")
    return lines


def lowest_score_lines(scores: dict) -> list[str]:
    by_evaluator = {}
    for result in scores.values():
        attributes = result["attributes"]
        by_evaluator.setdefault(attributes["gen_ai.evaluation.name"], []).append(attributes)

    # The lowest score of each evaluator, worst first. Refusal is left out: a high Refusal score
    # means the agent declined, which isn't better or worse by itself.
    lowest = sorted(
        (min(results, key=lambda a: a["gen_ai.evaluation.score.value"])
         for evaluator, results in by_evaluator.items() if evaluator != "Builtin.Refusal"),
        key=lambda a: a["gen_ai.evaluation.score.value"],
    )
    lines = []
    for a in lowest:
        lines += [
            f"  {a['gen_ai.evaluation.name'].removeprefix('Builtin.')}: "
            f"{a['gen_ai.evaluation.score.value']:.2f} ({a['gen_ai.evaluation.score.label']}), "
            f"lowest of {len(by_evaluator[a['gen_ai.evaluation.name']])} scores, in session {a['session.id']}",
            explanation(a),
            "",
        ]
    return lines


def section(title: str) -> list[str]:
    return ["", "=" * 110, title, "=" * 110, ""]


def write_report(scores: dict) -> Path:
    """Writes the scorecard and the lowest score of each evaluator with the judge's explanation."""
    lines = [
        f"AgentCore Evaluations results for {RUNTIME_NAME} - {datetime.now():%Y-%m-%d %H:%M}",
        *section(f"1. Scorecard ({len(scores)} scores, from 0 = worst to 1 = best)"),
        *scorecard_lines(scores),
        *section("2. Lowest score of each evaluator, with the judge's explanation"),
        *lowest_score_lines(scores),
    ]
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    return REPORT_PATH


def open_in_editor(path: Path) -> bool:
    """Opens the file in the running VS Code / Code Editor window, if the script runs in its terminal."""
    if os.environ.get("TERM_PROGRAM") != "vscode":
        return False
    for cli in ("code", "code-editor-server", "code-server"):
        if shutil.which(cli):
            try:
                if subprocess.run([cli, str(path)], capture_output=True, timeout=15).returncode == 0:
                    return True
            except (OSError, subprocess.TimeoutExpired):
                pass
    return False


def save_results(scores: dict):
    path = write_report(scores)
    print(f"\nResults are stored in {path}")
    if open_in_editor(path):
        print("Opened the results in the editor.")


def show_latest_results():
    scores = latest_run_scores()
    if not scores:
        print("❌ No batch evaluation results found. Run the script without --results-only first.")
        return
    save_results(scores)


def run():
    # --results-only: skip the conversations and evaluation, show the results of the latest run
    if "--results-only" in sys.argv:
        show_latest_results()
        return

    print(
        "\n\n"
        "So glad you made it this far in the workshop! It's time to see AgentCore Evaluations in action!\n\n"
        "This script will do a few things:\n\n"
        f"1. Simulate customer conversations with your agent (~{max(1, round(INJECTION_SECONDS / 60))} min).\n"
        f"   {THREADS} concurrent customers, 3 messages each, picked at random from {len(CONVERSATIONS)} scenarios.\n"
        "   Some ask for things the agent can do, others for things it can't, or shouldn't.\n"
        "2. Wait until the conversations' traces are available in CloudWatch "
        f"(up to {TRACES_TIMEOUT_SECONDS // 60} minutes).\n"
        "3. Run an AgentCore Evaluations batch evaluation over those conversations (~1-2 minutes).\n"
        f"   {len(EVALUATORS)} built-in evaluators score each conversation, response, and tool call.\n"
        "4. Save a summary of the results, with the judge's explanation for the lowest scores, to tmp/evals_results.txt.\n\n"
        f"AgentCore Runtime ARN: {AGENT_RUNTIME_ARN}\n"
    )
    input("Press ENTER when ready to start...")
    print()

    # Look for the conversations' traces from shortly before they started
    since = datetime.now(timezone.utc) - timedelta(minutes=1)
    session_turns = inject_conversations()
    if not session_turns:
        print("❌ No conversations completed, nothing to evaluate.")
        return

    wait_for_traces(session_turns, since)
    session_ids = list(session_turns)

    input("\nPress Enter to start batch evaluations...")

    scores = run_batch_evaluations(session_ids, since)
    if scores is not None:
        save_results(scores)
        print(
            f"\n✅ Evaluation results are ready for {len(session_ids)} conversations.\n\n"
            "You can now proceed with the workshop instructions."
        )
    else:
        print(
            f"\n❌ Evaluation results weren't ready within {EVALUATION_TIMEOUT_SECONDS // 60} minutes.\n"
            "\nThis is not expected. Check the batch evaluation status with below command and ask workshop facilitator for help:\n"
            f"  aws bedrock-agentcore list-batch-evaluations --region {REGION}"
        )


if __name__ == "__main__":
    run()

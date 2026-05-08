import sys
from pathlib import Path

from transport import AgentTransport

TMP_DIR = Path(__file__).parent.parent / "tmp"

def handle_auth(transport: AgentTransport):
    auth_url = transport.initialize()
    if auth_url:
        print(f"\nAuthorization required.")
        print(f"Open this URL in your browser:\n\n  {auth_url}\n")
        print("After authorizing, paste the session_id from the callback here.")
        session_id = input("session_id: ").strip()
        if not session_id:
            print("No session_id provided. Exiting.")
            sys.exit(1)
        transport.complete_auth(session_id)
        print("Authorization complete.\n")

def chat_loop(transport: AgentTransport):
    print("Connected! Type your question or 'exit' to quit.\n")
    while True:
        try:
            prompt = input("Your question (or 'exit' to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not prompt:
            continue
        if prompt.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        print("Waiting for agent response...\n")
        print(f"Agent: {transport.send_prompt(prompt)}\n")

def main():
    is_remote = "remote" in sys.argv[1:]

    print("-" * 20)
    print("Welcome to AwesomeCorp HR agent")
    print(f"Mode: {'remote (AgentCore)' if is_remote else 'local (localhost:8080)'}")
    print("-" * 20)
    print("Connecting to agent...")

    if is_remote:
        from transport_remote import RemoteTransport
        agent_runtime_arn = (TMP_DIR / "agent_runtime_arn.txt").read_text().strip()
        transport = RemoteTransport(agent_runtime_arn=agent_runtime_arn)
        print(f"Runtime ARN: {transport.agent_runtime_arn}")
        print(f"Session ID:  {transport.session_id}")
    else:
        from transport_local import LocalTransport
        transport = LocalTransport()

    handle_auth(transport)
    chat_loop(transport)

if __name__ == "__main__":
    main()

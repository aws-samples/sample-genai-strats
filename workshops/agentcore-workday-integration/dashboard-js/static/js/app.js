const USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/149/149071.png";
const BOT_AVATAR  = "images/workday-logo-small.png";
const EXAMPLES = {
  mcp: [
    "How can you help me?",
    "How many workers do we have, and how many open positions by job type?",
    "Who's on the Sales & Marketing team, and has anyone been recognized?",
    "Give Amy Frost Teamwork feedback for staying calm under pressure."
  ],
  a2a: [
    "Who are you?",
    "How can you help me?",
    "What's my PTO balance?",
    "Which department am I in?",
    "What's my employment start date?"
  ]
};

let authUrl = null;

const escapeHtml = (t) => $("<div>").text(t).html();

// Agent replies are markdown. Rendered with marked, then sanitized with DOMPurify, because the
// text includes data returned by Workday. Falls back to plain text if either library failed to load.
const hasMarkdown = typeof marked !== "undefined" && typeof DOMPurify !== "undefined";
if (hasMarkdown) {
  DOMPurify.addHook("afterSanitizeAttributes", (node) => {
    if (node.tagName === "A") {
      node.setAttribute("target", "_blank");
      node.setAttribute("rel", "noopener noreferrer");
    }
  });
}
const renderMarkdown = (t) => hasMarkdown
  ? DOMPurify.sanitize(marked.parse(t, { gfm: true, breaks: true }), { FORBID_TAGS: ["img"] })
  : escapeHtml(t).replace(/\n/g, "<br>");

function appendMsg(role, html) {
  const isUser = role === "user";
  const avatar  = isUser ? USER_AVATAR : BOT_AVATAR;
  const cls     = isUser ? "msg-user" : "msg-bot";
  const dir     = isUser ? "justify-content-end" : "justify-content-start";
  $("#chat-empty").remove();
  $("#chat-box").append(`
    <div class="d-flex ${dir} align-items-end gap-2 mb-2 ${cls}">
      ${!isUser ? `<img src="${avatar}" alt="bot">` : ""}
      <div class="bubble">${html}</div>
      ${isUser  ? `<img src="${avatar}" alt="user">` : ""}
    </div>`).scrollTop(1e9);
}

const PAGE_HEADERS = {
  a2a: "AWSome HR Agent — Amazon Bedrock AgentCore + Workday via A2A",
  mcp: "AWSome HR Agent — Amazon Bedrock AgentCore + Workday via MCP"
};

function showChat(agentMode) {
  $("#overlay").hide();
  $("#page-header").text(PAGE_HEADERS[agentMode] || PAGE_HEADERS.a2a);
  const examples = EXAMPLES[agentMode] || EXAMPLES.a2a;
  examples.forEach(ex => {
    $("#examples").append($('<button class="btn btn-sm btn-outline-secondary example-btn">').text(ex));
  });
  $("#chat-input").focus();
}

// Initialize on page load
$.post("/app/api/init")
  .done(data => {
    if (data.status === "ok") {
      $("#chat-form button[type=submit]").text(`Send (${data.agent_mode})`);
      showChat(data.agent_mode);
    } else {
      authUrl = data.auth_url;
      $("#ov-connecting").hide();
      $("#ov-login").show();
    }
  })
  .fail(() => {
    $("#ov-connecting").html('<p class="text-danger">Failed to connect to agent.</p>');
  });

$("#btn-login").on("click", () => {
  if (authUrl) window.location.href = authUrl;
});

// Renders the streamed reply into the last bot bubble:
// tool calls (muted), the reply text, an error if any, and a status line while the agent works.
function renderReply(reply) {
  const tools = reply.tools.length
    ? `<div class="tool-calls">${reply.tools.map(t => `&#9881; ${escapeHtml(t)}`).join("<br>")}</div>`
    : "";
  const text = `<div class="reply-text">${reply.text ? renderMarkdown(reply.text) : ""}</div>`;
  const error = reply.error ? `<div class="reply-error">${escapeHtml(reply.error)}</div>` : "";
  const status = reply.status
    ? `<div class="status"><span class="typing"><span></span><span></span><span></span></span>${escapeHtml(reply.status)}</div>`
    : "";
  $("#chat-box .msg-bot:last .bubble").html(tools + text + error + status);
  $("#chat-box").scrollTop(1e9);
}

// Applies one agent event ({delta}, {tool}, {error}, {done}) to the reply.
function applyEvent(reply, event) {
  if (event.delta) {
    reply.text += event.delta;
    reply.status = null;
  }
  if (event.tool) {
    reply.tools.push(event.tool);
    reply.status = `Calling ${event.tool}`;
  }
  if (event.error) {
    reply.error = event.error;
    reply.status = null;
  }
  if (event.done) {
    reply.status = null;
  }
}

$(document).on("click", ".example-btn", function () {
  $("#chat-input").val($(this).text());
  $("#chat-form").trigger("submit");
});

$("#chat-form").on("submit", function (e) {
  e.preventDefault();
  const msg = $("#chat-input").val().trim();
  if (!msg) return;
  $("#chat-input").val("").prop("disabled", true);
  $("#chat-form button[type=submit]").prop("disabled", true);
  appendMsg("user", escapeHtml(msg));
  appendMsg("bot", "");

  const reply = { text: "", tools: [], error: null, status: "Thinking" };
  renderReply(reply);

  fetch("/app/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  }).then(res => {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    function pump() {
      return reader.read().then(({ done, value }) => {
        if (done) return;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const event = JSON.parse(line.slice(6));
          if (!(event.delta || event.tool || event.error || event.done)) continue; // keepAlive
          applyEvent(reply, event);
          renderReply(reply);
        }
        return pump();
      });
    }
    return pump();
  }).catch(() => {
    reply.error = "Error communicating with agent. Try again.";
  }).finally(() => {
    reply.status = null;
    if (!reply.text && !reply.error) reply.error = "No response from agent. Try again.";
    renderReply(reply);
    $("#chat-input").prop("disabled", false);
    $("#chat-form button[type=submit]").prop("disabled", false);
    $("#chat-input").focus();
  });
});

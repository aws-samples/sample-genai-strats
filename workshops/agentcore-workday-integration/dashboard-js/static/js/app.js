const USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/149/149071.png";
const BOT_AVATAR  = "images/workday-logo-small.png";
const EXAMPLES = {
  // mcp: [
  //   "How can you help me?",
  //   "How many workers are in the system?",
  //   "What positions are currently open?",
  //   "Check Logan McNeil’s succession plan"
  // ],
  mcp:[
    "How can you help me?",
    "SENTINEL, how many operatives are active and what’s the horde score??",
    "SENTINEL, how many open positions are in the system? Break it down by job type.",
    "SENTINEL, map the active mentorship network. Who has development coverage right now — show me the active pairs and their mentorship IDs (mentorships with no end date)?",
    "SENTINEL, from the mentorship network you just mapped, identify the mentee whose field readiness most needs reinforcement. Fortify their record — add a Joel-style: disciplined resilience and protective instinct under sustained pressure-style comment. This operative will not face the horde unprepared"
  ],
  a2a: [
    "How can you help me?",
    "What's my PTO balance?",
    "Which department am I in?",
    "What's my employment start date?"
  ]
};

let authUrl = null;

function appendMsg(role, text) {
  const isUser = role === "user";
  const avatar  = isUser ? USER_AVATAR : BOT_AVATAR;
  const cls     = isUser ? "msg-user" : "msg-bot";
  const dir     = isUser ? "justify-content-end" : "justify-content-start";
  const escaped = $("<div>").text(text).html();
  const html = `
    <div class="d-flex ${dir} align-items-end gap-2 mb-2 ${cls}">
      ${!isUser ? `<img src="${avatar}" alt="bot">` : ""}
      <div class="bubble">${escaped}</div>
      ${isUser  ? `<img src="${avatar}" alt="user">` : ""}
    </div>`;
  $("#chat-box").append(html).scrollTop(1e9);
}

const PAGE_HEADERS = {
  a2a: "AWSome HR Agent — Amazon Bedrock AgentCore + Workday via A2A",
  mcp: "SENTINEL — Amazon Bedrock AgentCore + Workday via MCP"
};

function showChat(agentMode) {
  $("#overlay").hide();
  $("#page-header").text(PAGE_HEADERS[agentMode] || PAGE_HEADERS.a2a);
  const examples = EXAMPLES[agentMode] || EXAMPLES.a2a;
  examples.forEach(ex => {
    $("#examples").append(`<button class="btn btn-sm btn-outline-secondary example-btn">${ex}</button>`);
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

const waitingModal = new bootstrap.Modal($("#waiting-modal")[0]);

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
  waitingModal.show();
  appendMsg("user", msg);
  appendMsg("bot", "…");
  $.ajax({
    url: "/app/api/chat",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ message: msg }),
    dataType: "json"
  })
    .done(data => {
      const text = data.response || "Error. Try again.";
      const html = $("<div>").text(text).html().replace(/\n/g, "<br>");
      $("#chat-box .msg-bot:last .bubble").html(html);
    })
    .fail(() => {
      $("#chat-box .msg-bot:last .bubble").text("Error communicating with agent. Try again.");
    })
    .always(() => {
      waitingModal.hide();
      $("#chat-input").prop("disabled", false);
      $("#chat-form button[type=submit]").prop("disabled", false);
      $("#chat-input").focus();
      $("#chat-box").scrollTop(1e9);
    });
});

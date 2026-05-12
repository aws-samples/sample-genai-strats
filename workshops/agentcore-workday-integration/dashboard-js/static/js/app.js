const USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/149/149071.png";
const BOT_AVATAR  = "https://cdn-icons-png.flaticon.com/512/4712/4712042.png";
const EXAMPLES = [
  "How can you help me?",
  "What's my PTO balance?",
  "Which department am I in?",
  "What's my employment start date?"
];

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

function showChat() {
  $("#overlay").hide();
  EXAMPLES.forEach(ex => {
    $("#examples").append(`<button class="btn btn-sm btn-outline-secondary example-btn">${ex}</button>`);
  });
  $("#chat-input").focus();
}

// Initialize on page load
$.post("/app/api/init")
  .done(data => {
    if (data.status === "ok") {
      showChat();
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
      $("#chat-box .msg-bot:last .bubble").text(data.response || "Error. Try again.");
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

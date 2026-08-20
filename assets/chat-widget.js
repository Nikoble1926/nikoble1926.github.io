/* PlugInSolarHub chat widget - vanilla JS, no deps.
   Talks to /api/chat (AI Search over this site's pages only). */
(function () {
  "use strict";
  if (window.__pshChat) return; window.__pshChat = 1;

  var css = ""
    + "#psh-chat-btn{position:fixed;bottom:18px;right:18px;z-index:9999;background:#0ea5e9;color:#fff;"
    + "border:none;border-radius:24px;padding:11px 17px;font:600 14px/1 system-ui,sans-serif;cursor:pointer;"
    + "box-shadow:0 3px 12px rgba(0,0,0,.25)}"
    + "#psh-chat-btn:hover{background:#0284c7}"
    + "#psh-chat{position:fixed;bottom:70px;right:18px;z-index:9999;width:min(360px,calc(100vw - 28px));"
    + "max-height:70vh;display:none;flex-direction:column;background:#fff;color:#111;border:1px solid #d1d5db;"
    + "border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.3);font:14px/1.45 system-ui,sans-serif;overflow:hidden}"
    + "#psh-chat.open{display:flex}"
    + "#psh-chat header{background:#0ea5e9;color:#fff;padding:10px 12px;font-weight:600;display:flex;justify-content:space-between;align-items:center}"
    + "#psh-chat header button{background:none;border:none;color:#fff;font-size:18px;cursor:pointer;line-height:1}"
    + "#psh-log{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px}"
    + ".psh-m{padding:8px 11px;border-radius:10px;max-width:88%;white-space:pre-wrap;word-wrap:break-word}"
    + ".psh-q{align-self:flex-end;background:#e0f2fe}"
    + ".psh-a{align-self:flex-start;background:#f3f4f6}"
    + ".psh-a a{color:#0369a1;word-break:break-all}"
    + ".psh-src{font-size:12px;margin-top:6px}"
    + "#psh-form{display:flex;gap:6px;padding:10px;border-top:1px solid #e5e7eb}"
    + "#psh-in{flex:1;border:1px solid #d1d5db;border-radius:8px;padding:8px 10px;font:inherit}"
    + "#psh-send{background:#0ea5e9;color:#fff;border:none;border-radius:8px;padding:8px 14px;font:inherit;cursor:pointer}"
    + "#psh-send[disabled]{opacity:.5;cursor:wait}"
    + "#psh-note{font-size:11px;color:#6b7280;text-align:center;padding:0 10px 8px}";

  var style = document.createElement("style"); style.textContent = css;
  document.head.appendChild(style);

  var btn = document.createElement("button");
  btn.id = "psh-chat-btn"; btn.type = "button";
  btn.textContent = "Ask about plug-in solar";
  document.body.appendChild(btn);

  var panel = document.createElement("div"); panel.id = "psh-chat";
  panel.innerHTML = '<header><span>Ask about plug-in solar</span>'
    + '<button type="button" id="psh-x" aria-label="Close">×</button></header>'
    + '<div id="psh-log"></div>'
    + '<form id="psh-form"><input id="psh-in" maxlength="300" placeholder="e.g. Is plug-in solar legal in Kansas?" autocomplete="off">'
    + '<button id="psh-send" type="submit">Ask</button></form>'
    + '<div id="psh-note">Answers come only from this site’s verified pages.</div>';
  document.body.appendChild(panel);

  var log = panel.querySelector("#psh-log");
  var form = panel.querySelector("#psh-form");
  var input = panel.querySelector("#psh-in");
  var send = panel.querySelector("#psh-send");

  btn.addEventListener("click", function () { panel.classList.toggle("open"); if (panel.classList.contains("open")) input.focus(); });
  panel.querySelector("#psh-x").addEventListener("click", function () { panel.classList.remove("open"); });

  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

  function add(kind, text, sources) {
    var m = document.createElement("div"); m.className = "psh-m psh-" + kind;
    m.innerHTML = esc(text);
    if (sources && sources.length) {
      var s = document.createElement("div"); s.className = "psh-src";
      s.appendChild(document.createTextNode("Sources: "));
      sources.forEach(function (u, i) {
        if (i) s.appendChild(document.createTextNode(" · "));
        var a = document.createElement("a"); a.href = u; a.target = "_blank"; a.rel = "noopener";
        a.textContent = u.replace("https://pluginsolarhub.org", "");
        s.appendChild(a);
      });
      m.appendChild(s);
    }
    log.appendChild(m); log.scrollTop = log.scrollHeight;
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var q = input.value.trim();
    if (!q || send.disabled) return;
    add("q", q); input.value = ""; send.disabled = true;
    fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question: q })
    }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, status: r.status, j: j }; }); })
      .then(function (res) {
        if (res.ok) add("a", res.j.answer || "", res.j.sources || []);
        else if (res.status === 429) add("a", "Slow down a little — 10 questions per minute is the limit.");
        else add("a", "Something went wrong (" + (res.j.error || res.status) + "). Try again.");
      })
      .catch(function () { add("a", "Network error — try again."); })
      .then(function () { send.disabled = false; input.focus(); });
  });
})();

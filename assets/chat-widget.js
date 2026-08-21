/* PlugInSolarHub - Solar Assistant widget v2 (per Figma "Chat Widget v2").
   Vanilla JS, no deps. Talks to /api/chat. Sources arrive as [{url,title}].
   All non-ASCII glyphs are HTML entities / escapes so encoding round-trips safely. */
(function () {
  "use strict";
  if (window.__pshChat) return; window.__pshChat = 2;

  var css = ""
    /* launcher: orange pill, soft glow, hover lift */
    + "#psh-chat-btn{position:fixed;bottom:18px;right:18px;z-index:9999;background:#f59e0b;color:#10141b;"
    + "border:none;border-radius:24px;padding:12px 20px;font:600 14px/1 system-ui,sans-serif;cursor:pointer;"
    + "box-shadow:0 0 18px rgba(245,158,11,.45),0 3px 10px rgba(0,0,0,.35);transition:transform .15s ease,box-shadow .15s ease}"
    + "#psh-chat-btn:hover{transform:translateY(-2px);box-shadow:0 0 26px rgba(245,158,11,.6),0 6px 14px rgba(0,0,0,.4)}"
    /* panel */
    + "#psh-chat{position:fixed;bottom:74px;right:18px;z-index:9999;width:min(380px,calc(100vw - 28px));"
    + "max-height:72vh;display:none;flex-direction:column;background:#161b24;color:#e5e7eb;border:1px solid #2b3444;"
    + "border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.55);font:14px/1.5 system-ui,sans-serif;overflow:hidden;"
    + "opacity:0;transform:translateY(14px)}"
    + "#psh-chat.open{display:flex;animation:pshin .2s ease forwards}"
    + "@keyframes pshin{to{opacity:1;transform:translateY(0)}}"
    + "@media(prefers-reduced-motion:reduce){#psh-chat.open{animation:none;opacity:1;transform:none}"
    + "#psh-chat-btn{transition:none}.psh-dots span{animation:none!important;opacity:.8}}"
    /* header */
    + "#psh-hd{background:#10141b;padding:12px 14px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #2b3444}"
    + "#psh-sun{width:34px;height:34px;border-radius:50%;background:#f59e0b;display:flex;align-items:center;"
    + "justify-content:center;font-size:17px;flex:0 0 34px;color:#10141b}"
    + "#psh-ttl{flex:1;min-width:0}"
    + "#psh-ttl b{display:block;font-size:15px;font-weight:600;color:#e5e7eb}"
    + "#psh-ttl span{display:block;font-size:11px;color:#34d399;margin-top:1px}"
    + "#psh-x{background:none;border:none;color:#9ca3af;font-size:19px;cursor:pointer;line-height:1;padding:4px}"
    + "#psh-x:hover{color:#e5e7eb}"
    /* log + bubbles */
    + "#psh-log{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#161b24}"
    + ".psh-m{padding:9px 13px;border-radius:14px;max-width:86%;white-space:pre-wrap;word-wrap:break-word;font-size:14px}"
    + ".psh-q{align-self:flex-end;background:#2a3547;border-bottom-right-radius:4px}"
    + ".psh-a{align-self:flex-start;background:#1f2733;border-bottom-left-radius:4px}"
    /* source chips */
    + ".psh-src{display:flex;flex-wrap:wrap;gap:6px;align-self:flex-start;max-width:88%}"
    + ".psh-chip{display:inline-flex;align-items:center;gap:5px;border:1px solid #f59e0b;color:#f59e0b!important;"
    + "border-radius:24px;padding:4px 11px;font-size:12px;text-decoration:none;background:transparent;transition:background .12s}"
    + ".psh-chip:hover{background:rgba(245,158,11,.12)}"
    /* typing dots */
    + ".psh-dots{align-self:flex-start;background:#1f2733;border-radius:14px;border-bottom-left-radius:4px;"
    + "padding:11px 14px;display:inline-flex;gap:5px}"
    + ".psh-dots span{width:7px;height:7px;border-radius:50%;background:#f59e0b;display:inline-block;"
    + "animation:pshdot 1.1s ease-in-out infinite}"
    + ".psh-dots span:nth-child(2){animation-delay:.18s}.psh-dots span:nth-child(3){animation-delay:.36s;background:#4b5563}"
    + "@keyframes pshdot{0%,100%{opacity:.35;transform:translateY(0)}50%{opacity:1;transform:translateY(-3px)}}"
    /* input row */
    + "#psh-form{display:flex;gap:8px;padding:12px;background:#10141b;border-top:1px solid #2b3444;align-items:center}"
    + "#psh-in{flex:1;border:1px solid #2b3444;background:#161b24;color:#e5e7eb;border-radius:24px;"
    + "padding:10px 15px;font:inherit;outline:none}"
    + "#psh-in::placeholder{color:#9ca3af}"
    + "#psh-in:focus{border-color:#f59e0b}"
    + "#psh-send{background:#f59e0b;color:#10141b;border:none;border-radius:24px;width:42px;height:42px;"
    + "font-size:19px;font-weight:700;cursor:pointer;flex:0 0 42px;display:flex;align-items:center;justify-content:center}"
    + "#psh-send[disabled]{opacity:.5;cursor:wait}"
    /* suggestions */
    + "#psh-sugg{padding:2px 0}"
    + "#psh-sugg .psh-sh{font-size:12px;color:#9ca3af;margin:2px 0 8px}"
    + "#psh-sugg .psh-chip{margin:0 6px 6px 0;cursor:pointer}"
    /* mobile */
    + "@media(max-width:480px){#psh-chat{width:calc(100vw - 16px);right:8px;max-height:70vh}}";

  var style = document.createElement("style"); style.textContent = css;
  document.head.appendChild(style);

  var btn = document.createElement("button");
  btn.id = "psh-chat-btn"; btn.type = "button";
  btn.innerHTML = "&#9728; Ask Solar Assistant"; /* sun glyph */
  document.body.appendChild(btn);

  var panel = document.createElement("div"); panel.id = "psh-chat";
  panel.innerHTML =
      '<div id="psh-hd"><div id="psh-sun">&#9728;</div>'
    + '<div id="psh-ttl"><b>Solar Assistant</b><span>&#9679; Answers only from verified pages</span></div>'
    + '<button type="button" id="psh-x" aria-label="Close">&#10005;</button></div>'
    + '<div id="psh-log"></div>'
    + '<form id="psh-form"><input id="psh-in" maxlength="300" placeholder="Ask anything about plug-in solar&#8230;" autocomplete="off">'
    + '<button id="psh-send" type="submit" aria-label="Send">&#8594;&#xFE0E;</button></form>';
  document.body.appendChild(panel);

  var log = panel.querySelector("#psh-log");
  var form = panel.querySelector("#psh-form");
  var input = panel.querySelector("#psh-in");
  var send = panel.querySelector("#psh-send");

  // Popular questions: fetched once, shown while the log is empty, hidden after
  // the first question. 8 random picks per open (rotation).
  var suggBox = null, suggLoaded = false;
  function killSugg() { if (suggBox) { suggBox.remove(); suggBox = null; } }
  function showSugg() {
    if (log.children.length || suggBox) return;
    fetch("/api/chat/suggestions").then(function (r) { return r.json(); }).then(function (j) {
      if (suggLoaded || log.children.length) return;
      var qs = (j.suggestions || []).slice();
      for (var i = qs.length - 1; i > 0; i--) { var k = Math.floor(Math.random() * (i + 1)); var t = qs[i]; qs[i] = qs[k]; qs[k] = t; }
      qs = qs.slice(0, 8);
      if (!qs.length) return;
      suggLoaded = true;
      suggBox = document.createElement("div"); suggBox.id = "psh-sugg";
      var h = document.createElement("div"); h.className = "psh-sh"; h.textContent = "Popular questions";
      suggBox.appendChild(h);
      qs.forEach(function (q) {
        var c = document.createElement("a"); c.className = "psh-chip"; c.textContent = q;
        c.addEventListener("click", function () { input.value = q; form.dispatchEvent(new Event("submit", { cancelable: true })); });
        suggBox.appendChild(c);
      });
      log.appendChild(suggBox);
    }).catch(function () {});
  }

  btn.addEventListener("click", function () {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) { input.focus(); showSugg(); }
  });
  panel.querySelector("#psh-x").addEventListener("click", function () { panel.classList.remove("open"); });

  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

  function addMsg(kind, text) {
    var m = document.createElement("div"); m.className = "psh-m psh-" + kind;
    m.innerHTML = esc(text);
    log.appendChild(m); log.scrollTop = log.scrollHeight;
  }
  function addChips(sources) {
    if (!sources || !sources.length) return;
    var row = document.createElement("div"); row.className = "psh-src";
    sources.forEach(function (s) {
      var url = (typeof s === "string") ? s : s.url;
      var title = (typeof s === "string") ? s.replace("https://pluginsolarhub.org", "") : (s.title || "Verified page");
      var a = document.createElement("a"); a.className = "psh-chip";
      a.href = url; a.target = "_blank"; a.rel = "noopener";
      a.innerHTML = "&#128196; " + esc(title); /* page icon */
      row.appendChild(a);
    });
    log.appendChild(row); log.scrollTop = log.scrollHeight;
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var q = input.value.trim();
    if (!q || send.disabled) return;
    killSugg();
    addMsg("q", q); input.value = ""; send.disabled = true;

    var wait = document.createElement("div");
    wait.className = "psh-dots";
    wait.innerHTML = "<span></span><span></span><span></span>";
    log.appendChild(wait); log.scrollTop = log.scrollHeight;
    function clearWait() { if (wait) { wait.remove(); wait = null; } }

    var ctrl = ("AbortController" in window) ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 75000);

    fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question: q }),
      signal: ctrl ? ctrl.signal : undefined
    }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, status: r.status, j: j }; }); })
      .then(function (res) {
        clearWait();
        if (res.ok) { addMsg("a", res.j.answer || ""); addChips(res.j.sources); }
        else if (res.status === 503) addMsg("a", res.j.answer || "The assistant is busy right now - please try again in a few seconds.");
        else if (res.status === 429) addMsg("a", "Slow down a little - 10 questions per minute is the limit.");
        else addMsg("a", "Something went wrong (" + (res.j.error || res.status) + "). Try again.");
      })
      .catch(function (e) {
        clearWait();
        if (e && e.name === "AbortError") addMsg("a", "Taking too long - try again.");
        else addMsg("a", "Network error - try again.");
      })
      .then(function () { clearTimeout(timer); send.disabled = false; input.focus(); });
  });
})();

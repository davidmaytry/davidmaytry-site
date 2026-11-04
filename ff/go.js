// Short links davidmaytry.com/ff/<network>/ -> Flurry Fray on Steam, with a utm mark.
// One script for every page in ff/. A page only says which network it is
// (data-source on <html>; if missing, the folder name after /ff/ is used).
//
//   PC browser          try the Steam app (steam://openurl/...), and if the page
//                       does not lose focus in ~1.5 s, go to the store page instead.
//   phone, in-app       straight to the store page: custom schemes are blocked there,
//   browser, Steam      and the Steam app on a phone picks up store links by itself.
//
// Add #check to the address to see what this device would do, without leaving.
(function () {
  var STORE = "https://store.steampowered.com/app/5411930/FlurryFray/";
  var FOLDERS = { tt: "tiktok", ig: "instagram", yt: "youtube", x: "x", rd: "reddit", th: "threads" };
  var WAIT_MS = 1500;

  var root = document.documentElement;
  var source = root.getAttribute("data-source");
  if (!source) {
    var m = location.pathname.match(/\/ff\/([a-z]+)\/?/);
    source = (m && FOLDERS[m[1]]) || "site";
  }
  var web = STORE + "?utm_source=" + encodeURIComponent(source) +
    (source === "site" ? "" : "&utm_medium=social") + "&utm_campaign=shortlink";
  // The Steam client takes everything after "steam://openurl/" as the address, query
  // included, so the store link goes in as is (encoding it would hide the ?/& from Steam).
  var app = "steam://openurl/" + web;

  var ua = navigator.userAgent || "";
  var inApp = /FBAN|FBAV|FB_IAB|FBIOS|FB4A|Instagram|Barcelona|Threads|TikTok|musical_ly|Bytedance|trill_|Twitter|Reddit|Snapchat|Line\/|; wv\)/i.test(ua);
  var phone = /Android|iPhone|iPad|iPod|Mobile|Silk|Kindle|BlackBerry|Opera Mini|IEMobile/i.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);   // iPad that says it is a Mac
  var inSteam = /Valve Steam|Steam Client|GameOverlay/i.test(ua);
  var path = inSteam ? "steam-browser" : inApp ? "in-app" : phone ? "phone" : "pc";

  var openWeb = document.getElementById("open-web");
  var openApp = document.getElementById("open-app");
  var status = document.getElementById("status");
  openWeb.href = web;
  openApp.href = app;
  root.classList.add("js", "path-" + path);

  if (location.hash === "#check") {
    root.classList.add("checking");
    status.textContent = "Check: " + path;
    var out = document.getElementById("check-out");
    out.hidden = false;
    out.textContent = (path === "pc" ? "1) " + app + "\n2) after " + WAIT_MS / 1000 + " s, if still here: " : "") +
      web + "\n\n" + ua;
    return;
  }

  function settle(text) {
    status.textContent = text;
    root.classList.add("settled");
  }
  function goWeb() { location.replace(web); }   // replace: Back returns to the post, not here

  // Back from the store page can bring this page back from the cache: show the buttons, do nothing.
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) settle("Flurry Fray is on Steam");
  });

  if (path !== "pc") { goWeb(); return; }

  var timer = setTimeout(goWeb, WAIT_MS);
  function left() {
    // the Steam app took focus, or the browser is asking "Open Steam?": stay put, so the
    // question is not swept away, and leave both buttons on the page
    if (!timer) return;
    clearTimeout(timer);
    timer = 0;
    settle("Opened in Steam?");
  }
  window.addEventListener("blur", left);
  document.addEventListener("visibilitychange", function () { if (document.hidden) left(); });
  if (/Firefox\//.test(ua)) {
    // Firefox swaps the whole page for an error page when no app takes the scheme,
    // which would kill the timer above; from a hidden frame only the frame breaks.
    var frame = document.createElement("iframe");
    frame.hidden = true;
    frame.src = app;
    document.body.appendChild(frame);
  } else {
    location.href = app;
  }
})();

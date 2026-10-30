// Fills the page from window.SITE (config.js) and draws the hand-made paper look.
// No content lives here.
(function () {
  var S = window.SITE;
  var root = document.documentElement;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)");
  root.classList.add("js");

  // ---------- text from config ----------
  document.querySelectorAll("[data-site]").forEach(function (n) {
    var key = n.getAttribute("data-site");
    if (S[key] != null) n.textContent = S[key];
  });
  document.querySelectorAll("[data-site-alt]").forEach(function (n) {
    n.alt = S[n.getAttribute("data-site-alt")] || n.alt;
  });
  document.getElementById("email").href = "mailto:" + S.email;
  document.getElementById("year").textContent = new Date().getFullYear();

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function sticker(name, w, h, cls) {
    var pic = el("picture", cls);
    var dark = el("source");
    dark.srcset = "assets/brand/" + name + "-dark.webp";
    dark.media = "(prefers-color-scheme: dark)";
    var img = el("img");
    img.src = "assets/brand/" + name + "-light.webp";
    img.alt = "";
    img.width = w;
    img.height = h;
    pic.appendChild(dark);
    pic.appendChild(img);
    return pic;
  }

  // ---------- game cards ----------
  var TILTS = ["-1.6deg", "1.3deg", "-0.9deg", "1.8deg"];
  var grid = document.getElementById("games-grid");
  S.games.forEach(function (g, i) {
    var slot = el("div", "drop");
    slot.style.setProperty("--d", (1.0 + i * 0.22).toFixed(2) + "s");

    var card = el("article", "card" + (g.image ? "" : " card--soon"));
    card.style.setProperty("--tilt", TILTS[i % TILTS.length]);
    card.dataset.shape = "card";
    // the boy reacts to whichever card you look at
    card.dataset.face = g.image ? "tongue" : "suspicious";

    var media = el("div", "card__media");
    media.dataset.shape = g.image ? "frame" : "soon";
    if (g.image) {
      var img = el("img");
      img.src = g.image;
      img.alt = g.imageAlt || g.title;
      img.width = 920;
      img.height = 430;
      img.decoding = "async";
      media.appendChild(img);
    } else {
      media.appendChild(sticker("icon-hourglass", 170, 233, "soon__icon boil"));
    }
    card.appendChild(media);

    if (g.status) {
      var tag = el("span", "card__tag", g.status);
      tag.dataset.shape = "tag";
      card.appendChild(tag);
    }

    card.appendChild(el("h3", "card__title", g.title));
    if (g.blurb) card.appendChild(el("p", "card__blurb", g.blurb));

    if (g.links && g.links.length) {
      var row = el("div", "card__links");
      g.links.forEach(function (l, k) {
        var a = el("a", "btn " + (k === 0 ? "btn--pink" : "btn--cyan"), l.label);
        a.dataset.shape = "btn";
        a.href = l.href;
        a.target = "_blank";
        a.rel = "noopener";
        row.appendChild(a);
      });
      card.appendChild(row);
    }
    slot.appendChild(card);
    grid.appendChild(slot);
  });

  // ---------- social buttons: a paper plate with the network's icon ----------
  var STILTS = ["-4deg", "3deg", "-2deg", "4deg", "-3deg", "2deg", "-4deg"];
  var socials = document.getElementById("socials");
  (S.socials || []).forEach(function (s, i) {
    var li = el("li", "drop");
    li.style.setProperty("--d", (0.35 + i * 0.08).toFixed(2) + "s");
    var a = el("a", "social");
    a.dataset.shape = "social";
    a.dataset.face = "smile";
    a.style.setProperty("--tilt", STILTS[i % STILTS.length]);
    a.href = s.href;
    a.target = "_blank";
    a.rel = "noopener";
    a.setAttribute("aria-label", s.name);
    a.title = s.name;
    var img = el("img");
    img.src = "assets/social/" + s.icon + ".png";
    img.alt = "";
    img.width = 192;
    img.height = 192;
    img.decoding = "async";
    a.appendChild(img);
    li.appendChild(a);
    socials.appendChild(li);
  });

  // ---------- hand-drawn outlines ----------
  // A rounded rectangle whose sides bow a little like a marker line, from a seeded random
  // (the same idea as the shorts renderer). Three seeds per shape, cycled = paper "boil".
  function rng(seed) {
    var a = seed >>> 0 || 1;
    return function () {
      a = (a + 0x6d2b79f5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function f(n) { return n.toFixed(1); }

  function handRect(w, h, r, wob, seed) {
    var rand = rng(seed);
    r = Math.min(r, w / 2, h / 2);
    var C = [[0, 0], [w, 0], [w, h], [0, h]];
    var OUT = [[0, -1], [1, 0], [0, 1], [-1, 0]];
    var d = "";
    for (var i = 0; i < 4; i++) {
      var a = C[i], b = C[(i + 1) % 4], c = C[(i + 2) % 4];
      var len = Math.hypot(b[0] - a[0], b[1] - a[1]);
      var u = [(b[0] - a[0]) / len, (b[1] - a[1]) / len];
      var p0 = [a[0] + u[0] * r, a[1] + u[1] * r];
      var p1 = [b[0] - u[0] * r, b[1] - u[1] * r];
      var L = Math.max(len - 2 * r, 1);
      var n = Math.max(1, Math.round(L / 170));
      if (i === 0) d += "M " + f(p0[0]) + " " + f(p0[1]);
      var cps = [];
      for (var k = 0; k < n; k++) {
        var t = (k + 0.5) / n, o = (rand() - 0.5) * 2 * wob;
        cps.push([p0[0] + u[0] * L * t + OUT[i][0] * o, p0[1] + u[1] * L * t + OUT[i][1] * o]);
      }
      for (k = 0; k < n; k++) {
        var nx = k < n - 1 ? [(cps[k][0] + cps[k + 1][0]) / 2, (cps[k][1] + cps[k + 1][1]) / 2] : p1;
        d += " Q " + f(cps[k][0]) + " " + f(cps[k][1]) + " " + f(nx[0]) + " " + f(nx[1]);
      }
      // corner: a slightly uneven curve into the next side
      var v = [(c[0] - b[0]), (c[1] - b[1])];
      var vl = Math.hypot(v[0], v[1]);
      var q = [b[0] + (rand() - 0.5) * wob, b[1] + (rand() - 0.5) * wob];
      d += " Q " + f(q[0]) + " " + f(q[1]) + " " + f(b[0] + v[0] / vl * r) + " " + f(b[1] + v[1] / vl * r);
    }
    return d + " Z";
  }

  // per kind: corner radius, wobble, marker width, white cut border width (dark sheet only)
  var KINDS = {
    card:  { r: 10, wob: 2.6, line: 4.5, cut: 14 },
    frame: { r: 6,  wob: 1.8, line: 4,   cut: 0, clip: true },
    soon:  { r: 6,  wob: 1.8, line: 3,   cut: 0 },
    btn:   { r: 22, wob: 1.6, line: 3.5, cut: 0 },
    tag:   { r: 6,  wob: 1.4, line: 3,   cut: 8 },
    social: { r: 16, wob: 1.6, line: 3.5, cut: 9 },
  };
  var SVGNS = "http://www.w3.org/2000/svg";
  var shapes = [];
  var seedNext = 7;

  document.querySelectorAll("[data-shape]").forEach(function (node) {
    var kind = KINDS[node.dataset.shape];
    var svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("class", "shape");
    svg.setAttribute("aria-hidden", "true");
    var paths = {};
    ["cut", "fill", "line"].forEach(function (part) {
      if (part === "cut" && !kind.cut) return;
      if (part === "fill" && kind.clip) return;
      var p = document.createElementNS(SVGNS, "path");
      p.setAttribute("class", part);
      if (part === "cut") p.setAttribute("stroke-width", kind.cut);
      if (part === "line") p.setAttribute("stroke-width", kind.line);
      svg.appendChild(p);
      paths[part] = p;
    });
    node.insertBefore(svg, node.firstChild);
    shapes.push({ node: node, svg: svg, kind: kind, paths: paths, seed: (seedNext += 53), variants: [], img: kind.clip ? node.querySelector("img") : null });
  });

  function draw(s) {
    var w = s.node.offsetWidth, h = s.node.offsetHeight;
    if (!w || !h) return;
    s.svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    s.variants = [0, 1, 2].map(function (k) { return handRect(w, h, s.kind.r, s.kind.wob, s.seed + k * 101); });
    paint(s, frame);
  }
  function paint(s, k) {
    var d = s.variants[k % s.variants.length];
    if (!d) return;
    for (var part in s.paths) s.paths[part].setAttribute("d", d);
    if (s.img) s.img.style.clipPath = 'path("' + d + '")';
  }

  var frame = 0;
  shapes.forEach(draw);
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(function (entries) {
      entries.forEach(function (e) {
        shapes.forEach(function (s) { if (s.node === e.target) draw(s); });
      });
    });
    shapes.forEach(function (s) { ro.observe(s.node); });
  } else {
    window.addEventListener("resize", function () { shapes.forEach(draw); });
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { shapes.forEach(draw); });

  // boil: a new outline every ~0.2 s, like a cut-out redrawn on twos
  setInterval(function () {
    if (still.matches || document.hidden) return;
    frame = (frame + 1) % 3;
    shapes.forEach(function (s) { paint(s, frame); });
  }, 200);

  // ---------- the boy looks at what you look at ----------
  var boy = document.getElementById("boy");
  document.querySelectorAll("[data-face]").forEach(function (n) {
    if (n === boy || n.classList.contains("boy__face")) return;
    var on = function () { boy.dataset.face = n.dataset.face; };
    var off = function () { boy.dataset.face = "head"; };
    n.addEventListener("mouseenter", on);
    n.addEventListener("mouseleave", off);
    n.addEventListener("focusin", on);
    n.addEventListener("focusout", off);
  });

  // ---------- pieces fall onto the sheet as they come into view ----------
  var drops = Array.prototype.slice.call(document.querySelectorAll(".drop")).concat([boy]);
  var t0 = Date.now(), batch = 0, batchAt = 0;
  function go(n) {
    // pieces that scroll in later fall at once, one after another, not after the first-load delays
    if (Date.now() - t0 > 1500) {
      if (Date.now() - batchAt > 300) batch = 0;
      batchAt = Date.now();
      n.style.setProperty("--d", (0.05 + 0.12 * batch++).toFixed(2) + "s");
    }
    n.classList.add("go");
  }
  if (still.matches || !("IntersectionObserver" in window)) {
    drops.forEach(go);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { go(e.target); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px" });
    drops.forEach(function (n) { io.observe(n); });
  }
})();

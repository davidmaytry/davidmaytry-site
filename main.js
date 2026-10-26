// Fills the page from window.SITE (config.js). No content lives here.
(function () {
  var S = window.SITE;

  document.querySelectorAll("[data-site]").forEach(function (el) {
    var key = el.getAttribute("data-site");
    if (S[key] != null) el.textContent = S[key];
  });

  var email = document.querySelector('[data-site="email"]');
  if (email) email.href = "mailto:" + S.email;

  document.getElementById("year").textContent = new Date().getFullYear();

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  var grid = document.getElementById("games-grid");
  S.games.forEach(function (g) {
    var card = el("article", "card" + (g.image ? "" : " card--soon"));

    var media = el("div", "card__media");
    if (g.image) {
      var img = el("img");
      img.src = g.image;
      img.alt = g.imageAlt || g.title;
      img.width = 920;
      img.height = 430;
      img.loading = "lazy";
      img.decoding = "async";
      media.appendChild(img);
    } else {
      media.appendChild(el("span", "card__placeholder", g.title));
    }
    if (g.status) media.appendChild(el("span", "card__status", g.status));
    card.appendChild(media);

    var body = el("div", "card__body");
    body.appendChild(el("h3", "card__title", g.title));
    if (g.blurb) body.appendChild(el("p", "card__blurb", g.blurb));

    if (g.links && g.links.length) {
      var row = el("div", "card__links");
      g.links.forEach(function (l, i) {
        var a = el("a", "btn" + (i === 0 ? " btn--primary" : ""), l.label);
        a.href = l.href;
        a.target = "_blank";
        a.rel = "noopener";
        row.appendChild(a);
      });
      body.appendChild(row);
    }
    card.appendChild(body);
    grid.appendChild(card);
  });
})();

// Everything the page says lives here. Edit this file, not index.html.
//
// The studio name is also written, for link previews that do not run
// JavaScript, in the <head> of index.html (title, og:*, twitter:*).
// To rename the studio: change `name` below and replace "davidmaytry" in the
// <head> of index.html. The logo pictures (wordmark, og-image) show the
// studio's own "DAVID may try" lettering and come from tools/make_assets.py.

window.SITE = {
  name: "davidmaytry",
  tagline: "Small indie studio making cozy multiplayer games",
  email: "hello@davidmaytry.com",
  contactLine: "for press, feedback and support",

  // One entry per game. Order here is order on the page.
  //   image   - path to a 920x430 picture (omit for a "coming soon" card)
  //   links   - buttons, in order; omit or leave empty for none
  //   status  - optional small label over the card, e.g. "Coming soon"
  // The first link is the pink button, the second the cyan one.
  games: [
    {
      title: "Flurry Fray",
      blurb: "A cozy 2v2 snowball fight for 2–4 players, in local splitscreen or online.",
      image: "assets/flurry-fray-capsule.webp",
      imageAlt: "Flurry Fray logo pressed into snow next to a kid in a red coat making a snow angel",
      links: [
        { label: "Website", href: "https://flurryfray.davidmaytry.com" },
        { label: "Steam", href: "https://store.steampowered.com/app/5411930/" },
      ],
    },
    {
      title: "The Hired Wall",
      blurb: "In development.",
      status: "Coming soon",
    },
  ],
};

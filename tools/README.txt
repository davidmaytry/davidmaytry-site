Brand art on this site
======================

Everything under assets/ (logo head, wordmarks, the boy's faces and hand, the
hourglass sticker, favicon.ico, apple-touch-icon.png, icon-192/512.png,
og-image.png, fonts and their licenses) is made by one script from the
studio's own files. The sources are only read, never changed:

  D:/Important/Games/DavidMayTry/david_may_try_icon_1024.png   favicon, icons, og-image
  C:/Projects/media/postkit/brand/logo/                       head_color, wordmark_black/white
  C:/Projects/media/postkit/stickers/cut, cut_light/           faces, hand, hourglass (dark / light theme)
  C:/Projects/media/postkit/brand/fonts/                       Shantell Sans, Gochi Hand + licenses

Run from the repo root (needs: pip install pillow fonttools brotli):

  python tools/make_assets.py

Social icons (assets/social/*.png: discord, steam, youtube, reddit, x, instagram, tiktok) are not
copied from anywhere: the same script draws them, in the stickers' marker-and-flat-fill
look. They are the glyph only; the paper plate around each is drawn by main.js like the
cards. To redraw just them, without touching the rest:

  python tools/make_assets.py social

The links themselves are in config.js, `socials` (one line per network).

The page picks the dark or light copy of each sticker by the system theme
(<picture> with a prefers-color-scheme source), as the shorts do: white
sticker border on the dark sheet, none on cream paper.

Screenshots for checking (not committed, shots/ is ignored):

  shots/snap.sh <url> <name> <width> <height> [dark]   headless Edge, final state

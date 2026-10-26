Rendering the pictures that contain the studio name (Edge, headless).
Run from the repo root in Git Bash after changing config.js or assets/mark.svg:

  E="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
  "$E" --headless --disable-gpu --hide-scrollbars --window-size=1200,630 \
       --virtual-time-budget=5000 --screenshot="$PWD/assets/og-image.png" "file:///$PWD/tools/og.html"
  python tools/make_icons.py

The favicon is assets/mark.svg (a drawn "d", no font involved);
make_icons.py draws the same shape into favicon.ico, apple-touch-icon.png
and tools/mark-512.png (a large copy of the mark for avatars etc.).
If you change mark.svg, change the numbers in make_icons.py too.

On Windows pass Windows-style paths (cygpath -m "$PWD") to Edge.

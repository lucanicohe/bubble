Puzzle Bobble clone (HTML, CSS, JavaScript) - bubble characters edition

puzzle_bobble.html : single file, all sprites embedded. Double click to play.
source/            : readable version (index.html, game.js, assets/).
                     Canvas pixel reading needs a local server:
                     cd source && python3 -m http.server 8000
                     then open http://localhost:8000
tools/             : make_sprites.py  draws assets/blob_bubbles.png and assets/hero_character.png
                     build_single.py  rebuilds puzzle_bobble.html from source/

Controls: left/right arrows or mouse to aim, Space or click to shoot.

What changed
- Every bubble is now the blob character (8 colours). Sheet: assets/blob_bubbles.png,
  8 rows (blue red green yellow orange cyan gray purple) x 28 frames of 32x32.
- The character who turns the wheel is snow white, a colour no bubble uses, and never changes
  colour. Sheet: assets/hero_character.png (palette swap of the original sheet).
- Animations: breathing bob, blinks and glances (each character on its own timing), squash on
  landing + ripple through the stack, surprise/flash/burst pop, screaming fall, tumbling shot,
  shivering when the stack gets low, smirking on game over. The loaded character watches your
  aim, the NEXT character hops in and waves.

To change the art: edit tools/make_sprites.py, run it, then run tools/build_single.py.

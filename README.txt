https://lucanicohe.github.io/bubble/




Puzzle Bobble clone (HTML, CSS, JavaScript)  

puzzle_bobble.html : single file, all sprites embedded. Double click to play.
source/            : readable version (index.html, game.js, assets/).
                     Canvas pixel reading needs a local server:
                     cd source && python3 -m http.server 8000
                     then open http://localhost:8000
tools/             : make_sprites.py  draws assets/blob_bubbles.png and assets/hero_character.png
                     build_single.py  rebuilds puzzle_bobble.html from source/

Controls: left/right arrows or mouse to aim, Space or click to shoot.



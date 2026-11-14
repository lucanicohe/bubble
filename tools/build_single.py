#!/usr/bin/env python3
"""Builds puzzle_bobble.html: one file, game.js inlined and every sprite embedded as a data URI.
Run from the project folder:  python3 tools/build_single.py"""
import base64, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'source')
js = open(os.path.join(SRC, 'game.js'), encoding='utf-8').read()
html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()

def embed(m):
    name = m.group(1)
    if name.endswith('Green_Nebula_07-512x512.png'):  # the game shrinks it to 128px anyway, so embed the 128px copy (keeps the file small)
        name = 'assets/nebula_128.png'
    path = os.path.join(SRC, name)
    data = base64.b64encode(open(path, 'rb').read()).decode()
    return "'data:image/png;base64," + data + "'"
js = re.sub(r"'(assets/[^']+\.png)'", embed, js)
assert '</script' not in js
out = html.replace('<script src="game.js"></script>', '<script>\n' + js + '\n</script>')
open(os.path.join(SRC, '..', 'puzzle_bobble.html'), 'w', encoding='utf-8').write(out)
print('puzzle_bobble.html', round(len(out) / 1024), 'KB')

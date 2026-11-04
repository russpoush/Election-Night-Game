"""Rebuild everything: verify the data, build data/elections.json, then the game page.
(Congress data: run data/build_congress.py with the two MIT files first; see its docstring.)

    python3 build.py
"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
def run(*a): subprocess.run([sys.executable, "-I", *a], check=True)
run(os.path.join(ROOT, "data", "verify.py"))
run(os.path.join(ROOT, "data", "build_data.py"))
tpl = open(os.path.join(ROOT, "mystery-election-night", "template.html")).read()
game = open(os.path.join(ROOT, "mystery-election-night", "game.js")).read()
data = open(os.path.join(ROOT, "data", "elections.json")).read()
congress = open(os.path.join(ROOT, "data", "congress.json")).read()  # built by data/build_congress.py
run(os.path.join(ROOT, "data", "build_governor.py"))
governor = open(os.path.join(ROOT, "data", "governor.json")).read()
game = game.replace("__DATA__", data).replace("__CONGRESS__", congress).replace("__GOVERNOR__", governor)
open(os.path.join(ROOT, "mystery-election-night", "index.html"), "w").write(tpl.replace("__GAME__", game))
print("Built mystery-election-night/index.html")

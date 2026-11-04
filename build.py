"""Rebuild everything: verify the data, build data/elections.json, then the game page.

    python3 build.py
"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
def run(*a): subprocess.run([sys.executable, "-I", *a], check=True)
run(os.path.join(ROOT, "data", "verify.py"))
run(os.path.join(ROOT, "data", "build_data.py"))
tpl = open(os.path.join(ROOT, "mystery-election-night", "template.html")).read()
data = open(os.path.join(ROOT, "data", "elections.json")).read()
open(os.path.join(ROOT, "mystery-election-night", "index.html"), "w").write(tpl.replace("__DATA__", data))
print("Built mystery-election-night/index.html")

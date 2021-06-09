import os, sys

PYTHON = sys.executable

os.chdir("./lynx")
os.system(PYTHON + " main.py " + ' '.join(sys.argv[1:]))

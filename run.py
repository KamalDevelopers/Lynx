import os, sys

PYTHON = sys.executable

os.chdir("./src")
os.system(PYTHON + " main.py")

from shutil import copyfile
import filecmp
import sys
import os

PYTHON = sys.executable

compare = filecmp.cmp(
    "./lynx-profile/config.ini", "./resources/config/default.ini"
)

if not compare:
    print("[Updating Resources]")
    os.chdir("./resources")
    os.system(PYTHON + " update.py")
    os.chdir("..")
    copyfile("./resources/config/default.ini", "./lynx-profile/config.ini")

os.chdir("./lynx")
os.system(PYTHON + " main.py " + ' '.join(sys.argv[1:]))

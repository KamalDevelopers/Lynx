import PyInstaller.__main__
import platform
import shutil
import os
import requests
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


print("Building Lynx for", platform.system(), "estimated build time: ~2 min")

version = input(str("Version: "))
fname = ("Lynx (" + str(platform.system()) + ") v" + version)
os.mkdir(fname)

PyInstaller.__main__.run([
    'src/main.py',
    '--onefile',
    '--noconsole',
    '-isrc/img/icons/logo.ico'
])

if platform.system() == "Linux":
    shutil.move("dist/main", "./" + fname + "/lynx")
if platform.system() == "Windows":
    shutil.move("dist/main.exe", "./" + fname + "/Lynx.exe")

shutil.copytree("src/img", "./" + fname + "/img")
shutil.copyfile("src/lynx.json", "./" + fname + "/lynx.json")
zips = (fname.replace("(", "[").replace(")", "]")) + ".zip"

zipf = zipfile.ZipFile(zips, "w", zipfile.ZIP_DEFLATED, compresslevel=1)
zipdir(fname+"/"+"img", zipf)
zipdir(fname, zipf)
zipf.close()

shutil.rmtree(fname)
shutil.rmtree("dist")
shutil.rmtree("build")
os.remove("main.spec")


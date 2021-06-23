import PyInstaller.__main__
import platform
import shutil
import os
import zipfile
import subprocess
import json
import sys


def gversion(path):
    with open(path) as f:
        data = json.load(f)

    if "{git-commit-hash}" in data["package"]["version"]:
        lv = subprocess.check_output(["git", "describe", "--always"]).strip()

        return data["package"]["version"].replace(
            "{git-commit-hash}", lv.decode()
        )
    return data["package"]["version"]


def package(version, source, destination, profile):
    with open(source) as f:
        data = json.load(f)

    data["package"]["profile"] = profile
    data["package"]["version"] = version
    with open(destination, "w") as f:
        json.dump(data, f)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


print(
    "Building Lynx for",
    platform.system(),
    "estimated build time: ~2 min, Continue? [Y]/[n]",
    end=": ",
)

exit = input()
if str(exit) == "n":
    sys.exit()

version = gversion("lynx/lynx.json")
zips = "Lynx " + str(platform.system()) + " " + version + ".zip"
fname = "Lynx"
os.mkdir(fname)

PyInstaller.__main__.run(
    ["lynx/main.py", "--noconsole", "--onefile", "-ilynx-profile/themes/icons/logo.ico", "--hidden-import=PyQt5.sip"]
)

# Rename Executable
if platform.system() == "Linux":
    shutil.move("dist/main", "./" + fname + "/Lynx")
if platform.system() == "Windows":
    shutil.move("dist/main.exe", "./" + fname + "/Lynx.exe")

# Copy Files
shutil.copytree("lynx-profile", "./" + fname + "/lynx-profile")

# Write Package Info
package(version, "lynx/lynx.json", "./" + fname + "/lynx.json", "lynx-profile/")

# Create Zip
zipf = zipfile.ZipFile(zips, "w", zipfile.ZIP_DEFLATED, compresslevel=1)
zipdir(fname, zipf)
zipf.close()

# Remove Temporary Directories
shutil.rmtree(fname)
shutil.rmtree("dist")
shutil.rmtree("build")
os.remove("main.spec")

import os
import sys
import shutil
import subprocess
import confvar
import utils.log
import platform as arch


def lynxQuit():
    if os.path.isdir("./temp/"):
        shutil.rmtree("./temp")
    utils.log.msg("INFO")("Browser exited successfully")


def launchLynx(url=""):
    exec_file = sys.argv[0]
    if ".py" in exec_file:
        subprocess.Popen([sys.executable, exec_file, url])
    else:
        subprocess.Popen([exec_file, url])


def launchStealth(window):
    exec_file = sys.argv[0]
    window.close()
    if ".py" in exec_file:
        subprocess.run([sys.executable, exec_file, "-s"])
    else:
        subprocess.run([exec_file, "-s"])


def openFolder(path):
    if arch.system() == "Windows":
        os.startfile(path)
    elif arch.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def storeSession(urls):
    with open(confvar.BASE_PATH + "restore.session", "w") as f:
        f.write(str(urls))


def decodeLynxUrl(qurl):
    if qurl.toString() == "lynx:blank":
        return qurl.toString()
    if str(qurl.toString())[:5] == "lynx:":
        base = qurl.toString().replace("lynx:", "")
        lfile = str(qurl.toString()).split(":")[1]
        if os.path.isfile(
            confvar.BASE_PATH
            + "lynx/"
            + base
            + "/"
            + confvar.BROWSER_STYLESHEET
            + "_"
            + lfile
            + ".html"
        ):
            lfile = confvar.BROWSER_STYLESHEET + "_" + lfile
        elif os.path.isfile(
            confvar.BASE_PATH + "lynx/" + base + "/" + lfile + ".html"
        ):
            lfile = lfile
        lfile = os.path.abspath(
            confvar.BASE_PATH + "lynx/" + base + "/" + lfile
        )
    else:
        return qurl.toString()
    lfile = lfile.replace("\\", "/")
    return "file:///" + lfile + ".html"


def encodeLynxUrl(qurl):
    if str(qurl.toString())[:8] == "file:///" and "lynx/" in qurl.toString():
        lfile = str(qurl.toString()).split("/")
        lfile = lfile[len(lfile) - 1]
    else:
        return qurl.toString()
    if "_" in lfile:
        return "lynx:" + lfile.split("_")[1][:-5]
    return "lynx:" + lfile[:-5]


def checkLynxUrl(qurl):
    if str(qurl.toString())[:5] == "lynx:":
        return True
    return False

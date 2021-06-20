import os
import sys
import shutil
import subprocess
import confvar
import random
import utils.log
import urllib.request
import platform as arch


def lynx_quit():
    if os.path.isdir("./temp/"):
        shutil.rmtree("./temp")
    if os.path.isdir("./temp/"):
        os.remove("./temp")
    utils.log.dbg("INFO")("Browser exited successfully")


def launch_lynx(url=""):
    exec_file = sys.argv[0]
    if ".py" in exec_file:
        subprocess.Popen([sys.executable, exec_file, url])
    else:
        subprocess.Popen([exec_file, url])


def launch_stealth(window):
    exec_file = sys.argv[0]
    window.close()
    if ".py" in exec_file:
        subprocess.run([sys.executable, exec_file, "-s"])
    else:
        subprocess.run([exec_file, "-s"])


def open_folder(path):
    if arch.system() == "Windows":
        os.startfile(path)
    elif arch.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def store_session(urls):
    with open(confvar.BASE_PATH + "restore.session", "w") as f:
        f.write(str(urls))


def decode_lynx_url(qurl):
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


def encode_lynx_url(qurl):
    if str(qurl.toString())[:8] == "file:///" and "lynx/" in qurl.toString():
        lfile = str(qurl.toString()).split("/")
        lfile = lfile[len(lfile) - 1]
    else:
        return qurl.toString()
    if "_" in lfile:
        return "lynx:" + lfile.split("_")[1][:-5]
    return "lynx:" + lfile[:-5]


def check_lynx_url(qurl):
    if str(qurl.toString())[:5] == "lynx:":
        return True
    return False


def feature_parser(feature):
    return [
        "notifications",
        "location",
        "microphone",
        "camera",
        "audio and camera",
        "mouse lock",
        "desktop video capture",
        "desktop video and audio capture",
    ][feature]


def search_engine_hosts():
    return ["duckduckgo.com"]


def random_user_agent():
    agents = urllib.request.urlopen(
        "https://raw.githubusercontent.com/Kikobeats/"
        + "top-user-agents/master/index.json"
    ).read()

    return random.choice(eval(agents))

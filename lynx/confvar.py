import os
import sys
import json
import platform
from os.path import expanduser
from configparser import ConfigParser

import utils.version
import utils.log
from utils.stylesheet import StyleSheet


with open("lynx.json") as f:
    data = json.load(f)

configur = ConfigParser()
style = None

STEALTH_FLAG = 0
CURRENT_OS = platform.system()
OS_HOME = expanduser("~")
DOWNLOAD_PATH = OS_HOME + "/" + "Downloads/"
BASE_PATH = data["package"]["profile"]
VERSION = utils.version.version()

if not os.path.isdir("./temp"):
    os.mkdir("./temp")

if not os.path.isdir(BASE_PATH):
    utils.log.dbg("ERROR")(
        "Failed to find lynx profile"
    )
    sys.exit()

BROWSER_OPEN_URLS = []
if os.path.isfile(BASE_PATH + "restore.session"):
    with open(BASE_PATH + "restore.session") as f:
        BROWSER_OPEN_URLS = eval(f.read())
    os.remove(BASE_PATH + "restore.session")

# Default Values
BROWSER_WINDOW_TITLE = "Lynx"
BROWSER_BORDERLESS = True
BROWSER_LOCALE = None
BROWSER_HOMEPAGE = "lynx:home"
BROWSER_NEWTAB = "lynx:blank"
BROWSER_FONT_FAMILY = "Noto"
BROWSER_STYLESHEET = "equinox"
BROWSER_FONT_SIZE = 10
BROWSER_SHORT_URL = 2
BROWSER_STORAGE = False
BROWSER_ADBLOCKER = True
BROWSER_MINER_BLOCKER = True
BROWSER_STORE_VISITED_LINKS = False
BROWSER_HTTPS_ONLY = False
BROWSER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
)
BROWSER_PROXY = None
BROWSER_TS_DISABLED = True

WEBKIT_JAVASCRIPT_ENABLED = 1
WEBKIT_FULLSCREEN_ENABLED = 1
WEBKIT_WEBGL_ENABLED = 1
WEBKIT_PLUGINS_ENABLED = 1
WEBKIT_JAVASCRIPT_POPUPS_ENABLED = 1


def alter_value(cat, var, val):
    global configur
    val = str(val)
    configur.read(BASE_PATH + "config.ini")
    BROWSER = configur[cat]
    BROWSER[var] = val
    with open(BASE_PATH + "config.ini", "w") as conf:
        configur.write(conf)


def sparse(string):
    if (
        string == "None" or
        string == "0" or
        string == "False" or
        string == "Default"
    ):
        return None
    return string


def configure():
    global configur
    global style

    global BROWSER_WINDOW_TITLE, BROWSER_HOMEPAGE, BROWSER_NEWTAB, \
        BROWSER_FONT_FAMILY, BROWSER_STYLESHEET, BROWSER_ADBLOCKER, \
        BROWSER_STORAGE, BROWSER_HTTPS_ONLY, BROWSER_AGENT, \
        BROWSER_MINER_BLOCKER, BROWSER_PROXY, BROWSER_STORAGE, \
        BROWSER_LOCALE, STEALTH_FLAG, BROWSER_TS_DISABLED, BROWSER_SHORT_URL, \
        BROWSER_BORDERLESS

    global WEBKIT_JAVASCRIPT_ENABLED, WEBKIT_FULLSCREEN_ENABLED, \
        WEBKIT_WEBGL_ENABLED, WEBKIT_PLUGINS_ENABLED, \
        WEBKIT_JAVASCRIPT_POPUPS_ENABLED

    configur.read(BASE_PATH + "config.ini")

    BROWSER_WINDOW_TITLE = "Lynx"
    BROWSER_HOMEPAGE = configur.get("BROWSER", "HOMEPAGE")
    BROWSER_NEWTAB = configur.get("BROWSER", "NEWTAB")
    BROWSER_BORDERLESS = configur.getboolean("BROWSER", "BORDERLESS")
    BROWSER_LOCALE = sparse(configur.get("BROWSER", "LOCALE"))
    BROWSER_FONT_FAMILY = configur.get("BROWSER", "FONT_FAMILY")
    BROWSER_STYLESHEET = configur.get("BROWSER", "STYLESHEET")
    BROWSER_HTTPS_ONLY = configur.getboolean("BROWSER", "HTTPS_ONLY")
    BROWSER_STORAGE = sparse(configur.get("BROWSER", "STORAGE"))
    BROWSER_ADBLOCKER = configur.getboolean("BROWSER", "ADBLOCKER")
    BROWSER_MINER_BLOCKER = configur.getboolean("BROWSER", "MINER_BLOCKER")
    BROWSER_STORE_VISITED_LINKS = configur.getboolean(
        "BROWSER", "STORE_VISITED_LINKS"
    )
    BROWSER_AGENT = sparse(configur.get("BROWSER", "AGENT"))
    BROWSER_PROXY = sparse(configur.get("BROWSER", "PROXY"))
    BROWSER_SHORT_URL = configur.getint("BROWSER", "SHORT_URL")
    BROWSER_TS_DISABLED = configur.getboolean("BROWSER", "TS_DISABLED")
    STEALTH_FLAG = configur.getboolean("BROWSER", "STEALTH")

    WEBKIT_JAVASCRIPT_POPUPS_ENABLED = configur.getboolean(
        "WEBKIT", "JAVASCRIPT_POPUPS_ENABLED"
    )
    WEBKIT_JAVASCRIPT_ENABLED = configur.getboolean(
        "WEBKIT", "JAVASCRIPT_ENABLED"
    )
    WEBKIT_FULLSCREEN_ENABLED = configur.getboolean(
        "WEBKIT", "FULLSCREEN_ENABLED"
    )
    WEBKIT_WEBGL_ENABLED = configur.getboolean("WEBKIT", "WEBGL_ENABLED")
    WEBKIT_PLUGINS_ENABLED = configur.getboolean("WEBKIT", "PLUGINS_ENABLED")

    if STEALTH_FLAG:
        BROWSER_STYLESHEET = "stealth"
        BROWSER_ADBLOCKER = True
        BROWSER_MINER_BLOCKER = True
        BROWSER_STORAGE = "./temp"
        BROWSER_STORE_VISITED_LINKS = False
        BROWSER_HTTPS_ONLY = True
        BROWSER_TS_DISABLED = True
        BROWSER_AGENT = (
            "Mozilla/5.0 (Windows NT 10.0;rv:78.0) Gecko/20100101 Firefox/78.0"
        )
        BROWSER_PROXY = None
        BROWSER_WINDOW_TITLE = "Lynx Stealth"
        WEBKIT_WEBGL_ENABLED = 0
        WEBKIT_PLUGINS_ENABLED = 0
        WEBKIT_JAVASCRIPT_POPUPS_ENABLED = 0

    with open(BASE_PATH + "themes/" + BROWSER_STYLESHEET + ".qss") as f:
        style = StyleSheet(f.read())


try:
    configure()
except:
    utils.log.dbg("ERROR")(
        "Failed to load configuration from profile"
    )

import os
import sys
import json
import platform
import resources
from os.path import expanduser
from configparser import ConfigParser

import utils.version
import utils.log
from utils.stylesheet import StyleSheet
from PyQt5.QtCore import QFile, QIODevice


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

if os.getenv('LYNX_PROFILE'):
    BASE_PATH = os.getenv('LYNX_PROFILE')

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

with open(BASE_PATH + "shortcuts.json") as f:
    keyboard_shortcuts = json.load(f)["shortcuts"]


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
        BROWSER_LOCALE, STEALTH_FLAG, BROWSER_TS_DISABLED, BROWSER_SHORT_URL, \
        BROWSER_BORDERLESS, BROWSER_ALWAYS_ALLOW, BROWSER_SEARCH_ENGINE, \
        BROWSER_PROXY, BROWSER_STORAGE, BROWSER_BLOCK_CANVAS, \
        BROWSER_STEALTH_STYLESHEET, BROWSER_COOKIE_FILTER, \
        BROWSER_STORE_VISITED_LINKS, BROWSER_BLOCK_WEBRTC_LEAKS

    global WEBKIT_JAVASCRIPT_ENABLED, WEBKIT_FULLSCREEN_ENABLED, \
        WEBKIT_WEBGL_ENABLED, WEBKIT_PLUGINS_ENABLED, \
        WEBKIT_JAVASCRIPT_POPUPS_ENABLED, WEBKIT_DEBUG_LEVEL

    default_file = QFile(":/config/default.ini")
    default_file.open(QIODevice.ReadOnly)
    default_config = default_file.readAll().data().decode()
    default_file.close()

    configur.read_string(default_config)
    if os.path.isfile(BASE_PATH + "config.ini"):
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
    BROWSER_COOKIE_FILTER = configur.getboolean("BROWSER", "COOKIE_FILTER")
    BROWSER_ALWAYS_ALLOW = sparse(configur.get("BROWSER", "ALWAYS_ALLOW"))
    BROWSER_SEARCH_ENGINE = sparse(configur.get("BROWSER", "SEARCH_ENGINE"))
    BROWSER_BLOCK_WEBRTC_LEAKS = configur.getboolean(
        "BROWSER", "BLOCK_WEBRTC_LEAKS"
    )
    BROWSER_STEALTH_STYLESHEET = sparse(configur.get(
        "BROWSER", "STEALTH_STYLESHEET"
    ))
    BROWSER_BLOCK_CANVAS = configur.getboolean(
        "BROWSER", "BLOCK_CANVAS"
    )
    BROWSER_STORE_VISITED_LINKS = configur.getboolean(
        "BROWSER", "STORE_VISITED_LINKS"
    )

    BROWSER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    if sparse(configur.get("BROWSER", "AGENT")):
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
    WEBKIT_DEBUG_LEVEL = 0
    WEBKIT_WEBGL_ENABLED = configur.getboolean("WEBKIT", "WEBGL_ENABLED")
    WEBKIT_PLUGINS_ENABLED = configur.getboolean("WEBKIT", "PLUGINS_ENABLED")

    if STEALTH_FLAG:
        BROWSER_STYLESHEET = BROWSER_STEALTH_STYLESHEET
        BROWSER_ADBLOCKER = True
        BROWSER_COOKIE_FILTER = True
        BROWSER_STORAGE = "./temp"
        BROWSER_STORE_VISITED_LINKS = False
        BROWSER_HTTPS_ONLY = True
        BROWSER_TS_DISABLED = True
        BROWSER_AGENT = "randomize"
        BROWSER_PROXY = None
        BROWSER_ALWAYS_ALLOW = None
        BROWSER_BLOCK_WEBRTC_LEAKS = True
        BROWSER_BLOCK_CANVAS = True
        BROWSER_WINDOW_TITLE = "Lynx Stealth"
        WEBKIT_WEBGL_ENABLED = 0
        WEBKIT_PLUGINS_ENABLED = 0
        WEBKIT_JAVASCRIPT_POPUPS_ENABLED = 0

    with open(BASE_PATH + "themes/" + BROWSER_STYLESHEET + ".qss") as f:
        style = StyleSheet(f.read())


configure()

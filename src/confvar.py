import os
import sys
import json
import platform
from os.path import expanduser
from configparser import ConfigParser

with open('lynx.json') as f:
    data = json.load(f)

CURRENT_OS = platform.system()
OS_HOME = expanduser("~")
configur = ConfigParser() 
BASE_PATH = data['package']['profile']
VERSION = data['package']['version']
print(data)

if not os.path.isdir(BASE_PATH):
    print("Failed to find lynx profile")
    sys.exit()

# Default Values
BROWSER_WINDOW_TITLE = "Lynx"
BROWSER_LOCALE = None 
BROWSER_HOMEPAGE = "lynx:home"
BROWSER_FONT_FAMILY = "Noto"
BROWSER_STYLESHEET = "equinox"
BROWSER_FONT_SIZE = 10 
BROWSER_ADBLOCKER = True 
BROWSER_MINER_BLOCKER = True 
BROWSER_STORE_VISITED_LINKS = False 
BROWSER_HTTPS_ONLY = False
BROWSER_AGENT = None 
BROWSER_PROXY = None 

WEBKIT_JAVASCRIPT_ENABLED = 1
WEBKIT_FULLSCREEN_ENABLED = 1
WEBKIT_WEBGL_ENABLED = 1
WEBKIT_PLUGINS_ENABLED = 1
WEBKIT_JAVASCRIPT_POPUPS_ENABLED = 1

def stealth(mode=True):
    global configur 
    configur.read(BASE_PATH + 'config.ini')
    BROWSER = configur["BROWSER"]
    BROWSER["stealth"] = str(mode) 
    with open(BASE_PATH + 'config.ini', 'w') as conf:
        configur.write(conf)

def sparse(string):
    if string == "None" or string == "0" or string == "False" or string == "Default":
        return None
    return string

def confb():
    global configur
    global STEALTH_MODE 
    global BROWSER_WINDOW_TITLE, BROWSER_HOMEPAGE, BROWSER_FONT_FAMILY, BROWSER_FONT_SIZE, BROWSER_STYLESHEET, BROWSER_ADBLOCKER, BROWSER_HTTPS_ONLY, BROWSER_AGENT, BROWSER_MINER_BLOCKER, BROWSER_PROXY, BROWSER_STORE_VISITED_LINKS, BROWSER_LOCALE 
    global WEBKIT_JAVASCRIPT_ENABLED, WEBKIT_FULLSCREEN_ENABLED, WEBKIT_WEBGL_ENABLE, WEBKIT_PLUGINS_ENABLED, WEBKIT_JAVASCRIPT_POPUPS_ENABLED
    
    configur.read(BASE_PATH + 'config.ini')
    BROWSER_HOMEPAGE = (configur.get('BROWSER', 'HOMEPAGE')) 
    BROWSER_LOCALE = sparse(configur.get('BROWSER', 'LOCALE')) 
    BROWSER_FONT_FAMILY = (configur.get('BROWSER', 'FONT_FAMILY')) 
    BROWSER_FONT_SIZE = (configur.getint('BROWSER', 'FONT_SIZE')) 
    BROWSER_STYLESHEET = (configur.get('BROWSER', 'STYLESHEET')) 
    BROWSER_HTTPS_ONLY = (configur.getboolean('BROWSER', 'HTTPS_ONLY')) 
    BROWSER_ADBLOCKER = (configur.getboolean('BROWSER', 'ADBLOCKER')) 
    BROWSER_MINER_BLOCKER = (configur.getboolean('BROWSER', 'MINER_BLOCKER')) 
    BROWSER_STORE_VISITED_LINKS = (configur.getboolean('BROWSER', 'STORE_VISITED_LINKS')) 
    BROWSER_AGENT = sparse(configur.get('BROWSER', 'AGENT')) 
    BROWSER_PROXY = sparse(configur.get('BROWSER', 'PROXY')) 
    STEALTH_FLAG = (configur.getboolean('BROWSER', 'STEALTH')) 
    
    WEBKIT_JAVASCRIPT_POPUPS_ENABLED = (configur.getboolean('WEBKIT', 'JAVASCRIPT_POPUPS_ENABLED')) 
    WEBKIT_JAVASCRIPT_ENABLED = (configur.getboolean('WEBKIT', 'JAVASCRIPT_ENABLED')) 
    WEBKIT_FULLSCREEN_ENABLED = (configur.getboolean('WEBKIT', 'FULLSCREEN_ENABLED')) 
    WEBKIT_WEBGL_ENABLED = (configur.getboolean('WEBKIT', 'WEBGL_ENABLED')) 
    WEBKIT_PLUGINS_ENABLED = (configur.getboolean('WEBKIT', 'PLUGINS_ENABLED')) 
 
    if STEALTH_FLAG:
        BROWSER_STYLESHEET = "stealth"
        BROWSER_ADBLOCKER = True 
        BROWSER_MINER_BLOCKER = True 
        BROWSER_STORE_VISITED_LINKS = False 
        BROWSER_HTTPS_ONLY = True
        BROWSER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" 
        BROWSER_PROXY = None 
        BROWSER_WINDOW_TITLE = "Lynx Stealth"
        WEBKIT_WEBGL_ENABLED = 0
        WEBKIT_PLUGINS_ENABLED = 0
        WEBKIT_JAVASCRIPT_POPUPS_ENABLED = 0
try:
    confb()
except:
    print("Could not load configurations from profile")

import os
import sys
from configparser import ConfigParser 
configur = ConfigParser() 

BASE_PATH = "../lynx-profile/"
if not os.path.isdir(BASE_PATH):
    print("Failed to find lynx profile")
    sys.exit()

# Default Values
BROWSER_WINDOW_TITLE = "LynxWeb"
BROWSER_HOMEPAGE = "lynx::home"
BROWSER_FONT_FAMILY = "Noto"
BROWSER_STYLESHEET = "qdark"
BROWSER_ADBLOCKER = "lite"
BROWSER_FONT_SIZE = 10 

WEBKIT_JAVASCRIPT_ENABLED = 1
WEBKIT_FULLSCREEN_ENABLED = 1
WEBKIT_WEBGL_ENABLED = 1
WEBKIT_PLUGINS_ENABLED = 1

def confb():
    global configur
    global BROWSER_WINDOW_TITLE, BROWSER_HOMEPAGE, BROWSER_FONT_FAMILY, BROWSER_FONT_SIZE, BROWSER_STYLESHEET, BROWSER_ADBLOCKER
    global WEBKIT_JAVASCRIPT_ENABLED, WEBKIT_FULLSCREEN_ENABLED, WEBKIT_WEBGL_ENABLE, WEBKIT_PLUGINS_ENABLED
    
    configur.read(BASE_PATH + 'config.ini')
    BROWSER_HOMEPAGE = (configur.get('BROWSER', 'HOMEPAGE')) 
    BROWSER_FONT_FAMILY = (configur.get('BROWSER', 'FONT_FAMILY')) 
    BROWSER_FONT_SIZE = (configur.getint('BROWSER', 'FONT_SIZE')) 
    BROWSER_STYLESHEET = (configur.get('BROWSER', 'STYLESHEET')) 
    BROWSER_ADBLOCKER = (configur.get('BROWSER', 'ADBLOCKER')) 
    
    WEBKIT_JAVASCRIPT_ENABLED = (configur.getboolean('WEBKIT', 'JAVASCRIPT_ENABLED')) 
    WEBKIT_FULLSCREEN_ENABLED = (configur.getboolean('WEBKIT', 'FULLSCREEN_ENABLED')) 
    WEBKIT_WEBGL_ENABLED = (configur.getboolean('WEBKIT', 'WEBGL_ENABLED')) 
    WEBKIT_PLUGINS_ENABLED = (configur.getboolean('WEBKIT', 'PLUGINS_ENABLED')) 
confb()

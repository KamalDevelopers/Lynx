from confvar import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PyQt5.QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWebEngineCore import *
import json
import os

extension_data = {}
def readExtension(extension_file):
    global extension_data
    with open(BASE_PATH + "extensions/" + extension_file) as f:
        data = json.load(f)
    for host in data['extension']['host']:
        extension_data[host.replace("www.", "")] = data['extension']['js']

def readExtensions():
    files = os.listdir(BASE_PATH + "extensions/")
    for i, extension_file in enumerate(files):
        if extension_file[-5:] == ".json":
            readExtension(extension_file)
    print(extension_data)

def pageLoad(browser):
    match = browser.page().url().host().replace("www.", "")

    if match in list(extension_data.keys()):
        with open(BASE_PATH + "extensions/" + extension_data[match]) as f:
            js_code = f.read()
        browser.page().runJavaScript(js_code)
        return 1
    return 0

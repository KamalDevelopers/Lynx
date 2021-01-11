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

    if 'extension' not in data.keys():
        return False

    for i, host in enumerate(data['extension']['host']):
        if data['enabled'] == False:
            return
        if host.replace("www.", "") not in extension_data:
            extension_data[host.replace("www.", "")] = []

        if data['extension']['js'][-3:] == ".ts":
            new_name = data['extension']['js'].replace(".ts", ".js")
            if BROWSER_TS_DISABLED:
                return
            if not os.path.isfile(BASE_PATH + "extensions/" + new_name):
                print("Transpiling TS code")
                os.system("npx tsc " + BASE_PATH + "extensions/" + data['extension']['js'])
            data['extension']['js'] = new_name
        extension_data[host.replace("www.", "")].append(data['extension']['js'])

def readExtensions():
    files = os.listdir(BASE_PATH + "extensions/")
    for i, extension_file in enumerate(files):
        if extension_file[-5:] == ".json":
            readExtension(extension_file)
    print(extension_data)

def pageLoad(browser):
    match = browser.page().url().host().replace("www.", "")

    if match in list(extension_data.keys()):
        for load_scripts in extension_data[match]:
            with open(BASE_PATH + "extensions/" + load_scripts) as f:
                js_code = f.read()
            browser.page().runJavaScript(js_code)

    if "*" in list(extension_data.keys()):
        for load_scripts in extension_data["*"]:
            with open(BASE_PATH + "extensions/" + load_scripts) as f:
                js_code = f.read()
            browser.page().runJavaScript(js_code)
        return 1
    return 0

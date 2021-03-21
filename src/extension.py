from confvar import *
from webkit import * 

from PyQt5.QtCore import QFile, QIODevice, QTimer

import json
import os
import re
import time

extension_data = {} # Holds the loaded extensions
preload_data = {}   # Holds the preloaded code of all extensions
permissions = {}    # Holds the permissions of each extension
script_list = {}

apiFile = QFile(":/qtwebchannel/qwebchannel.js")
if not apiFile.open(QIODevice.ReadOnly):
    print("Could not open API file")

apiScript = apiFile.readAll().data().decode()
apiFile.close()

def readExtension(extension_file):
    global extension_data, permissions, script_list 

    with open(BASE_PATH + "extensions/" + extension_file) as f:
        data = json.load(f)

    if 'extension' not in data.keys():
        return False

    if 'permissions' in data.keys():
        permissions[data['name']] = data['permissions']

    for _, host in enumerate(data['extension']['host']):
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
        script_list[data['extension']['js']] = data['name']
        extension_data[host.replace("www.", "")].append(data['extension']['js'])

def readExtensions():
    files = os.listdir(BASE_PATH + "extensions/")
    for _, extension_file in enumerate(files):
        if extension_file[-5:] == ".json":
            readExtension(extension_file)
    print(extension_data, permissions)

def javascriptLoad(path):
    global preload_data

    if path not in list(preload_data.keys()):
        with open(path) as f:
            js_code = f.read()
            preload_data[path] = js_code
    return preload_data[path]

def execute(load_scripts, browser):
    js_code = javascriptLoad(BASE_PATH + "extensions/" + load_scripts)
    if script_list[load_scripts] in list(permissions.keys()):
        setPrivileges(permissions[script_list[load_scripts]])

    browser.page().runJavaScript(js_code, 0)
    QTimer.singleShot(500, setPrivileges) # FIXME: This should wait for the JS to execute

def pageLoad(browser):
    global apiScript

    browser.page().runJavaScript(apiScript)
    time.sleep(0.01)
    match = browser.page().url().host().replace("www.", "")

    if match in list(extension_data.keys()):
        for load_scripts in extension_data[match]:
            execute(load_scripts, browser)

    if "*" in list(extension_data.keys()):
        for load_scripts in extension_data["*"]:
            execute(load_scripts, browser)
        return 1
    return 0

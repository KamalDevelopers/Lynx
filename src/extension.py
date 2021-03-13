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
import re

extension_data = {} # Holds the loaded extensions
preload_data = {}   # Holds the preloaded code of all extensions
external_data = {}  # Holds the external data that the extensions can use 

def readExtension(extension_file):
    global extension_data, external_data
    with open(BASE_PATH + "extensions/" + extension_file) as f:
        data = json.load(f)

    if 'extension' not in data.keys():
        return False

    if 'external' in data.keys():
        for i, external in enumerate(data['external'].keys()):
            external_data[external] = list(data['external'].values())[i]

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
    print(external_data)

def javascriptLoad(path):
    global preload_data, external_data

    if path not in list(preload_data.keys()):
        with open(path) as f:
            js_code = f.read()

            for index, line in enumerate(js_code.split("\n")):
                if "@" in line:
                    fn_match = re.match(r".*@(?P<function>\w+)\s?\((?P<arg>(?P<args>\w+(,\s?)?)+)\).*", line)
                    if not fn_match:
                        print("Failed to parse:", line)
                        return
                    fn_dict = fn_match.groupdict()
                    del fn_dict['args']
                    fn_dict['arg'] = [arg.strip() for arg in fn_dict['arg'].split(',')]

                    if not fn_dict['arg'][0] in list(external_data.keys()):
                        print("External resource not found:", fn_dict['arg'][0])
                        return
                    external_file = external_data[fn_dict['arg'][0]]
                    if not os.path.isfile(BASE_PATH + "extensions/" + external_file):
                        print("External file not found:", external_file)
                        return

                    with open(BASE_PATH + "extensions/" + external_file) as F:
                        data = F.read()
                    new_line = re.sub(r"@read\(.*\)", "`" + data + "`", line)

                    new_code = js_code.split("\n")
                    new_code[index] = new_line
                    js_code = '\n'.join(new_code)

            preload_data[path] = js_code

    return preload_data[path]

def pageLoad(browser):
    match = browser.page().url().host().replace("www.", "")

    if match in list(extension_data.keys()):
        for load_scripts in extension_data[match]:
            js_code = javascriptLoad(BASE_PATH + "extensions/" + load_scripts)
            browser.page().runJavaScript(js_code)

    if "*" in list(extension_data.keys()):
        for load_scripts in extension_data["*"]:
            js_code = javascriptLoad(BASE_PATH + "extensions/" + load_scripts)
            browser.page().runJavaScript(js_code)
        return 1
    return 0

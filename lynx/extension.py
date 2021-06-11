import confvar
import scripts
import webkit as wk
import utils.log

import json
import os
import time

from PyQt5.QtCore import QFile, QIODevice, QTimer

extension_data = {}
preload_data = {}
permissions = {}
script_list = {}

api_file = QFile(":/qtwebchannel/qwebchannel.js")
if not api_file.open(QIODevice.ReadOnly):
    utils.log.dbg("ERROR")("Could not open API file")

scripts.ScriptDatabase()
api_script = api_file.readAll().data().decode()
api_file.close()


def read_extension(extension_file):
    global extension_data, permissions, script_list

    with open(confvar.BASE_PATH + "extensions/" + extension_file) as f:
        data = json.load(f)

    if "extension" not in data.keys():
        return False

    if "permissions" in data.keys():
        permissions[data["name"]] = data["permissions"]

    for _, host in enumerate(data["extension"]["host"]):
        if not data["enabled"]:
            return
        if host.replace("www.", "") not in extension_data:
            extension_data[host.replace("www.", "")] = []

        if data["extension"]["js"][-3:] == ".ts":
            new_name = data["extension"]["js"].replace(".ts", ".js")
            if confvar.BROWSER_TS_DISABLED:
                return
            if not os.path.isfile(
                confvar.BASE_PATH + "extensions/" + new_name
            ):
                utils.log.msg("INFO")("Transpiling TS code")
                os.system(
                    "npx tsc "
                    + confvar.BASE_PATH
                    + "extensions/"
                    + data["extension"]["js"]
                )
            data["extension"]["js"] = new_name
        script_list[data["extension"]["js"]] = data["name"]
        extension_data[host.replace("www.", "")].append(
            data["extension"]["js"]
        )


def read_extensions():
    files = os.listdir(confvar.BASE_PATH + "extensions/")
    for _, extension_file in enumerate(files):
        if extension_file[-5:] == ".json":
            read_extension(extension_file)


def javascript_load(path):
    global preload_data

    if path not in list(preload_data.keys()):
        with open(path) as f:
            js_code = f.read()
            preload_data[path] = js_code
    return preload_data[path]


def execute(load_scripts, browser):
    js_code = javascript_load(confvar.BASE_PATH + "extensions/" + load_scripts)
    script_id = "-1"

    if script_list[load_scripts] in list(permissions.keys()):
        script_id = scripts.get_database().create(
            permissions[script_list[load_scripts]]
        )

    js_code = js_code.replace("{id}", script_id)
    browser.page().runJavaScript(js_code, 0)


def on_page_load(browser):
    global api_script

    browser.page().runJavaScript(api_script)
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

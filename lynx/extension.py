import confvar
import scripts
import resources
import webkit as wk
import utils.log

import json
import os

from PyQt5.QtCore import QFile, QIODevice

extension_data = {}
preload_data = {}
permissions = {}
script_list = {}
script_load = {}
api_scripts = {}


def load_api(api_scripts):
    webchannel_file = QFile(":/qtwebchannel/qwebchannel.js")
    webchannel_file.open(QIODevice.ReadOnly)
    webchannel_script = webchannel_file.readAll().data().decode()
    webchannel_file.close()

    api_file = QFile(":/scripts/api.js")
    api_file.open(QIODevice.ReadOnly)
    api_script = api_file.readAll().data().decode()
    api_file.close()

    run_file = QFile(":/scripts/run.js")
    run_file.open(QIODevice.ReadOnly)
    run_script = run_file.readAll().data().decode()
    run_file.close()

    api_scripts["webchannel"] = webchannel_script
    api_scripts["api"] = api_script
    api_scripts["run"] = run_script


def read_extension(path, extension_file):
    global extension_data
    global permissions
    global script_list
    global script_load
    global api_scripts

    load_api(api_scripts)
    scripts.ScriptDatabase()

    with open(path + extension_file) as f:
        data = json.load(f)

    if "extension" not in data.keys():
        return False

    if "permissions" in data.keys():
        permissions[data["name"]] = data["permissions"]

    if "run" in data.keys():
        script_load[data["name"]] = data["run"]
    else:
        script_load[data["name"]] = "onfinished"

    for _, host in enumerate(data["extension"]["host"]):
        if not data["enabled"]:
            return
        if host.replace("www.", "") not in extension_data:
            extension_data[host.replace("www.", "")] = []

        if data["extension"]["js"][-3:] == ".ts":
            new_name = data["extension"]["js"].replace(".ts", ".js")
            if confvar.BROWSER_TS_DISABLED:
                return
            if not os.path.isfile(path + new_name):
                utils.log.msg("INFO")("Transpiling TS code")
                os.system("npx tsc " + path + data["extension"]["js"])
            data["extension"]["js"] = new_name

        script_list[path + data["extension"]["js"]] = data["name"]
        extension_data[host.replace("www.", "")].append(
            path + data["extension"]["js"]
        )


def read_extensions():
    extension_files = []
    extension_paths = []

    for path, subdirs, files in os.walk(confvar.BASE_PATH + "extensions/"):
        for name in files:
            extension_files.append(name)
            extension_paths.append(path + "/")

    for i, extension_file in enumerate(extension_files):
        if extension_file[-5:] == ".json":
            try:
                read_extension(extension_paths[i], extension_file)
            except KeyError:
                utils.log.dbg("WARNING")("Faulty extension: " + extension_file)


def javascript_load(path):
    global preload_data

    if path not in list(preload_data.keys()):
        try:
            with open(path) as f:
                js_code = f.read()
                preload_data[path] = [js_code, os.path.dirname(path) + "/"]
        except OSError:
            utils.log.dbg("WARNING")("Could not read: " + path)
            preload_data[path] = [False, False]

    return preload_data[path]


def execute(load_scripts, browser, onload):
    js_code = javascript_load(load_scripts)[0]
    path = javascript_load(load_scripts)[1]

    if not js_code and not path:
        return False

    if onload and script_load[script_list[load_scripts]] != "onload":
        return
    if not onload and script_load[script_list[load_scripts]] == "onload":
        return

    if script_list[load_scripts] in list(permissions.keys()):
        script_id = scripts.get_database().create(
            permissions[script_list[load_scripts]]
        )
    else:
        script_id = scripts.get_database().create([])

    script = (
        api_scripts["run"]
        .replace("{id}", script_id)
        .replace("{path}", '"' + path + '"')
    )

    js_code = script.replace("{source}", js_code)
    browser.page().runJavaScript(js_code, 0)


def on_page_load(browser, onload=False):
    browser.page().runJavaScript(api_scripts["webchannel"])
    browser.page().runJavaScript(api_scripts["api"])

    match = browser.page().url().host().replace("www.", "")
    if match in list(extension_data.keys()):
        for load_scripts in extension_data[match]:
            execute(load_scripts, browser, onload)

    if "*" in list(extension_data.keys()):
        for load_scripts in extension_data["*"]:
            execute(load_scripts, browser, onload)
        return 1
    return 0

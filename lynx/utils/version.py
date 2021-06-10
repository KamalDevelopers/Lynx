import subprocess
import json


def version():
    with open("lynx.json") as f:
        data = json.load(f)

    if "{git-commit-hash}" in data["package"]["version"]:
        lv = subprocess.check_output(["git", "describe", "--always"]).strip()

        return data["package"]["version"].replace(
            "{git-commit-hash}", lv.decode()
        )

    return data["package"]["version"]


print("Lynx Version", version())

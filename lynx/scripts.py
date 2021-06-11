import random

obj = None


class ScriptDatabase:
    def __init__(self):
        global obj
        obj = self
        self.privileges = {}
        self.scripts = []

    def create(self, priv):
        script_id = 0

        while not script_id or script_id in self.scripts:
            script_id = str(random.randint(0, 99999))

        self.privileges[script_id] = priv
        return script_id

    def get(self, script_id):
        if str(script_id) not in list(self.privileges.keys()):
            return []
        return self.privileges[str(script_id)]


def get_database():
    return obj

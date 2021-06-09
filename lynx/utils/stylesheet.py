class StyleSheet:
    def __init__(self, style):
        self.style = style

    def get(self):
        return self.style

    def value(self, element, rule, alter=None):
        lines = self.get().split("\n")
        search = False
        changed = False

        for i, line in enumerate(lines):
            if element == line.replace(" ", "").replace("{", ""):
                search = True
            if "}" in line:
                search = False
            if search:
                if line.split(":")[0].replace(" ", "") == rule:
                    if alter is not None:
                        if not changed:
                            lines[i] = rule + ":" + alter + ";"
                        self.style = " ".join(lines)
                    return line.split(":")[1].replace(" ", "").replace(";", "")
                elif alter is not None and not changed:
                    changed = True
                    lines[i + 1] = rule + ":" + alter + ";" + lines[i + 1]

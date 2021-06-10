import argparse
import confvar


class ArgumentParser:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("URL", nargs="?")
        parser.add_argument("-s", "--stealth", action="store_true")
        parser.add_argument("-l", "--locale", type=str)
        parser.add_argument("-t", "--theme", type=str)
        parser.add_argument("-a", "--agent", type=str)
        parser.add_argument("-p", "--proxy", type=str)
        self.args = parser.parse_args()

    def load(self):
        if self.args.locale:
            confvar.alter_value("BROWSER", "locale", self.args.locale)
        if self.args.theme:
            confvar.alter_value("BROWSER", "stylesheet", self.args.theme)
        if self.args.agent:
            confvar.alter_value("BROWSER", "agent", self.args.agent)
        if self.args.proxy:
            confvar.alter_value("BROWSER", "proxy", self.args.proxy)
        confvar.alter_value("BROWSER", "stealth", self.args.stealth)
        confvar.configure()

    def get(self):
        return self.args


arguments = ArgumentParser()
arguments.load()

import argparse
import confvar


class ArgumentParser:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("URL", nargs="?")
        parser.add_argument("-s", action="store_true")
        parser.add_argument("-l", type=str)
        parser.add_argument("-t", type=str)
        self.args = parser.parse_args()

    def load(self):
        if self.args.l:
            confvar.locale(self.args.l)
        if self.args.t:
            confvar.theme(self.args.t)
        if self.args.s:
            confvar.stealth()
        else:
            confvar.stealth(False)
        confvar.configure()

    def get(self):
        return self.args


arguments = ArgumentParser()
arguments.load()

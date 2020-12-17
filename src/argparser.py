import argparse

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("URL", nargs='?')
    parser.add_argument("-s", action="store_true")
    args = parser.parse_args()
    return args


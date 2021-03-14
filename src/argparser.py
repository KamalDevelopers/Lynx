import argparse

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("URL", nargs='?')
    parser.add_argument("-s", action="store_true")
    parser.add_argument("-l", type=str)
    parser.add_argument("-t", type=str)
    args = parser.parse_args()
    return args


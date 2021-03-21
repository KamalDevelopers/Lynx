import confvar

size = 0
rules = []


def readBlocker():
    global rules, size

    if confvar.BROWSER_ADBLOCKER is True:
        with open(confvar.BASE_PATH + "adblock/lite.txt") as F:
            rules += F.read().split("\n")
    if confvar.BROWSER_MINER_BLOCKER is True:
        with open(confvar.BASE_PATH + "adblock/coinminer.txt") as F:
            rules += F.read().split("\n")
    size = len(rules) - 1

    for x in range(0, size):
        if "*" in rules[x]:
            rules[x] = rules[x].replace("*", "")

    while "" in rules:
        rules.remove("")


def match(url):
    for i, bu in enumerate(rules):
        if bu in url:
            return [i, bu]
    return False

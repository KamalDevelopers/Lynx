from confvar import *
import re

size = 0
rules = [] 
def readBlocker():
    global rules, size
 
    if BROWSER_ADBLOCKER == True:
        with open(BASE_PATH + "adblock/lite.txt") as F:
            rules += F.read().split("\n")
    if BROWSER_MINER_BLOCKER == True:
        with open(BASE_PATH + "adblock/coinminer.txt") as F:
            rules += F.read().split("\n")
    size = len(rules)-1

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

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

def match(url):
    for i, bu in enumerate(rules):
        if bu.replace("*", "") in url and i != size and bu != "":
            return [i, bu]
    return False

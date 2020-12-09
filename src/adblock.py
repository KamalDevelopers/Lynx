from confvar import *
import re

size = 0
rules = [] 
def readBlocker():
    global rules, size
    if BROWSER_ADBLOCKER == "none":
        return

    with open(BASE_PATH + "adblock/" + BROWSER_ADBLOCKER + ".txt") as F:
        rules = F.read().split("\n")
    size = len(rules)-1

def match(url):
    for i, bu in enumerate(rules):
        if bu.replace("*", "") in url and i != size:
            return [i, bu]
    return False

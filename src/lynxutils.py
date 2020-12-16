import os
import sys
from confvar import *

def decodeLynxUrl(qurl):
    if str(qurl.toString())[:5] == "lynx:":
        lfile = str(qurl.toString()).split(":")[1]
        lfile = os.path.abspath(BASE_PATH + "lynx/" + lfile)
    else:
        return qurl.toString()
    lfile = lfile.replace("\\", "/")
    return "file:///" + lfile + ".html"

def encodeLynxUrl(qurl):
    if str(qurl.toString())[:8] == "file:///":
        lfile = str(qurl.toString()).split("/")
        lfile = lfile[len(lfile)-1]
    else:
        return qurl.toString()
    return "lynx:" + lfile[:-5] 

def checkLynxUrl(qurl):
    if str(qurl.toString())[:5] == "lynx:":
        return True
    return False

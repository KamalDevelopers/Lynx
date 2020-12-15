from confvar import *
import json
bookmarks = []

def readBookmarks():
    global bookmarks 
    
    with open(BASE_PATH + 'bookmarks.json') as f:
        data = json.load(f)
    bookmarks = data["bookmarks"]

def getBookmarks():
    return bookmarks

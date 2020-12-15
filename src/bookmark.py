from confvar import *
import json
bookmarks = []

def readBookmarks():
    global bookmarks 
    
    with open(BASE_PATH + 'bookmarks.json') as f:
        data = json.load(f)
    bookmarks = data["bookmarks"]
    print(bookmarks)

def getBookmarks():
    return bookmarks

import confvar
import json

bookmarks = []


def readBookmarks():
    global bookmarks

    with open(confvar.BASE_PATH + "bookmarks.json") as f:
        data = json.load(f)
    bookmarks = data["bookmarks"]


def getBookmarks():
    return bookmarks


def removeBookmark(url):
    if url not in bookmarks:
        return False

    data = {}
    bookmarks.remove(url)
    data["bookmarks"] = bookmarks
    with open(confvar.BASE_PATH + "bookmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    readBookmarks()
    return True


def addBookmark(url, remove=False):
    if url in bookmarks:
        if remove:
            removeBookmark(url)
        return False

    data = {}
    bookmarks.append(url)
    data["bookmarks"] = bookmarks
    with open(confvar.BASE_PATH + "bookmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    readBookmarks()
    return True

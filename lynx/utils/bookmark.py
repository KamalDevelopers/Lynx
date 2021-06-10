import confvar
import json

bookmarks = []


def read_bookmarks():
    global bookmarks

    with open(confvar.BASE_PATH + "bookmarks.json") as f:
        data = json.load(f)
    bookmarks = data["bookmarks"]


def get_bookmarks():
    return bookmarks


def remove_bookmarks(url):
    if url not in bookmarks:
        return False

    data = {}
    bookmarks.remove(url)
    data["bookmarks"] = bookmarks
    with open(confvar.BASE_PATH + "bookmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    read_bookmarks()
    return True


def add_bookmark(url, remove=False):
    if url in bookmarks:
        if remove:
            remove_bookmarks(url)
        return False

    data = {}
    bookmarks.append(url)
    data["bookmarks"] = bookmarks
    with open(confvar.BASE_PATH + "bookmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    read_bookmarks()
    return True

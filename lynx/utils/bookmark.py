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


def has_bookmark(url):
    for i, bookmark in enumerate(bookmarks):
        if bookmark[0] == url:
            return i
    return None


def remove_bookmark(url):
    if has_bookmark(url) is None:
        return False

    data = {}
    del bookmarks[has_bookmark(url)]
    data["bookmarks"] = bookmarks
    with open(confvar.BASE_PATH + "bookmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    read_bookmarks()
    return True


def add_bookmark(url, icon_url, title):
    if has_bookmark(url) is not None:
        remove_bookmark(url)
        return False

    data = {}
    bookmarks.append([url, icon_url, title])
    data["bookmarks"] = bookmarks
    with open(confvar.BASE_PATH + "bookmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    read_bookmarks()
    return True

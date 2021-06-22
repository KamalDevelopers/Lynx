cookie_filter = None
default = True


def read_filter(path):
    global cookie_filter
    global default

    with open(path) as f:
        cookie_filter = f.read().replace(" ", "")
    cookie_filter = cookie_filter.split()

    if "Default:Reject" in cookie_filter:
        default = False


def filter(request):
    if not cookie_filter:
        return True

    if "Allow:" + request.origin.host() in cookie_filter:
        return True
    if "Reject:" + request.origin.host() in cookie_filter:
        return False
    return default

import adblock


adblocker = None
resource_types = [
    "main_frame",
    "sub_frame",
    "stylesheet",
    "script",
    "image",
    "font",
    "sub_frame",
    "object",
    "media",
    "other",
    "other",
    "other",
    "image",
    "xhr",
    "ping",
    "other",
    "csp_report",
    "other",
    "other",
    "other",
    "other",
]


def read_filter(path, regen=False):
    global adblocker

    filter_set = adblock.FilterSet()

    with open(path) as f:
        filter_set.add_filter_list(f.read())

    adblocker = adblock.Engine(filter_set)


def match(url, first_party_url, resource_type):
    global adblocker

    if not adblocker:
        return False

    result = adblocker.check_network_urls(
        url, first_party_url, resource_types[int(resource_type)]
    )
    if not result.matched:
        return False

    return True

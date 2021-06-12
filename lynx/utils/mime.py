import mimetypes

mimetypes.init()


def get_extensions_for_type(general_type):
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split("/")[0] == general_type:
            yield "*" + ext


def get_extensions(mimes):
    extensions = []
    for mime in mimes:
        if "/" in mime and "*" in mime:
            extensions += list(get_extensions_for_type(mime.split("/")[0]))
        elif "/" in mime:
            extensions += mimetypes.guess_all_extensions(mime)
        else:
            extensions.append(mime)
    return extensions

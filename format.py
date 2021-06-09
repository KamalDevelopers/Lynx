import os
import sys
from os import listdir
from os.path import isfile, join

format_paths = ["lynx/", "lynx/utils/"]
format_command = "black --line-length=79 "
ignore = ["confvar.py"]
files = {}
for format_path in format_paths:
    files[format_path] = [f for f in listdir(format_path) if isfile(join(format_path, f))]

for i, fp in enumerate(list(files.keys())):
    for ff in list(files.values())[i]:
        if len(sys.argv) == 2:
            if ff == sys.argv[1]:
                os.system(format_command + fp + ff)
        elif ff not in ignore and ".py" in ff:
            print(ff)
            os.system(format_command + fp + ff)
            print()

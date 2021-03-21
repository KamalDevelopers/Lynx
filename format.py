import os
import sys
from os import listdir
from os.path import isfile, join

format_path = "src/"
format_command = "black --line-length=79 "
ignore = ["main.py"]
files = [f for f in listdir(format_path) if isfile(join(format_path, f))]

for ff in files:
    if len(sys.argv) is 2:
        if ff == sys.argv[1]:
            os.system(format_command + format_path + ff)
    elif ff not in ignore and ".py" in ff:
        print(ff)
        os.system(format_command + format_path + ff)
        print()

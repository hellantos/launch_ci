from git import Repo
from pydriller import Repository
import lizard
import lizard_ext
from pathlib import Path

exts = lizard.get_extensions(["duplicate"])
a = lizard.analyze(paths=["/home/christoph/ws_ros2/src/launch_ros"], exts=exts)
for item in a:
    if hasattr(item, "function_list"):
        for func in item.function_list:
            print(func.__dict__)

for ext in exts:
    if hasattr(ext, "duplicate_rate"):
        dups = ext.get_duplicates()
        for dup in dups:
            pass
        print("Total duplicate rate: %.2f%%" % (ext.duplicate_rate() * 100))
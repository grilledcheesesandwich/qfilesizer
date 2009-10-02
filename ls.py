#!/usr/bin/python
import cPickle as pickle
from FileSize import format_size,File
f = open("sizes.pickle", "rb")
rv = pickle.load(f)
f.close()

rv.set_parents()
#nondirs.sort(File.cmp) # Sort by size

#recurse_all(rv)


for f in rv.children:
    if f.name == ".amsn":
        d = f
rv = d

for f in rv.children:
    p = [x.name for x in f.path]
    p = "/".join(p)
    print "%06s %s" % (format_size(f.size), p)

"""
nondirs = rv.all_nondir_children()

for f in nondirs:
    p = [x.name for x in f.path]
    p = "/".join(p)
    print "%06s %s" % (format_size(f.size), p)
"""

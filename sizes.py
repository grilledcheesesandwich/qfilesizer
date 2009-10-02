#!/usr/bin/python
# Extract object sizes recursively from file system
import sys
import cPickle as pickle

from FileSize import File,recursive_walk
root = sys.argv[1]

rv = recursive_walk(root)  

f = open("sizes.pickle", "wb")
pickle.dump(rv, f, 2)
f.close()


"""
for (dir, dnames, fnames) in os.walk(root):
    (parent, dname) = path.split(dir)
    print parent, dname
    for name in fnames:
        fullname = path.join(dir, name)
        if path.isfile(fullname) and not path.islink(fullname):
            #print fullname, path.getsize(fullname)
            pass

"""
import os
from os import path

class File(object):
    name = None
    size = None
    children = None
    def __init__(self, name, size, children=None):
        self.name = name
        self.size = size
        if children is not None:
            self.children = children
        else:
            self.children = []
    @staticmethod
    def cmp(a, b):
        return cmp(a.size, b.size)

def recursive_walk(root):
    children = []
    try:
        files = os.listdir(root)
    except OSError:
        pass # ignore, regard as empty
    else:
        for fname in files:
            fullname = path.join(root, fname)
            if not path.islink(fullname) and not path.ismount(fullname): # ignore links and mounts
                if path.isdir(fullname):
                    children.append(recursive_walk(fullname))
                else:
                    fsize = path.getsize(fullname)
                    if fsize > 0: # ignore zero sized files
                        children.append(File(fname, fsize))
    # sort children by size
    children.sort(File.cmp)
    (_,name) = path.split(root)
    size = sum([child.size for child in children]) # total size of children
    size += path.getsize(root) # size of dir itself
    return File(name, size, children)
      

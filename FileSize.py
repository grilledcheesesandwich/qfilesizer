# -*- coding: utf-8 -*-
import os
from os import path

class File(object):
    name = None
    size = None
    children = None # None if plain file, [...] if dir
    def __init__(self, name, size, children=None):
        self.name = name
        self.size = size
        self.children = children
    def is_dir(self):
        return self.children is not None

    @staticmethod
    def cmp(a, b):
        """Sort by size descending"""
        return -cmp(a.size, b.size)
    
    def all_nondir_children(self):
        """Return plain list of all non directory children of this node"""
        nondirs = []
        def recurse_all(f): # recurse through, accumulate all nondir children
            if f.is_dir():
                for s in f.children:
                    recurse_all(s)
            else:
                nondirs.append(f)
        recurse_all(self)
        return nondirs

    def set_parents(self):
        """Set parent attribute for all children, recursively"""
        self.parent = None # assume no parent
        if not self.is_dir():
            return # Nothing to do
        for x in self.children:
            x.set_parents()
            x.parent = self
            
    @property
    def path(self):
        """
        Return path from root to here. Only works if parent attributes have been
        created.
        """
        f = self
        dirs = []
        while f is not None:
            dirs.append(f)
            f = f.parent
        dirs.reverse()
        return dirs

    @property
    def path_str(self):
        p = [x.name for x in self.path]
        p = "/".join(p)
        return p

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

def format_size(x):
    if x<1000:
        return "%iB" % (x)
    elif x<1000000:
        return "%.1fK" % (x/1000.0)
    elif x<1000000000:
        return "%.1fM" % (x/1000000.0)
    else:
        return "%.1fG" % (x/1000000000.0)

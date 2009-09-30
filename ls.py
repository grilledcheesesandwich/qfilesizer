#!/usr/bin/python
import pickle

f = open("sizes.pickle", "rb")
rv = pickle.load(f)
f.close()

for f in rv.children:
    print f.name, f.size

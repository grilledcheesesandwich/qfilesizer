# -*- coding: utf-8 -*-
"""
RGB(A) color gradient.
W.J van der Laan 2009
"""
from bisect import bisect_left,insort

class Gradient(object):
    stops = None # (pos, R,G,B,A)
    def __init__(self):
        # Start with simple black to white gradient
        self.stops = [0.0, 1.0]
        self.stop_values = {
        0.0: (0.0, 0.0, 0.0, 1.0),
        1.0: (1.0, 1.0, 1.0, 1.0),
        }
    def set_color_at(self, pos, color):
        # color is 4-tuple (rr,gg,bb,aa)
        # or 3-tuple (rr,gg,bb)
        # Find stop, if not in there, add it
        color = tuple(color)
        if len(color)==3:
            color += (1.0, )
        if not self.stop_values.has_key(pos):
            # Not yet in stops()
            insort(self.stops, pos)
        self.stop_values[pos] = color
    def get_color_at(self, pos):
        if pos > 1.0: # clip
            pos = 1.0
        if pos < 0.0:
            pos = 0.0
        lv = bisect_left(self.stops, pos)
        lv = max(lv, 1)
        lv = min(lv, len(self.stops)-1)
        (a,b) = (self.stops[lv-1],self.stops[lv])
        adata = self.stop_values[a]
        bdata = self.stop_values[b]
        rpos = (pos - a) / (b-a)
        # interpolate pos between adata..bdata depending on rpos
        return tuple([bdata[x]*rpos + (1.0-rpos)*adata[x] for x in xrange(0,4)])
        #print rpos, adata, bdata

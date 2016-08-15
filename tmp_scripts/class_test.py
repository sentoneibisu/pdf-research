#!/usr/bin/env python
import sys
import pandas as pd

class Path:
    def __init__(self):
       self.count = 0
       self.paths = pd.Series("TEST",index=[self.count])

    def add_path(self,path):
        self.count += 1
        new_path = pd.Series(path,index=[self.count])
        self.paths = self.paths.append(new_path)

    def print_path(self):
        print self.paths

if __name__ == "__main__":
    path = Path()
    path.add_path("/aaaa/bbbb")
    path.add_path("/aaaa1/bbbb1")
    path.add_path("/aaaa2/bbbb2")
    path.add_path("/aaaa3/bbbb3")
    path.add_path("/aaaa4/bbbb4")
    print path.print_path()


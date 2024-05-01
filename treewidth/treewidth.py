# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 12:49:28 2017
@author: Arcombe
"""
from  scipy import *
from  pylab import *
import sys
import numpy as np
import random as rd
import time

class treewidth():
    
    def __init__(self, file):
        f_td = open(file + ".td", 'r')
        f_gr = open(file + ".gr", 'r')
        
        line = f_td.readline()
        while line[0] == 'c':
            line = f_td.readline()
        s, td, N, w, n = line.split()
        self.N = int(N)
        self.w = int(w)
        
        line = f_gr.readline()
        while line[0] == 'c':
            line = f_gr.readline()
            
        p, tw, n, m = line.split()
        self.n = int(n)
        self.m = int(m)
        
        self.G_E = [[] for _ in range(self.n + 1)]
        
        for x in range(0, self.m):
            u, v = f_gr.readline().split()
             
            self.G_E[int(u)].append(int(v))
            self.G_E[int(v)].append(int(u))
           
        self.bags = [[] for _ in range(self.N + 1)]
        
        for x in range(1, self.N + 1):
            line = f_td.readline().split()[2:]
            for y in line:
                self.bags[x].append(int(y))
        
        self.T_E = [[] for _ in range(self.N + 1)]
        
        line = f_td.readline()
        while line != "":
            u, v = line.split()
            
            self.T_E[int(u)].append(int(v))
            self.T_E[int(v)].append(int(u))
            
            line = f_td.readline()
        
    def __call__(self):
        self.in_tree = [0 for _ in range(self.N + 1)]
        self.tree = [[] for _ in range(self.N + 1)]
        self.build_tree(1)
        
        best = 0
        root = self.find_best(1)
        for x in root:
            value = root[x]
            if value > best:
                best = value
        print("n =", self.n, "w =", self.w - 1, "best", best)
      
    def check_independent(self, U):
        if len(U) == 0 or len(U) == 1:
            return len(U)
        for i in range(len(U)):
            u = U[i]
            neighbours = self.G_E[u]
            for n in neighbours:
                if n in U:
                    return -1
        return len(U)
    
    def build_tree(self, x):
        self.in_tree[x] = 1
        neighbours = self.T_E[x]
        for n in neighbours:
            if self.in_tree[n] == 0:
                self.tree[x].append(n)
                self.build_tree(n)
    
    def build_bitstrings(self, V_t):
        n = 2**len(V_t) - 1
        length = len(bin(n).split('b')[1])
        T_U = {}
        for x in range(0, n + 1):
            b = bin(x)
            b = b.replace('b', '0')
            if len(b) > length:
                b = b[-1*length:]
            while len(b) < length:
                b = '0' + b
            U = []
            for y in range(length):
                if b[y] == '1':
                    U.append(V_t[y])
            value = self.check_independent(U)
            if value != -1:
                T_U[b] = value
        return T_U
    
    def solve(self, P_Tu, C_Tu, p, c):
        bag_p = self.bags[p]
        bag_c = self.bags[c]
        for pU in P_Tu:
            pU_v = []
            for y in range(len(pU)):
                if pU[y] == '1':
                    pU_v.append(bag_p[y])
            snitt = [val for val in pU_v if val in bag_c]
            best = 0
            for cU in C_Tu:
                cU_v = []
                for y in range(len(cU)):
                    if cU[y] == '1':
                        cU_v.append(bag_c[y])
                if snitt == [val for val in cU_v if val in bag_p]:
                    value = C_Tu[cU] - len([val for val in pU_v if val in cU_v])
                    if value > best:
                        best = value    
            P_Tu[pU] += best
        return P_Tu
    
    
    def find_best(self, bag):
        if (self.tree[bag] == []):
            return self.build_bitstrings(self.bags[bag])
        else:
            children = self.tree[bag]
            P_Tu = self.build_bitstrings(self.bags[bag])
            for child in children:
                C_Tu = self.find_best(child)
                P_Tu = self.solve(P_Tu, C_Tu, bag, child)
            return P_Tu
        
        
        
if __name__ == "__main__":
    start_time = time.time()
    tw = treewidth(sys.argv[1])
    tw()
    print("--- %s seconds ---" % (time.time() - start_time))    
        
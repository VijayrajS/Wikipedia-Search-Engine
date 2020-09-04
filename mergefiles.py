import os
import heapq

n_files = len([u for u in os.listdir() if u.startswith('inter-')])
files = [open('inter-' + str(i), 'r') for i in range(n_files)]

heap = [(files[i].read_line, i) for i in range(len(files))]




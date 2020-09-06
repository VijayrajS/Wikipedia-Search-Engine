import time
t = time.time()
fp = open('dictionary.txt', 'r')
v = fp.readline().split('^')
from search import QueryEvaluator

u = QueryEvaluator()
l = u.evaluateQuery('randy blythe', 10)
for entry in l:
    print(v[entry+1])


print(time.time()-t)

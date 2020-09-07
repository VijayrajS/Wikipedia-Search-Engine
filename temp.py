import time
fp = open('dictionary.txt', 'r')
v = fp.readline().split('^')
from search import QueryEvaluator

u = QueryEvaluator()

time_arr = []

with open('queries_op.txt', 'w') as fp2:
    with open('queries.txt', 'r') as fp:
        while True:
            try:
                t = time.time()
                query = [u.strip() for u in fp.readline().split(',')]
                l = u.evaluateQuery(query[1], int(query[0]))
                time_arr.append(time.time()-t)

                for entry in l:
                    fp2.write(str(entry) + ', ' +str(v[entry+1]) + '\n')
    
                fp2.write(str(sum(time_arr)) +', ' +str(sum(time_arr)/len(time_arr))+'\n')
            except:
                exit()




import os
import heapq as hpq
from functools import reduce

n_files = len([u for u in os.listdir('inter-files/') if u.startswith('inter-')])
files = [open('inter-files/inter-' + str(i), 'r') for i in range(n_files)]

# n_files = len([u for u in sorted(os.listdir('.')) if u.startswith('temp')])
# files = [open('temp' + str(i), 'r') for i in range(1, n_files+1)]

current_prefix = ''
current_term = ''

heap = []

class Node(object):
    def __init__(self, *args):
        self.val = (args)

    def __repr__(self):
        return str(self.val)

    def __lt__(self, other):
        return self.val[0] < other.val[0] if self.val[0] != other.val[0] else self.val[2] < other.val[2]

write_buffer = ''

#first heap_push
for i in range(len(files)):
    line = files[i].readline()
    token, token_cnt = line.split(';', 1)
    n = Node(token, token_cnt, i)
    hpq.heappush(heap, n)
terms = 0

while True:
    try:
        top = hpq.heappop(heap)
        prefix =  top.val[0][:3]
        
        if current_prefix != prefix:
            if current_prefix:
                with open('final-index/' + current_prefix, 'w') as fp:
                    fp.write(write_buffer)
                    current_term = ''
                    write_buffer = ''

            current_prefix = prefix
            print("CURRENT PREFIX SET TO:", current_prefix)
        
        if current_term != top.val[0]:
            terms += 1
            if current_term != '':
                write_buffer += '\n'

            current_term = top.val[0]
            write_buffer += top.val[0] + ';' + top.val[1].strip()

        else:
            write_buffer += top.val[1].strip()
        
        try:
            line = files[top.val[2]].readline()
            if not line:
                files[top.val[2]].close()
                continue
            
            token, token_cnt = line.split(';', 1)
            hpq.heappush(heap, Node(token, token_cnt, top.val[2]))
        except:
            continue
    except IndexError:
        with open('final-index/' + prefix, 'a') as fp:
            fp.write(write_buffer)
            break

print(terms)


import time, re, heapq, math
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import Counter, defaultdict

class QueryEvaluator:
    def __init__(self):
        self.stemmer = SnowballStemmer('english')
        self.stop_words = set(stopwords.words('english'))
        # open docID title file
        
    def OneWordQuery(self, query, fields, k):
        posting_list = query[1].split(';')
        heap = []
        
        for posting in posting_list:
            if not fields:
                nos = [int(u) for u in re.findall(r'\d+', posting)]
                entry = (-sum(nos[1:]), nos[0])
                heap.append(entry)
            else:
                nos = [int(u) for u in re.findall(r'\d+', posting)]
                field_p = re.findall(r'[a-z]', posting)
                sum_ = 0
                
                for i in range(len(nos)-1):
                    if field_p[i] in fields[query]:
                        sum_ += 30 * nos[i+1]
                    else:
                        sum_ += nos[i+1]/30
                
                entry = (-sum(nos[1:]), nos[0])
                heap.append(entry)
        
        heapq.heapify(heap)
        docids = [heap[1] for doc in heap]
        return docids if len(docids) < k else docids[:k]
    
    def extractPosting(self, token):
        fil = 'final-index/' + token[:2]
        fp = open(fil, 'r')
        
        # checking in the first line
        fp.seek(0)
        line = fp.readline()
        if token == line.split(';', 1)[0]:
            return line.strip('\n').split(';', 1)

        fp.seek(0, 2)
        l = 0; r = fp.tell() - 1
        end = r
        prev_mid = -1
        mid = (l + r) >> 1
        
        try:
            while prev_mid != mid and l <= r:
                prev_mid = mid
                fp.seek(mid)

                fp.readline()
                line = fp.readline()
                word = line.split(';', 1)

                if not line or word[0] > token:
                    r = mid - 1
                elif word[0] == token:
                    return [word[0], word[1].strip('\n')]
                else:
                    l = mid
                mid = (l + r) >> 1
        except:
            return ""

    def topK(self, query_vector, query_tokens, posting_list, fields, k):
        tfidf_vectors = defaultdict(lambda: [0] * len(query_tokens))
        
        posting_list = [';'.split(u) for u in posting_list]
        
        docset = None
        
        for lis in posting_list:
            docIDs = [re.findall(r'\d+', posting)[0] for posting in lis]
            if not docset:
                docset = set(docIDs)
            else:
                docset = set.intersection(docset, set(docIDs))

        # for i in range(len(posting_list)):
            
        #     idf = math.log()
        #     nos = [int(u) for u in re.findall(r'\d+', posting_list[i])]
        #     if fields == None:
        #         # if 't' posting_list[i]
        #         # tf = sum(nos[1:])
                
    
    def evaluateQuery(self, query, k):
        query = query.lower()
        query_fields = re.findall(r'[tbcirl]:', query)
        
        query_token_fields = defaultdict(list)
        
        if query_fields:
            s = query
            for field in reversed(query_fields):
                splitted = s.split(field)
                tokens = self.processText(splitted[-1])
                
                for token in tokens:
                    query_token_fields[token].append(field[0])
                s = splitted[0]
            
            query_tokens = list(query_token_fields.keys())
            if len(query_tokens) > 1:
                query_vector = [len(query_token_fields[t]) for t in query_tokens]

        else:
            query_tokens = self.processText(query)
            q_count = Counter(query_tokens)

            query_token_fields = None
            query_tokens = list(set(query_tokens))

            if len(query_tokens) > 1:
                query_vector = [q_count[token] for token in query_tokens]
        
        query_pl = [] #posting lists related to the query
        
        for query_term in query_tokens:
            posting_list = self.extractPosting(query_term)
            
            if len(query_tokens) == 1:
                if posting_list != "":
                   return self.OneWordQuery(posting_list[1], query_token_fields, k)

            else:
                # self.calculateTFIDF(query_vector, posting, , query_token[1])
                query_pl.append(posting_list[1])
        
        return self.topK(query_vector, query_tokens)
        
    def processText(self, text):
        toks = re.findall(r"[\w']{3,}", text.replace("'", "").replace("_", ""))
        nsw = [word for word in toks if word not in self.stop_words]
        stemmed_toks = [self.stemmer.stem(word) for word in nsw]
        return stemmed_toks
    
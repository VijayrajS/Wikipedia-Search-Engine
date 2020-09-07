import time, re, heapq, math, random
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import Counter, defaultdict

class QueryEvaluator:
    def __init__(self):
        self.stemmer = SnowballStemmer('english')
        self.stop_words = set(stopwords.words('english'))
        # open docID title file
        self.N_doc = 731739
        
    def OneWordQuery(self, query, term, fields, k):
        posting_list = query.split(';')
        heap = []
        
        # print(posting_list)
        for posting in posting_list:
            if not fields:
                nos = [int(u) for u in re.findall(r'\d+', posting)]
                if not nos:
                    break
                title_factor = 10 if 't' in posting else 1
                entry = (-sum(nos[1:])*title_factor, nos[0])
                heap.append(entry)
            else:
                nos = [int(u) for u in re.findall(r'\d+', posting)]
                if not nos:
                    break
                field_p = re.findall(r'[a-z]', posting)
                sum_ = 0

                for i in range(len(nos)-1):
                    if field_p[i] in fields[term]:
                        sum_ += 100*nos[i+1]
                    else:
                        sum_ += nos[i+1]/10

                entry = (-sum_, nos[0])
                heap.append(entry)
        
        heapq.heapify(heap)
        docids = [doc[1] for doc in heap]
        return docids if len(docids) < k else docids[:k]

    def extractPosting(self, token):
        fname = token[:3]
        fil = 'final-index/' + fname
        print(fil)
        fp = open(fil, 'r')
        
        while True:
            line = fp.readline()
            line = line.split(';', 1)

            if line[0] == token:
                return [line[0], line[1].strip()]
            
        return ''


    def MultiWordQuery(self, query_vector, query_tokens, posting_list, fields, k):
        tfidf_vectors = defaultdict(lambda: [0] * len(query_tokens))
        
        posting_list = [u.split(';') for u in posting_list]
        docset = None
        idf = []
        
        for lis in posting_list:
            idf.append(self.N_doc/len(lis))
            docIDs = set()
            for posting in lis:
                if posting:
                    docIDs.add(int(re.split(r'([a-z]+)', posting)[0]))
            
            if not docset:
                docset = docIDs
            else:
                docset = set.intersection(docset, set(docIDs))
        tfidf_scores = [{} for _ in range(len(query_tokens))]
        
        for i in range(len(posting_list)):
            for posting in posting_list[i]:
                l = re.split(r'([a-z]+)',posting)
                if l[0] != '' and int(l[0]) in docset:
                    if l[0] == '144657':
                        print(posting)
                    
                    tf = sum([int(l[j]) for j in range(2, len(l), 2)])
                    tf = (1 + math.log10(tf))**2
                    
                    if not fields:
                        if 't' in l:
                            tf = tf **3
                        if 'i' in l:
                            tf *= 2
                        if 'l' in l:
                            tf = tf ** 0.5
                        else:
                            tf /= 3
                    if fields:
                        for j in range(1, len(l), 2):
                            if l[j] in fields[query_tokens[i]]:
                                tf = tf**3
                            else:
                                tf = tf**0.8

                    tfidf = tf * idf[i]
                    tfidf_scores[i][int(l[0])] = tfidf

        heap = []
        # calculate IIIlarity scores
        for docID in docset:
            vector = [tfidf_scores[i][docID] for i in range(len(query_tokens))]
            docscore = sum([vector[i]*query_vector[i] for i in range(len(vector))])
            heap.append((-docscore, docID))
        
        heapq.heapify(heap)
        print(heap[:k])
        docids = [doc[1] for doc in heap]
        return docids if len(docids) < k else docids[:k]

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
                   return self.OneWordQuery(posting_list[1], posting_list[0], query_token_fields, k)

            else:
                query_pl.append(posting_list[1])
        
        return self.MultiWordQuery(query_vector, query_tokens, query_pl, query_token_fields, k)
        
    def processText(self, text):
        toks = re.findall(r"[\w']{3,}", text.replace("'", "").replace("_", ""))
        nsw = [word for word in toks if word not in self.stop_words]
        stemmed_toks = [self.stemmer.stem(word) for word in nsw]
        return stemmed_toks
    
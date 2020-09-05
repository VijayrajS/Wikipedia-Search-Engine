import time, re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import Counter

class QueryEvaluator:
    def __init__(self):
        self.stemmer = SnowballStemmer('english')
        self.stop_words = set(stopwords)
    
    def extractPosting(self, token):
        file = 'final-index/' + token[:2]
        fp = open(file, 'r')
        
        # checking in the first line
        fp.seek(0)
        line = fp.readline()
        if token == line.split(';', 1)[0]:
            return line.strip('\n').split(';', 1)

        fp.seek(0, 2)
        l = 0; r = fp.tell() - 1
        prev_mid = -1
        mid = (l + r) >> 1
        
        while prev_mid != mid and l <= r:
            prev_mid = mid
            fp.seek(mid)

            fp.readline()
            line = fp.readline()
            print(line)
            
            word = line.split(';', 1)[0]

            if not line or word[0] > token:
                r = mid - 1
            elif word[0] == token:
                return [word[0], word[1].strip('\n')]
            else:
                l = mid
            mid = (l + r) >> 1

        return ""

    def evaluateQuery(self, query):
        query = query.lower()
        query_counter = self.processText(query)
        
        query_tokens = sorted(query_counter.keys())
        query_vector = [query_counter[tok] for tok in query_tokens]
        
        for query_term in query_tokens:
            posting_list = self.extractPosting(query_term)
            print(posting_list)
            
            # if posting_list != "":
                # if len(query_tokens) == 1:
                    # self.calculateOneWordRank(posting, 10, query_token[1])
                    # return
                # else:
                    # self.calculateTFIDF(query_vector, docs_vectors, posting, i, query_token[1])
        
    def processText(self, text):
        toks = re.findall(r"[\w']{3,}", text.replace("'", "").replace("_", ""))
        nsw = [word for word in toks if word not in self.stop_words]
        stemmed_toks = [self.stemmer.stem(word) for word in nsw]
        
        return Counter(stemmed_toks)
    
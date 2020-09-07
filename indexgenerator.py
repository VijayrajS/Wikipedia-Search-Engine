import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import time
from collections import defaultdict, Counter

class IndexGenerator:
    
    def __init__(self):
        
        self.FILE_LIMIT = 10000
        self.inv_index = defaultdict(list)
        self.docIDdict = []

        self.stemmer = SnowballStemmer('english')
        self.stop_words = set(stopwords.words('english'))
        self.link_stopwords = ['pp-semi-indef', 'use dmy dates', 'bots', 'google books', 'as of', 'cite']
        self.stub_stopwords = ['doi', 'pmc', 'volume', 'issue', 'pages', 'year', 'pmid', 'journal', 'cite', 'bots']
        
        self.title = ""
        self.stemming_cache = {}
        self.docID = 0
        
        self.abbr_arr = ['t', 'b', 'c', 'i', 'r', 'l']

    def processDict(self, wiki):
        if self.docID % 1000 == 0 and self.docID:
            print(self.docID)
        
        self.title = wiki['title'].strip()
        self.docIDdict.append(self.title)
        counter_arrays = [Counter()]*6
        
        counter_arrays[0] = self.processText(self.title, 0)
        if wiki['body']:
            counter_arrays[1] = self.processText(wiki['body'], 1)
        
        if wiki['categories']:
            counter_arrays[2] = self.processText(wiki['categories'], 2)
        
        if wiki['infobox']:
            counter_arrays[3] = self.processText(wiki['infobox'], 3)
        
        if wiki['references']:
            counter_arrays[4] = self.processText(wiki['references'], 4)
        
        if wiki['externalLinks']:
            counter_arrays[5] = self.processText(wiki['externalLinks'], 5)
        
        # time_s = time.time()
        token_set = []
        for i in range(6):
            token_set += list(counter_arrays[i].keys())
        token_set = set(token_set)
        
        for token in token_set:
            
            index_string = str(self.docID)
            for i in range(6):
                if counter_arrays[i][token] > 0:
                    index_string += (self.abbr_arr[i] + str(counter_arrays[i][token]))
            
            self.inv_index[token].append(index_string)
        
        # self.global_times[0] += time.time() - time_s
        self.docID += 1

    def processText(self, raw_text, index):
        
        raw_text = raw_text.lower()
        raw_text = self.fix_links(raw_text)
        
        tokenised_text = self.tokenize(raw_text)
        
        no_stopw_text = self.removeStopWords(tokenised_text)
        stemmed_tokens = self.stemTokens(no_stopw_text)
        
        return Counter(stemmed_tokens)
        
    def tokenize(self, text):
        # time_s = time.time()
        u = re.findall(r"[\w']{3,}", text.replace("'", "").replace("_", ""))
        
        # self.global_times[1] += time.time() - time_s
        return u
    
    def removeStopWords(self, text):
        # time_s = time.time()
        u = [word for word in text if word not in self.stop_words and ord(word[0]) <= ord('z') and ord(word[1]) <= ord('z') and ord(word[2]) <= ord('z')]
        # self.global_times[2] += time.time() - time_s
        return u
        
    def fix_links(self, text):
        # time_s = time.time()
        text = re.sub(r"(http(s)?://)?([\w\-]+\.)+[\w\-]+(/[\w\- ;,./?%&=]*)?", '', text)
        link_list = re.findall(r"{{[\w |=,:'–\./-]*}}", text)
        text = re.sub(r"{{[\w |=,:'–\./-]*}}", '', text)
        
        if link_list:
            for link in link_list:
                link = link.strip('{').strip('}').split('|')
                for stub in link:
                    if len(stub) < 3 or stub[0] in self.link_stopwords:
                        continue
                    else:
                        for i in range(1, len(stub)):
                            temp = stub.split('=')
                            temp[0] = temp[0].strip()
                            
                            if 'date' in temp[0] or 'url' in temp[0] or temp[0] in self.stub_stopwords:
                                continue
                            else:
                                if len(temp) == 1 and temp[0] != 'vauthors' and temp[0] != 'title':
                                    text += (' ' + temp[0])
                                if len(temp) > 1:
                                    text += (' ' + temp[1])

        # self.global_times[3] += time.time() - time_s
        return text

    def stemTokens(self, tokens):
        # time_s = time.time()
        stemmed_tokens = []
        for token in tokens:
            try:
                stemmed_tokens.append(self.stemming_cache[token][0])
                self.stemming_cache[token][1] += 1
            except:
                self.stemming_cache[token] = [self.stemmer.stem(token), 1]
                stemmed_tokens.append(self.stemming_cache[token][0])
        
        if len(self.stemming_cache) > 100000:
            least_used = sorted(self.stemming_cache.items(), key=lambda x: x[1][0])[:50000]
            for word in least_used:
                del self.stemming_cache[word[0]]
        
        # self.global_times[4] += time.time() - time_s
        return stemmed_tokens
        
    def write_index(self, dump_number):
        with open('inter-files/inter-' + str(dump_number), 'w') as fp:
            for token in sorted(self.inv_index.keys()):
                fp.write(token + ';')
                for entry in self.inv_index[token]:
                    fp.write(entry + ';')
                fp.write('\n')

        with open('dictionary.txt', 'a') as fp:
            fp.write('^' + '^'.join(self.docIDdict))

        self.inv_index = defaultdict(list)
        self.docIDdict = []

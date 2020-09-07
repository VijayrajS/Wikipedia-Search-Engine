import re, sys, os, pickle
import xml.sax
import time
from indexgenerator import IndexGenerator

indGen = IndexGenerator()

class WikiContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.docID = 0
        self.CurrentTag = ""
        self.CurrentPage = {
            'title': '',
            'infobox' : '',
            'body' : '',
            'categories' : '',
            'references': '',
            'externalLinks' : '',
            'infoboxFound': 0,
            'referencesFound': False,
            'extLinksFound' : False
        }

    def startElement(self, tag, attributes):
        self.CurrentTag = tag
    
    def unsetPage(self):
        self.CurrentPage = {
            'title': '',
            'body' : '',
            'categories' : '',
            'infobox' : '',
            'references': '',
            'externalLinks' : '',
            'infoboxFound': 0,
            'referencesFound': False,
            'extLinksFound' : False
        }
        self.CurrentTag = ""
    
    def endElement(self, tag):
        if tag == "page":
            global indGen
            indGen.processDict(self.CurrentPage)
            self.unsetPage()

    def characters(self, content):
        if self.CurrentTag == "title":
            self.CurrentPage['title'] += content
            
        elif self.CurrentTag == "text":
            infoboxFound = re.search(r"{{Infobox", content, re.IGNORECASE)
            condition_matched = False # To check if any condtion has already matched
            
            if infoboxFound:
                self.CurrentPage['infoboxFound'] = 1
                condition_matched = True
            
            if not condition_matched:
                categoryFound = re.search(r'\[\[Category:', content, re.IGNORECASE)
                if categoryFound:
                    self.CurrentPage['categories'] += content[categoryFound.start() :]
                    return
            
            if not condition_matched:
                referenceFound = re.search(r'==reference', content, re.IGNORECASE)
                if referenceFound:
                    self.CurrentPage['referencesFound'] = True
                    condition_matched = True
            
            if not condition_matched:
                categoryFound = re.search(r'==(\ ?)External links==', content, re.IGNORECASE)
                if categoryFound:
                    self.CurrentPage['extLinksFound'] = True
                    condition_matched = True
            
            if not condition_matched:
                self.CurrentPage['body'] += content
            
            if self.CurrentPage['infoboxFound'] > 0:
                self.CurrentPage['infobox'] += content
                if '{{' in content:
                    self.CurrentPage['infoboxFound'] += 1
                
                if '}}' in content:
                    self.CurrentPage['infoboxFound'] -= 1
                
                if content.strip() == '}}':
                    self.CurrentPage['infoboxFound'] = 0
                return
            
            if self.CurrentPage['referencesFound']:
                
                if content.startswith('==') and not (
                    content.startswith('==reference') or content.startswith('==Reference') ):
                    self.CurrentPage['referencesFound'] = False
                
                if len(content) > 1:
                    self.CurrentPage['references'] += content
            
            if self.CurrentPage['extLinksFound']:
                if content[0] == '*':
                    self.CurrentPage['externalLinks'] += content
                
            
if __name__ == "__main__":

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = WikiContentHandler()
    parser.setContentHandler(Handler)

    start = time.time()
    dumps = [u for u in sorted(os.listdir(sys.argv[1])) if u.startswith('enwiki')]
    print(dumps)
    
    for i in range(len(dumps)):
        print("Dump #: ", str(i))
        parser.parse(os.path.join(sys.argv[1], dumps[i].strip()))
        indGen.write_index(i)
    
    print(time.time()-start)
    
    with open('ndocs.txt', 'w') as fp:
        fp.write(str(indGen.docID + 1))


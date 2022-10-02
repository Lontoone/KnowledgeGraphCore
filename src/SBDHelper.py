#import pysbd
from email.policy import default
import spacy
import time
from spacy.tokens import Span
from WikiHelper import wikiHelper
from spacy.language import Language
   
class SbdHelper():
    #@Language.component("briefSbd")
    def briefSbd(self,doc):
        #doc = nlp(text)
        sents = list(doc.sents)

        new_sents=[];
        new_sents.append(sents[0]) #第一個句子
        for i in range(1,len(sents)):
            first_token = sents[i][0]; #每句第一個單字

            if(first_token.pos_ != "PROPN"  ):
                #new_sents[len(new_sents)-1]+=sents[i]; #句首不是PROP就加入前個句子
                span =Span(doc, start=new_sents[len(new_sents)-1].start , end= sents[i].end)
                new_sents[len(new_sents)-1]=span
            else:
                new_sents.append(sents[i])
                
        
        doc._.briefSents=new_sents
        return doc
            
        


if __name__ == "__main__":
    #text = "My name is Jonas E. Smith.          Please turn to p. 55."
    start_time = time.time()

    wiki = wikiHelper()
    text = wiki.GetPage(topic='Python_(programming_language)')

    start_time = time.time()
    nlp = spacy.blank("en")
    nlp.add_pipe('sentencizer')
    doc = nlp(text)
    print("sentencizer ", len(list(doc.sents)))
    print("--- %s seconds ---" % (time.time() - start_time))
    # for sent in doc.sents:
    #    print(sent)

    start_time = time.time()
    nlp1 = spacy.load("en_core_web_sm")
    doc1 = nlp1(text)
    print("en_core_web_sm ", len(list(doc1.sents)))
    print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()
    nlp2 = spacy.load("en_core_web_md")
    doc2 = nlp2(text)
    print("en_core_web_md ", len(list(doc2.sents)))
    print("--- %s seconds ---" % (time.time() - start_time))

    '''
    nlp = spacy.blank('en')

    # add as a spacy pipeline component
    nlp.add_pipe(pysbd_sentence_boundaries)
    doc = nlp(text)
        
    print('sent_id', 'sentence', sep='\t|\t')
    for sent_id, sent in enumerate(doc.sents, start=1):
        print(sent_id, sent.text, sep='\t|\t')
    '''


# Load your usual SpaCy model (one of SpaCy English models)
import re
import spacy
import neuralcoref


class AnaphoraResolutionHelper():
    def arReplacement(self , doc):
        #輸入短句 doc ，替換詞
        #print(doc)
        _str= doc.text
        clusters = doc._.coref_clusters
        for cluster in clusters:
            mainWord = cluster.main.text #主詞
            for word in cluster:
                print("替代",word.text , "主詞 ",mainWord , "找到? ", _str.find(mainWord))   #替換代詞
                #取代所有格
                if word.root.dep_=="poss":                    
                    _str = _str.replace(word.text,mainWord+"'s" , 1)
                #取代代名詞
                else:
                    _str = _str.replace(word.text,mainWord , 1)
                
                
            #token_start = doc.text.find()
            
        #print(_str)
        #doc.text = _str;
        doc._.referedSents=_str;
        return doc
            
        
if __name__ =="__main__":
    nlp = spacy.load("en_core_web_sm")
    #nlp =spacy.blank("en")
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    # Add neural coref to SpaCy's pipe
    neuralcoref.add_to_pipe(nlp)
    text="Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python 0.9.0."  
    doc = nlp(text)

    print("has cor ",doc._.has_coref)
    print("clusters ",doc._.coref_clusters)
    #print("clusters ",doc._.coref_clusters[0].mentions)
    span = doc[-1:]
    print("span",span._.coref_cluster)

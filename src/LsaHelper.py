import numpy as np
from numpy.linalg import norm
from sklearn.feature_extraction import DictVectorizer
import matplotlib.pyplot as plt

class LsaHelper:
    def __init__(self,doc):        
        self.words_count_dict={}#紀錄 <字,字數>的字典
        self.sentCount=0
        
        if (doc==None):
            return
        
        for sent in doc.sents:
            for word in sent:
                #不考慮stop word跟標點符號
                if word.is_stop or word.is_punct:
                    continue
                #剩下的加入字典                
                #self.words_count_dict[word.lemma_.lower()]=0
                self.words_count_dict[word.lower_]=0              
                    
        #print(self.words_count_dict)
        
    #用Pairs初始化字典
    def initWithPairs(self , pairs):
        for pair in pairs:
            #加入字典                            
            self.words_count_dict[pair.lower()]=0          
            
        pass
    
    def getSentencesImportence(self , sents):
        #Sentences embedding
        wcDicts=[]
        _sc=0
        #每個句子的word count dict
        for s in sents:
            #_wcDict = self.getCooccDict(s.lemma_)
            #_wcDict = self.getCooccDict(s.lower_) #[重要更改]
            _wcDict = self.getCooccDict(s)            
            wcDicts.append(_wcDict)
            _sc+=1
        if(len(wcDicts)==0):
            return [-1]
        #合併成一個matrix
        self.f , self.d = self.combineVecsToMatrix(wcDicts)
        #u,s,vh = self.featuresSVD(f)        
        
        #Sentences relativities matrix (填充句子關聯程度矩陣 )
        self.sents_cosSim = np.arange(_sc*_sc).reshape(_sc,_sc).astype(float)
        for i in range(0,_sc):
            for j in range(0,_sc):
                a= self.f[i]
                b=self.f[j]
                sim1_2 = a@b /(norm(a)*norm(b))
                self.sents_cosSim[i,j]=sim1_2
        # nan轉0
        self.sents_cosSim[np.isnan(self.sents_cosSim)]=0
        #avg
        self.sents_avgSim= (self.sents_cosSim.sum(axis=1)-1)/(_sc-1)
        return self.sents_avgSim
    def drawFeatureHeatMap(self):
        #熱圖
        fig, ax = plt.subplots()
        count=len(self.sents_avgSim)
        labels= ["S"+ str(i) for i in np.arange(count)]
        ax.set_xticks(np.arange(count), labels=labels)
        ax.set_yticks(np.arange(count), labels=labels)

        plt.imshow(self.sents_cosSim, cmap='cool', interpolation='nearest')
        plt.show()

    
    #取得該句子的共現向量
    def getCooccDict(self,sent):
        words= sent.lower().split()
        temp_dict = self.words_count_dict.copy()
        for word in words:
            if word in temp_dict:
                temp_dict[word]+=1
        return temp_dict
    
    def combineDictToMatrix(self,pairs):
        pair_coDicts =[]
        for pair in pairs:
            pair_coDicts.append(pair.coVector)
        dictvectorizer = DictVectorizer(sparse=False)
        features = dictvectorizer.fit_transform(pair_coDicts)
        #print(features)
        #print(dictvectorizer.get_feature_names())
        return features,dictvectorizer
    
    def combineVecsToMatrix(self,coVecs):
        pair_coDicts =[]       
        dictvectorizer = DictVectorizer(sparse=False)
        features = dictvectorizer.fit_transform(coVecs)
        #print(features)
        #print(dictvectorizer.get_feature_names())
        return features,dictvectorizer
    
    def featuresSVD(self, features):
        u,s,vh = np.linalg.svd(features)
        self.u=u
        self.s=s
        self.vh =vh
        return u,s,vh
    #給定通過率，取得相對應的閥值
    def getPassThreshold(self,targetRate):
        xlab = np.arange(0.01,0.99,step=0.01) 
        for x in xlab:            
            y= sum(self.sents_avgSim>=x)/len(self.sents_avgSim)
            if y<=targetRate:                
                return x
                
if __name__ =="__main__":
    import spacy
    nlp = spacy.load("en_core_web_sm")    
    #text='Python is often described as a "batteries included" language due to Python comprehensive standard library.Python supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming.'
    '''
    text = 'General elections were held in Lesotho on 24 May 1998, except in the Moyeni constituency, where voting was postponed until 1 August due to the death of one of the candidates.\
            The result was a comprehensive victory for the new Lesotho Congress for Democracy, which claimed 79 of the 80 seats.\
            The party was formed by a breakaway from the Basutoland Congress Party, which had won the 1993 elections Of the 1,017,753 registered voters, there were 593,955 valid votes.'
    '''
    text="Python is a high-level, interpreted, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. \
        Python is dynamically-typed and garbage-collected. It supports multiple programming paradigms, including structured , object-oriented and functional programming. It is often described as a 'batteries included' language due to its comprehensive standard library.\
        Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python-0.9.0. Python-2.0 was released in 2000 and introduced new features such as list comprehensions, cycle-detecting garbage collection, reference counting, and Unicode support. Python-3.0, released in 2008, was a major revision that is not completely backward-compatible with earlier versions. Python-2 was discontinued with version-2.7.18 in 2020.\
        Python consistently ranks as one of the most popular programming languages. Python was conceived in the late 1980s by Guido van Rossum at Centrum Wiskunde and Informatica in the Netherlands as a successor to the ABC programming language, which was inspired by SETL, capable of exception handling and interfacing with the Amoeba operating system. Its implementation began in December-1989. Van Rossum shouldered sole responsibility for the project, as the lead developer, until 12 July 2018, when he announced his 'permanent vacation' from his responsibilities as Python's 'benevolent dictator for life', a title the Python community bestowed \
        upon him to reflect his long-term commitment as the project's chief decision-maker. In January-2019, active Python core developers elected a five-member Steering Council to lead the project.\
        Python-2.0 was released on 16 October 2000, with many major new features. Python-3.0, released on 3 December 2008, with many of its major features backported to Python-2.6.x and 2.7.x. Releases of Python-3 include\
        the 2to3 utility, which automates the translation of Python-2 code to Python-3."
    doc= nlp(text)
    lsa = LsaHelper(doc)    
    sents = list(doc.sents)
    
    lsa.getSentencesImportence(sents)
    
    #熱圖
    fig, ax = plt.subplots()
    count=len(sents)
    labels= ["S"+ str(i) for i in np.arange(count)]
    ax.set_xticks(np.arange(count), labels=labels)
    ax.set_yticks(np.arange(count), labels=labels)

    plt.imshow(lsa.sents_cosSim, cmap='cool', interpolation='nearest')
    plt.show()

    print(lsa.sents_avgSim)
    '''
    sent_coVecs=[]
    for s in sents:
        coVector = lsa.getCooccDict(s.lemma_)
        sent_coVecs.append(coVector)
    
    f , d = lsa.combineVecsToMatrix(sent_coVecs)
    u,s,vh = lsa.featuresSVD(f)
    print (u,s,vh)
    '''
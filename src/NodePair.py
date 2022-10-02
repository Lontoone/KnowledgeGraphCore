class NodePair:    
    def __init__(self,node1,node2,relation):
        self.entity1=node1
        self.entity2=node2
        self.relation=relation
        self.coVector={}
        #self.sent = node1+relation+node2
        
        
class Node:
    def __init__(self,name,verb=""):
        self.name=name
        self.verb=verb
        
        
class NodeSpliter:
    def __init__(self,chunks) :
        self.chunks= chunks
        self.pairs=[]
        self.words_count_dict={}#紀錄 <字,字數>的字典 
    
    #將noun chunks 分成多個NodePair
    def split(self):       
        if len(self.chunks)<1:
            return
        
        self.mainSubject= self.chunks[0].lemma_
        self.rootVerb=self.chunks[0].root.head.lemma_
        self.nounBuffer=""
        _nextIndex=0
        for i in range(1,len(self.chunks)):
            if i<_nextIndex:
                continue
            object_noun ,end = self.findNounRange(self.chunks[i:])
            # 有subject rootV object ，組成 Node Pair
            subjectNode = Node(self.mainSubject)
            objectNode = Node(object_noun)
            
            # 若沒root verb，則使用該句的root verb (通常發生在最後一句)
            if self.rootVerb=="":
                self.rootVerb=self.chunks[i].root.head.lemma_
            
            self.pairs.append(NodePair(subjectNode,objectNode,self.rootVerb))
            
            # 重置
            self.mainSubject=self.nounBuffer
            self.rootVerb=""
            self.nounBuffer=""
            
            _nextIndex=i+end+1
            #i=i+end+1
        return self.pairs
        
    def findNounRange(self,chunks):
        if len(chunks)==1:
           return chunks[0].lemma_ , len(self.chunks)
       
        endIndex=0
        for j in range(0, len(chunks)):  
            c=chunks[j]
            _dep =c.root.head.dep_
            #----------------判斷 dep ----------------------
            if _dep=="prep":
                if self.rootVerb=="":
                    #若無rootVerb，則prep詞當rootVerb
                    self.rootVerb=chunks[j].root.head.lemma_
                else:
                    #否則捨棄該詞，串接主詞與nounBuffer
                    self.nounBuffer+=chunks[j].lemma_
                #繼續抓下一句
                    
            # acl = 例動詞過去式當作形容詞
            elif _dep == "acl":
                # 把root當作該主詞的形容詞
                self.nounBuffer += " "+(chunks[j].root.head.text +" "+ chunks[j].lemma_)
                endIndex=j
                break
                '''
                if self.rootVerb!="" and self.mainSubject!="":
                    return self.nounBuffer
                '''
            
            else:
                # 重設受詞為該句主詞
                self.nounBuffer=chunks[j].lemma_
                endIndex=j
                break
            
        
        # 判斷index
        # 判斷dep
        # 判斷isStop
        
        return self.nounBuffer , endIndex
    
    
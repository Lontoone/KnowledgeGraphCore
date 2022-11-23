class NodePair:    
    def __init__(self,node1,node2,relation):
        self.entity1=node1
        self.entity2=node2
        self.relation=relation
        self.coVector={}        
        #self.isRemoved=False
        self.edgeCounts=0
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
        
        #self.mainSubject= self.chunks[0].lemma_
        self.mainSubject= self.chunks[0].lower_
        self.rootVerb=""
        self.nounBuffer=""
        _nextIndex=0
        for i in range(1,len(self.chunks)):
            if i<_nextIndex:
                continue
            
            c= self.chunks[i]
            #----------- 找Obj-------------            
            object_noun ,end = self.findNounRange(self.chunks[i:])
            
            #----------- 找relation-------------            
            obj_chunk=self.chunks[min(i+end ,len(self.chunks)-1)] #用obj所屬的chunk的動詞決定   
            for j_chunks in self.chunks[i:]:                
                if j_chunks.root.head.pos_  in ["VERB","ADP","SCONJ"]:
                    if j_chunks.root.head.dep_ not in ["pcomp" , "acl"]:
                        self.rootVerb=j_chunks.root.head.lemma_
                        break
                            
            
            #組合node
            subjectNode = Node(self.mainSubject)
            objectNode = Node(object_noun)
            self.pairs.append(NodePair(subjectNode,objectNode,self.rootVerb))
            
            # 重置
            self.mainSubject=self.nounBuffer
            self.rootVerb=""
            self.nounBuffer=""
            _nextIndex=i+end+1
            
        _allCount = len(self.pairs)
        self.pairs= list(filter(lambda p : p.relation!="",self.pairs))
        print("減去空白關聯",_allCount - len(self.pairs),"個")
        return self.pairs
        
        
    def findNounRange(self,chunks):
        #self.nounBuffer=""
        if len(chunks)==1:
           #return chunks[0].lemma_ , len(self.chunks)
           return chunks[0].lower_ , len(self.chunks)
       
        endIndex=0
        j=0
        while j <len(chunks): 
            print("find noun range ", self.nounBuffer) 
            c=chunks[j]
            #direct object =>結束
            #_text=c.lemma_
            _text=c.lower_
            print("current chunks ", _text) 
            if c.root.dep_ in ["dobj","nsubj"]:            
                #self.nounBuffer+=chunks[j].lemma_+" "
                # ====== 判斷head是否為形容詞 =======
                if c.root.head.dep_=="pcomp": #後綴用
                    self.nounBuffer= self.nounBuffer+" "+ _text +" " + c.root.head.text
                elif c.root.head.dep_ in ["acl","prep"]: #前綴用
                    self.nounBuffer=  self.nounBuffer+c.root.head.text+" "+_text
                else:
                    self.nounBuffer+=_text
                
                endIndex=j
                print("== dobj end ==",self.nounBuffer)
                return self.nounBuffer , endIndex
                break
            
            elif c.root.dep_ =="pobj":
                self.nounBuffer =_text+" "+self.nounBuffer              
            print()
          
            j+=1
        endIndex=j
        print('找到obj: ',self.nounBuffer)
        return self.nounBuffer , endIndex
    
def pairs_trim(pairs):    
    newPairsBuffer=[]
    for i_it in range(0,len(pairs)):
        for j_it in range(i_it+1,len(pairs)):
                                   
            i=pairs[i_it]
            j=pairs[j_it]
            sent1=i.entity1.name.lower()
            sent2=j.entity1.name.lower()   
           
            sents=[sent1,sent2]
            #依照長度排a,b
            a,b= min(sents,key=len).lower(),max(sents,key=len).lower()
            isOrdered= ([a,b]==sents)
            #計算a(短的)占比b中多少字
            b_wordCount= len(b.split())
            #過短的就跳過
            if(len(a)<2):
                continue
            #b_wordCount= len(b)
            sim= (b.count(a)) / b_wordCount
            print(a,b,sim)                
            
            if sim>=0.5:#幾乎重複                
                if isOrdered: #留短的
                    j.entity1.name = i.entity1.name
                else:
                    i.entity1.name = j.entity1.name
                print(" [合併] 幾乎重複的node ", sent1, sent2)
                i.edgeCounts+=1
                j.edgeCounts+=1
                #i.toRemove=False
                #j.toRemove=False
            elif sim>0.25:                
                #建立關聯
                if isOrdered: #短的在前
                    newPair=NodePair(Node(sent1),Node(sent2),"about")
                else:
                    newPair=NodePair(Node(sent2),Node(sent1),"about")
                    
                print(" [新增] 新關聯 ", sent1, sent2)
                newPairsBuffer.append(newPair)
                i.edgeCounts+=1
                j.edgeCounts+=1
                #i.toRemove=False
                #j.toRemove=False
            
            pass
        pass
    if len(newPairsBuffer)>0:
        pairs.extend(newPairsBuffer)
    pairs = list(set(pairs)) #刪除重複的
    pairs = [p for p in pairs if p.edgeCounts>1]
    return pairs
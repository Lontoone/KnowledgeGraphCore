class idfHelper:
    def __init__(self):
        self.words_count_dict={}#紀錄 <字,字數>的字典
        self.sentCount=0
        
    def count(self, nodePairs):
        for pairs in nodePairs[:]:        
            for pair in pairs:
                #計算字數
                if pair.entity1.name in self.words_count_dict:
                    self.words_count_dict[pair.entity1.name]+=1
                else:
                    self.words_count_dict[pair.entity1.name]=1

                if pair.entity2.name in self.words_count_dict:
                    self.words_count_dict[pair.entity2.name]+=1
                else:
                    self.words_count_dict[pair.entity2.name]=1            
                self.sentCount+=1
                
                
    

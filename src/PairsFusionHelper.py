#幫助比對pairs 核心node的相似度。
#例如將Python_(genus)的結果nodes群中的核心"Python"比對原本的"Python_(programming_language)"的核心"Python"BOW相似度，
#   不相似則=> noe4j =>使用不同label
from Neo4jHelper import Neo4JHelper
from LsaHelper import LsaHelper
neo4j = Neo4JHelper()
def CheckPairsFusion(pairs1 , label, rate = 0.2):
    #neo4j = Neo4JHelper()
    pairs2 = neo4j.getAllByLabel(label)
    
    if(len(pairs2)==0):
        return -1,""
    
    
    pairs2TextList = [p['name'].lower() for p in pairs2 ]
    #TODO:其實可以弄成class，不然pair1每次都要重建
    pairs1TextList = [p.entity1.name for p in pairs1] + ([p.entity2.name for p in pairs1])
    
    #測試程式用:
    #pairs1TextList = [p['entity1']['name'].lower() for p in pairs1] + ([p['entity2']['name'].lower() for p in pairs1])
    
    p2Text = " ".join(pairs2TextList)
    p1Text = " ".join(pairs1TextList)
    allPairs = [p2Text , p1Text]
    
    #print(allPairs)
    #return 0
    
    #建立BOW
    lsa= LsaHelper(None)
    lsa.initWithPairs(pairs1TextList+pairs2TextList)
    
    #計算pairs1的關聯度
    pair1_importance = lsa.getSentencesImportence(allPairs)    
    avg_imp = sum(pair1_importance)/len(pair1_importance)
    auto_threshold = lsa.getPassThreshold(rate)
    
    #取得bow字數最多的
    d = lsa.getCooccDict(p2Text)
    centerNode = max(d , key=d.get)
    #print(centerNode)
    
    print(f"img {avg_imp} threshold {auto_threshold}")
    if auto_threshold ==None:
        return -1 , ""
    #lsa.drawFeatureHeatMap()
    #print(pair1_importance)
    return (avg_imp/auto_threshold , str(centerNode))
    #建立自己的BOW
    #for 每個已在neo4j的label nodes
    
    #   建立BOW
    #   比較
    
if __name__ =="__main__":
    pairs=[]
    entity1={'name':'Python'}
    entity2={'name':'Pythonidae'}
    pair={"entity1":entity1,"entity2":entity2}
    pairs.append( pair)
    
    entity1={'name':'nonvenomous snakes'}
    entity2={'name':'Africa'}
    pair={"entity1":entity1,"entity2":entity2}
    pairs.append( pair)
    
    entity1={'name':'Africa'}
    entity2={'name':'Good Place'}
    pair={"entity1":entity1,"entity2":entity2}
    pairs.append( pair)
    
    
    #print(pairs)
    labs = neo4j.getAllLabels()
    imp = CheckPairsFusion(pairs, "Python");
    print(imp)
    
    max_imp=0
    for page in labs:        
        importance, maxNode = CheckPairsFusion( pairs , page)
        print(f"To Label: {page} importance {importance}")
        max_imp = max(max_imp , importance)        
        if max_imp >0:
            label = page
            break
    print(max_imp)
    #print(neo4j.getAllLabels())
from faulthandler import disable
from spacy.tokens import Doc
from ARHelper import AnaphoraResolutionHelper
from Id_tdfHelper import idfHelper
from LsaHelper import LsaHelper
from Neo4jHelper import Neo4JHelper
from NodePair import Node, NodePair, NodeSpliter, pairs_trim
from SBDHelper import SbdHelper
from TextCleaner import textCleaner
from WikiHelper import wikiHelper
import spacy
import numpy as np
import neuralcoref
#from spacy.matcher import Matcher
import PairsFusionHelper
import re
#jupyter notebook --notebook-dir=D:\Work\NUTC_gdb\src
processed_pages=[]
db= Neo4JHelper()
nlp = spacy.load("en_core_web_sm")    
def setupNlp(nlp):    
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    #--------- 合併斷句 ------------
    sbd= SbdHelper()
    Doc.set_extension("briefSents" , default=None , force=True)
    nlp.add_pipe(sbd.briefSbd, after="sentencizer",name="sbd")
    
    # ar 處理
    #nlp_ar.remove_pipe('sbd')
    Doc.set_extension("referedSents" , default=None , force=True)
    neuralcoref.add_to_pipe(nlp, name="neuralcoref",after="briefSents")    
    ar = AnaphoraResolutionHelper()    
    nlp.add_pipe(ar.arReplacement,name="arReplacement", after="neuralcoref")  
    
    # 文本後處理
    #nlp.remove_pipe('sentencizer')
    
    
    

def main(_cleanText,preserveRate ):
    # 取得文本
    cleanedText = _cleanText
    #cleanParas= tc.cleanParagraphs()
    
    #---------- 斷句 --------------
    
    #--------- 合併斷句 ------------
    
    disabled = nlp.disable_pipes(["neuralcoref","arReplacement"]);
    doc= nlp(cleanedText)    
    disabled.restore()
    
    print("句子數 ",len(list(doc.sents)), len(doc._.briefSents))    
    print(doc._.briefSents [:15])
    
    #--------- 回指消解 ------------    
    print("--------- 回指消解 ------------")
    
    disabled = nlp.disable_pipes(["sbd"])
    
    clean_full_text= ""
    for sent in doc._.briefSents[:]:
        sent_doc= nlp(sent.text)    
        clean_full_text+=sent_doc._.referedSents
    disabled.restore()
    
    print("------- ar doc長度--------")
    #print(len(doc_array))
    print("------- 乾淨full文本 --------")
    #print(clean_full_text)
   
    #----------- 文本後處理 ?----------------
    
    disabled = nlp.disable_pipes(["sentencizer","sbd","neuralcoref","arReplacement"]);
    nlp_full = nlp
    full_doc = nlp_full(clean_full_text)
    sents= [s.lower_ for s in list(full_doc.sents)] #[重要更改]
    
    print("------------ LSA -------------")
    lsa = LsaHelper(full_doc) #初始化辭庫
    lsa.getSentencesImportence(sents)
    #lsa.drawFeatureHeatMap() #畫關聯圖
    print("------------ LSA剔除 -------------")
    filtered_sents=[]
    threshold=lsa.getPassThreshold(preserveRate)
    #threshold = 0.45
    for i , val in enumerate(lsa.sents_avgSim):
        if val>=threshold:
            filtered_sents.append(sents[i])
        else:
            #print("拒絕 ", sents[i].text) #[重要更改]
            print("拒絕 ", sents[i]) #[重要更改]
    
    print("閥值",threshold,"接受率", sum(lsa.sents_avgSim>=threshold) / len(lsa.sents_avgSim))

    
    # 知識抽取    
    #------------- 實體 ------------------    
    print("------- Noun chunks --------")
    nodePairs=[]
    for sent in filtered_sents:
        #print("保留",sent.text) #[重要更改]
        print("保留",sent) #[重要更改]
        sent_doc=nlp_full(sent)
        nuns=list(sent_doc.noun_chunks)
        
        # 跟merge_nps 工作重複? => 沒有，這個效果比較好?
        spliter=NodeSpliter(nuns) #合併noun chunks
        pairs=spliter.split()
        if pairs:    
            nodePairs.append(pairs[:])              
    
    disabled.restore()
    
    #-------------- 文本相似度 ---------------------    
    #finalNodes = pairs_trim([p.pairs for p in nodePairs])    
    #print("[pair trim] 刪除 " ,len(nodePairs) - len(finalNodes),'個')
    
    finalNodes=[]    
    i=0
    for pairs in nodePairs[:]:        
        for pair in pairs:           
            finalNodes.append(pair)
            print(pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)    
    #用詞頻合併或新增關聯給單字太像的
    finalNodes = pairs_trim(finalNodes)
    
    #finalNodes = [p for p in finalNodes if p.isRemoved==False]
    
    # 得出nodes....繼續
    return finalNodes

def doProcess(pageTitle , itLeft,writeDB,preserveRate=0.1):
    if (itLeft<=0):
        return;
    
    
    wiki = wikiHelper()
    #NLP
    text= wiki.GetPage(pageTitle)
    tc=textCleaner(text)
    cleanText = tc.cleanText(text);
    nodes = main(cleanText,preserveRate)
    
    #Fusion比對
    label = pageTitle
    max_imp=0
    for page in processed_pages:        
        importance , centerNode = PairsFusionHelper.CheckPairsFusion(nodes , page)
        print(f"{pageTitle} To Label: {page} importance {importance}")
        max_imp = max(max_imp , importance)       
        #>1就改寫label (代表label很重複?) 
        if max_imp >1:
            label = page
            print(f"!! [Change] {pageTitle} To Label: {page} !!")
            break
        #替已存在的node群核心添加新label
        '''
        #結果不太優，會誤加很多，還是不要多label好了
        elif max_imp >0.8:            
            db.addLabelToNode(page , centerNode , label )
        ''' 
        
    #-------------- 上傳 Neo4j ---------------------
    if writeDB:
        #db= Neo4JHelper()        
        db.writeNode(nodes,label=label)
            
    
    #寫成文字檔
    '''
    filename = 'Out_'+pageTitle+".txt"
    f=open(filename,'w')
    txt=''
    for pair in nodes:
        txt +=pair.entity1.name +" -> [ "+pair.relation+" ] -> " +pair.entity2.name +'\n'
    f.write(txt)
    f.close()
    '''
    
    #爬蟲
    links = wiki.GetLinks()
    relativeLinks=[]
    for pair in nodes:
        _ent1_pureText= re.sub(r"[_\W]","",pair.entity1.name).lower()
        _ent2_pureText= re.sub(r"[_\W]","",pair.entity2.name).lower()                
        for link in links:
            _lk_pureText=re.sub(r"\(.*\)" , "" , link).lower()
            if _lk_pureText in _ent1_pureText or _lk_pureText in _ent2_pureText:                
                relativeLinks.append(link)
        
                
            #print(pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)
    relativeLinks = [l for l in relativeLinks if l not in processed_pages];
    relativeLinks =  list(dict.fromkeys(relativeLinks)) #移除重複的
    processed_pages.extend(relativeLinks)
    print("==================",itLeft," :相關 link ", relativeLinks,"=====================")
    for link in relativeLinks:
        doProcess(link,(itLeft-1),writeDB)
        
    pass

if __name__=="__main__":
    setupNlp(nlp)
    #先載入目前已有的labels
    processed_pages = db.getAllLabels()
    MAX_IT=1
    #doProcess("Sword_Art_Online",MAX_IT,True);
    #doProcess("Python_(programming_language)",MAX_IT,True,0.1);
    #doProcess("Python_(genus)",MAX_IT,True,0.35);
    doProcess("Kamran_Michael",MAX_IT,True,0.25);
    doProcess("Sam_Michael",MAX_IT,True,0.25);
    doProcess("Michael_Jordan",MAX_IT,True,0.1);
    doProcess("Chicago_Bulls",MAX_IT,True,0.1);
    
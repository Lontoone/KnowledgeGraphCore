from faulthandler import disable
from spacy.tokens import Doc
from ARHelper import AnaphoraResolutionHelper
from Id_tdfHelper import idfHelper
from LsaHelper import LsaHelper
from Neo4jHelper import Neo4JHelper
from NodePair import Node, NodePair, NodeSpliter
from SBDHelper import SbdHelper
from TextCleaner import textCleaner
from WikiHelper import wikiHelper
import spacy
import numpy as np
import neuralcoref
from spacy.matcher import Matcher
import re
#jupyter notebook --notebook-dir=D:\Work\NUTC_gdb\src

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
    
    
    

def main(_cleanText,preserveRate , writeDB):
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
    sents= list(full_doc.sents)
    
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
            print("拒絕 ", sents[i].text)
    
    print("閥值",threshold,"接受率", sum(lsa.sents_avgSim>=threshold) / len(lsa.sents_avgSim))

    
    # 知識抽取    
    #------------- 實體 ------------------    
    print("------- Noun chunks --------")
    nodePairs=[]
    for sent in filtered_sents:
        print("保留",sent.text)
        sent_doc=nlp_full(sent.text)
        nuns=list(sent_doc.noun_chunks)
        
        # 跟merge_nps 工作重複? => 沒有，這個效果比較好?
        spliter=NodeSpliter(nuns) #合併noun chunks
        pairs=spliter.split()
        if pairs:    
            nodePairs.append(pairs[:])              
    
    disabled.restore()
    
    #-------------- 文本相似度 ---------------------    
    finalNodes=[]    
    i=0
    for pairs in nodePairs[:]:        
        for pair in pairs:           
            finalNodes.append(pair)
            print(pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)    
   
    #-------------- 上傳 Neo4j ---------------------
    if writeDB:
        db= Neo4JHelper()
        db.writeNode(finalNodes)
        ##db.writeNode(nodePairs)
            
    # 得出nodes....繼續
    return finalNodes

def doProcess(pageTitle , itLeft):
    if (itLeft<=0):
        return;
    
    wiki = wikiHelper()
        #NLP
    text= wiki.GetPage(pageTitle)
    tc=textCleaner(text)
    cleanText = tc.cleanText(text);
    nodes = main(cleanText,0.15,True)
        
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
    relativeLinks =  list(dict.fromkeys(relativeLinks)) #移除重複的
    print("==================",itLeft," :相關 link ", relativeLinks,"=====================")
    for link in relativeLinks:
        doProcess(link,(itLeft-1))
        
    pass

if __name__=="__main__":
    setupNlp(nlp)
    MAX_IT=3
    doProcess("Sword_Art_Online",MAX_IT);
    '''
    wiki = wikiHelper()
    for i in range(0,MAX_IT):
        if i==0:
            #TODO: 第一次只查關鍵字            
            # 取得文本    
            #text= wiki.GetLocalPage("Python_(programming_language)")
            text= wiki.GetPage("Python_(programming_language)")
            #text= wiki.GetLocalPage("Sword_Art_Online")
            # 文本清理    
            tc=textCleaner(text)
            cleanText = tc.cleanText(text);
            nodes = main(cleanText,0.15,False)
            
            pass
        
        else:
            #TODO:找links
            links = wiki.GetLinks()
            relativeLinks=[]
            for pair in nodes:
                _ent1_pureText= re.sub(r"[_\W]","",pair.entity1.name).lower()
                _ent2_pureText= re.sub(r"[_\W]","",pair.entity2.name).lower()                
                for link in links:
                    _lk_pureText=re.sub(r"\(.*\)" , "" , link).lower()
                    if _lk_pureText not in relativeLinks \
                        and (_lk_pureText in _ent1_pureText or _lk_pureText in _ent2_pureText):
                        relativeLinks.append(link)
                        pass
                    pass               
                
                #print(pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)       
            pass        
            print("相關 link ", relativeLinks)
        pass
    '''
    
    '''
    paras= tc.cleanParagraphs(text)
    for para in paras:
        #temp! 句子數過短的暫時跳過
        if(len(para)<300):
            continue
        print("=== 處理 ===",para)
        print()
        nodes = main(para)
    '''
import math
from unicodedata import name
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
#jupyter notebook --notebook-dir=D:\Work\NUTC_gdb\src
def main(_cleanText):
    # 取得文本
    '''
    wiki = wikiHelper()
    #text =wiki.GetPage("Caracalla")
    #text =wiki.GetPage()
    #text= wiki.GetLocalPage("1998_Lesotho_general_election")
    #text= wiki.GetLocalPage("Semantic_Web")
    text= wiki.GetLocalPage("Python_(programming_language)")
    #text= wiki.GetLocalPage("Caracalla")
    #text= wiki.GetLocalPage("Magic_(game_terminology)")
    #text= wiki.GetLocalPage("Sword_Art_Online")
    #text =wiki.GetPage("Semantic_Web")
    #text='Python supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming.'
    #text='Python is often described as a "batteries included" language due to Python comprehensive standard library.'
    #text ="An animated film titled Sword Art Online The Movie: Ordinal Scale, featuring an original story by Kawahara set after the events of Sword Art Online II, premiered in Japan and Southeast Asia on February 18, 2017, and was released in the United States on March 9, 2017."
    
    #print("取得文本 ", text)
    
    # 文本清理    
    tc=textCleaner(text)
    cleanedText=tc.cleanText()
    '''
    cleanedText = _cleanText
    #cleanParas= tc.cleanParagraphs()
    
    #---------- 斷句 --------------
    nlp = spacy.load("en_core_web_sm")    
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    #--------- 合併斷句 ------------
    sbd= SbdHelper()
    Doc.set_extension("briefSents" , default=None , force=True)
    nlp.add_pipe(sbd.briefSbd, after="sentencizer",name="sbd")
    
    doc= nlp(cleanedText)    
    #matches = matcher(doc)
    
    print("句子數 ",len(list(doc.sents)), len(doc._.briefSents))    
    print(doc._.briefSents [:15])
    
    #--------- 回指消解 ------------
    Doc.set_extension("referedSents" , default=None , force=True)
    print("--------- 回指消解 ------------")
    #nlp_ar=spacy.load("en_core_web_sm")
    nlp_ar= nlp
    nlp_ar.remove_pipe('sbd')
    neuralcoref.add_to_pipe(nlp_ar, name="neuralcoref",after="briefSents")    
    ar = AnaphoraResolutionHelper()    
    nlp_ar.add_pipe(ar.arReplacement,name="arReplacement", after="neuralcoref")  
    
    print("has cor ",doc._.has_coref)
    print("clusters ",doc._.coref_clusters)
    
    
    #doc_array= []
    clean_full_text= ""
    for sent in doc._.briefSents[:]:
        sent_doc= nlp_ar(sent.text)
        #print("------------------------------ ar 結果-----------------------------------------")
        #print(sent_doc._.referedSents)
        #doc_array.append(sent_doc)
        clean_full_text+=sent_doc._.referedSents
        #print(sent_doc._.coref_clusters)
        
    print("------- ar doc長度--------")
    #print(len(doc_array))
    print("------- 乾淨full文本 --------")
    print(clean_full_text)
   
    #----------- 文本後處理 ?----------------
    
    # full process
    #nlp_full = spacy.load("en_core_web_sm")    
    nlp_full = nlp
    nlp_full.remove_pipe('sentencizer')
    full_doc = nlp_full(clean_full_text)
    sents= list(full_doc.sents)
    
    print("------------ LSA -------------")
    lsa = LsaHelper(full_doc) #初始化辭庫
    lsa.getSentencesImportence(sents)
    #lsa.drawFeatureHeatMap()
    print("------------ LSA剔除 -------------")
    filtered_sents=[]
    threshold=lsa.getPassThreshold(0.15)
    for i , val in enumerate(lsa.sents_avgSim):
        if val>=threshold:
            filtered_sents.append(sents[i])
        else:
            print("拒絕 ", sents[i].text)
    
    print("閥值",threshold,"接受率", sum(lsa.sents_avgSim>=threshold) / len(lsa.sents_avgSim))

    
    # 知識抽取    
    #------------- 實體 ------------------    
    #merge_nps = nlp.create_pipe("merge_noun_chunks")
    #nlp_full.add_pipe(merge_nps)
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
            
    #idf_helper= idfHelper()    
    #idf_helper.count(nodePairs)
    #print("sent長度",len(sent_doc),"nodePair長度",len(nodePairs), "idf總數",idf_helper.sentCount)
    '''
    #計算共現次數
    print("------- 計算共現 --------")
    for pairs in nodePairs[:]:
        for pair in pairs:
            #print(pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)
            pair.coVector = lsa.getCooccDict(pair.entity1.name+" "+pair.relation+" "+pair.entity2.name);
            print(pair.coVector)
        #print()
    
    #return nodePairs;     
    features, dictvectorizer= lsa.combineDictToMatrix([y for x in nodePairs for y in x])
    lsa.featuresSVD(features)
    # 重建Lsa權重矩陣 
    #r=5 #取前幾個奇異值
    #up , sp , vp = lsa.u[:,0:r] , np.diag(lsa.s[0:r]) , lsa.vh[:,0:r]
    #ap = up @ sp @ vp.T
    print("======= SVD ============")
    #print(up, sp , vp,ap)
    print("======= s normalized ============")
    norm =np.linalg.norm(lsa.s)
    norm_lsa_s = lsa.s / norm  #標準化後的，每個句子的奇異值    
    #print(norm_lsa_s)    
    '''
 
    
    #-------------- 文本相似度 ---------------------    
    finalNodes=[]    
    filteredNodes=[]    
    i=0
    for pairs in nodePairs[:]:        
        for pair in pairs:           
            finalNodes.append(pair)
            print(pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)
            '''
            pair.sentSing=norm_lsa_s[i]
            if pair.sentSing>0.001:
                finalNodes.append(pair)
            else:
                filteredNodes.append(pair)
            i+=1
            print()             
            '''             
            
        #print()
    
    #檢查結果
    '''
    print("============ Final Outcomes=============")
    for pair in finalNodes:
        print(pair.sentSing,pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)
    print("============ Filter Outcomes=============")
    for pair in filteredNodes:
        print(pair.sentSing,pair.entity1.name,"-> [",pair.relation,"] ->",pair.entity2.name)
    '''
    #-------------- 上傳 Neo4j ---------------------
    '''
    '''
    db= Neo4JHelper()
    db.writeNode(finalNodes)
    ##db.writeNode(nodePairs)
            
    # 得出nodes....繼續
    return finalNodes

if __name__=="__main__":
    # 取得文本    
    wiki = wikiHelper()
    text= wiki.GetLocalPage("Python_(programming_language)")
    # 文本清理    
    tc=textCleaner(text)
    paras= tc.cleanParagraphs(text)
    for para in paras:
        print("=== 處理 ===",para)
        print()
        nodes = main(para)
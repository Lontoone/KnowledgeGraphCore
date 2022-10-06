import re
import wikipediaapi

class wikiHelper:
    def __init__(self):
        self.page=""
        
    def GetPage(self, topic='Python_(programming_language)', lang='en'):
        '''
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page_py = wiki_wiki.page('Python_(programming_language)')

        if(page_py.exists()):
            print(page_py.text);
        '''
        wiki_html = wikipediaapi.Wikipedia(
            language=lang,
            extract_format=wikipediaapi.ExtractFormat.HTML
            #extract_format=wikipediaapi.ExtractFormat.WIKI
            
        )
        p_html = wiki_html.page(topic)
        self.page=p_html
        if(p_html.exists()):
            # print(p_html.text)
            return p_html.text
        else:
            pass
            #TODO: page 不存在 callback
    
    def GetLocalPage(self , topic ):
        import os
        from os.path import exists
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "webPages/"+topic+".txt")
        file_exists = exists(filename)
        if(file_exists):
            f=open(filename, encoding='UTF-8')
            res= f.read()
        else:
            res = self.GetPage(topic)
            with open(filename, 'w' ,encoding='UTF-8') as f:
                f.write(res)
        return res;
    def GetLinks(self):
        if self.page!='':
            return self.page.links.keys()
        else :
            return ""

def main():
    wh =wikiHelper()
    #print(wh.GetLocalPage(topic='Semantic_Web'))
    #print(wh.GetLocalPage(topic='Caracalla'))
    #print(wh.GetLocalPage(topic='Chien-Ming_Wang'))
    #print(wh.GetLocalPage(topic='Wang_Jianmin_(full_general)'))
    #print(wh.GetLocalPage(topic='Python_(programming_language)'))
    #print(wh.GetPage(topic='Python_(programming_language)'))
    
    #from TextCleaner import textCleaner
    text = wh.GetPage(topic='Python_(programming_language)')
    print(wh.GetLinks())
    #tc= textCleaner(text)
    #cleanedText=tc.cleanText()
    #print(cleanedText)


if __name__ == '__main__':
    main()

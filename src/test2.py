from random import sample
import spacy

text="Python is a high-level, interpreted, general-purpose programming language.Python's design philosophy emphasizes code readability with the use of significant indentation.Python is dynamically-typed and garbage-collected. Python supports multiple programming paradigms, including structured , object-oriented and functional programming. Python is often described as a 'batteries included' language due to Python's comprehensive standard library."
#text="Python's core philosophy is summarized in the document The-Zen-of-Python, which includes aphorisms such as:"
    
nlp =spacy.load("en_core_web_sm")
doc = nlp(text)

for token in doc:
    print(token.text , token.lemma_ ,token.pos_,token.tag_ , token.dep_,token.shape_,token.is_stop )
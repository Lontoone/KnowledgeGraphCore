import spacy

nlp = spacy.load("en_core_web_sm")
#text="Python's core philosophy is summarized in the document The-Zen-of-Python, which includes aphorisms such as:"
#text2="Python-2.7's end-of-life was initially set for 2015, then postponed to 2020 out of concern that a large body of existing code could not easily be forward-ported to Python 3."
text2="Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python3."
doc = nlp(text2)
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_,
            chunk.root.head.text , chunk.root.head.dep_,)
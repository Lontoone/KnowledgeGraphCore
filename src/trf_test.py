import spacy
import numpy as np
from spacy.vectors import Vectors
#config = {"model": DEFAULT_TOK2VEC_MODEL}
#nlp.add_pipe("tok2vec", config=config)

nlp= spacy.blank("en")
nlp.add_pipe(nlp.create_pipe('tok2vec'))
#nlp_trf = spacy.load('en_core_web_trf') #限定spacy 3.0+

example_doc = nlp("Helsinki is the capital of Finland.")

print(example_doc)
# Check the length of the Doc object
#print(example_doc.__len__())
#print(example_doc._.trf_data)
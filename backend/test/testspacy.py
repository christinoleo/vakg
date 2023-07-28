import time
import timeit

import spacy
nlp = spacy.load("en_core_web_md")

#%%

doc1 = nlp(u'the person wear red T-shirt')

doc2 = nlp(u'this person is walking')
t1 = time.time()
for i in range(1000):
    doc1.similarity(doc2)
print(time.time() - t1)


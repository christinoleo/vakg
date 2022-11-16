import json
from typing import Tuple

import spacy
from fastapi import APIRouter, Depends
from py2neo import Transaction

from app.api.nlp.models import NLPGetFilteredNodes
from app.graph.connector2 import neodbsession

nlp = spacy.load("en_core_web_md")
cache_texts = {}

router = APIRouter()
url = '/nlp'


def remove_stopwords(text: str) -> Tuple[list, nlp]:
    nlptext = nlp(text.lower())
    lemmas = [t.lemma_ for t in nlptext if not t.is_stop and not t.is_punct]
    return lemmas, nlptext


def add_text(text, node_key='text', r_filter: str = 'none'):
    global cache_texts
    lemmas, nlptext = remove_stopwords(text)
    lemmas = frozenset(lemmas)
    if r_filter not in cache_texts:
        cache_texts[r_filter] = {}
    if lemmas not in cache_texts:
        cache_texts[r_filter][lemmas] = {'nlp': nlptext, node_key: {text}}
    else:
        cache_texts[r_filter][lemmas][node_key].add(text)


def load_text(r: NLPGetFilteredNodes, tx: Transaction, r_filter: str = 'none'):
    from app.api.knowledge.knowledge import all_insights
    texts = all_insights(r, tx)
    for t in texts:
        add_text(list(t.values())[0], r.return_value, r_filter)


def clear_cache_texts():
    global cache_texts
    cache_texts = {}


@router.post(url + '/similar/{text}', tags=['custom'])
async def get_similar(text: str, r: NLPGetFilteredNodes, tx: Transaction = Depends(neodbsession.get_db)):
    node_key = r.return_value
    min_score = r.min_score
    r_filter = 'none' if r.filter is None else json.dumps(r.filter)

    # load data
    if len(cache_texts) == 0:
        load_text(r, tx, r_filter)

    if r_filter not in cache_texts:
        cache_texts[r_filter] = {}

    lemma, nlptext = remove_stopwords(text)
    res = [{node_key: v[node_key], 'score': nlptext.similarity(v['nlp']), 'lemmas': k} for k, v in cache_texts[r_filter].items()]
    res = list(sorted(res, key=lambda x: x['score'], reverse=True))
    print(res)
    res = list(filter(lambda x: x['score'] > min_score, res))
    res = [
        {node_key: item, 'score': sublist['score'], 'lemmas': sublist['lemmas']}
        for sublist in res for item in sublist[node_key]
    ]
    return dict(suggestions=res[:10], lemmas=sorted(lemma))

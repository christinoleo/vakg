# %%
import time
from collections import abc, MutableMapping
from dataclasses import dataclass, field
from typing import Optional, Dict
import json

# %%
import requests

from app.api.knowledge.knowledge import State, Update, Sequence

url = 'http://localhost:8080/'


def req(*, h: Optional[Sequence], m: Optional[Sequence], graph: int = 0):
    t1 = time.time()
    data = dict(graph=dict(id=graph))
    if h is not None: data['h_sequence'] = h.dict()
    if m is not None: data['c_sequence'] = m.dict()
    print(data)
    print(requests.post(url + 'knowledge/new_state', json=data, timeout=0.5).json())
    t2 = time.time()
    print(f'Time: {t2 - t1}')


def get_suggestions(text: str, filter: str = 'intention'):
    r = requests.post('http://localhost:8080/nlp/similar/' + text,
                      json=dict(filters=dict(label=filter)), timeout=0.5).json()
    return r


@dataclass
class StateUpdate:
    label: str
    data: Dict = field(default_factory=dict)


def new_machine(state: StateUpdate, update: StateUpdate, graph=0, user=1, analysis=1):
    req(graph=graph,
        m=Sequence(
            state=State(label=state.label, state_data=flatten_dict(state.data)),
            update=Update(label=update.label, update_data=flatten_dict(update.data), user=user, analysis=analysis)
        ), h=None)
    return state, update


def update(d, u):
    for k, v in u.items():
        if isinstance(v, abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            if v is not None:
                d[k] = v
            else:
                del d[k]
    return d


def new_user(state: StateUpdate, update: StateUpdate, graph=0, user=1, analysis=1):
    req(graph=graph,
        h=Sequence(
            state=State(label=state.label, state_data=state.data),
            update=Update(label=update.label, update_data=update.data, user=user, analysis=analysis)
        ), m=None)
    return state, update


class VAKGSequence:
    def __init__(self, user=1, analysis=1, graph=0):
        self.user = user
        self.analysis = analysis
        self.graph = graph
        self.state = dict()

    def new_insight(self, text: str):
        s = get_suggestions(text)
        lemmas = s['lemmas']
        if len(s['suggestions']) > 0:
            lemmas = sorted(s['suggestions'][0]['lemmas'])

        return new_user(
            state=StateUpdate(label='insight', data=dict(lemmas=lemmas)),
            update=StateUpdate(label='insight', data=dict(text=text)),
            graph=self.graph, user=self.user, analysis=self.analysis)

    def new_intention(self, text: str):
        s = get_suggestions(text, filter='intention')
        lemmas = s['lemmas']
        if len(s['suggestions']) > 0:
            lemmas = sorted(s['suggestions'][0]['lemmas'])

        return new_user(
            state=StateUpdate(label='intention', data=dict(lemmas=lemmas)),
            update=StateUpdate(label='intention', data=dict(text=text)),
            graph=self.graph, user=self.user, analysis=self.analysis)

    def new_specification(self, event, data: Dict = dict(), override=False):
        self.state = update(self.state, data)
        new_machine(
            StateUpdate(label='specification', data=self.state),
            StateUpdate(label=event, data=self.state),
            graph=self.graph, user=self.user, analysis=self.analysis)
        return data

    def new_vis(self, event, data: Dict = dict()):
        _data = update(data.copy(), self.state.copy())
        _data['event'] = event
        new_machine(
            StateUpdate(label='viz', data=_data),
            StateUpdate(label=event, data=_data),
            graph=self.graph, user=self.user, analysis=self.analysis)
        return _data


def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.') -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# %%

print(requests.delete('http://localhost:8888/knowledge/graph/0/'))
new_intention('create rule to compare age groups')
new_specification(dict(rules=['age<45', 'age>45'], view='rules'), 'create rule')
new_vis(dict(rules=['age<45', 'age>45'], view='table'), 'generate')
new_insight('it worked')
new_insight('many notables of lower age group')

# %%
print(requests.delete('http://localhost:8888/knowledge/graph/0/'))
# new_intention('create rule to compare age groups')
new_specification(dict(rules=['age<45', 'age>=45'], view='rules'), 'create rule')
new_vis(dict(rules=['age<45', 'age>=45'], view='table'), 'generate')
new_insight('some bug happened')
new_specification(dict(rules=['age<45', 'age>45'], view='rules'), 'create rule')
new_vis(dict(rules=['age<45', 'age>45'], view='table'), 'generate')
new_insight('many notables of lower age group')

# %%
print(requests.delete('http://localhost:8080/knowledge/graph/0/'))
t = VAKGSequence(1, 1)
t.new_specification('filter by region', dict(filter=dict(region=dict(Passage=False))))
t.new_specification('filter by region', dict(filter=dict(dataset=dict(Shark=False))))
t = VAKGSequence(2, 1)
t.new_specification('filter by region', dict(filter=dict(dataset=dict(Shark=False))))
t.new_specification('filter by region', dict(filter=dict(region=dict(Passage=False))))
# %%

print(requests.delete(url + 'knowledge/graph/0/'))
t = VAKGSequence(1, 1)
t.new_specification('download data')
t.new_vis('load default')
t.new_intention('check shark in the passage')
t.new_specification('filter by region', dict(filter=dict(region='Passage')))
t.new_vis('apply filter')
t.new_specification('filter by dataset', dict(filter=dict(dataset='Shark')))
t.new_vis('apply filter')
t.new_insight('I see that sharks appeared mostly in the north')
t.new_vis('hover map', dict(id=100, station='PASSAGE1', animal_id='12978', count=50))
t.new_insight('there is a station where I see more sharks')
t.new_intention('i want to verify where this shark has appeared before')
t.new_specification('filter by region', dict(filter=dict(region=None)))
t.new_specification('filter by animal_id', dict(filter=dict(animal_id='12978')))
t.new_vis('apply filter')
t.new_insight('this shark is doing well')
t.new_intention('now I will check the fish in the same area')
t.new_specification('filter by animal_id', dict(filter=dict(animal_id=None)))
t.new_specification('filter by dataset', dict(filter=dict(dataset='StripedBass')))
t.new_vis('apply filter')
t.new_insight('overall, it seems fish are the same in the area as in other places')
t.new_intention('I will check if there is anything strange in the weekend')
t.new_specification('filter by dataset', dict(filter=dict(dayofweek='Saturday')))
t.new_vis('apply filter')
t.new_insight('overall, it seems fish are the same in the area as in other places')

print('end')
# %%
print(requests.delete(url + 'knowledge/graph/0/'))
t = VAKGSequence(1, 1)
t.new_specification('download data')
t.new_vis('load default')
t.new_intention('check shark in the passage')
t.new_specification('filter by region', dict(filter=dict(region='Passage')))
t.new_vis('apply filter')
t.new_specification('filter by dataset', dict(filter=dict(dataset='Shark')))
t.new_vis('apply filter')
t.new_insight('I see that sharks appeared mostly in the north')
t.new_vis('hover map', dict(id=100, station='PASSAGE1', animal_id='12978', count=50))
t.new_insight('there is a station where I see more sharks')
t.new_intention('is the region strange in the weekends?')
t.new_specification('filter by dataset', dict(filter=None))
t.new_specification('filter by weekday', dict(filter=dict(dayofweek='Saturday')))
t.new_vis('apply filter')
t.new_insight('the region where I saw the shark is doing well even on saturdays')
t = VAKGSequence(2, 1)
t.new_specification('download data')
t.new_vis('load default')
t.new_intention('check shark in the passage')
t.new_specification('filter by region', dict(filter=dict(region='Passage')))
t.new_specification('filter by dataset', dict(filter=dict(dataset='Shark')))
t.new_vis('apply filter')
t.new_insight('I see that sharks appeared mostly in the south')
t.new_vis('hover map', dict(id=13, station='PASSAGE2', animal_id='5415', count=50))
t.new_insight('passage seems good')
t.new_specification('filter by region', dict(filter=dict(region='Avon')))
t.new_vis('apply filter')
t.new_insight('avon seems good')
t.new_specification('filter by region', dict(filter=dict(region=None)))
t.new_specification('filter by region', dict(filter=dict(dataset=None)))
t.new_specification('filter by weekday', dict(filter=dict(dayofweek='Saturday')))
t.new_vis('apply filter')
t.new_insight('saturday seems good')
print('end')

# %%
print(requests.delete(url + 'knowledge/graph/0/'))
t = VAKGSequence(1, 1)
t.new_intention('lets check the sharks')
t.new_specification('filter by dataset', dict(filter=dict(dataset=1)))
t.new_vis('apply filter')
t.new_insight('saturday seems good')
t = VAKGSequence(2, 1)
t.new_intention('lets check the sharks')
t.new_specification('filter by dataset', dict(filter=dict()))
t.new_vis('apply filter')
t.new_specification('filter by dataset', dict(filter=dict(dataset=1)))
t.new_vis('apply filter')
t.new_insight('saturday seems good')
#%%
text = 'lets check the sharks'
r = requests.post('http://localhost:8080/nlp/similar/' + text, json=dict(filter=dict(label='insight')), timeout=0.5).json()
print(json.dumps(r, indent=2))


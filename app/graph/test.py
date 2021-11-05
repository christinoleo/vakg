# %%
from app.graph.connector2 import neodb

# %%
for a in neodb.query("MATCH (c) RETURN c"):
    for aa in a.values():
        print(aa.labels)

# %%
t = neodb.begin()
print(t.run("MATCH (u1)-[r]-(u2) RETURN *"))
neodb.commit(t)

# %%
import requests

print(requests.delete('http://localhost:8888/knowledge/graph/0/'))
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=1)), update=dict(update_data=dict(test=1), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=2)), update=dict(update_data=dict(test=2), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=3)), update=dict(update_data=dict(test=3), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=1)), update=dict(update_data=dict(test=1), user=2, analysis=2)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=3)), update=dict(update_data=dict(test=3), user=2, analysis=2)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    u_sequence=dict(state=dict(state_data=dict(knowledge=3)), update=dict(update_data=dict(knowledge=3), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    u_sequence=dict(state=dict(state_data=dict(knowledge=30)), update=dict(update_data=dict(knowledge=30), user=2, analysis=2)),
)).json())

# %%
import requests

print(requests.delete('http://localhost:8888/knowledge/graph/0/'))
print(requests.post('http://localhost:8888/knowledge/new_state', json={
    "graph": {"id": 0},
    "va_state": {"state_data": {"test": 1}, "label": "string"},
    "va_update": {"user": 1, "analysis": 1, "update_data": {"test": 1}, "label": "string"}
}).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json={
    "graph": {"id": 0},
    "va_state": {"state_data": {"test": 2}, "label": "string"},
    "va_update": {"user": 1, "analysis": 1, "update_data": {"test": 2}, "label": "string"}
}).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json={
    "graph": {"id": 0},
    "va_state": {"state_data": {"test": 1}, "label": "string"},
    "va_update": {"user": 2, "analysis": 2, "update_data": {"test": 1}, "label": "string"}
}).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json={
    "graph": {"id": 0},
    "va_state": {"state_data": {"test": 3}, "label": "string"},
    "va_update": {"user": 2, "analysis": 2, "update_data": {"test": 3}, "label": "string"}
}).json())
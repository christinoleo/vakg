# %%
import os

os.environ['NEO4J_LOGIN'] = 'neo4j'
os.environ['NEO4J_URL'] = 'bolt://192.168.0.17:7687'
os.environ['NEO4J_PASSWORD'] = '1234554321'

from app.graph.connector import neodb
import statistics

# %%

with neodb.get_db() as db:
    print('users', db.run("match (n) where n.user is not null return distinct(n.user)").data())
    print('number of nodes', db.run("match (n) return count(n)").data())
    print('number of users', db.run("match (n) where n.user is not null return count(distinct(n.user))").data())
    print('total insights', db.run("match (n:H_UPDATE {label:'insight'}) return count(*)").data())
    print('total qol insights', db.run("match (n:H_UPDATE {label:'insight', tool:'qol'}) return count(*)").data())
    print('total ocean insights', db.run("match (n:H_UPDATE {label:'insight', tool:'ocean'}) return count(*)").data())
    print('total intentions', db.run("match (n:H_UPDATE {label:'intention'}) return count(*)").data())
    print('total qol intentions', db.run("match (n:H_UPDATE {label:'intention', tool:'qol'}) return count(*)").data())
    print('total ocean insights', db.run("match (n:H_UPDATE {label:'intention', tool:'ocean'}) return count(*)").data())
    print('unique insights', db.run("match (n:H_STATE {label:'insight'}) return count(*)").data())
    print('unique qol insights', db.run("match (n:H_STATE {label:'insight', tool:'qol'}) return count(*)").data())
    print('unique ocean insights', db.run("match (n:H_STATE {label:'insight', tool:'ocean'}) return count(*)").data())
    print('unique intentions', db.run("match (n:H_STATE {label:'intention'}) return count(*)").data())
    print('unique qol intentions', db.run("match (n:H_STATE {label:'intention', tool:'qol'}) return count(*)").data())
    print('unique ocean intentions', db.run("match (n:H_STATE {label:'intention', tool:'ocean'}) return count(*)").data())
    print('events', db.run("match (n:C_UPDATE) return count(*)").data())
    print('events qol', db.run("match (n:C_UPDATE {tool:'qol'}) return count(*)").data())
    print('events ocean', db.run("match (n:C_UPDATE {tool:'ocean'}) return count(*)").data())
    print('unique events', db.run("match (n:C_STATE) return count(*)").data())
    print('unique events qol', db.run("match (n:C_STATE {tool:'qol'}) return count(*)").data())
    print('unique events ocean', db.run("match (n:C_STATE {tool:'ocean'}) return count(*)").data())

    #########
    # first_intentions = db.run("""
    #     match (n:H_UPDATE {tool:'qol'})
    #     with distinct n.user as user, min(n.created) as created
    #     match (n2:H_UPDATE {tool:'qol'})
    #     where n2.created = created
    #     match (n2)-[:FOLLOWS_INSIGHT*0..5]-(m {label:'insight', tool:'qol'})
    #     return n2.text as intention, m.text as insight, user, n2.analysis as analysis
    # """).data()
    # for fi in first_intentions:
    #     print(fi)
    #     path = db.run("""
    #             match p1=(
    #                 (n1 {text:$intention, label:'intention', tool:'qol'})-[:LEADS_TO]-()-[:FEEDBACK]-(c)-[:UPDATE*0..20]-(m:C_STATE)-[:FEEDBACK]-()-[:LEADS_TO]-(n {text:$insight, label:'insight', tool:'qol'})
    #                 )
    #             WITH nodes(p1) as px order by length(p1) limit 1
    #             UNWIND px as mainPath
    #             optional match (mainPath)-[:LEADS_TO]-(interactions:C_UPDATE)
    #             return count(interactions) as cnt
    #             """, insight=fi['insight'], intention=fi['intention']).data()
    #     fi['path'] = path[0]['cnt']
    # print('average amount of interactions for first task', statistics.mean([f['path'] for f in first_intentions if f['path'] > 0]))

    # print('Average insights on WMT1', db.run("""match (n:H_UPDATE {tool:'qol'})
    #     with distinct n.user as user, min(n.created) as created
    #     match (n2:H_UPDATE {tool:'qol'})
    #     where n2.created = created
    #     match (n2)-[:FOLLOWS_INSIGHT*0..5]-(m {label:'insight', tool:'qol'})
    #     CALL {
    #         with n2
    #         match (ni {label: 'insight', tool:'qol'})
    #         where ni.analysis = n2.analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())

    # print('Average insights on all tasks', db.run("""match (n:H_UPDATE {label:'insight', tool:'qol'})
    #     with distinct n.user as user, n.analysis as analysis
    #     CALL {
    #         with user, analysis
    #         match (ni {label: 'insight', tool:'qol'})
    #         where ni.user = user and ni.analysis = analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())
    # 
    # print('Average intentions on all tasks', db.run("""match (n:H_UPDATE {label:'intention', tool:'qol'})
    #     with distinct n.user as user, n.analysis as analysis
    #     CALL {
    #         with user, analysis
    #         match (ni {label: 'intention', tool:'qol'})
    #         where ni.user = user and ni.analysis = analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())
    # 
    # print('Average insights on all tasks of WBT', db.run("""match (n:H_UPDATE {label:'insight', tool:"qol"})
    #     with distinct n.user as user, n.analysis as analysis
    #     CALL {
    #         with user, analysis
    #         match (ni {label: 'insight', tool:"qol"})
    #         where ni.user = user and ni.analysis = analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())
    # 
    # print('Average intentions on all tasks of WBT', db.run("""match (n:H_UPDATE {label:'intention', tool:"qol"})
    #     with distinct n.user as user, n.analysis as analysis
    #     CALL {
    #         with user, analysis
    #         match (ni {label: 'intention', tool:"qol"})
    #         where ni.user = user and ni.analysis = analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())
    # 
    # print('Average insights on all tasks of ocean', db.run("""match (n:H_UPDATE {label:'insight', tool:"ocean"})
    #     with distinct n.user as user, n.analysis as analysis
    #     CALL {
    #         with user, analysis
    #         match (ni {label: 'insight', tool:"ocean"})
    #         where ni.user = user and ni.analysis = analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())
    # 
    # print('Average intentions on all tasks', db.run("""match (n:H_UPDATE {label:'intention', tool:"ocean"})
    #     with distinct n.user as user, n.analysis as analysis
    #     CALL {
    #         with user, analysis
    #         match (ni {label: 'intention', tool:"ocean"})
    #         where ni.user = user and ni.analysis = analysis
    #       RETURN count(*) as cnt
    #     }
    #     return avg(cnt)""").data())

    # print('Average number of interactions per task in all tasks', db.run("""match (n:H_UPDATE {label: 'insight'})
    #     with n, n.text as text
    #     CALL{
    #       with text
    #       match p1=((n {label:'intention'})-[:LEADS_TO]-()-[:FEEDBACK]-()-[:UPDATE*0..20]-(:C_STATE)-[:FEEDBACK]-()-[:LEADS_TO]-(nn:H_UPDATE {text:text, label:'insight'}))
    #       WITH nodes(p1) as px order by length(p1) limit 1
    #       UNWIND px as mainPath
    #       optional match (mainPath)-[:LEADS_TO]-(interactions:C_UPDATE)
    #       return count(interactions) as cnt
    #     }
    #     return avg(cnt)""").data())

#     type_task = 'qol'
# #     type_task = 'ocean'
#     insights = db.run("""match (n:H_UPDATE {label: 'insight', tool:'""" + type_task + """'})
# with n, n.text as text, ID(n) as nid
# return nid""").data()
#     paths = []
#     for i, nid in enumerate(insights):
#         path = db.run("""match p1=((n1:H_UPDATE {label:'intention', tool:'""" + type_task + """'})-[:LEADS_TO]-()-[:FEEDBACK]-()-[:UPDATE*0..20]-(:C_STATE)-[:FEEDBACK]-()-[:LEADS_TO]-(n:H_UPDATE {label:'insight', tool:'""" + type_task + """'}))
#           WHERE ID(n) = $nid
#           WITH nodes(p1) as px order by length(p1) limit 1
#           UNWIND px as mainPath
#           optional match (mainPath)-[:LEADS_TO]-(interactions:C_UPDATE)
#           return count(interactions) as cnt""", nid=nid['nid']).data()
#         paths.append(path)
#         print(i, len(insights), path)
#     # print(path)
#     print('Average number of interactions per task in ' + type_task + ' tasks', statistics.mean([p[0]['cnt'] for p in paths]))

    # print('Average number of interactions per task in QOL tasks', db.run("""match (n:H_UPDATE {label: 'insight', tool:'qol'})
    #     with n, n.text as text
    #     CALL{
    #       with text
    #       match p1=((n {label:'intention', tool:"qol"})-[:LEADS_TO]-()-[:FEEDBACK]-()-[:UPDATE*0..20]-(:C_STATE)-[:FEEDBACK]-()-[:LEADS_TO]-(nn:H_UPDATE {text:text, label:'insight', tool:"qol"}))
    #       WITH nodes(p1) as px order by length(p1) limit 1
    #       UNWIND px as mainPath
    #       optional match (mainPath)-[:LEADS_TO]-(interactions:C_UPDATE)
    #       return count(interactions) as cnt
    #     }
    #     return avg(cnt)""").data()) # leva 5 min

    # print('Average number of interactions per task in ocean tasks', db.run("""match (n:H_UPDATE {label: 'insight', tool:'ocean'})
    #     with n, n.text as text limit 1
    #     CALL{
    #       with text
    #       match p1=((n {label:'intention', tool:"ocean"})-[:LEADS_TO]-()-[:FEEDBACK]-()-[:UPDATE*0..20]-(:C_STATE)-[:FEEDBACK]-()-[:LEADS_TO]-(nn:H_UPDATE {text:text, label:'insight', tool:"ocean"}))
    #       WITH nodes(p1) as px order by length(p1) limit 1
    #       UNWIND px as mainPath
    #       optional match (mainPath)-[:LEADS_TO]-(interactions:C_UPDATE)
    #       return count(interactions) as cnt
    #     }
    #     return avg(cnt)""").data())

    # print('unique intentions qol', db.run("""match (n:H_UPDATE {label:'intention', tool:'qol'}) - [:
    # LEADS_TO]-(n1)
    # return count(distinct(ID(n1))) as count""").data())
#     print('unique paths of intention to insight', db.run("""match p=((n:H_STATE {label:'insight', tool:'qol'})-
#     [:INSIGHT*0..20]-(n1:H_STATE {label:'intention', tool:'qol'})) return count(p)""").data())
#     print('total paths of intention to insight', db.run("""match p2=((n:H_UPDATE {label:'insight', tool:'qol'})-
#     [:LEADS_TO]->()-[:INSIGHT*0..20]-()-[:LEADS_TO]-(n1:H_UPDATE {label:'intention', tool:'qol'}))
#      return count(p2)
# """).data())
#     print('unique paths of intention to insight', db.run("""match p=((n:H_STATE {label:'insight', tool:'qol'})-[:INSIGHT*0..20]-(n1:H_STATE {label:'intention', tool:'qol'}))
# match p1=((n1:H_STATE {label:'intention', tool:'qol'})-[:FEEDBACK]-(c)-[:UPDATE*0..20]-(m:C_STATE)-[:FEEDBACK]-(n:H_STATE {label:'insight', tool:'qol'}))
# return count(p1)""").data())




    

# %%
t = neodb.begin()
print(t.run("MATCH (u1)-[r]-(u2) RETURN *"))
neodb.commit(t)

# %%
import requests

print(requests.delete('http://localhost:8888/knowledge/graph/0/'))
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=1)),
                     update=dict(update_data=dict(test=1), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=2)),
                     update=dict(update_data=dict(test=2), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=3)),
                     update=dict(update_data=dict(test=3), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=1)),
                     update=dict(update_data=dict(test=1), user=2, analysis=2)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    va_sequence=dict(state=dict(state_data=dict(test=3)),
                     update=dict(update_data=dict(test=3), user=2, analysis=2)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    u_sequence=dict(state=dict(state_data=dict(knowledge=3)),
                    update=dict(update_data=dict(knowledge=3), user=1, analysis=1)),
)).json())
print(requests.post('http://localhost:8888/knowledge/new_state', json=dict(
    graph=dict(id=0),
    u_sequence=dict(state=dict(state_data=dict(knowledge=30)),
                    update=dict(update_data=dict(knowledge=30), user=2, analysis=2)),
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

#%%

with neodb.get_db() as db:
    # [print(x) for x in db.run("match (n:H_UPDATE {tool:'qol', label:'insight'}) return n.text as insight").data()]
    [print(x) for x in db.run("""
    match (n:H_UPDATE {tool:'qol', label:'intention'}) 
    CALL { with n 
         MATCH ((n)-[:LEADS_TO]-()-[:INSIGHT*0..20]-()-[:LEADS_TO]
            -(n1:H_UPDATE {label:'insight', tool:'qol'}))
        return count(n1) as insightcount
     }
    return n.text as insight, insightcount order by insightcount desc""").data()]

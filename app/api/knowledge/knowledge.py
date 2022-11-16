import base64
import datetime
import glob
import json
import os
import random
import uuid

from fastapi import APIRouter, Depends, HTTPException
from py2neo import Node, Transaction, NodeMatcher

from app.api.knowledge.models import *
from app.api.knowledge.utils import *
from app.api.nlp.nlp import add_text, clear_cache_texts
from app.graph.connector2 import neodbsession

router = APIRouter()
url = '/knowledge'


def apply_sequence(tx, seq: Sequence, graph: GraphData, prefix='C'):
    curr_time = datetime.datetime.now()
    matcher = NodeMatcher(tx.graph)
    relationship_data = dict(
        id=graph.id, analysis=seq.update.analysis, user=seq.update.user)
    r_follows = r_follows_update if prefix == 'C' else r_follows_insight
    r_state = r_update if prefix == 'C' else r_insight

    prev_update = get_first_desc(
        tx, f'MATCH (n:{prefix}_UPDATE {{id: $graph_id, analysis: $analysis, user: $user}}) WITH * ORDER BY n.created DESC LIMIT 1 RETURN *',
        graph_id=graph.id, analysis=seq.update.analysis, user=seq.update.user)

    prev_state = get_first_desc(
        tx, f'MATCH (u:{prefix}_UPDATE {{id: $graph_id, analysis: $analysis, user: $user}})-[:LEADS_TO]->(n:{prefix}_STATE {{id: $graph_id}}) '
            'WHERE ID(u)=$update_id '
            'WITH * '
            'ORDER BY n.updated DESC LIMIT 1 RETURN n',
        graph_id=graph.id, analysis=seq.update.analysis, user=seq.update.user, update_id=prev_update.identity) if prev_update else None

    # state
    state_data = seq.state.state_data.copy()
    state_data['label'] = seq.state.label
    for k in state_data.keys():
        if not isinstance(state_data[k], str):
            state_data[k] = json.dumps(state_data[k])
    state_data['id'] = graph.id
    print(state_data)
    state_node = matcher.match(f"{prefix}_STATE", **state_data).first()
    if state_node is None:
        state_data['updated'] = curr_time
        state_data['created'] = curr_time
        state_node = Node(f'{prefix}_STATE', **state_data)
        tx.create(state_node)
    else:
        state_node.update(dict(updated=curr_time))
        tx.push(state_node)

    # update
    update_data = seq.update.update_data.copy()
    update_data['label'] = seq.update.label
    for k in update_data.keys():
        if not isinstance(update_data[k], str):
            update_data[k] = json.dumps(update_data[k])
    update_data.update(relationship_data)
    update_data['updated'] = curr_time
    update_data['created'] = curr_time
    if 'base64' in seq.update.metadata:
        update_data['ref'] = str(uuid.uuid4())
        with open(f"local_storage/images/{update_data['ref']}.jpg", "wb") as fh:
            fh.write(base64.urlsafe_b64decode(seq.update.metadata['base64'].split(',')[1]))
    update_node = Node(f'{prefix}_UPDATE', **update_data)
    tx.create(r_leads_to(update_node, state_node, **relationship_data))

    if prev_update is not None:
        if prev_update == update_node:
            raise HTTPException(404, 'New update state required')

        tx.merge(r_follows(prev_update, update_node, **relationship_data),
                 r_follows.label, tuple(relationship_data.keys()))
        if prev_state is not None and prev_state != state_node:
            # if prev_state == state_node:
            #     raise Exception('Change of state required')
            tx.merge(r_state(prev_state, state_node), r_state.label, dict())
            tx.merge(r_does(prev_state, update_node, **relationship_data),
                     r_does.label, tuple(relationship_data.keys()))

    return state_node, update_node


@router.post(url + '/query_data')
def all_insights(req: GetFilteredNodes, tx: Transaction = Depends(neodbsession.get_db)):
    where = ''
    if len(req.filter) > 0:
        where = ' where ' + ' AND '.join([f"n.{k}='{v}'" for k, v in req.filter.items()])
    ret = tx.run(
        f"match (n:{req.label}) {where} return {'DISTINCT' if req.distinct else ''} {f'n.{req.return_value}' if req.return_value is not None else '*'}")
    return ret.data()


@router.post(url + '/new_state', tags=['KB'])
def new_state(graph: GraphData,
              c_sequence: Optional[Sequence] = None,
              h_sequence: Optional[Sequence] = None,
              tx: Transaction = Depends(neodbsession.get_db)):
    analysis = None
    if c_sequence is not None and c_sequence.update.analysis is not None:
        analysis = c_sequence.update.analysis
    if h_sequence is not None and h_sequence.update.analysis is not None:
        analysis = h_sequence.update.analysis
    if analysis is None:
        analysis = random.randrange(0, 100000)

    user = None
    if c_sequence is None and h_sequence is None:
        raise Exception('need to update something')

    if c_sequence is not None:
        c_sequence.update.analysis = analysis
        state_c, update_c = apply_sequence(tx, c_sequence, graph, 'C')
        user = c_sequence.update.user
        state_h = get_first_desc(
            tx,
            'MATCH (m:H_UPDATE)-[:LEADS_TO {id: $graph_id, user:$user, analysis:$analysis}]->(n:H_STATE {id: $graph_id}) WITH * ORDER BY n.updated DESC LIMIT 1 RETURN n',
            graph_id=graph.id, analysis=analysis, user=user)
        if state_h is not None and state_c is not None:
            tx.create(Relationship(state_h, r_interact.label, state_c))
            if tx.run('match (m:H_STATE)-[e:FEEDBACK]-()-[:UPDATE*0..30]-(m1:C_STATE) where ID(m)=$idm and ID(m1)=$idm1 return count(e) as n',
                      idm=state_h.identity, idm1=state_c.identity).data()[0]['n'] == 0:
                tx.create(Relationship(state_c, r_feedback.label, state_h))

    if h_sequence is not None:
        h_sequence.update.analysis = analysis
        state_h, update_h = apply_sequence(tx, h_sequence, graph, 'H')
        if 'text' in update_h:
            add_text(update_h['text'], 'text', json.dumps(dict(label=update_h['label'])))
        user = h_sequence.update.user
        state_c = get_first_desc(
            tx,
            'MATCH (m:C_UPDATE)-[:LEADS_TO {id: $graph_id, user:$user, analysis:$analysis}]->(n:C_STATE {id: $graph_id}) WITH * ORDER BY n.updated DESC LIMIT 1 RETURN n',
            graph_id=graph.id, analysis=analysis, user=user)
        if state_h is not None and state_c is not None:
            tx.create(Relationship(state_c, r_feedback.label, state_h))
    return dict(result='success', analysis=analysis)


@router.delete(url + '/graph/{graph_id}', tags=['KB'])
async def delete_graph(graph_id: int, tx: Transaction = Depends(neodbsession.get_db)):
    clear_cache_texts()

    # with yappi.run():
    tx.run('MATCH (n:C_STATE) WHERE n.id=$graph_id DETACH DELETE n',
           graph_id=graph_id)
    tx.run('MATCH (n:H_STATE) WHERE n.id=$graph_id DETACH DELETE n',
           graph_id=graph_id)
    tx.run('MATCH (u:C_UPDATE) WHERE u.id=$graph_id DETACH DELETE u',
           graph_id=graph_id)
    tx.run('MATCH (u:H_UPDATE) WHERE u.id=$graph_id DETACH DELETE u',
           graph_id=graph_id)
    # yappi.get_func_stats()._save_as_PSTAT('E:\Projects\phd\knowledgebase\call.pstat')

    files = glob.glob('local_storage/images/*')
    for f in files:
        os.remove(f)
    return 'deleted'

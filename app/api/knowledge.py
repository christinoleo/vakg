import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from py2neo import Node, Transaction, NodeMatcher, Relationship
from pydantic import BaseModel
import json
import random

from app.graph.connector2 import neodbsession

router = APIRouter()
url = '/knowledge'


class KnowledgeUpdateQuery(BaseModel):
    user: str
    analysis: int
    what: str
    by: str
    type: str = 'none'


class GraphData(BaseModel):
    id: int


class State(BaseModel):
    state_data: dict = dict()
    label: Optional[str]


class Update(BaseModel):
    user: int
    analysis: Optional[int]
    update_data: dict = dict()
    label: Optional[str]


class Sequence(BaseModel):
    state: State
    update: Update


class ProcessedNeo4jQuery(BaseModel):
    query: str
    argument: dict = dict()


def dict_converter(d: dict, prefix: str) -> Optional[ProcessedNeo4jQuery]:
    if d is None:
        return None
    # don't use any key with space, use with camelcase or _
    for k in d.keys():
        if not isinstance(k, str) or ' ' in k:
            raise Exception('Only strings with no spaces are allowed!')
    return ProcessedNeo4jQuery(query=', '.join([f'{k}: ${prefix}{k}' for k in d.keys()]),
                               argument={prefix + k: d[k] for k in d.keys()})


def get_first_desc(tx, cypher, node_var='n', **params):
    ret = tx.run(cypher, **params).data()
    if len(ret) == 1:
        return ret[0][node_var]
    else:
        return None


def apply_sequence(tx, seq: Sequence, graph: GraphData, prefix='VA'):
    UPDATES = Relationship.type('UPDATES')
    RUNS = Relationship.type('RUNS')
    PREV_UPDATE = Relationship.type('PREV_UPDATE')
    PREV_STATE = Relationship.type('PREV_STATE')

    curr_time = datetime.datetime.now()
    matcher = NodeMatcher(tx.graph)
    relationship_data = dict(
        id=graph.id, analysis=seq.update.analysis, user=seq.update.user)

    prev_update = get_first_desc(
        tx, f'MATCH (n:{prefix}_UPDATE {{id: $graph_id, analysis: $analysis, user: $user}}) WITH * ORDER BY n.created DESC LIMIT 1 RETURN *',
        graph_id=graph.id, analysis=seq.update.analysis, user=seq.update.user)

    # state
    state_data = seq.state.state_data.copy()
    for k in state_data.keys():
        if not isinstance(state_data[k], str):
            state_data[k] = json.dumps(state_data[k])
    state_data['id'] = graph.id
    print(state_data)
    state_node = matcher.match(f"{prefix}_STATE", **state_data).first()
    if state_node is None:
        state_node = Node(f'{prefix}_STATE', **state_data)
        tx.create(state_node)

    # update
    update_data = seq.update.update_data.copy()
    for k in update_data.keys():
        if not isinstance(update_data[k], str):
            update_data[k] = json.dumps(update_data[k])
    update_data.update(relationship_data)
    update_data['updated'] = curr_time
    update_data['created'] = curr_time
    update_node = Node(f'{prefix}_UPDATE', **update_data)
    tx.create(UPDATES(update_node, state_node, **relationship_data))

    if prev_update is not None:
        if prev_update == update_node:
            raise Exception('Change of update state required')

        prev_state = get_first_desc(
            tx, f'MATCH (u:{prefix}_UPDATE {{id: $graph_id}})-[:UPDATES]->(n:{prefix}_STATE {{id: $graph_id}}) '
            'WHERE ID(u)=$update_id '
            'WITH * '
            'ORDER BY n.updated DESC LIMIT 1 RETURN n',
            graph_id=graph.id, update_id=prev_update.identity)

        tx.merge(PREV_UPDATE(update_node, prev_update, **relationship_data),
                 'PREV_UPDATE', tuple(relationship_data.keys()))
        if prev_state is not None:
            if prev_state == state_node:
                raise Exception('Change of state required')
            tx.merge(PREV_STATE(state_node, prev_state), 'PREV_STATE', dict())
            tx.merge(RUNS(prev_state, update_node, **relationship_data),
                     'RUNS', tuple(relationship_data.keys()))


@router.post(url + '/new_state', tags=['KB'])
async def new_state(graph: GraphData,
                    va_sequence: Optional[Sequence] = None,
                    u_sequence: Optional[Sequence] = None,
                    tx: Transaction = Depends(neodbsession.get_db)):
    analysis = None
    if va_sequence is not None and va_sequence.update.analysis is not None:
        analysis = va_sequence.update.analysis
    if u_sequence is not None and u_sequence.update.analysis is not None:
        analysis = u_sequence.update.analysis
    if analysis is None:
        analysis = random.randrange(0, 100000)

    user = None
    if va_sequence is None and u_sequence is None:
        raise Exception('need to update something')
    if va_sequence is not None:
        va_sequence.update.analysis = analysis
        apply_sequence(tx, va_sequence, graph, 'VA')
        user = va_sequence.update.user
    if u_sequence is not None:
        u_sequence.update.analysis = analysis
        apply_sequence(tx, u_sequence, graph, 'U')
        user = u_sequence.update.user

    state_u = get_first_desc(
        tx, 'MATCH ()-[:UPDATES {user:$user, analysis:$analysis}]->(n:U_STATE {id: $graph_id}) WITH * ORDER BY n.updated DESC LIMIT 1 RETURN n',
        graph_id=graph.id, analysis=analysis, user=user)
    state_va = get_first_desc(
        tx, 'MATCH ()-[:UPDATES {user:$user, analysis:$analysis}]->(n:VA_STATE {id: $graph_id}) WITH * ORDER BY n.updated DESC LIMIT 1 RETURN n',
        graph_id=graph.id, analysis=analysis, user=user)
    if state_u is not None and state_va is not None:
        tx.create(Relationship(state_va, 'LINKS_TO', state_u))

    return dict(result='success', analysis=analysis)


@router.delete(url + '/graph/{graph_id}', tags=['KB'])
async def delete_graph(graph_id: int, tx: Transaction = Depends(neodbsession.get_db)):
    tx.run('MATCH (n:U_STATE) WHERE n.id=$graph_id DETACH DELETE n',
           graph_id=graph_id)
    tx.run('MATCH (n:VA_STATE) WHERE n.id=$graph_id DETACH DELETE n',
           graph_id=graph_id)
    tx.run('MATCH (u:U_UPDATE) WHERE u.id=$graph_id DETACH DELETE u',
           graph_id=graph_id)
    tx.run('MATCH (u:VA_UPDATE) WHERE u.id=$graph_id DETACH DELETE u',
           graph_id=graph_id)
    return 'deleted'

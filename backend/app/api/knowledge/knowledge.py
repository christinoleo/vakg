import base64
import datetime
import glob
import json
import os
import random
import uuid
import copy

from fastapi import APIRouter, Depends, HTTPException
from py2neo import Node, Transaction, NodeMatcher, Relationship as Neo4jRelationship

from app.api.knowledge.models import *
from app.api.knowledge.utils import *
from app.api.nlp.nlp import add_text, clear_cache_texts
from app.graph.connector2 import neodbsession

router = APIRouter()
url = "/knowledge"


def apply_sequence(
    tx, seq: Sequence, graph: GraphData, prefix: Ownership = Ownership.MACHINE
):
    curr_time = datetime.datetime.now()
    matcher = NodeMatcher(tx.graph)
    relationship_data = dict(
        id=graph.id, analysis=seq.sequence.analysis, user=seq.sequence.user
    )

    # get the previous update and state
    prev_update = get_first_desc(
        tx,
        f"MATCH (n:{prefix}_{Temporality.SEQUENCE} "
        f"{{id: $graph_id, analysis: $analysis, user: $user}}) "
        "WITH * ORDER BY n.created DESC LIMIT 1 RETURN *",
        graph_id=graph.id,
        analysis=seq.sequence.analysis,
        user=seq.sequence.user,
    )

    r_state_sequence = (
        Relationship.UPDATES_HUMAN
        if prefix == Ownership.HUMAN
        else Relationship.UPDATES_MACHINE
    )

    prev_state = (
        get_first_desc(
            tx,
            f"MATCH (u:{prefix}_{Temporality.SEQUENCE} {{id: $graph_id, analysis: $analysis, user: $user}})-[:{r_state_sequence}]->(n:{prefix}_{Temporality.STATE} {{id: $graph_id}}) "
            "WHERE ID(u)=$update_id "
            "WITH * "
            "ORDER BY n.updated DESC LIMIT 1 RETURN n",
            graph_id=graph.id,
            analysis=seq.sequence.analysis,
            user=seq.sequence.user,
            update_id=prev_update.identity,
        )
        if prev_update
        else None
    )

    # state
    state_data = seq.state.data.copy()
    state_data["label"] = seq.state.label
    for k in state_data.keys():
        if not isinstance(state_data[k], str):
            state_data[k] = json.dumps(state_data[k])
    state_data["id"] = graph.id
    state_data_without_label: dict = copy.deepcopy(state_data)
    state_data_without_label.pop("label")
    print(state_data)
    state_node = matcher.match(
        f"{prefix}_{Temporality.STATE}", **state_data_without_label
    ).first()
    if state_node is None:
        state_data["updated"] = curr_time
        state_data["created"] = curr_time
        state_node = Node(f"{prefix}_{Temporality.STATE}", **state_data)
        tx.create(state_node)
    else:
        state_node.update(dict(updated=curr_time))
        tx.push(state_node)

    # update
    sequence_data = seq.sequence.data.copy()
    sequence_data["label"] = seq.sequence.label
    for k in sequence_data.keys():
        if not isinstance(sequence_data[k], str):
            sequence_data[k] = json.dumps(sequence_data[k])
    sequence_data.update(relationship_data)
    sequence_data["updated"] = curr_time
    sequence_data["created"] = curr_time
    if "base64" in seq.sequence.metadata:  # save image if is there
        sequence_data["ref"] = str(uuid.uuid4())
        with open(f"local_storage/images/{sequence_data['ref']}.jpg", "wb") as fh:
            fh.write(
                base64.urlsafe_b64decode(seq.sequence.metadata["base64"].split(",")[1])
            )
    sequence_node = Node(f"{prefix}_{Temporality.SEQUENCE}", **sequence_data)
    tx.create(r_state_sequence(sequence_node, state_node, **relationship_data))

    if prev_update is not None:
        if prev_update == sequence_node:
            raise HTTPException(404, "New update state required")

        tx.merge(
            Relationship.PREV_UPDATE(sequence_node, prev_update, **relationship_data),
            Relationship.PREV_UPDATE.label,
            tuple(relationship_data.keys()),
        )
        if prev_state is not None and prev_state != state_node:
            # if prev_state == state_node:
            #     raise Exception('Change of state required')
            tx.merge(
                Relationship.PREV_STATE(state_node, prev_state),
                Relationship.PREV_STATE.label,
                dict(),
            )
            r_does = (
                Relationship.NEW_KNOWLEDGE
                if prefix == Ownership.HUMAN
                else Relationship.NEW_BEHAVIOR
            )
            tx.merge(
                r_does(prev_state, sequence_node, **relationship_data),
                r_does.label,
                tuple(relationship_data.keys()),
            )

    return state_node, sequence_node


@router.post(url + "/query_data")
def all_insights(req: GetFilteredNodes, tx: Transaction = Depends(neodbsession.get_db)):
    where = ""
    if len(req.filter) > 0:
        where = " where " + " AND ".join(
            [f"n.{k}='{v}'" for k, v in req.filter.items()]
        )
    ret = tx.run(
        f"match (n:{req.label}) {where} return {'DISTINCT' if req.distinct else ''} {f'n.{req.return_value}' if req.return_value is not None else '*'}"
    )
    return ret.data()


@router.post(url + "/new_state", tags=["KB"])
def new_state(
    graph: GraphData,
    m_sequence: Optional[Sequence] = None,
    h_sequence: Optional[Sequence] = None,
    tx: Transaction = Depends(neodbsession.get_db),
):
    analysis = None
    if m_sequence is not None and m_sequence.sequence.analysis is not None:
        analysis = m_sequence.sequence.analysis
    if h_sequence is not None and h_sequence.sequence.analysis is not None:
        analysis = h_sequence.sequence.analysis
    if analysis is None:
        analysis = str(random.randrange(0, 100000))

    user = None
    if m_sequence is None and h_sequence is None:
        raise Exception("need to update something")

    if m_sequence is not None:
        m_sequence.sequence.analysis = analysis
        state_c, update_c = apply_sequence(tx, m_sequence, graph, Ownership.MACHINE)
        user = m_sequence.sequence.user
        state_h = get_first_desc(
            tx,
            f"MATCH (m:{Ownership.HUMAN}_{Temporality.SEQUENCE})-[:{Relationship.UPDATES_HUMAN} {{id: $graph_id, user:$user, analysis:$analysis}}]->(n:{Ownership.HUMAN}_{Temporality.STATE} {{id: $graph_id}}) WITH * ORDER BY n.updated DESC LIMIT 1 RETURN n",
            graph_id=graph.id,
            analysis=analysis,
            user=user,
        )
        if state_h is not None and state_c is not None:
            tx.create(
                Neo4jRelationship(state_h, Relationship.SYNCHRONIZES_TO.label, state_c)
            )
            if (
                tx.run(
                    f"match (m:{Ownership.HUMAN}_{Temporality.STATE})-[e:{Relationship.SYNCHRONIZES_TO.label}]-()-[:{Relationship.PREV_STATE}*0..30]-(m1:{Ownership.MACHINE}_{Temporality.STATE}) where ID(m)=$idm and ID(m1)=$idm1 return count(e) as n",
                    idm=state_h.identity,
                    idm1=state_c.identity,
                ).data()[0]["n"]
                == 0
            ):
                tx.create(
                    Neo4jRelationship(
                        state_c, Relationship.SYNCHRONIZES_TO.label, state_h
                    )
                )

    if h_sequence is not None:
        h_sequence.sequence.analysis = analysis
        state_h, update_h = apply_sequence(tx, h_sequence, graph, Ownership.HUMAN)
        if "text" in update_h:
            add_text(
                update_h["text"], "text", json.dumps(dict(label=update_h["label"]))
            )
        user = h_sequence.sequence.user
        state_c = get_first_desc(
            tx,
            f"MATCH (m:{Ownership.MACHINE}_{Temporality.SEQUENCE})-[:{Relationship.UPDATES_MACHINE} {{id: $graph_id, user:$user, analysis:$analysis}}]->(n:{Ownership.MACHINE}_{Temporality.STATE} {{id: $graph_id}}) WITH * ORDER BY n.updated DESC LIMIT 1 RETURN n",
            graph_id=graph.id,
            analysis=analysis,
            user=user,
        )
        if state_h is not None and state_c is not None:
            tx.create(
                Neo4jRelationship(state_c, Relationship.SYNCHRONIZES_TO.label, state_h)
            )
    return dict(result="success", analysis=analysis)


@router.delete(url + "/graph/{graph_id}", tags=["KB"])
async def delete_graph(graph_id: int, tx: Transaction = Depends(neodbsession.get_db)):
    clear_cache_texts()

    # tx.run("MATCH (n:C_STATE) WHERE n.id=$graph_id DETACH DELETE n", graph_id=graph_id)
    # tx.run("MATCH (n:H_STATE) WHERE n.id=$graph_id DETACH DELETE n", graph_id=graph_id)
    # tx.run("MATCH (u:C_UPDATE) WHERE u.id=$graph_id DETACH DELETE u", graph_id=graph_id)
    # tx.run("MATCH (u:H_UPDATE) WHERE u.id=$graph_id DETACH DELETE u", graph_id=graph_id)
    tx.run("MATCH (u) WHERE u.id=$graph_id DETACH DELETE u", graph_id=graph_id)

    files = glob.glob("local_storage/images/*")
    for f in files:
        os.remove(f)
    return "deleted"

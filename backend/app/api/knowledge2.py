from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.graph.connector import neodb

router = APIRouter()
url = "/knowledge"


class KnowledgeUpdateQuery(BaseModel):
    user: str
    analysis: str
    what: str
    by: str
    type: str = "none"


class KnowledgeQuery(BaseModel):
    from_state: dict = {}
    to_state: dict = {}
    update: KnowledgeUpdateQuery
    knowledge: Optional[dict] = None


class ProcessedNeo4jQuery(BaseModel):
    query: str
    argument: dict = {}


def dict_converter(d: dict, prefix: str) -> Optional[ProcessedNeo4jQuery]:
    if d is None:
        return None
    # don't use any key with space, use with camelcase or _
    for k in d.keys():
        if not isinstance(k, str) or " " in k:
            raise Exception("Only strings with no spaces are allowed!")
    return ProcessedNeo4jQuery(
        query=", ".join([f"{k}: ${prefix}{k}" for k in d.keys()]),
        argument={prefix + k: d[k] for k in d.keys()},
    )


@router.post(url)
async def get_all(r: KnowledgeQuery, db=Depends(neodb.get_db)):
    from_state = dict_converter(r.from_state, "from_state_")
    update = dict_converter(r.update.dict(), "update_")
    to_state = dict_converter(r.to_state, "to_state_")
    knowledge = dict_converter(r.knowledge, "knowledge_")
    query = f"""
            MERGE (s1:STATE {{{from_state.query}}})
            MERGE (s2:STATE {{{to_state.query}}})
            WITH *, [s1, s2] as elements
            CALL apoc.lock.nodes(elements)
            MERGE (s1)<-[rps:PREV_STATE]-(s2)
            WITH *
            CALL {{
                WITH *
                OPTIONAL MATCH (u0:UPDATE {{user: $update_user, analysis: $update_analysis}})
                RETURN u0
                ORDER BY u0.created DESC
                LIMIT 1
            }}
            CREATE (s1)-[r:RUNS]->(u:UPDATE {{{update.query}, created: timestamp()}})-[ru:UPDATES]->(s2)
            FOREACH (ignoreme in CASE WHEN u0 IS NOT null THEN [1] ELSE [] END | MERGE (u0)<-[rpu:PREV_UPDATE]-(u))
            RETURN u, s1, s2, u0
    """

    query2 = f"""
            MATCH (u0:UPDATE)
            ORDER BY u0.created DESC
            LIMIT 2
            RETURN u0
    """

    params: dict = from_state.argument
    params.update(update.argument)
    params.update(to_state.argument)

    # OPTIONAL MATCH(u0: UPDATE {update.query})-[:UPDATES]->(s1)
    # WITH MAX(u0.created) as created0max
    # WHERE u0.created = created0max
    # UNION
    # MATCH(s1: STATE $from_state) < -[: UPDATE]-(u:UPDATE {analysis: $analysis, user:$user})
    # RETURN *

    def _run(tx):
        if r.knowledge is None or len(r.knowledge) == 0:
            ret1 = tx.run(query, **params).data()
            # ret2 = tx.run(query2, **params).data()
            return [ret1]
        else:
            params.update(knowledge.argument)
            return tx.run(
                query,
                from_state=r.from_state,
                to_state=r.to_state,
                update=r.update.dict(),
                analysis=r.update.analysis,
                user=r.update.user,
            ).data()

    with db as session:
        result = session.write_transaction(_run)
        print(result)
    return result


@router.delete(url + "/all")
async def delete_all(db=Depends(neodb.get_db)):
    query = f"""
    MATCH (u:UPDATE), (s:STATE)
    DETACH DELETE u, s
    """

    def _run(tx):
        return tx.run(query).data()

    with db as session:
        result = session.write_transaction(_run)
        print(result)
    return result

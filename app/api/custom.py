from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends
from py2neo import Transaction
from pydantic import BaseModel

from app.graph.connector2 import neodbsession

router = APIRouter()
url = '/custom_query'


class Neo4jCustomQuery(BaseModel):
    main_request: str = 'MATCH (u1)-[r]-(u2) RETURN *'
    variables: Optional[Dict[str, Any]] = None


@router.post(url, tags=['custom'])
async def get_all(r: Neo4jCustomQuery, tx: Transaction = Depends(neodbsession.get_db)):
    print(f"custom {r.main_request} {r.variables}")
    result = tx.run(r.main_request, r.variables).data()
    print(result)
    return result


@router.get(url+'/get_all_nodes_and_relationships', tags=['custom'])
async def get_all_nodes_and_relationships(tx: Transaction = Depends(neodbsession.get_db)):
    result = tx.run('MATCH (n1)-[r]-(n2) RETURN *').data()
    print(result)
    return result


@router.get(url+'/get_all_nodes', tags=['custom'])
async def get_all_nodes(tx: Transaction = Depends(neodbsession.get_db)):
    result = tx.run('MATCH (n) RETURN n').data()
    print(result)
    return result


@router.get(url+'/get_all_relationships', tags=['custom'])
async def get_all_relationships(tx: Transaction = Depends(neodbsession.get_db)):
    result = tx.run('MATCH ()-[r]-() RETURN r').data()
    print(result)
    return result

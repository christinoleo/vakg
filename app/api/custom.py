from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends
from py2neo import Transaction
from pydantic import BaseModel
from starlette.responses import FileResponse

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

@router.get(url+'/get_cypher', tags=['custom'])
async def get_cypher(tx: Transaction = Depends(neodbsession.get_db)):
    result = tx.run('CALL apoc.export.cypher.all(null, {stream:true})').data()
    try:
        filename = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.cy"
        filepath = f"local_storage/snapshots/{filename}"
        with open(filepath, "wt") as fh:
            fh.write(result[0]['cypherStatements'])
        return FileResponse(filepath,
                            media_type='application/octet-stream',
                            filename=filename)

    except:
        print('NO FILE')
    print(result)
    return result

@router.get(url+'/run_cypher/{file}', tags=['custom'])
async def run_cypher(file:str, tx: Transaction = Depends(neodbsession.get_db)):
    with open(f"local_storage/snapshots/{file}.cy", "rt") as fh:
        qs = fh.read().replace(':begin', '').replace(':commit', '').replace('\n', '').split(';')
        for q in qs:
            tx.run(q)
        # for line in fh:
        #     print(line)
        #     if ':commit' in line:
        #         # tx.commit()
        #         pass
        #     elif 'awaitIndexes' in line:
        #         # tx.commit()
        #         pass
        #     elif ':begin' not in line:
        #         result = tx.run(line)

    return {}

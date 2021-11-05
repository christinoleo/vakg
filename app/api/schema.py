from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.graph.connector import neodb

router = APIRouter()
url = '/schema'


class SchemaResult(BaseModel):
    nodes: List[dict]
    relationships: List[dict]


@router.get(url, response_model=SchemaResult)
async def get_all(db=Depends(neodb.get_db)):
    with db as session:
        result = session.write_transaction(lambda tx: tx.run('call db.schema.visualization()').single())
    relationships = []
    for r in result['relationships']:
        relationships.append(dict(source=r.start_node.id, name=r.type, target=r.end_node.id, id=r.id))
    nodes = []
    for n in result['nodes']:
        nodes.append(dict(id=n.id, labels=n.labels))
    ret = SchemaResult(nodes=nodes, relationships=relationships)
    return ret

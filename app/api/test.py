from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.graph.connector import neodb

router = APIRouter()
url = '/neo4j'


class DataFields(BaseModel):
    name: str


class MapRequest(BaseModel):
    index_field: str = 'location_postal'


class MapResponse(BaseModel):
    data: str


@router.get(url,
            # response_model=MapResponse,
            # response_model_exclude_none=True,
            )
async def get_all(
        # request: Request,
        # response: Response,
        # map_request: MapRequest,
        db=Depends(neodb.get_db)):
    print("CREATE (a:Greeting) SET a.message = $message RETURN a.message + ', from node ' + id(a)")

    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)",
                        message=message)
        return result.single()[0]

    with db as session:
        greeting = session.write_transaction(_create_and_return_greeting, 'asd')
        print(greeting)
    return {}

import re
from typing import Optional, Dict

from py2neo import Relationship
from pydantic import BaseModel, constr, ConstrainedStr


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
    label: str


class Update(BaseModel):
    user: str
    analysis: Optional[int]
    update_data: dict = dict()
    metadata: dict = dict()
    label: str


class Sequence(BaseModel):
    state: State
    update: Update


class ProcessedNeo4jQuery(BaseModel):
    query: str
    argument: dict = dict()


class ConstrainedParameter(ConstrainedStr):
    regex = re.compile("^[0-9a-z_A-Z]*$")


class GetFilteredNodes(BaseModel):
    label: ConstrainedParameter
    filter: Dict[ConstrainedParameter, ConstrainedParameter] = {}
    return_value: Optional[ConstrainedParameter] = None
    distinct: bool = True


class NeoRelationship:
    def __init__(self, label):
        self.label = label
        self.r = Relationship.type(label)

    def __call__(self, *args, **kwargs):
        return self.r(*args, **kwargs)


r_insight = NeoRelationship('INSIGHT')
r_follows_insight = NeoRelationship('FOLLOWS_INSIGHT')
r_update = NeoRelationship('UPDATE')
r_follows_update = NeoRelationship('FOLLOWS_UPDATE')
r_interact = NeoRelationship('INTERACT')
r_feedback = NeoRelationship('FEEDBACK')
r_does = NeoRelationship('DOES')
r_leads_to = NeoRelationship('LEADS_TO')
r_relates_to = NeoRelationship('RELATES_TO')
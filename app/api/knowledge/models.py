import re
from typing import List, Optional, Dict, Tuple

from py2neo import Relationship
from pydantic import BaseModel, constr, ConstrainedStr
from enum import Enum


class KnowledgeUpdateQuery(BaseModel):
    user: str
    analysis: str
    what: str
    by: str
    type: str = "none"


class GraphData(BaseModel):
    id: int


class State(BaseModel):
    data: dict = dict()
    label: str


class Sequence(BaseModel):
    user: str
    analysis: Optional[str]
    data: dict = dict()
    metadata: dict = dict()
    label: str


class Sequence(BaseModel):
    state: State
    sequence: Sequence


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


class Elements(Enum):
    X = "X"
    P = "P"
    E = "E"
    K_T = "K_T"
    K_E = "K_E"
    D = "D"
    S = "S"
    V = "V"
    A = "A"


class SetEntity:
    def __init__(self, *elements) -> None:
        self.elements = elements


class Sets(Enum):
    HU = SetEntity(Elements.X, Elements.P, Elements.E)
    HS = SetEntity(Elements.K_T)
    MS = SetEntity(Elements.K_E, Elements.D, Elements.S)
    MU = SetEntity(Elements.V, Elements.A)


class NeoRelationship:
    def __init__(self, label):
        self.label = label
        self.r = Relationship.type(label)

    def __call__(self, *args, **kwargs):
        return self.r(*args, **kwargs)

    def __str__(self):
        return self.label

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.label == __value
        if isinstance(__value, NeoRelationship):
            return self.label == __value.label
        raise NotImplementedError(f"Cannot compare {type(self)} with {type(__value)}")


class Ownership(Enum):
    MACHINE = "M"
    HUMAN = "H"

    def __str__(self):
        return str(self.value)


class Temporality(Enum):
    STATE = "STATE"
    SEQUENCE = "SEQUENCE"

    def __str__(self):
        return str(self.value)


class Relationship(Enum):
    PREV_UPDATE = NeoRelationship(
        "PREV_UPDATE"
        # , [(Sets.HU, Sets.HU), (Sets.MU, Sets.MU)]
    )
    PREV_STATE = NeoRelationship(
        "PREV_STATE"
        # , [(Sets.HS, Sets.HS), (Sets.MS, Sets.MS)]
    )

    NEW_KNOWLEDGE = NeoRelationship(
        "NEW_KNOWLEDGE"
        # , [(Elements.K_T, Elements.X), (Elements.K_T, Elements.E)]
    )  # HS to HU
    UPDATES_HUMAN = NeoRelationship(
        "UPDATES_HUMAN"
        # , [(Elements.P, Elements.K_T)]
    )  # reaches human update

    NEW_BEHAVIOR = NeoRelationship(
        "NEW_BEHAVIOR"
        # ,[
        #     (Elements.S, Elements.V),
        #     (Elements.S, Elements.A),
        #     (Elements.D, Elements.A),
        #     (Elements.D, Elements.V),
        #     (Elements.K_E, Elements.A),
        #     (Elements.K_E, Elements.V),
        # ],
    )  # MS to MU
    UPDATES_MACHINE = NeoRelationship(
        "UPDATES_MACHINE"
        #                               , [
        # (Elements.X, Elements.K_E),
        # (Elements.E, Elements.S),
        # (Elements.A, Elements.D),
        # (Elements.A, Elements.S),
        # (Elements.A, Elements.K_E),
        # ]
    )  # reaches machine update

    SYNCHRONIZES_TO = NeoRelationship("SYNCHRONIZES_TO")  # Between Update types

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

    def __str__(self):
        return str(self.value.label)

    @property
    def label(self) -> str:
        return self.value.label


# r_insight = NeoRelationship('INSIGHT')
# r_follows_insight = NeoRelationship('FOLLOWS_INSIGHT')
# r_update = NeoRelationship('UPDATE')
# r_follows_update = NeoRelationship('FOLLOWS_UPDATE')
# r_interact = NeoRelationship('INTERACT')
# r_feedback = NeoRelationship('FEEDBACK')
# r_does = NeoRelationship('DOES')
# r_leads_to = NeoRelationship('LEADS_TO')
# r_relates_to = NeoRelationship('RELATES_TO')

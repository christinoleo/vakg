from app.api.knowledge.models import (
    GetFilteredNodes,
    ConstrainedParameter,
    Ownership,
    Temporality,
)


class NLPGetFilteredNodes(GetFilteredNodes):
    label: ConstrainedParameter = (
        Ownership.HUMAN.value + "_" + Temporality.SEQUENCE.value
    )
    return_value: ConstrainedParameter = "text"
    distinct: bool = True
    min_score: float = 0.5

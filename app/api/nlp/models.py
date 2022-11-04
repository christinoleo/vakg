from app.api.knowledge.models import GetFilteredNodes, ConstrainedParameter


class NLPGetFilteredNodes(GetFilteredNodes):
    label: ConstrainedParameter = 'H_UPDATE'
    return_value: ConstrainedParameter = 'text'
    distinct: bool = True
    min_score: float = 0.5

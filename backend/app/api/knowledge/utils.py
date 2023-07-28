from typing import Optional

from app.api.knowledge.models import ProcessedNeo4jQuery


def dict_converter(d: dict, prefix: str) -> Optional[ProcessedNeo4jQuery]:
    if d is None:
        return None
    # don't use any key with space, use with camelcase or _
    for k in d.keys():
        if not isinstance(k, str) or ' ' in k:
            raise Exception('Only strings with no spaces are allowed!')
    return ProcessedNeo4jQuery(query=', '.join([f'{k}: ${prefix}{k}' for k in d.keys()]),
                               argument={prefix + k: d[k] for k in d.keys()})


def get_first_desc(tx, cypher, node_var='n', **params):
    ret = tx.run(cypher, **params).data()
    if len(ret) == 1:
        return ret[0][node_var]
    else:
        return None
from app.api import test, custom, schema
from app.api.knowledge import knowledge
from app.api.nlp import nlp


def include_routers(app):
    app.include_router(test.router)
    app.include_router(custom.router)
    app.include_router(schema.router)
    app.include_router(knowledge.router)
    app.include_router(nlp.router)

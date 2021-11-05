from app.api import test, custom, schema, knowledge


def include_routers(app):
    app.include_router(test.router)
    app.include_router(custom.router)
    app.include_router(schema.router)
    app.include_router(knowledge.router)

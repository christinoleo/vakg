# from app import patch
import time
import timeit

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pyinstrument import Profiler
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

from app.api import include_routers

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8888)
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8080, reload_dirs=['./app', './main.py'])

app = FastAPI(title='test', docs_url="/api/docs", openapi_url="/api")

# app.mount("/dash", WSGIMiddleware(dash_server))

origins = [
    "http://localhost:*",
    "http://localhost:3000",
    "http://localhost:8001",
    "http://localhost:8888",
    "https://ocean.aknakos.com",
    "https://ocean.aknakos.com/",
    "https://qol.vav.aknakos.com",
    "http://qol.vav.aknakos.com",
    "https://qol.vav.aknakos.com/",
    "http://qol.vav.aknakos.com/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import yappi


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # t1 = time.time()
    # print(f'Time Start!')
    # p = Profiler(async_mode='enabled')
    # with p:
    # request.state.db = SessionLocal()
    response = await call_next(request)
    # request.state.db.close()
    response.headers["Access-Control-Expose-Headers"] = '*'
    # p.print()
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get('/x')
def test():
    return {}


include_routers(app)

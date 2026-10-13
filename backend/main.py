from fastapi import FastAPI
from rotas.auth_routes import auth_router
from rotas.blocos_routes import bloco_router
from rotas.apart_routes import apart_router
from rotas.residente_routes import residente_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(bloco_router)
app.include_router(apart_router)
app.include_router(residente_router)

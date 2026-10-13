from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.models import Usuario
from database.db_sessao import pegar_sessao
from core.seguranca import verificar_senha, ALGORITHM, ACESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from DTO.schemas import LoginSchema
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["rota de autenticação"])

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

seguranca_bearer = HTTPBearer()

def verificar_token(credenciais: HTTPAuthorizationCredentials = Depends(seguranca_bearer), session: Session = Depends(pegar_sessao)):
    erro_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        dic_info = jwt.decode(credenciais.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dic_info["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro_token

    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise erro_token
    return usuario

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not verificar_senha(senha, usuario.senha):
        return False
    return usuario


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        acess_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            "acess_token": acess_token,
            "refresh_token": refresh_token,
            "token_jwt": "Bearer "
            }

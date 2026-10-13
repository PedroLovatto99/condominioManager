from fastapi import APIRouter, Depends, status, HTTPException
from database.db_sessao import pegar_sessao
from typing import List
from DTO.schemas import *
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from rotas.auth_routes import verificar_token
from database.models import Bloco

bloco_router = APIRouter(prefix="/blocos", tags=["blocos"], dependencies=[Depends(verificar_token)])


@bloco_router.get("", status_code=status.HTTP_200_OK, response_model=List[BlocoResponseSchema])
async def listar_blocos(db: Session = Depends(pegar_sessao)):
    blocos = db.query(Bloco).all()
    return blocos

@bloco_router.post("", status_code=status.HTTP_201_CREATED, response_model=BlocoResponseSchema)
async def criar_bloco(bloco_data: BlocoRequestSchema, db: Session = Depends(pegar_sessao)):
    novo_bloco = Bloco(numero=bloco_data.numero)
    db.add(novo_bloco)
    db.commit()
    return novo_bloco

@bloco_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=BlocoResponseSchema)
async def selecionar_bloco(id:int, db: Session = Depends(pegar_sessao)):
    bloco = db.query(Bloco).filter(Bloco.id == id).first()

    if not bloco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bloco não encontrado"
        )

    return bloco

@bloco_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=BlocoResponseSchema)
async def editar_bloco(id: int, bloco_data: BlocoRequestSchema, db: Session = Depends(pegar_sessao)):
    bloco = db.query(Bloco).filter(Bloco.id == id).first()

    if not bloco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bloco não encontrado"
        )

    bloco.numero = bloco_data.numero
    db.commit()
    db.refresh(bloco)

    return bloco

@bloco_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_bloco(id: int, db: Session = Depends(pegar_sessao)):
    bloco = db.query(Bloco).filter(Bloco.id == id).first()

    if not bloco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bloco não encontrado"
        )

    try:
        db.delete(bloco)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bloco possui apartamentos vinculados"
        )

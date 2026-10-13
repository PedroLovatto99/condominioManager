from fastapi import APIRouter, Depends, status, HTTPException
from database.db_sessao import pegar_sessao
from typing import List
from DTO.schemas import *
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from rotas.auth_routes import verificar_token
from database.models import Bloco, Apartamento

apart_router = APIRouter(prefix="/apartamentos", tags=["apartamentos"], dependencies=[Depends(verificar_token)])


def buscar_bloco(bloco_id: int, db: Session):
    bloco = db.query(Bloco).filter(Bloco.id == bloco_id).first()

    if not bloco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bloco não encontrado"
        )

    return bloco

def montar_resposta(apartamento: Apartamento, db: Session):
    bloco = db.query(Bloco).filter(Bloco.id == apartamento.bloco).first()
    return ApartamentoResponseSchema(
        id=apartamento.id,
        bloco=BlocoResponseSchema.model_validate(bloco),
        numero=apartamento.numero
    )


@apart_router.get("", status_code=status.HTTP_200_OK, response_model=List[ApartamentoResponseSchema])
async def listar_apartamentos(db: Session = Depends(pegar_sessao)):
    apartamentos = db.query(Apartamento).all()
    return [montar_resposta(apartamento, db) for apartamento in apartamentos]

@apart_router.post("", status_code=status.HTTP_201_CREATED, response_model=ApartamentoResponseSchema)
async def criar_apartamento(apartamento_data: ApartamentoRequestSchema, db: Session = Depends(pegar_sessao)):
    buscar_bloco(apartamento_data.bloco_id, db)

    novo_apartamento = Apartamento(bloco=apartamento_data.bloco_id, numero=apartamento_data.numero)
    db.add(novo_apartamento)
    db.commit()
    db.refresh(novo_apartamento)
    return montar_resposta(novo_apartamento, db)

@apart_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ApartamentoResponseSchema)
async def selecionar_apartamento(id: int, db: Session = Depends(pegar_sessao)):
    apartamento = db.query(Apartamento).filter(Apartamento.id == id).first()

    if not apartamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartamento não encontrado"
        )

    return montar_resposta(apartamento, db)

@apart_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ApartamentoResponseSchema)
async def editar_apartamento(id: int, apartamento_data: ApartamentoRequestSchema, db: Session = Depends(pegar_sessao)):
    apartamento = db.query(Apartamento).filter(Apartamento.id == id).first()

    if not apartamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartamento não encontrado"
        )

    buscar_bloco(apartamento_data.bloco_id, db)

    apartamento.bloco = apartamento_data.bloco_id
    apartamento.numero = apartamento_data.numero
    db.commit()
    db.refresh(apartamento)

    return montar_resposta(apartamento, db)

@apart_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_apartamento(id: int, db: Session = Depends(pegar_sessao)):
    apartamento = db.query(Apartamento).filter(Apartamento.id == id).first()

    if not apartamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartamento não encontrado"
        )

    try:
        db.delete(apartamento)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Apartamento possui residentes vinculados"
        )

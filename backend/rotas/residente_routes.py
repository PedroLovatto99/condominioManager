from fastapi import APIRouter, Depends, status, HTTPException
from database.db_sessao import pegar_sessao
from typing import List
from DTO.schemas import *
from sqlalchemy.orm import Session
from rotas.auth_routes import verificar_token
from database.models import Bloco, Apartamento, Residente

residente_router = APIRouter(prefix="/residentes", tags=["residentes"], dependencies=[Depends(verificar_token)])


def buscar_apartamento(apartamento_id: int, db: Session):
    apartamento = db.query(Apartamento).filter(Apartamento.id == apartamento_id).first()

    if not apartamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartamento não encontrado"
        )

    return apartamento

def verificar_email_disponivel(email: str, db: Session, ignorar_id: int = None):
    query = db.query(Residente).filter(Residente.email == email)

    if ignorar_id is not None:
        query = query.filter(Residente.id != ignorar_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um residente com esse e-mail"
        )

def montar_resposta(residente: Residente, db: Session):
    apartamento = db.query(Apartamento).filter(Apartamento.id == residente.apartamento).first()
    bloco = db.query(Bloco).filter(Bloco.id == apartamento.bloco).first()

    return ResidenteResponseSchema(
        id=residente.id,
        nome=residente.nome,
        apartamento=ApartamentoResponseSchema(
            id=apartamento.id,
            bloco=BlocoResponseSchema.model_validate(bloco),
            numero=apartamento.numero
        ),
        cpf=residente.cpf,
        telefone=residente.telefone,
        email=residente.email,
        data_inicio=residente.data_inicio,
        data_vencimento=residente.data_vencimento,
        valor_aluguel=residente.valor_aluguel
    )


@residente_router.get("", status_code=status.HTTP_200_OK, response_model=List[ResidenteResponseSchema])
async def listar_residentes(db: Session = Depends(pegar_sessao)):
    residentes = db.query(Residente).all()
    return [montar_resposta(residente, db) for residente in residentes]

@residente_router.post("", status_code=status.HTTP_201_CREATED, response_model=ResidenteResponseSchema)
async def criar_residente(residente_data: ResidenteRequestSchema, db: Session = Depends(pegar_sessao)):
    buscar_apartamento(residente_data.apartamento_id, db)
    verificar_email_disponivel(residente_data.email, db)

    novo_residente = Residente(
        nome=residente_data.nome,
        apartamento=residente_data.apartamento_id,
        cpf=residente_data.cpf,
        telefone=residente_data.telefone,
        email=residente_data.email,
        data_inicio=residente_data.data_inicio,
        data_vencimento=residente_data.data_vencimento,
        valor_aluguel=residente_data.valor_aluguel
    )
    db.add(novo_residente)
    db.commit()
    db.refresh(novo_residente)
    return montar_resposta(novo_residente, db)

@residente_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResidenteResponseSchema)
async def selecionar_residente(id: int, db: Session = Depends(pegar_sessao)):
    residente = db.query(Residente).filter(Residente.id == id).first()

    if not residente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Residente não encontrado"
        )

    return montar_resposta(residente, db)

@residente_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResidenteResponseSchema)
async def editar_residente(id: int, residente_data: ResidenteRequestSchema, db: Session = Depends(pegar_sessao)):
    residente = db.query(Residente).filter(Residente.id == id).first()

    if not residente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Residente não encontrado"
        )

    buscar_apartamento(residente_data.apartamento_id, db)
    verificar_email_disponivel(residente_data.email, db, ignorar_id=id)

    residente.nome = residente_data.nome
    residente.apartamento = residente_data.apartamento_id
    residente.cpf = residente_data.cpf
    residente.telefone = residente_data.telefone
    residente.email = residente_data.email
    residente.data_inicio = residente_data.data_inicio
    residente.data_vencimento = residente_data.data_vencimento
    residente.valor_aluguel = residente_data.valor_aluguel
    db.commit()
    db.refresh(residente)

    return montar_resposta(residente, db)

@residente_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_residente(id: int, db: Session = Depends(pegar_sessao)):
    residente = db.query(Residente).filter(Residente.id == id).first()

    if not residente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Residente não encontrado"
        )

    db.delete(residente)
    db.commit()

from pydantic import BaseModel, EmailStr, model_validator, Field
from datetime import date

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True


class BlocoResponseSchema(BaseModel):
    id: int 
    numero: int 

    class Config:
        from_attributes = True

class BlocoRequestSchema(BaseModel):
    numero: int = Field(gt=0)

    class Config:
        from_attributes = True


class ApartamentoResponseSchema(BaseModel):
    id: int
    bloco: BlocoResponseSchema
    numero: int 

    class Config:
        from_attributes = True

class ApartamentoRequestSchema(BaseModel):
    bloco_id: int
    numero: int 

    class Config:
        from_attributes = True

 
class ResidenteResponseSchema(BaseModel):
    id: int
    nome: str
    apartamento: ApartamentoResponseSchema
    cpf: str 
    telefone: int
    email: EmailStr 
    data_inicio: date
    data_vencimento: date 
    valor_aluguel: float     

    class Config:
        from_attributes = True

class ResidenteRequestSchema(BaseModel):
    nome: str
    apartamento_id: int
    cpf: str 
    telefone: int
    email: EmailStr 
    data_inicio: date
    data_vencimento: date 
    valor_aluguel: float     

    @model_validator(mode='after')
    def verificar_datas(self):
        if self.data_vencimento < self.data_inicio:
            raise ValueError("A data de vencimento não pode ser anterior à data de início.")
        return self

    class Config:
        from_attributes = True
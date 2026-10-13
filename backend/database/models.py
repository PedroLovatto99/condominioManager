from sqlalchemy import create_engine, Column, String, Integer, BigInteger, Boolean, Float, ForeignKey, Date
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

pg_username = os.getenv("PG_USERNAME")
pg_password = os.getenv("PG_PASSWORD")
pg_host = os.getenv("PG_HOST", "localhost")
pg_port = os.getenv("PG_PORT", "5432")

db = create_engine(f'postgresql://{pg_username}:{pg_password}@{pg_host}:{pg_port}/condominio')

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String)
    admin = Column("admin", Boolean, default=False)



class Bloco(Base):
    __tablename__ = "blocos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    numero = Column("numero", Integer, nullable=False)


class Apartamento(Base):
    __tablename__ = "apartamentos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    bloco = Column("bloco", ForeignKey("blocos.id"), nullable=False)
    numero = Column("numero", Integer, nullable=False)


class Residente(Base):
    __tablename__ = "residentes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(255), nullable=False, index=True)
    apartamento = Column("apartamento", ForeignKey("apartamentos.id"), nullable=False)
    cpf = Column("cpf", String(16), nullable=False)
    telefone = Column("telefone", BigInteger, nullable=False)
    email = Column("email", String(255), unique=True, nullable=False, index=True)
    data_inicio = Column("data_inicio", Date, nullable=False)
    data_vencimento = Column("data_vencimento", Date, nullable=False)
    valor_aluguel = Column("valor_aluguel", Float, nullable=False)



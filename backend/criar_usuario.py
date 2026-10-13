import argparse
from sqlalchemy.orm import sessionmaker
from database.models import db, Usuario
from core.seguranca import gerar_hash_senha

parser = argparse.ArgumentParser(description="Cria um usuário no banco")
parser.add_argument("nome")
parser.add_argument("email")
parser.add_argument("senha")
parser.add_argument("--admin", action="store_true")
args = parser.parse_args()

session = sessionmaker(bind=db)()

if session.query(Usuario).filter(Usuario.email == args.email).first():
    raise SystemExit(f"Já existe um usuário com o e-mail {args.email}")

session.add(Usuario(
    nome=args.nome,
    email=args.email,
    senha=gerar_hash_senha(args.senha),
    admin=args.admin
))
session.commit()
session.close()
print(f"Usuário {args.email} criado")

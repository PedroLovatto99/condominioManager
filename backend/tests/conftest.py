import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from core.seguranca import gerar_hash_senha
from database.db_sessao import pegar_sessao
from database.models import Base, Usuario, pg_host, pg_password, pg_port, pg_username
from main import app

BANCO_TESTE = "condominio_teste"

EMAIL_USUARIO = "admin@teste.com"
SENHA_USUARIO = "senha-de-teste-123"


def _url(banco: str) -> URL:
    return URL.create(
        "postgresql",
        username=pg_username,
        password=pg_password,
        host=pg_host,
        port=int(pg_port),
        database=banco,
    )


def _criar_banco_se_nao_existir():
    admin = create_engine(_url("postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conexao:
            existe = conexao.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :nome"), {"nome": BANCO_TESTE}
            ).scalar()
            if not existe:
                conexao.execute(text(f'CREATE DATABASE "{BANCO_TESTE}"'))
    finally:
        admin.dispose()


@pytest.fixture(scope="session")
def engine_teste():
    assert BANCO_TESTE != "condominio", "os testes não podem rodar no banco de desenvolvimento"

    try:
        _criar_banco_se_nao_existir()
    except Exception as erro:
        pytest.exit(
            f"Não foi possível conectar ao Postgres em {pg_host}:{pg_port} ({type(erro).__name__}). "
            "Suba o banco com: docker compose up -d db",
            returncode=1,
        )

    engine = create_engine(_url(BANCO_TESTE))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def sessao_teste(engine_teste):
    return sessionmaker(bind=engine_teste)


@pytest.fixture
def limpar_banco(engine_teste):
    yield
    with engine_teste.begin() as conexao:
        conexao.execute(
            text("TRUNCATE TABLE residentes, apartamentos, blocos, usuarios RESTART IDENTITY CASCADE")
        )


@pytest.fixture
def client(sessao_teste, limpar_banco):
    def sessao_de_teste():
        sessao = sessao_teste()
        try:
            yield sessao
        finally:
            sessao.close()

    app.dependency_overrides[pegar_sessao] = sessao_de_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def usuario(sessao_teste, limpar_banco):
    with sessao_teste() as sessao:
        novo = Usuario(
            nome="Admin de teste",
            email=EMAIL_USUARIO,
            senha=gerar_hash_senha(SENHA_USUARIO),
            admin=True,
        )
        sessao.add(novo)
        sessao.commit()
        sessao.refresh(novo)
        sessao.expunge(novo)
    return novo


@pytest.fixture
def token(client, usuario):
    resposta = client.post("/auth/login", json={"email": EMAIL_USUARIO, "senha": SENHA_USUARIO})
    assert resposta.status_code == 200
    return resposta.json()["acess_token"]


@pytest.fixture
def client_auth(client, token):
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def criar_bloco(client_auth):
    def _criar(numero: int = 1) -> dict:
        resposta = client_auth.post("/blocos", json={"numero": numero})
        assert resposta.status_code == 201
        return resposta.json()

    return _criar


@pytest.fixture
def criar_apartamento(client_auth):
    def _criar(bloco_id: int, numero: int = 101) -> dict:
        resposta = client_auth.post("/apartamentos", json={"bloco_id": bloco_id, "numero": numero})
        assert resposta.status_code == 201
        return resposta.json()

    return _criar


@pytest.fixture
def dados_residente():
    def _dados(apartamento_id: int, **alteracoes) -> dict:
        dados = {
            "nome": "Maria Silva",
            "apartamento_id": apartamento_id,
            "cpf": "123.456.789-00",
            "telefone": 11987654321,
            "email": "maria@email.com",
            "data_inicio": "2026-01-01",
            "data_vencimento": "2026-12-31",
            "valor_aluguel": 1500.5,
        }
        dados.update(alteracoes)
        return dados

    return _dados


@pytest.fixture
def criar_residente(client_auth, dados_residente):
    def _criar(apartamento_id: int, **alteracoes) -> dict:
        resposta = client_auth.post("/residentes", json=dados_residente(apartamento_id, **alteracoes))
        assert resposta.status_code == 201
        return resposta.json()

    return _criar

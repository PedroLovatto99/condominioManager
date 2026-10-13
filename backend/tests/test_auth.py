from datetime import datetime, timedelta, timezone

import jwt
import pytest

from core.seguranca import ALGORITHM, SECRET_KEY
from database.models import Usuario
from rotas.auth_routes import criar_token
from tests.conftest import EMAIL_USUARIO, SENHA_USUARIO

ROTAS_PROTEGIDAS = [
    ("GET", "/blocos"),
    ("POST", "/blocos"),
    ("GET", "/blocos/1"),
    ("PUT", "/blocos/1"),
    ("DELETE", "/blocos/1"),
    ("GET", "/apartamentos"),
    ("POST", "/apartamentos"),
    ("GET", "/apartamentos/1"),
    ("PUT", "/apartamentos/1"),
    ("DELETE", "/apartamentos/1"),
    ("GET", "/residentes"),
    ("POST", "/residentes"),
    ("GET", "/residentes/1"),
    ("PUT", "/residentes/1"),
    ("DELETE", "/residentes/1"),
]


class TestLogin:
    def test_login_correto_devolve_os_tokens(self, client, usuario):
        resposta = client.post("/auth/login", json={"email": EMAIL_USUARIO, "senha": SENHA_USUARIO})

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["acess_token"]
        assert corpo["refresh_token"]
        assert corpo["acess_token"] != corpo["refresh_token"]

    def test_token_devolvido_identifica_o_usuario(self, client, usuario):
        corpo = client.post("/auth/login", json={"email": EMAIL_USUARIO, "senha": SENHA_USUARIO}).json()
        dados = jwt.decode(corpo["acess_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert dados["sub"] == str(usuario.id)

    def test_senha_errada(self, client, usuario):
        resposta = client.post("/auth/login", json={"email": EMAIL_USUARIO, "senha": "errada"})
        assert resposta.status_code == 400

    def test_email_inexistente(self, client, usuario):
        resposta = client.post("/auth/login", json={"email": "ninguem@teste.com", "senha": SENHA_USUARIO})
        assert resposta.status_code == 400

    def test_email_mal_formatado(self, client):
        resposta = client.post("/auth/login", json={"email": "sem-arroba", "senha": "123"})
        assert resposta.status_code == 422

    def test_corpo_incompleto(self, client):
        resposta = client.post("/auth/login", json={"email": EMAIL_USUARIO})
        assert resposta.status_code == 422


class TestProtecaoDasRotas:
    @pytest.mark.parametrize("metodo, caminho", ROTAS_PROTEGIDAS)
    def test_sem_token_devolve_401(self, client, metodo, caminho):
        assert client.request(metodo, caminho).status_code == 401

    def test_token_lixo(self, client):
        resposta = client.get("/blocos", headers={"Authorization": "Bearer isso-nao-e-um-jwt"})
        assert resposta.status_code == 401

    def test_esquema_de_autorizacao_errado(self, client, token):
        resposta = client.get("/blocos", headers={"Authorization": f"Basic {token}"})
        assert resposta.status_code == 401

    def test_token_expirado(self, client, usuario):
        token = criar_token(usuario.id, duracao_token=timedelta(seconds=-10))
        resposta = client.get("/blocos", headers={"Authorization": f"Bearer {token}"})
        assert resposta.status_code == 401

    def test_token_assinado_com_outra_chave(self, client, usuario):
        token = jwt.encode({"sub": str(usuario.id)}, "outra-chave-qualquer-com-32-caracteres!", algorithm=ALGORITHM)
        resposta = client.get("/blocos", headers={"Authorization": f"Bearer {token}"})
        assert resposta.status_code == 401

    def test_token_sem_sub(self, client, usuario):
        token = jwt.encode({"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, SECRET_KEY, algorithm=ALGORITHM)
        resposta = client.get("/blocos", headers={"Authorization": f"Bearer {token}"})
        assert resposta.status_code == 401

    def test_token_de_usuario_que_nao_existe_mais(self, client, usuario, token, sessao_teste):
        with sessao_teste() as sessao:
            sessao.query(Usuario).filter(Usuario.id == usuario.id).delete()
            sessao.commit()

        resposta = client.get("/blocos", headers={"Authorization": f"Bearer {token}"})
        assert resposta.status_code == 401

    def test_token_valido_da_acesso(self, client, token):
        resposta = client.get("/blocos", headers={"Authorization": f"Bearer {token}"})
        assert resposta.status_code == 200


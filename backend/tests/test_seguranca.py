from datetime import datetime, timedelta, timezone

import jwt
import pytest

from core.seguranca import ACESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, gerar_hash_senha, verificar_senha
from rotas.auth_routes import criar_token


class TestHashDeSenha:
    def test_hash_nao_guarda_a_senha_em_texto(self):
        assert gerar_hash_senha("minha-senha") != "minha-senha"

    def test_senha_correta_confere(self):
        senha_hash = gerar_hash_senha("minha-senha")
        assert verificar_senha("minha-senha", senha_hash) is True

    def test_senha_errada_nao_confere(self):
        senha_hash = gerar_hash_senha("minha-senha")
        assert verificar_senha("outra-senha", senha_hash) is False

    def test_mesma_senha_gera_hashes_diferentes(self):
        assert gerar_hash_senha("minha-senha") != gerar_hash_senha("minha-senha")

    def test_senha_acima_de_72_bytes_nao_quebra_a_verificacao(self):
        senha_hash = gerar_hash_senha("minha-senha")
        assert verificar_senha("a" * 100, senha_hash) is False

    def test_hash_invalido_nao_confere(self):
        assert verificar_senha("minha-senha", "isso-nao-e-um-hash") is False


class TestToken:
    def test_token_carrega_o_id_do_usuario_como_texto(self):
        dados = jwt.decode(criar_token(5), SECRET_KEY, algorithms=[ALGORITHM])
        assert dados["sub"] == "5"

    def test_token_expira_no_tempo_configurado(self):
        dados = jwt.decode(criar_token(1), SECRET_KEY, algorithms=[ALGORITHM])
        esperado = datetime.now(timezone.utc) + timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
        expiracao = datetime.fromtimestamp(dados["exp"], tz=timezone.utc)
        assert abs((expiracao - esperado).total_seconds()) < 5

    def test_duracao_personalizada(self):
        dados = jwt.decode(criar_token(1, duracao_token=timedelta(days=7)), SECRET_KEY, algorithms=[ALGORITHM])
        esperado = datetime.now(timezone.utc) + timedelta(days=7)
        expiracao = datetime.fromtimestamp(dados["exp"], tz=timezone.utc)
        assert abs((expiracao - esperado).total_seconds()) < 5

    def test_token_expirado_e_rejeitado(self):
        token = criar_token(1, duracao_token=timedelta(seconds=-10))
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_token_com_outra_chave_e_rejeitado(self):
        token = jwt.encode({"sub": "1"}, "outra-chave-qualquer-com-32-caracteres!", algorithm=ALGORITHM)
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

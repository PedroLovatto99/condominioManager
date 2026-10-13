import pytest
from pydantic import ValidationError

from DTO.schemas import ApartamentoRequestSchema, BlocoRequestSchema, LoginSchema, ResidenteRequestSchema


def dados_residente(**alteracoes) -> dict:
    dados = {
        "nome": "Maria Silva",
        "apartamento_id": 1,
        "cpf": "123.456.789-00",
        "telefone": 11987654321,
        "email": "maria@email.com",
        "data_inicio": "2026-01-01",
        "data_vencimento": "2026-12-31",
        "valor_aluguel": 1500.5,
    }
    dados.update(alteracoes)
    return dados


class TestBloco:
    def test_numero_positivo_e_valido(self):
        assert BlocoRequestSchema(numero=1).numero == 1

    @pytest.mark.parametrize("numero", [0, -1])
    def test_numero_zero_ou_negativo_e_invalido(self, numero):
        with pytest.raises(ValidationError):
            BlocoRequestSchema(numero=numero)

    def test_numero_e_obrigatorio(self):
        with pytest.raises(ValidationError):
            BlocoRequestSchema()

    def test_nome_do_campo_diferencia_maiuscula(self):
        with pytest.raises(ValidationError):
            BlocoRequestSchema(**{"Numero": 4})


class TestApartamento:
    def test_dados_validos(self):
        schema = ApartamentoRequestSchema(bloco_id=1, numero=101)
        assert (schema.bloco_id, schema.numero) == (1, 101)

    def test_bloco_id_e_obrigatorio(self):
        with pytest.raises(ValidationError):
            ApartamentoRequestSchema(numero=101)


class TestResidente:
    def test_dados_validos(self):
        assert ResidenteRequestSchema(**dados_residente()).nome == "Maria Silva"

    def test_vencimento_igual_ao_inicio_e_valido(self):
        ResidenteRequestSchema(**dados_residente(data_inicio="2026-05-10", data_vencimento="2026-05-10"))

    def test_vencimento_anterior_ao_inicio_e_invalido(self):
        with pytest.raises(ValidationError, match="não pode ser anterior"):
            ResidenteRequestSchema(**dados_residente(data_inicio="2026-05-10", data_vencimento="2026-05-09"))

    def test_email_invalido(self):
        with pytest.raises(ValidationError):
            ResidenteRequestSchema(**dados_residente(email="isso-nao-e-email"))

    def test_data_em_formato_invalido(self):
        with pytest.raises(ValidationError):
            ResidenteRequestSchema(**dados_residente(data_inicio="01/01/2026"))

    def test_valor_do_aluguel_precisa_ser_numero(self):
        with pytest.raises(ValidationError):
            ResidenteRequestSchema(**dados_residente(valor_aluguel="caro"))


class TestLogin:
    def test_dados_validos(self):
        assert LoginSchema(email="a@b.com", senha="123").email == "a@b.com"

    def test_email_invalido(self):
        with pytest.raises(ValidationError):
            LoginSchema(email="sem-arroba", senha="123")

    def test_senha_e_obrigatoria(self):
        with pytest.raises(ValidationError):
            LoginSchema(email="a@b.com")

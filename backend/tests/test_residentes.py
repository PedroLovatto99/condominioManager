import pytest


@pytest.fixture
def apartamento(criar_bloco, criar_apartamento):
    return criar_apartamento(criar_bloco(1)["id"], 101)


class TestCriarResidente:
    def test_cria_e_devolve_apartamento_e_bloco_aninhados(self, client_auth, apartamento, dados_residente):
        resposta = client_auth.post("/residentes", json=dados_residente(apartamento["id"]))

        assert resposta.status_code == 201
        assert resposta.json() == {
            "id": 1,
            "nome": "Maria Silva",
            "apartamento": apartamento,
            "cpf": "123.456.789-00",
            "telefone": 11987654321,
            "email": "maria@email.com",
            "data_inicio": "2026-01-01",
            "data_vencimento": "2026-12-31",
            "valor_aluguel": 1500.5,
        }

    def test_telefone_com_ddd_e_celular_nao_estoura(self, client_auth, apartamento, dados_residente):
        resposta = client_auth.post("/residentes", json=dados_residente(apartamento["id"], telefone=21999998888))

        assert resposta.status_code == 201
        assert resposta.json()["telefone"] == 21999998888

    def test_apartamento_inexistente(self, client_auth, dados_residente):
        resposta = client_auth.post("/residentes", json=dados_residente(999))

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Apartamento não encontrado"

    def test_email_duplicado(self, client_auth, apartamento, dados_residente, criar_residente):
        criar_residente(apartamento["id"], email="repetido@email.com")

        resposta = client_auth.post(
            "/residentes", json=dados_residente(apartamento["id"], nome="Outra Pessoa", email="repetido@email.com")
        )

        assert resposta.status_code == 409
        assert len(client_auth.get("/residentes").json()) == 1

    def test_vencimento_anterior_ao_inicio(self, client_auth, apartamento, dados_residente):
        dados = dados_residente(apartamento["id"], data_inicio="2026-06-01", data_vencimento="2026-05-31")
        assert client_auth.post("/residentes", json=dados).status_code == 422

    def test_email_invalido(self, client_auth, apartamento, dados_residente):
        assert client_auth.post("/residentes", json=dados_residente(apartamento["id"], email="x")).status_code == 422

    def test_campo_obrigatorio_ausente(self, client_auth, apartamento, dados_residente):
        dados = dados_residente(apartamento["id"])
        del dados["cpf"]
        assert client_auth.post("/residentes", json=dados).status_code == 422

    def test_dois_residentes_no_mesmo_apartamento(self, client_auth, apartamento, criar_residente):
        criar_residente(apartamento["id"], email="a@email.com")
        criar_residente(apartamento["id"], email="b@email.com")

        assert len(client_auth.get("/residentes").json()) == 2


class TestListarResidentes:
    def test_lista_vazia(self, client_auth):
        resposta = client_auth.get("/residentes")

        assert resposta.status_code == 200
        assert resposta.json() == []

    def test_lista_com_apartamento_aninhado(self, client_auth, apartamento, criar_residente):
        criar_residente(apartamento["id"])

        resposta = client_auth.get("/residentes")

        assert resposta.status_code == 200
        assert [r["apartamento"] for r in resposta.json()] == [apartamento]


class TestSelecionarResidente:
    def test_devolve_o_residente(self, client_auth, apartamento, criar_residente):
        residente = criar_residente(apartamento["id"])

        resposta = client_auth.get(f"/residentes/{residente['id']}")

        assert resposta.status_code == 200
        assert resposta.json() == residente

    def test_inexistente(self, client_auth):
        resposta = client_auth.get("/residentes/999")

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Residente não encontrado"


class TestEditarResidente:
    def test_altera_os_dados(self, client_auth, apartamento, criar_residente, dados_residente):
        residente = criar_residente(apartamento["id"])

        novos = dados_residente(apartamento["id"], nome="Maria Souza", valor_aluguel=2000)
        resposta = client_auth.put(f"/residentes/{residente['id']}", json=novos)

        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Maria Souza"
        assert resposta.json()["valor_aluguel"] == 2000

    def test_mantem_o_proprio_email(self, client_auth, apartamento, criar_residente, dados_residente):
        residente = criar_residente(apartamento["id"], email="maria@email.com")

        resposta = client_auth.put(
            f"/residentes/{residente['id']}", json=dados_residente(apartamento["id"], email="maria@email.com")
        )

        assert resposta.status_code == 200

    def test_email_de_outro_residente(self, client_auth, apartamento, criar_residente, dados_residente):
        criar_residente(apartamento["id"], email="a@email.com")
        segundo = criar_residente(apartamento["id"], email="b@email.com")

        resposta = client_auth.put(
            f"/residentes/{segundo['id']}", json=dados_residente(apartamento["id"], email="a@email.com")
        )

        assert resposta.status_code == 409
        assert client_auth.get(f"/residentes/{segundo['id']}").json()["email"] == "b@email.com"

    def test_muda_de_apartamento(self, client_auth, apartamento, criar_apartamento, criar_residente, dados_residente):
        outro = criar_apartamento(apartamento["bloco"]["id"], 102)
        residente = criar_residente(apartamento["id"])

        resposta = client_auth.put(f"/residentes/{residente['id']}", json=dados_residente(outro["id"]))

        assert resposta.status_code == 200
        assert resposta.json()["apartamento"] == outro

    def test_apartamento_inexistente(self, client_auth, apartamento, criar_residente, dados_residente):
        residente = criar_residente(apartamento["id"])

        resposta = client_auth.put(f"/residentes/{residente['id']}", json=dados_residente(999))

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Apartamento não encontrado"

    def test_residente_inexistente(self, client_auth, apartamento, dados_residente):
        resposta = client_auth.put("/residentes/999", json=dados_residente(apartamento["id"]))

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Residente não encontrado"


class TestDeletarResidente:
    def test_remove_o_residente(self, client_auth, apartamento, criar_residente):
        residente = criar_residente(apartamento["id"])

        resposta = client_auth.delete(f"/residentes/{residente['id']}")

        assert resposta.status_code == 204
        assert client_auth.get(f"/residentes/{residente['id']}").status_code == 404

    def test_inexistente(self, client_auth):
        assert client_auth.delete("/residentes/999").status_code == 404

    def test_apos_remover_o_apartamento_pode_ser_deletado(self, client_auth, apartamento, criar_residente):
        residente = criar_residente(apartamento["id"])
        client_auth.delete(f"/residentes/{residente['id']}")

        assert client_auth.delete(f"/apartamentos/{apartamento['id']}").status_code == 204

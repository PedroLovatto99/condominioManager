import pytest


class TestCriarBloco:
    def test_cria_e_devolve_o_bloco(self, client_auth):
        resposta = client_auth.post("/blocos", json={"numero": 3})

        assert resposta.status_code == 201
        assert resposta.json() == {"id": 1, "numero": 3}

    @pytest.mark.parametrize("numero", [0, -5])
    def test_numero_zero_ou_negativo(self, client_auth, numero):
        assert client_auth.post("/blocos", json={"numero": numero}).status_code == 422

    def test_numero_com_maiuscula_no_nome_do_campo(self, client_auth):
        assert client_auth.post("/blocos", json={"Numero": 4}).status_code == 422

    def test_numero_nao_numerico(self, client_auth):
        assert client_auth.post("/blocos", json={"numero": "quatro"}).status_code == 422

    def test_corpo_vazio(self, client_auth):
        assert client_auth.post("/blocos", json={}).status_code == 422


class TestListarBlocos:
    def test_lista_vazia(self, client_auth):
        resposta = client_auth.get("/blocos")

        assert resposta.status_code == 200
        assert resposta.json() == []

    def test_lista_os_blocos_criados(self, client_auth, criar_bloco):
        criar_bloco(1)
        criar_bloco(2)

        resposta = client_auth.get("/blocos")

        assert resposta.status_code == 200
        assert sorted(b["numero"] for b in resposta.json()) == [1, 2]


class TestSelecionarBloco:
    def test_devolve_o_bloco(self, client_auth, criar_bloco):
        bloco = criar_bloco(7)

        resposta = client_auth.get(f"/blocos/{bloco['id']}")

        assert resposta.status_code == 200
        assert resposta.json() == bloco

    def test_inexistente(self, client_auth):
        resposta = client_auth.get("/blocos/999")

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Bloco não encontrado"

    def test_id_nao_numerico(self, client_auth):
        assert client_auth.get("/blocos/abc").status_code == 422


class TestEditarBloco:
    def test_altera_o_numero(self, client_auth, criar_bloco):
        bloco = criar_bloco(1)

        resposta = client_auth.put(f"/blocos/{bloco['id']}", json={"numero": 9})

        assert resposta.status_code == 200
        assert resposta.json() == {"id": bloco["id"], "numero": 9}
        assert client_auth.get(f"/blocos/{bloco['id']}").json()["numero"] == 9

    def test_inexistente(self, client_auth):
        assert client_auth.put("/blocos/999", json={"numero": 9}).status_code == 404

    def test_numero_invalido(self, client_auth, criar_bloco):
        bloco = criar_bloco(1)

        assert client_auth.put(f"/blocos/{bloco['id']}", json={"numero": 0}).status_code == 422
        assert client_auth.get(f"/blocos/{bloco['id']}").json()["numero"] == 1


class TestDeletarBloco:
    def test_remove_o_bloco(self, client_auth, criar_bloco):
        bloco = criar_bloco(1)

        resposta = client_auth.delete(f"/blocos/{bloco['id']}")

        assert resposta.status_code == 204
        assert client_auth.get(f"/blocos/{bloco['id']}").status_code == 404

    def test_inexistente(self, client_auth):
        assert client_auth.delete("/blocos/999").status_code == 404

    def test_com_apartamentos_devolve_409_e_mantem_o_bloco(self, client_auth, criar_bloco, criar_apartamento):
        bloco = criar_bloco(1)
        criar_apartamento(bloco["id"], 101)

        resposta = client_auth.delete(f"/blocos/{bloco['id']}")

        assert resposta.status_code == 409
        assert resposta.json()["detail"] == "Bloco possui apartamentos vinculados"
        assert client_auth.get(f"/blocos/{bloco['id']}").status_code == 200

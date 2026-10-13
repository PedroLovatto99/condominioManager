class TestCriarApartamento:
    def test_cria_e_devolve_o_bloco_aninhado(self, client_auth, criar_bloco):
        bloco = criar_bloco(2)

        resposta = client_auth.post("/apartamentos", json={"bloco_id": bloco["id"], "numero": 101})

        assert resposta.status_code == 201
        assert resposta.json() == {"id": 1, "bloco": bloco, "numero": 101}

    def test_bloco_inexistente(self, client_auth):
        resposta = client_auth.post("/apartamentos", json={"bloco_id": 999, "numero": 101})

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Bloco não encontrado"
        assert client_auth.get("/apartamentos").json() == []

    def test_bloco_id_obrigatorio(self, client_auth):
        assert client_auth.post("/apartamentos", json={"numero": 101}).status_code == 422

    def test_numero_obrigatorio(self, client_auth, criar_bloco):
        bloco = criar_bloco()
        assert client_auth.post("/apartamentos", json={"bloco_id": bloco["id"]}).status_code == 422


class TestListarApartamentos:
    def test_lista_vazia(self, client_auth):
        resposta = client_auth.get("/apartamentos")

        assert resposta.status_code == 200
        assert resposta.json() == []

    def test_lista_de_varios_blocos(self, client_auth, criar_bloco, criar_apartamento):
        bloco1 = criar_bloco(1)
        bloco2 = criar_bloco(2)
        criar_apartamento(bloco1["id"], 101)
        criar_apartamento(bloco2["id"], 201)

        resposta = client_auth.get("/apartamentos")

        assert resposta.status_code == 200
        assert sorted((a["bloco"]["numero"], a["numero"]) for a in resposta.json()) == [(1, 101), (2, 201)]


class TestSelecionarApartamento:
    def test_devolve_o_apartamento(self, client_auth, criar_bloco, criar_apartamento):
        apartamento = criar_apartamento(criar_bloco()["id"], 305)

        resposta = client_auth.get(f"/apartamentos/{apartamento['id']}")

        assert resposta.status_code == 200
        assert resposta.json() == apartamento

    def test_inexistente(self, client_auth):
        resposta = client_auth.get("/apartamentos/999")

        assert resposta.status_code == 404
        assert resposta.json()["detail"] == "Apartamento não encontrado"


class TestEditarApartamento:
    def test_altera_numero_e_bloco(self, client_auth, criar_bloco, criar_apartamento):
        bloco1 = criar_bloco(1)
        bloco2 = criar_bloco(2)
        apartamento = criar_apartamento(bloco1["id"], 101)

        resposta = client_auth.put(
            f"/apartamentos/{apartamento['id']}", json={"bloco_id": bloco2["id"], "numero": 202}
        )

        assert resposta.status_code == 200
        assert resposta.json() == {"id": apartamento["id"], "bloco": bloco2, "numero": 202}

    def test_apartamento_inexistente(self, client_auth, criar_bloco):
        bloco = criar_bloco()
        assert client_auth.put("/apartamentos/999", json={"bloco_id": bloco["id"], "numero": 1}).status_code == 404

    def test_bloco_inexistente_nao_altera_nada(self, client_auth, criar_bloco, criar_apartamento):
        apartamento = criar_apartamento(criar_bloco()["id"], 101)

        resposta = client_auth.put(f"/apartamentos/{apartamento['id']}", json={"bloco_id": 999, "numero": 202})

        assert resposta.status_code == 404
        assert client_auth.get(f"/apartamentos/{apartamento['id']}").json() == apartamento


class TestDeletarApartamento:
    def test_remove_o_apartamento(self, client_auth, criar_bloco, criar_apartamento):
        apartamento = criar_apartamento(criar_bloco()["id"], 101)

        resposta = client_auth.delete(f"/apartamentos/{apartamento['id']}")

        assert resposta.status_code == 204
        assert client_auth.get(f"/apartamentos/{apartamento['id']}").status_code == 404

    def test_inexistente(self, client_auth):
        assert client_auth.delete("/apartamentos/999").status_code == 404

    def test_com_residentes_devolve_409_e_mantem_o_apartamento(
        self, client_auth, criar_bloco, criar_apartamento, criar_residente
    ):
        apartamento = criar_apartamento(criar_bloco()["id"], 101)
        criar_residente(apartamento["id"])

        resposta = client_auth.delete(f"/apartamentos/{apartamento['id']}")

        assert resposta.status_code == 409
        assert resposta.json()["detail"] == "Apartamento possui residentes vinculados"
        assert client_auth.get(f"/apartamentos/{apartamento['id']}").status_code == 200

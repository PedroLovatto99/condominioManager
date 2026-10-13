# Condomínio Manager

Sistema web para administrar um condomínio residencial: blocos, apartamentos e residentes, com
autenticação por login e senha.

O backend é uma API REST em **FastAPI** com **PostgreSQL**, o frontend é um app **React**, e tudo sobe
junto com **Docker Compose**.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Início rápido (Docker)](#início-rápido-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Portas](#portas)
- [Rodando sem Docker](#rodando-sem-docker)
- [Banco de dados e migrations](#banco-de-dados-e-migrations)
- [API](#api)
- [Frontend](#frontend)
- [Testes](#testes)
- [Limitações conhecidas](#limitações-conhecidas)
- [Solução de problemas](#solução-de-problemas)

## Funcionalidades

- Login com e-mail e senha, usando token JWT.
- CRUD de **blocos**, **apartamentos** e **residentes**.
- Telas de login, lista de blocos e tabela de apartamentos e residentes de cada bloco.
- Todas as rotas de dados exigem login.
- Regras de integridade: não se apaga um bloco que tem apartamentos nem um apartamento que tem
  residentes, e não existem dois residentes com o mesmo e-mail.

## Tecnologias

| Camada | O que é usado |
| --- | --- |
| API | Python 3.14, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2 |
| Autenticação | JWT (PyJWT) e hash de senha com bcrypt |
| Banco | PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, React Router |
| Testes | pytest e httpx |
| Infra | Docker e Docker Compose |

## Estrutura do projeto

```
.
├── docker-compose.yml          # db, api e frontend
├── .env                        # variáveis de ambiente (não vai para o git)
├── .env.example                # modelo do .env
├── backend/
│   ├── main.py                 # cria o app e registra os routers
│   ├── core/seguranca.py       # variáveis do .env, hash de senha
│   ├── database/
│   │   ├── models.py           # engine e models (SQLAlchemy)
│   │   └── db_sessao.py        # dependency que entrega a sessão do banco
│   ├── DTO/schemas.py          # schemas de entrada e saída (Pydantic)
│   ├── rotas/
│   │   ├── auth_routes.py      # login e verificação do token
│   │   ├── blocos_routes.py
│   │   ├── apart_routes.py
│   │   └── residente_routes.py
│   ├── alembic/                # migrations
│   ├── tests/                  # testes (pytest)
│   ├── criar_usuario.py        # script para cadastrar usuários
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
└── frontend/condominio-frontend/
    └── src/
        ├── pages/              # Login, BlocosLista, Bloco
        ├── components/         # Layout (cabeçalho e rodapé), RequireAuth
        ├── services/api.ts     # chamadas à API e controle da sessão
        └── utils/formatar.ts   # datas, dinheiro, telefone e cores
```

## Início rápido (Docker)

Pré-requisito: [Docker](https://www.docker.com/) com o Compose.

**1. Crie o `.env` na raiz do projeto**

```
cp .env.example .env
```

Edite o arquivo e troque `SECRET_KEY` e `PG_PASSWORD`. Para gerar uma chave segura:

```
openssl rand -hex 32
```

**2. Suba tudo**

```
docker compose up -d
```

Na primeira vez isso baixa as imagens, instala as dependências do frontend e cria o banco. A API aplica
as migrations sozinha ao iniciar.

**3. Crie um usuário**

Não existe rota para cadastrar usuários, então use o script:

```
docker compose exec api python criar_usuario.py "Seu Nome" voce@email.com suasenha --admin
```

**4. Acesse**

- Sistema: http://localhost:5173
- Documentação interativa da API (Swagger): http://localhost:8000/docs

Para parar: `docker compose down`. Para apagar também os dados do banco: `docker compose down -v`.

## Variáveis de ambiente

Ficam em um único `.env`, na raiz do projeto. O Docker Compose e o backend leem o mesmo arquivo.

| Variável | Para que serve |
| --- | --- |
| `SECRET_KEY` | Chave que assina os tokens JWT. Use pelo menos 32 caracteres. |
| `ALGORITHM` | Algoritmo do JWT, normalmente `HS256`. |
| `ACESS_TOKEN_EXPIRE_MINUTES` | Validade do token de acesso, em minutos. O nome tem "ACESS" com um S só, e precisa ficar assim. |
| `PG_USERNAME` | Usuário do PostgreSQL. |
| `PG_PASSWORD` | Senha do PostgreSQL. |
| `PG_PORT` | Porta do banco **vista da sua máquina** (veja [Portas](#portas)). Dentro do Docker o backend usa a 5432 automaticamente. |
| `PG_HOST` | Opcional. Padrão `localhost`. O Compose define `db` para a API. |

O banco se chama `condominio` (e `condominio_teste` nos testes).

## Portas

| Serviço | Porta na sua máquina |
| --- | --- |
| Frontend (Vite) | 5173 |
| API (FastAPI) | 8000 |
| PostgreSQL | 5434 |

O banco usa a **5434** no lado de fora para não colidir com um PostgreSQL já instalado na máquina, que
costuma ocupar a 5432. Para conectar com DBeaver, pgAdmin ou `psql`, use `localhost:5434`.

## Rodando sem Docker

Útil para desenvolver com recarga automática. O banco continua no Docker.

**Backend** (a partir da pasta `backend`):

```
docker compose up -d db

python -m venv env
env\Scripts\Activate.ps1          # Linux/macOS: source env/bin/activate
pip install -r requirements-dev.txt

alembic upgrade head
uvicorn main:app --reload
```

**Frontend** (a partir da pasta `frontend/condominio-frontend`, com Node 24):

```
npm install
npm run dev
```

O Vite repassa as chamadas de `/api/...` para `http://localhost:8000`, então não é preciso configurar
CORS no desenvolvimento.

## Banco de dados e migrations

As migrations ficam em `backend/alembic/versions`. Comandos, a partir da pasta `backend`:

```
alembic upgrade head                                   # aplica as migrations
alembic revision --autogenerate -m "descrição"         # gera uma migration a partir dos models
alembic downgrade -1                                   # desfaz a última
```

Depois de gerar uma migration, abra o arquivo e confira antes de aplicar. O autogenerate não é perfeito
com renomeações e alguns tipos.

### Modelo de dados

```
usuarios        id, nome, email, senha (hash), admin
blocos          id, numero
apartamentos    id, bloco -> blocos.id, numero
residentes      id, nome, apartamento -> apartamentos.id, cpf, telefone,
                email (único), data_inicio, data_vencimento, valor_aluguel
```

O telefone é guardado como inteiro de 64 bits, para caber um celular com DDD.

## API

Documentação completa e interativa em http://localhost:8000/docs.

### Autenticação

`POST /auth/login` recebe e-mail e senha e devolve os tokens:

```
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "voce@email.com", "senha": "suasenha"}'
```

```json
{ "acess_token": "...", "refresh_token": "...", "token_jwt": "Bearer " }
```

Nas demais rotas, envie o `acess_token` no cabeçalho:

```
Authorization: Bearer <acess_token>
```

No Swagger, clique em **Authorize** e cole o token.

### Endpoints

Todos exigem login, exceto `/auth/login`.

| Método | Rota | Descrição |
| --- | --- | --- |
| POST | `/auth/login` | Login |
| GET | `/blocos` | Lista os blocos |
| POST | `/blocos` | Cria um bloco |
| GET | `/blocos/{id}` | Busca um bloco |
| PUT | `/blocos/{id}` | Edita um bloco |
| DELETE | `/blocos/{id}` | Remove um bloco |
| GET | `/apartamentos` | Lista os apartamentos, com o bloco incluído |
| POST | `/apartamentos` | Cria um apartamento |
| GET | `/apartamentos/{id}` | Busca um apartamento |
| PUT | `/apartamentos/{id}` | Edita um apartamento |
| DELETE | `/apartamentos/{id}` | Remove um apartamento |
| GET | `/residentes` | Lista os residentes, com apartamento e bloco incluídos |
| POST | `/residentes` | Cria um residente |
| GET | `/residentes/{id}` | Busca um residente |
| PUT | `/residentes/{id}` | Edita um residente |
| DELETE | `/residentes/{id}` | Remove um residente |

### Exemplos de corpo

Os nomes dos campos diferenciam maiúsculas de minúsculas: `numero`, não `Numero`.

```json
POST /blocos
{ "numero": 1 }
```

```json
POST /apartamentos
{ "bloco_id": 1, "numero": 101 }
```

```json
POST /residentes
{
  "nome": "Maria Silva",
  "apartamento_id": 1,
  "cpf": "123.456.789-00",
  "telefone": 11987654321,
  "email": "maria@email.com",
  "data_inicio": "2026-01-01",
  "data_vencimento": "2026-12-31",
  "valor_aluguel": 1500.50
}
```

Crie nesta ordem: bloco, apartamento, residente.

### Códigos de resposta

| Código | Quando |
| --- | --- |
| 200 / 201 / 204 | Sucesso (consulta e edição / criação / remoção) |
| 400 | Login com e-mail ou senha incorretos |
| 401 | Sem token, token inválido ou expirado |
| 404 | Registro não encontrado, ou bloco/apartamento informado não existe |
| 409 | E-mail de residente repetido, ou remoção de bloco/apartamento que ainda tem filhos |
| 422 | Dados inválidos (número de bloco menor que 1, vencimento antes do início, e-mail mal formado, campo ausente) |

## Frontend

| Rota | Tela |
| --- | --- |
| `/login` | Login |
| `/` | Lista de blocos, cada um com sua cor |
| `/blocos/:id` | Tabela de apartamentos e residentes do bloco |

Sem login, qualquer rota redireciona para `/login`. O token fica no `localStorage` do navegador, e uma
resposta 401 da API encerra a sessão automaticamente.

O visual (cores, logos, marca-d'água, tabela com a coluna de apartamento fixa) segue o do sistema
anterior do condomínio, feito em Django.

## Testes

Os testes ficam em `backend/tests`. A partir da pasta `backend`, com o banco no ar
(`docker compose up -d db`):

```
pip install -r requirements-dev.txt
pytest
```

| Arquivo | O que cobre |
| --- | --- |
| `test_seguranca.py` | Hash de senha e token JWT |
| `test_schemas.py` | Validações dos schemas, sem banco |
| `test_auth.py` | Login e proteção de todas as rotas |
| `test_blocos.py`, `test_apartamentos.py`, `test_residentes.py` | CRUD completo, 404, 409 e 422 |

Os testes de rota usam um banco próprio, `condominio_teste`, criado automaticamente no mesmo PostgreSQL.
O banco de desenvolvimento nunca é tocado. O arquivo `tests/conftest.py` monta esse banco e as fixtures
reutilizadas pelos testes (`client`, `client_auth`, `criar_bloco` e outras).

## Limitações conhecidas

- **Cadastro de usuários**: só pelo script `criar_usuario.py`. Não há rota nem tela.
- **Perfis**: o campo `admin` existe, mas não é aplicado. Qualquer usuário logado acessa tudo.
- **Refresh token**: é emitido no login, mas não há rota para renová-lo, e hoje ele vale como token de
  acesso.
- **Cor do bloco**: a API não tem esse campo. O frontend usa três cores (amarelo, azul e verde) em rodízio
  pelo número do bloco.
- **Duplicidade**: a API aceita dois blocos com o mesmo número, dois apartamentos com o mesmo número no
  mesmo bloco e dois residentes com o mesmo CPF. Só o e-mail do residente é único.
- **Campos do residente**: a API guarda só nome, CPF, telefone, e-mail, datas de início e vencimento e
  valor do aluguel.
- **Produção**: o serviço `frontend` do Compose roda o servidor de desenvolvimento do Vite. Um deploy de
  verdade pede `npm run build` servido por um servidor web, e um proxy para a API ou CORS liberado.
- **Exportação para Excel**: não existe.

## Solução de problemas

**`required variable PG_USERNAME is missing a value`**
O arquivo `.env` não existe na raiz do projeto, ou está sem essa variável. Crie-o a partir do `.env.example`.

**A API não conecta ao banco, ou o erro aparece como `UnicodeDecodeError`**
No Windows, falhas de conexão com mensagens em português podem aparecer assim. Confira se o container `db`
está saudável (`docker compose ps`) e se `PG_USERNAME` e `PG_PASSWORD` do `.env` são os mesmos com que o
banco foi criado. Se você trocou a senha depois da primeira subida, apague o volume com
`docker compose down -v` (isso apaga os dados).

**`port is already allocated`**
Alguma porta (5173, 8000 ou 5434) já está em uso. Feche o programa que a ocupa ou troque o mapeamento em
`docker-compose.yml`.

**Falha ao rodar `pytest`: "Suba o banco com: docker compose up -d db"**
Os testes não encontraram o PostgreSQL. Suba o banco e confira o `PG_PORT` do `.env`.

**O login funciona, mas as telas dão 401**
O token expirou. Saia e entre de novo.

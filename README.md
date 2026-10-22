# API de Cadastro de Clientes

API REST para cadastro de clientes, desenvolvida em **Python** com **FastAPI**, banco de dados **SQLite** e senhas protegidas com hash **bcrypt**. Projeto criado para praticar construção de APIs, persistência de dados, validação, segurança básica e testes automatizados.

## Funcionalidades

- Cadastro de clientes com nome, e-mail, telefone e senha
- Listagem de clientes com paginação (`skip` e `limit`)
- Busca de cliente por id
- Atualização de nome e telefone (atualização parcial)
- Remoção de cliente
- Validação de dados de entrada com Pydantic (formato de e-mail, tamanho mínimo e máximo dos campos)
- Bloqueio de e-mails duplicados (erro 409)
- Senha armazenada somente como hash (bcrypt) e **nunca** devolvida pela API
- Documentação interativa gerada automaticamente (Swagger UI)
- Testes automatizados com pytest, usando banco em memória

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.12 | Linguagem |
| FastAPI | Framework da API |
| SQLAlchemy | ORM / acesso ao banco |
| SQLite | Banco de dados |
| Pydantic | Validação e schemas |
| bcrypt | Hash de senhas |
| Uvicorn | Servidor ASGI |
| pytest + httpx | Testes automatizados |

## Estrutura do projeto

```
cadastro-clientes/
├── app/
│   ├── __init__.py
│   ├── database.py   # conexão e sessão do banco
│   ├── models.py     # tabela de clientes (SQLAlchemy)
│   ├── schemas.py    # validação de entrada e saída (Pydantic)
│   ├── security.py   # geração e verificação de hash de senha
│   ├── crud.py       # operações no banco (criar, ler, atualizar, apagar)
│   └── main.py       # rotas da API
├── tests/
│   ├── __init__.py
│   ├── test_clientes.py   # testes das rotas
│   └── test_security.py   # testes do hash de senha
├── requirements.txt
└── README.md
```

## Como rodar (Linux)

**Pré-requisitos:** Python 3.10+ e Git.

```bash
# 1. Clonar o repositório
git clone https://github.com/miguelcalatroni77/cadastro-clientes.git
cd cadastro-clientes

# 2. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Subir o servidor
uvicorn app.main:app --reload
```

Depois, abra no navegador:

- Documentação interativa: http://127.0.0.1:8000/docs

O arquivo do banco (`clientes.db`) é criado automaticamente na primeira execução.

## Endpoints

| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| POST | `/clientes` | Cadastra um cliente | 201, 409 (e-mail já cadastrado), 422 |
| GET | `/clientes` | Lista clientes (`?skip=0&limit=100`) | 200 |
| GET | `/clientes/{id}` | Busca cliente por id | 200, 404 |
| PUT | `/clientes/{id}` | Atualiza nome e/ou telefone | 200, 404, 422 |
| DELETE | `/clientes/{id}` | Remove um cliente | 204, 404 |

### Exemplo: criar cliente

Requisição:

```bash
curl -X POST http://127.0.0.1:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "email": "maria@email.com",
    "telefone": "48999998888",
    "senha": "senha12345"
  }'
```

Resposta (`201 Created`). Repare que a senha não é devolvida:

```json
{
  "id": 1,
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "telefone": "48999998888",
  "criado_em": "2026-10-21T22:00:00.000000"
}
```

## Segurança

- A senha é transformada em hash com **bcrypt** antes de ser salva; a senha original nunca vai para o banco.
- Os schemas de resposta não incluem senha nem hash.
- O arquivo do banco (`*.db`), o ambiente virtual e arquivos `.env` estão no `.gitignore`.

## Testes

Os testes usam um banco SQLite em memória, então **não alteram** o `clientes.db` real.

```bash
python -m pytest -v
```

Cenários cobertos: criação, e-mail duplicado, e-mail inválido, senha curta, listagem, busca (existente e inexistente), atualização (existente e inexistente), remoção e hash de senha.

## Próximas melhorias

- [ ] Autenticação com login e token JWT
- [ ] Validação de formato do telefone
- [ ] Migrações de banco com Alembic
- [ ] Trocar SQLite por PostgreSQL
- [ ] Containerização com Docker
- [ ] Integração contínua (GitHub Actions) rodando os testes a cada push

## Autor

**Miguel Calatroni**
GitHub: [@miguelcalatroni77](https://github.com/miguelcalatroni77)

# API de Cadastro de Clientes

API REST para cadastro de clientes, desenvolvida em **Python** com **FastAPI**, banco de dados **SQLite**, senhas protegidas com hash **bcrypt** e autenticação por **token JWT**. Projeto criado para praticar construção de APIs, persistência de dados, validação, segurança e testes automatizados.

## Funcionalidades

- Cadastro de clientes com nome, e-mail, telefone e senha
- Login com e-mail e senha, que devolve um token JWT
- Rotas protegidas: só clientes autenticados acessam a listagem, a busca e as alterações
- Cada cliente só pode **alterar ou apagar o próprio cadastro** (erro 403 caso contrário)
- Rota `/clientes/me` com os dados do cliente logado
- Listagem de clientes com paginação (`skip` e `limit`)
- Atualização parcial de nome e telefone
- Validação de dados de entrada com Pydantic (formato de e-mail, tamanho mínimo e máximo dos campos)
- Bloqueio de e-mails duplicados (erro 409)
- Senha armazenada somente como hash (bcrypt) e **nunca** devolvida pela API
- Documentação interativa gerada automaticamente (Swagger UI), com botão **Authorize**
- 19 testes automatizados com pytest, usando banco em memória

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem |
| FastAPI | Framework da API |
| SQLAlchemy | ORM / acesso ao banco |
| SQLite | Banco de dados |
| Pydantic | Validação e schemas |
| bcrypt | Hash de senhas |
| PyJWT | Geração e validação de tokens JWT |
| Uvicorn | Servidor ASGI |
| pytest + httpx | Testes automatizados |

## Estrutura do projeto

```
cadastro-clientes/
├── app/
│   ├── __init__.py
│   ├── config.py     # chave secreta, algoritmo e validade do token
│   ├── database.py   # conexão e sessão do banco
│   ├── models.py     # tabela de clientes (SQLAlchemy)
│   ├── schemas.py    # validação de entrada e saída (Pydantic)
│   ├── security.py   # hash de senha e criação/validação de token JWT
│   ├── crud.py       # operações no banco (criar, ler, atualizar, apagar)
│   └── main.py       # rotas da API e autenticação
├── tests/
│   ├── __init__.py
│   ├── test_clientes.py   # testes das rotas, do login e das permissões
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

# 4. (Recomendado) Definir uma chave secreta própria para assinar os tokens
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 5. Subir o servidor
uvicorn app.main:app --reload
```

Depois, abra no navegador:

- Documentação interativa: http://127.0.0.1:8000/docs

O arquivo do banco (`clientes.db`) é criado automaticamente na primeira execução.

## Autenticação

A API usa **JWT** (JSON Web Token) no padrão OAuth2 com senha:

1. O cliente se cadastra em `POST /clientes` (rota pública).
2. Faz login em `POST /login`, enviando e-mail (campo `username`) e senha. A resposta traz um `access_token`.
3. Nas demais rotas, envia o token no cabeçalho `Authorization: Bearer <token>`.
4. O token expira em **30 minutos**; depois disso é preciso fazer login de novo.

No Swagger (`/docs`), clique em **Authorize**, informe e-mail e senha, e as rotas protegidas passam a funcionar direto na tela.

### Exemplo com curl

```bash
# 1. Cadastrar
curl -X POST http://127.0.0.1:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{"nome": "Maria Silva", "email": "maria@email.com", "telefone": "48999998888", "senha": "senha12345"}'

# 2. Login (formulário, não JSON)
curl -X POST http://127.0.0.1:8000/login \
  -d "username=maria@email.com&password=senha12345"

# 3. Usar o token recebido
curl http://127.0.0.1:8000/clientes/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## Endpoints

| Método | Rota | Auth | Descrição | Respostas |
|---|---|---|---|---|
| POST | `/clientes` | Não | Cadastra um cliente | 201, 409 (e-mail já cadastrado), 422 |
| POST | `/login` | Não | Devolve o token JWT | 200, 401 (e-mail ou senha incorretos) |
| GET | `/clientes` | Sim | Lista clientes (`?skip=0&limit=100`) | 200, 401 |
| GET | `/clientes/me` | Sim | Dados do cliente logado | 200, 401 |
| GET | `/clientes/{id}` | Sim | Busca cliente por id | 200, 401, 404 |
| PUT | `/clientes/{id}` | Sim | Atualiza nome e/ou telefone (só o próprio cadastro) | 200, 401, 403, 404, 422 |
| DELETE | `/clientes/{id}` | Sim | Remove o cadastro (só o próprio) | 204, 401, 403, 404 |

## Segurança

- A senha é transformada em hash com **bcrypt** antes de ser salva; a senha original nunca vai para o banco.
- Os schemas de resposta não incluem senha nem hash.
- O login devolve a mesma mensagem para e-mail inexistente e senha errada, para não revelar quais e-mails estão cadastrados.
- O token tem validade curta (30 minutos) e é assinado com uma chave secreta.
- O arquivo do banco (`*.db`), o ambiente virtual e arquivos `.env` estão no `.gitignore`.

> **Atenção:** o código traz uma chave secreta de desenvolvimento como valor padrão, só para facilitar o uso local. Como ela está visível no repositório, **em qualquer uso real é obrigatório definir a variável de ambiente `SECRET_KEY`** com um valor aleatório, como no passo 4 da instalação.

## Testes

Os testes usam um banco SQLite em memória, então **não alteram** o `clientes.db` real.

```bash
python -m pytest -v
```

Cenários cobertos (19 testes):

- Cadastro: criação, e-mail duplicado, e-mail inválido e senha curta
- Consulta: listagem, busca por id (existente e inexistente) e `/clientes/me`
- Alteração: atualização e remoção (existente e inexistente)
- Autenticação: login correto, senha errada, acesso sem token e com token inválido
- Permissões: um cliente não consegue alterar nem apagar o cadastro de outro (403)
- Segurança: o hash gerado nunca é igual à senha, e a verificação distingue senha certa de errada

## Próximas melhorias

- [ ] Troca de senha e de e-mail com nova verificação
- [ ] Validação de formato do telefone
- [ ] Falhar na inicialização caso `SECRET_KEY` não esteja definida em produção
- [ ] Migrações de banco com Alembic
- [ ] Trocar SQLite por PostgreSQL
- [ ] Containerização com Docker
- [ ] Integração contínua (GitHub Actions) rodando os testes a cada push

## Autor

**Miguel Calatroni**
GitHub: [@miguelcalatroni77](https://github.com/miguelcalatroni77)
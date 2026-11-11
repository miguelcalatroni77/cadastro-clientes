from fastapi.testclient import TestClient 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.pool import StaticPool
import pytest

from app.database import Base, get_db
from app.main import app

# Banco SQLite só na memória: não cria arquivo e some quando o teste termina.
# StaticPool faz todas as conexões compartilharem o mesmo banco sem memória
# (sem isso, cada conexão veria um banco vazio diferente).
engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTeste = sessionmaker(bind=engine_teste, autocommit=False, autoflush=False)


def get_db_teste():
    """Versão de get_db que entrega sessões do banco de TESTE."""
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()

# Troca o get_db real pelo teste. Assim a API usa o banco em memória.
app.dependency_overrides[get_db] = get_db_teste

client = TestClient(app)  # "navegador" falso que chama a API sem precisar de uvicorn


@pytest.fixture(autouse=True)
def banco_limpo():
    """Antes de CADA teste: cria as tabelas. Depois: apaga tudo.
    Assim um teste nunca interfere no outro."""
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)


# Dados de exemplo reaproveitados nos testes
CLIENTE = {
    "nome": "Maria Silva",
    "email": "maria@email.com",
    "telefone": "48999998888",
    "senha": "senhamaria321",
}


# Segundo cliente, usado para tetsar que um usuário não mexa no cadastro do outro.
OUTRO = {
    "nome": "João Pedro",
    "email": "joao@email.com",
    "telefone": "48977778888",
    "senha": "outrasenha123",
}


def autenticar():
    """Cadastra o cliente de exemplo, faz login e devolve (cliente, cabeçalhos com o token)."""
    criado = client.post("/clientes", json=CLIENTE).json()
    # O login recebe um formulário (data=), e não JSON (json=)
    resposta = client.post(
        "/login", data={"username": CLIENTE["email"], "password": CLIENTE["senha"]}
    )
    token = resposta.json()["access_token"]
    return criado, {"Authorization": f"Bearer {token}"}


def test_criar_cliente():
    """POST válido deve devolver 201 e NÃO expor a senha."""
    resposta = client.post("/clientes", json=CLIENTE)
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["nome"] == "Maria Silva"
    assert dados["email"] == "maria@email.com"
    assert "id" in dados
    assert "senha" not in dados # a senha nunca pode voltar.
    assert "senha_hash" not in dados # nem o hash


def test_email_duplicado():
    """Cadastrar o mesmo e-amil duas vezes deve apresentar 409."""
    client.post("/clientes", json=CLIENTE)
    resposta = client.post("/clientes", json=CLIENTE)
    assert resposta.status_code == 409


def test_email_invalido():
    """E-mail sem formato válido deve ser recusado com 422."""
    resposta = client.post("/clientes", json={**CLIENTE, "email": "abc"})
    assert resposta.status_code == 422


def test_senha_curta():
    """Senha com menos de 8 caracteres deve ser recusada e retornar 422."""
    resposta = client.post("/clientes", json={**CLIENTE, "senha": "123"})
    assert resposta.status_code == 422


def test_listar_clientes():
    """Logado, a lista deve conter exatamente 1 cliente."""
    _, headers = autenticar()
    resposta = client.get("/clientes", headers=headers)
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_buscar_cliente_existente():
    """GET por id de um cliente que existe devolve 200 com os dados."""
    criado, headers = autenticar()
    resposta = client.get(f"/clientes/{criado['id']}", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["email"] == CLIENTE["email"]


def test_buscar_cliente_inexistente():
    """GET por id que não existe deve dar 404."""
    _, headers = autenticar()
    resposta = client.get("/clientes/999", headers=headers)
    assert resposta.status_code == 404


def test_atualizar_cliente():
    """ PUT só com o nome deve mudar o nome e manter o telefone."""
    criado, headers = autenticar()
    resposta = client.put(
        f"/clientes/{criado['id']}", json={"nome": "Maria Souza"}, headers=headers
    )
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Maria Souza"
    assert resposta.json()["telefone"] == CLIENTE["telefone"]


def test_atualizar_cliente_inexistente():
    """PUT em id que não existe deve dar 404."""
    _, headers = autenticar()
    resposta = client.put("/cliente/999", json={"nome": "Fulano"}, headers=headers)
    assert resposta.status_code == 404


def test_deletar_cliente():
    """DELETE do próprio cadastro devolve 204 e o cliente deixa de existir."""
    criado, headers = autenticar()
    resposta = client.delete(f"/clientes/{criado['id']}", headers=headers)
    assert resposta.status_code == 204
    # O token ainda é válido, mas o dono dele não existe mais: deve dar 401
    assert client.get("/clientes/me", headers=headers).status_code == 401


def test_login_correto():
    """E-mail e senha corretos devolvem um token."""
    client.post("/clientes", json=CLIENTE)
    resposta = client.post("/login", data={"username": CLIENTE["email"], "password": CLIENTE["senha"]}
    )
    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"
    assert "access_token" in resposta.json()


def test_login_senha_errada():
    """Senha errada deve apresentar 401."""
    client.post("/clientes", json=CLIENTE)
    resposta = client.post(
        "/login", data={"username": CLIENTE["email"], "password": "senhaerrada"}
    )
    assert resposta.status_code == 401


def test_rota_protegida_sem_token():
    """Sem token, as rotas protegidas devolvem 401."""
    assert client.get("/clientes").status_code == 401


def test_rota_protegida_com_token_inavalido():
    """Token inventado também deve dar 401."""
    headers = {"Authorization": "Bearer token-falso"}
    assert client.get("/clientes", headers=headers).status_code == 401


def test_meus_dados():
    """/clientes/me devolve o cliente dono do token."""
    _, headers = autenticar()
    resposta = client.get("/clientes/me", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["email"] == CLIENTE["email"]


def test_nao_pode_alterar_outro_cliente():
    """Um cliente não pode editar o cadastro de outro (403)."""
    _, headers = autenticar()
    outro = client.post("/clientes", json=OUTRO).json()
    resposta = client.put(f"/clientes/{outro['id']}", json={"nome": "Invasor"}, headers=headers)
    assert resposta.status_code == 403


def test_nao_pode_apagar_outro_cliente():
    """Um cliente não pode apagar o cadastro de outro cliente (403)."""
    _, headers = autenticar()
    outro = client.post("/clientes", json=OUTRO).json()
    resposta = client.delete(f"/clientes/{outro['id']}", headers=headers)
    assert resposta.status_code == 403
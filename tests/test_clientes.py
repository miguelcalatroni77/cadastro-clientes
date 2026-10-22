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
    """Depois de criar um cliente, a lista deve conter exatamente 1."""
    client.post("/clientes", json=CLIENTE)
    resposta = client.get("/clientes")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_buscar_cliente_existente():
    """GET por id de um cliente que existe devolve 200 com os dados."""
    criado = client.post("/clientes", json=CLIENTE).json()
    resposta = client.get(f"/clientes/{criado['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "maria@email.com"


def test_buscar_cliente_inexistente():
    """GET por id que não existe deve dar 404."""
    resposta = client.get("/clientes/999")
    assert resposta.status_code == 404


def test_atualizar_cliente():
    """ PUT só com o nome deve mudar o nome e manter o telefone."""
    criado = client.post("/clientes", json=CLIENTE).json()
    resposta = client.put(f"/clientes/{criado['id']}", json={"nome": "Maria Souza"})
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Maria Souza"
    assert resposta.json()["telefone"] == "48999998888" # não foi apagado


def test_atualizar_cliente_inexistente():
    """PUT em id que não existe deve dar 404."""
    resposta = client.put("/cliente/999", json={"nome": "Fulano"})
    assert resposta.status_code == 404


def test_deletar_cliente():
    """DELETE devolve 204 e, depois, o cliente não existe mais (404)."""
    criado = client.post("/clientes", json=CLIENTE).json()
    resposta = client.delete(f"/clientes/{criado['id']}").status_code == 404
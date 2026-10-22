# conexão com o banco de dados
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 

# Endereço do banco. "sqlite:///./clientes.db" cria um arquivo chamado
# clientes.db na pasta projeto (com isso não é necessário instalar servidor de banco).
DATABASE_URL = "sqlite:///./clientes.db"

#O "engine" é a conexão principal com o banco.
#check_same_thread=False é necessário no SQLite porque a FastAPI pode atender
#requisições em threads diferentes.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False })

# SessionLocal é uma "fábrica" de sessões. Uma sessão é uma conversa
# com o banco: você abre, faz operações (consultar, salvar) e fecha.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base é a classe-mãe de todos os modelos e (tabelas).
# Toda classe que herdar dela vira um tabela no banco.
Base = declarative_base()


def get_db():
    """Entrega uma sessão do banco para cada requisição e garante que ela seja fechada."""
    db = SessionLocal() #abre a sessão
    try:
        yield db # "empresta" a sessão para a rota em que a pediu
    finally:
        db.close() #sempre a fecha, mesmo que dê erro no meio do caminho
        
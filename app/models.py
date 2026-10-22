# tabela
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class Cliente(Base):
    """Representa a tabela 'clientes' no banco. Cada atributo é uma coluna."""


    __tablename__ = "clientes" # nome real da tabela no banco

    # Chave primária: número único que identifica cada cliente (1, 2, 3...)
    id = Column(Integer, primary_key=True, index=True)

    # nullable=Fable significa que o campo é obrigatório
    nome = Column(String(100), nullable=False)

    #unique=True impede dois clientes com o mesmo e-mail
    #index=True deixa a busca por e-mail mais rápida
    email = Column(String(120), unique=True, index=True, nullable=False)

    telefone = Column(String(20), nullable=False)

    # Guardamos aquin apenas o HASH da Senha, nunca a senha Original do Usuário.
    senha_hash = Column(String(255), nullable=False)

    # Data da criação preenchida automaticamente (em UTC) ao salvar o cliente
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
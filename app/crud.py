# operações no banco
from sqlalchemy.orm import Session

from . import models, schemas 
from .security import gerar_hash

# CRUD = Create, Read, Update, Delete (criar, ler, atualizar, apagar).
# É um arquivo que concentra toda a conversa com o banco, deixando todas as rotas limpas.

def buscar_por_id(db: Session, cliente_id: int):
    """Busca um cliente pelo id, Retorna o cliente ou None se não existir."""
    return db.get(models.Cliente, cliente_id)


def buscar_por_email(db: Session, email: str):
    """Busca o cliente pelo e-mail. Usada para evitar cadastro duplicado."""
    return db.query(models.Cliente).filter(models.Cliente.email == email).first()


def listar(db: Session, skip: int = 0, limit: int = 100):
    """Lista clientes com paginação: pula 'skip' registros e traz no máximo 'limit'."""
    return db.query(models.Cliente).offset(skip).limit(limit).all()


def criar(db: Session, dados: schemas.ClienteCreate):
    """Cria um cliente novo, guardando a senha já trasnformada em hash."""
    cliente = models.Cliente(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
        senha_hash=gerar_hash(dados.senha), # a senha original nunca vai para o banco de dados.
    )
    db.add(cliente)  #coloca o cliente na fila para ser salvo
    db.commit()      #confirma e grava de fato no banco
    db.refresh(cliente) #recarrega o objeto  para pegar  o id e a data gerados
    return cliente


def atualizar(db: Session, cliente: models.Cliente, dados: schemas.ClienteUpdate):
    """Atualiza apenas os campos que o usuário realmente enviou."""
    # exclude_unset=True ignora campos não enviados, assim não apagamos
    # o telefone por acidente quando o usuário só quis mudar o nome.
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor) #equivale a: cliente.nome = valor
    db.commit()
    db.refresh(cliente)
    return cliente


def deletar(db: Session, cliente: models.Cliente):
    """Remove o cliente do banco."""
    db.delete(cliente)
    db.commit()
    
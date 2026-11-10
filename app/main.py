# rotas da API
from fastapi.security import OAuth2PasswordRequestForm

from .security import criar_token, verificar_senha

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

#Cria as tabelas no banco caso ainda não existam (roda ao iniciar a API)
models.Base.metadata.create_all(bind=engine)

#Cria a aplicação. o título aparece na documentação em /docs
app = FastAPI(title="API de cadastro de clientes")



# @app.post(...) liga uma URL + método HTTP a uma função.
#response_model filtra a resposta para seguir o schema (sem senha).
#Depends(get_db) injeta automaticamente uma sessão do banco na função.
@app.post("/clientes", response_model=schemas.ClienteOut, status_code=status.HTTP_201_CREATED)
def criar_cliente(dados: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """Cadastra um novo cliente. Retorna 409 se o e-mail já existir."""
    #Antes de criar, ele verifica se o e-mail já está em uso.
    if crud.buscar_por_email(db, dados.email):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    return crud.criar(db, dados)



@app.get("/clientes", response_model=list[schemas.ClienteOut])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista os clientes. Use skip e limit na URL para paginar (?skip=0&limit=10)."""
    return crud.listar(db, skip, limit)



@app.get("/clientes/{cliente_id}", response_model=schemas.ClienteOut)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Busca um cliente pelo id. Retorna 404 se não existir."""
    cliente = crud.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail= "Cliente não encontrado")
    return cliente



@app.put("/clientes/{cliente_id}", response_model=schemas.ClienteOut)
def atualizar_cliente(cliente_id: int, dados: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    """Atualiza nome e/ou telefone de um cliente existente."""
    cliente = crud.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return crud.atualizar(db, cliente, dados)



@app.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Remove um cliente, Retorna 204 (sucesso, sem conteúdo) ou 404 se não existir."""
    cliente = crud.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    crud.deletar(db, cliente)
    

@app.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Recebe e-mail e senha e devolve um token JWT."""
    # O padrão OAuth2 chama o campo de "username"; aqui ele carrega o e-mail.
    cliente = crud.buscar_por_email(db, form.username)
    # Mesma mensagem para e-mail inexistente e senha errada, para não revelar
    # quais e-mails estão cadastrados
    if not cliente or not verificar_senha(form.password, cliente.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": criar_token(cliente.email), "token_type": "bearer"}
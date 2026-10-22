# validação de entrada e saída
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

#Schemas definem o FORMATO dos dados que entraem e saem da API.
# o Pydantic valida tudo automaticamente e devolve o erro 402 se algo estiver incorreto.
# (Model = como os dados ficam no banco / Schema = como trafegam na API)

class ClienteCreate(BaseModel):
    """Dados que o usuário envia para CRIAR um cliente."""

    nome: str = Field(min_length=2, max_length=100) # entre 2 e 100 caracteres
    email: EmailStr #valida se tem formato de e-mail ( ex: nome@dominio.com)
    telefone: str = Field(min_length=8, max_length=20)
    senha: str = Field(min_length=8, max_length=64) #mínimo de 8 caracteres.


class ClienteUpdate(BaseModel):
    """Dados que o usuário pode ALTERNAR. Todos opcionais (None = não mexer)."""

    nome: str | None = Field(default=None, min_length=2, max_length=100)
    telefone: str | None = Field(default= None, min_length=8, max_length=20)
    # E-mail e senha ficam d fora de propósito: alterá-los exigiria
    # regras extras de segurança.


class ClienteOut(BaseModel):
    """Dados que a API Devolve. Repare que NÃO tem senha nem a hash."""

    #from_attributes=True permite criar este schema a partir de um objeto
    # do banco (models.Cliente), lendo seus atributos.
    model_config = ConfigDict(from_attributes=True)

    id: int 
    nome: str
    email: EmailStr
    telefone: str
    criado_em: datetime
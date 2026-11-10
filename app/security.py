# hash da senha
from datetime import datetime, timedelta, timezone


import bcrypt
import jwt # biblioteca PyJWT

from .config import ACCES_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def gerar_hash(senha: str) -> str:
    """Transforma a senha em um hash irreversével, seguro para guardar no banco."""
    # encode() converte texto em bytes, que é o que o bcrypt exige.
    # O bcrypt só considera os primeiros 72 bytes, por isso o [:72].
    # gensalt() cria um "tempero" aleatório: duas senhas iguais geram hashes diferentes.
    return bcrypt.hashpw(senha.encode()[:72], bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha digitada corresponde ao hash guaradado. Retorna True ou False."""
    return bcrypt.checkpw(senha.encode()[:72], senha_hash.encode())


def criar_token(email: str) -> str:
    """Cria um token JWT assinado que identifica o cliente pelo e-mail."""
    # "exp" é um campo padrão do JWT: passado esse horário, o token é recusado
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    # "sub" (subject) é o campo padrão para dizer "de quem é" o token.
    dados = {"sub": email, "exp": expira_em}
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> str | None:
    """Valida o token e devolve o e-mail dentro dele. Retorna None se for inválido ou expirado."""
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return dados.get("sub")
    except jwt.PyJWTError:
        return None
        
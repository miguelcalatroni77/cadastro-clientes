# hash da senha
import bcrypt

def gerar_hash(senha: str) -> str:
    """Transforma a senha em um hash irreversével, seguro para guardar no banco."""
    # encode() converte texto em bytes, que é o que o bcrypt exige.
    # O bcrypt só considera os primeiros 72 bytes, por isso o [:72].
    # gensalt() cria um "tempero" aleatório: duas senhas iguais geram hashes diferentes.
    return bcrypt.hashpw(senha.encode()[:72], bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha digitada corresponde ao hash guaradado. Retorna True ou False."""
    return bcrypt.checkpw(senha.encode()[:72], senha_hash.encode())
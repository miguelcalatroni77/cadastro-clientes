from app.security import gerar_hash, verificar_senha


def test_hash_nao_e_a_senha_original():
    """O hash gerado nunca pode ser igual à senha em texto puro."""
    assert gerar_hash("senha12345") != "senha12345"


def test_verificar_senha_correta_e_errada():
    """A senha certa confere com o hash; uma errada, não."""
    hash_ = gerar_hash("senha12345")
    assert verificar_senha("senha12345", hash_) is True
    assert verificar_senha("outrasenha", hash_) is False
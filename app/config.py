import os

#Chave secreta que assina os  tokens. Quem a conhece consegue forjar os tokens.
#Em produção ela vem de uma variável de ambiente; o valor abaixo é só  para o desenvolvimento local
SECRET_KEY = os.getenv("SECRET_KEY", "chave-apenas-para-desenvolvimento-troque-em-produção")


# Algoritmo usado na assinatura do token
ALGORITHM = "HS256"


# Tempo de vida do token. Depois dissto, o usuário precisará realizar o login novamente.
ACCES_TOKEN_EXPIRE_MINUTES = 30

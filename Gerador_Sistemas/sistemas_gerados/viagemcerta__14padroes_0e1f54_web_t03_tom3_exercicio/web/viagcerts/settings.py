"""
SETTINGS DA APP viagcerts — as configurações deste módulo num lugar só.

Cada valor tem um PADRÃO aqui e pode ser trocado no config/settings.py do projeto com o prefixo
VIAGCERTS_ (ex.: VIAGCERTS_API_LIMITE = 20). O código da app lê sempre por valor("..."), nunca direto:
assim o projeto manda, e a app continua funcionando sozinha se ninguém configurar nada.
"""
from django.conf import settings

PADROES = {
    "API_LIMITE": 100,    # máximo de registros que a lista da API REST devolve por vez (?limite=N)
    "API_ESCRITA": True,  # False = API só de leitura (POST, PUT, PATCH e DELETE respondem 405)
}


def valor(nome):
    """O valor da configuração: o do projeto (VIAGCERTS_<NOME>), se houver; senão o padrão desta app."""
    return getattr(settings, f"VIAGCERTS_{nome}", PADROES[nome])

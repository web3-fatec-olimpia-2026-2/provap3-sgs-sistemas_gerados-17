"""
SETTINGS DA APP citricultura — as configurações deste módulo num lugar só.

Cada valor tem um PADRÃO aqui e pode ser trocado no cooperativa/settings.py do projeto com o prefixo
CITRICULTURA_ (ex.: CITRICULTURA_API_LIMITE = 20). O código da app lê sempre por valor("..."), nunca direto:
assim o projeto manda, e a app continua funcionando sozinha se ninguém configurar nada.
"""
from django.conf import settings

PADROES = {
    "API_LIMITE": 100,    # máximo de registros que a lista da API REST devolve por vez (?limite=N)
    "API_ESCRITA": True,  # False = API só de leitura (POST, PUT, PATCH e DELETE respondem 405)
    # Campos de cada endpoint — só o que MUDOU do padrão: {"v1": {"campo": False}, "resumo": {"campo": True}}.
    # Padrão: o v1 (REST) mostra id, os campos do model, total e valor_final; o resumo (api/) mostra id,
    # codigo, titulo e valor. O `sgs api config` grava a escolha no cooperativa/settings.py do projeto.
    "API_CAMPOS": {},
}


def valor(nome):
    """O valor da configuração: o do projeto (CITRICULTURA_<NOME>), se houver; senão o padrão desta app."""
    return getattr(settings, f"CITRICULTURA_{nome}", PADROES[nome])

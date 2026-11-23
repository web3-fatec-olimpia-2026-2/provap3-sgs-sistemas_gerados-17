"""A view da tela: repassa o pedido para tela_prompt.atender() — o MESMO caminho do `python tela_prompt.py`
(rotas, Host só 127.0.0.1/localhost, POST só em JSON, gzip). Aqui só se cria o Contexto, uma vez por processo."""
import atexit
import os
import threading

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import tela_prompt

_CONTEXTO = []
_TRAVA = threading.Lock()


def contexto_do_ambiente():
    """O Contexto da tela com o que o runserver do SGS deixou no ambiente: porta (SGS_PORTA), se abre janelas
    (SGS_ABRIR) e, nos testes, as pastas (SGS_SAIDA, SGS_CONFIG, SGS_RAIZ)."""
    amb = os.environ
    return tela_prompt.Contexto(saida=amb.get("SGS_SAIDA") or None, config=amb.get("SGS_CONFIG") or None,
                                raiz=amb.get("SGS_RAIZ") or tela_prompt.RAIZ_PROJETO,
                                porta_tela=int(amb.get("SGS_PORTA") or tela_prompt.PORTA_PADRAO),
                                abrir_janelas=amb.get("SGS_ABRIR", "1") == "1")


def contexto():
    """Um Contexto por processo (sistemas, config, sites no ar, pasta atual do terminal, histórico)."""
    with _TRAVA:
        if not _CONTEXTO:
            ctx = contexto_do_ambiente()
            atexit.register(ctx.servidores.parar_todos)     # sites que a tela subiu caem junto com ela
            tela_prompt.marcar_tela_aberta(ctx.porta_tela)
            _CONTEXTO.append(ctx)
    return _CONTEXTO[0]


@csrf_exempt   # sem formulários do Django: a proteção é a da tela (POST só em JSON + Host 127.0.0.1)
def tela(request):
    r = tela_prompt.atender(contexto(), request.method, request.get_full_path(), request.headers,
                            lambda tamanho: request.body[:tamanho])
    resposta = HttpResponse(r.corpo, status=r.status)
    for chave, valor in r.cabecalhos:
        resposta[chave] = valor
    return resposta

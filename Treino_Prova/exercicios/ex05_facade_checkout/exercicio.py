"""ex05 — Facade. SEU ARQUIVO: construa a CheckoutFacade."""
from subsistemas import (Email, Estoque, NotaFiscal, PagamentoRecusado,  # noqa: F401
                         Pagamentos, finalizar_na_mao)


class CheckoutFacade:
    def __init__(self, estoque, pagamentos, nota, email):
        raise NotImplementedError   # TODO: segurar os 4 subsistemas

    def finalizar(self, cliente, itens, valor):
        raise NotImplementedError   # TODO: orquestrar na ordem certa (ver enunciado)

"""ex05 — GABARITO comentado: Facade de checkout."""
from subsistemas import (Email, Estoque, NotaFiscal, PagamentoRecusado,  # noqa: F401
                         Pagamentos, finalizar_na_mao)


class CheckoutFacade:
    """Um balcão único na frente de Estoque, Pagamentos, NotaFiscal e Email.

    - Segura os subsistemas (injetados no __init__ → testável com fakes).
    - finalizar() só ORQUESTRA: decide a ORDEM e quando ABORTAR; cada regra específica
      (como cobrar, como numerar a nota...) continua dentro do seu subsistema.
    """

    def __init__(self, estoque, pagamentos, nota, email):
        self._estoque = estoque
        self._pagamentos = pagamentos
        self._nota = nota
        self._email = email

    def finalizar(self, cliente, itens, valor):
        # 1) Verifica estoque ANTES de cobrar: não se cobra o que não se pode entregar.
        if not self._estoque.tem(itens):
            return {"ok": False, "motivo": "sem estoque"}

        # 2) Cobra. Se recusar, para aqui: estoque intacto, sem nota, sem e-mail.
        try:
            tx = self._pagamentos.cobrar(cliente, valor)
        except PagamentoRecusado:
            return {"ok": False, "motivo": "pagamento recusado"}

        # 3) 4) 5) Só depois do dinheiro garantido: baixa, emite e avisa.
        self._estoque.baixar(itens)
        numero = self._nota.emitir(cliente, valor)
        self._email.enviar(cliente, f"Pedido confirmado - nota {numero}")
        return {"ok": True, "tx": tx, "nota": numero}


# Para explicar na P3:
# - O cliente (view/API/app) deixou de conhecer os 4 subsistemas, a ordem e as regras de aborto:
#   chama só checkout.finalizar(...). Acoplamento cai de 4 dependências para 1.
# - 6º passo (pontos de fidelidade) = um subsistema novo + 1 linha aqui; nenhum cliente muda.
# - Viraria God object se eu passasse a calcular imposto, numerar nota ou montar o e-mail
#   AQUI DENTRO, em vez de delegar. A fachada também não proíbe usar Estoque direto (não é prisão).
# - Seria cerimônia se o checkout fosse 1 chamada usada num só lugar (uma função basta).

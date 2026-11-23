# MODO EXERCÍCIO — nucleo/extras.py: implemente cada método (a resolução está em gabarito/nucleo/extras.py).
# Rode `python -m pytest` para conferir; `ALVO=gabarito python -m pytest` mostra o gabarito passando.
"""
Loja Virtual — DECORATOR (Aula 10): somar opcionais empilhando embrulhos.

COMPONENTE       PedidoBase(item)  → preco() / descricao()
DECORADOR BASE   Adicional          → guarda o embrulhado e DELEGA
DECORADORES      Com…               → chamam o de DENTRO e somam a SUA parte
Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro: EMPILHA.
Quando NÃO usar: extras que só somam valor fixo → lista + sum() basta.
O @decorator do Python decora FUNÇÕES; este padrão decora OBJETOS.
"""

class PedidoBase:
    """COMPONENTE: expõe a Pedido pela interface preco()/descricao()."""

    def __init__(self, item):
        raise NotImplementedError('TODO: implemente __init__')

    def preco(self):
        raise NotImplementedError('TODO: implemente preco')

    def descricao(self):
        raise NotImplementedError('TODO: implemente descricao')

class Adicional:
    """DECORADOR BASE: mesma interface; guarda o objeto de dentro e, por padrão, só repassa."""

    def __init__(self, componente):
        raise NotImplementedError('TODO: implemente __init__')

    def preco(self):
        raise NotImplementedError('TODO: implemente preco')

    def descricao(self):
        raise NotImplementedError('TODO: implemente descricao')

class ComEmbrulho(Adicional):
    """Soma R$ 15.00 (embrulho para presente) ao que está DENTRO."""
    VALOR = 15.0

    def preco(self):
        raise NotImplementedError('TODO: implemente preco')

    def descricao(self):
        raise NotImplementedError('TODO: implemente descricao')

class ComCartao(Adicional):
    """Soma R$ 5.00 (cartão) ao que está DENTRO."""
    VALOR = 5.0

    def preco(self):
        raise NotImplementedError('TODO: implemente preco')

    def descricao(self):
        raise NotImplementedError('TODO: implemente descricao')

class ComEntregaExpressa(Adicional):
    """Soma R$ 25.00 (entrega expressa) ao que está DENTRO."""
    VALOR = 25.0

    def preco(self):
        raise NotImplementedError('TODO: implemente preco')

    def descricao(self):
        raise NotImplementedError('TODO: implemente descricao')

class ComCupom10(Adicional):
    """MUDA comportamento: multiplica TUDO o que está dentro por 0.9 — aqui a ORDEM importa."""
    FATOR = 0.9

    def preco(self):
        raise NotImplementedError('TODO: implemente preco')

    def descricao(self):
        raise NotImplementedError('TODO: implemente descricao')

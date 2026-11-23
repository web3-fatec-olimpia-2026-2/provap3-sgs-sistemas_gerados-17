class Pedido:
    def __init__(self, cliente, produto, quantidade, preco_unitario, observacao=""):
        self.cliente = cliente
        self.produto = produto
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.observacao = observacao

    @property
    def cliente(self):
        return self._cliente

    @cliente.setter
    def cliente(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("cliente é obrigatório (texto não vazio)")
        valor = valor.strip()
        self._cliente = valor

    @property
    def produto(self):
        return self._produto

    @produto.setter
    def produto(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("produto deve ser um número inteiro")
        if valor < 1:
            raise ValueError("produto deve ser no mínimo 1")
        self._produto = valor

    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("quantidade deve ser um número inteiro")
        if not 1 <= valor <= 50:
            raise ValueError("quantidade deve estar entre 1 e 50")
        self._quantidade = valor

    @property
    def preco_unitario(self):
        return self._preco_unitario

    @preco_unitario.setter
    def preco_unitario(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("preco_unitario deve ser um número")
        if valor < 0:
            raise ValueError("preco_unitario deve ser no mínimo 0")
        self._preco_unitario = valor

    @property
    def total(self):
        return round(self.quantidade * self.preco_unitario, 2)

    def __repr__(self):
        return f"Pedido(cliente={self.cliente!r}, total={self.total})"

class Ingresso:
    def __init__(self, espectador, sessao, quantidade, preco, poltrona=""):
        self.espectador = espectador
        self.sessao = sessao
        self.quantidade = quantidade
        self.preco = preco
        self.poltrona = poltrona

    @property
    def espectador(self):
        return self._espectador

    @espectador.setter
    def espectador(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("espectador é obrigatório (texto não vazio)")
        valor = valor.strip()
        self._espectador = valor

    @property
    def sessao(self):
        return self._sessao

    @sessao.setter
    def sessao(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("sessao deve ser um número inteiro")
        if valor < 1:
            raise ValueError("sessao deve ser no mínimo 1")
        self._sessao = valor

    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("quantidade deve ser um número inteiro")
        if not 1 <= valor <= 10:
            raise ValueError("quantidade deve estar entre 1 e 10")
        self._quantidade = valor

    @property
    def preco(self):
        return self._preco

    @preco.setter
    def preco(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("preco deve ser um número")
        if valor < 0:
            raise ValueError("preco deve ser no mínimo 0")
        self._preco = valor

    @property
    def total(self):
        return round(self.quantidade * self.preco, 2)

    def __repr__(self):
        return f"Ingresso(espectador={self.espectador!r}, total={self.total})"

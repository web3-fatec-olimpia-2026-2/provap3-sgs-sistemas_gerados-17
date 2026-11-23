"""
Loja Virtual — entidade principal `Pedido` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - cliente: texto obrigatório (não pode ser vazio)
  - produto: inteiro maior ou igual a 1
  - quantidade: inteiro entre 1 e 50
  - preco_unitario: número maior ou igual a 0
  - observacao: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class Pedido:
    """Pedido do sistema Loja Virtual: total = quantidade × preco_unitario."""

    def __init__(self, cliente, produto, quantidade, preco_unitario, observacao=""):
        self.cliente = cliente  # passa pelo setter → validado já na criação
        self.produto = produto  # passa pelo setter → validado já na criação
        self.quantidade = quantidade  # passa pelo setter → validado já na criação
        self.preco_unitario = preco_unitario  # passa pelo setter → validado já na criação
        self.observacao = observacao  # sem regra → atributo simples (antifachada)

    @property
    def cliente(self):
        """Getter: lê `cliente` (o valor de verdade fica no atributo interno `_cliente`)."""
        return self._cliente

    @cliente.setter
    def cliente(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — cliente: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("cliente é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._cliente = valor

    @property
    def produto(self):
        """Getter: lê `produto` (o valor de verdade fica no atributo interno `_produto`)."""
        return self._produto

    @produto.setter
    def produto(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — produto: inteiro maior ou igual a 1."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("produto deve ser um número inteiro")
        if valor < 1:
            raise ValueError("produto deve ser no mínimo 1")
        self._produto = valor

    @property
    def quantidade(self):
        """Getter: lê `quantidade` (o valor de verdade fica no atributo interno `_quantidade`)."""
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — quantidade: inteiro entre 1 e 50."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("quantidade deve ser um número inteiro")
        if not 1 <= valor <= 50:
            raise ValueError("quantidade deve estar entre 1 e 50")
        self._quantidade = valor

    @property
    def preco_unitario(self):
        """Getter: lê `preco_unitario` (o valor de verdade fica no atributo interno `_preco_unitario`)."""
        return self._preco_unitario

    @preco_unitario.setter
    def preco_unitario(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — preco_unitario: número maior ou igual a 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("preco_unitario deve ser um número")
        if valor < 0:
            raise ValueError("preco_unitario deve ser no mínimo 0")
        self._preco_unitario = valor

    @property
    def total(self):
        """Valor total = quantidade × preco_unitario (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em quantidade ou preco_unitario.
        """
        return round(self.quantidade * self.preco_unitario, 2)

    def __repr__(self):
        return f"Pedido(cliente={self.cliente!r}, total={self.total})"

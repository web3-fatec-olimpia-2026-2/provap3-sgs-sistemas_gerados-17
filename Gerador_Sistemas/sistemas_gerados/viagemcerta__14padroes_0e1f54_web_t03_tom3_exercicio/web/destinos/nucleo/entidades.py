"""
ViagemCerta — entidade principal `Destino` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - cliente: texto obrigatório (não pode ser vazio)
  - codigo: inteiro maior ou igual a 1
  - quantidade: inteiro entre 1 e 100
  - valor_unitario: número maior ou igual a 0
  - cidade: texto obrigatório (não pode ser vazio)
  - pais: texto obrigatório (não pode ser vazio)
  - observacao: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class Destino:
    """Destino do sistema ViagemCerta: total = quantidade × valor_unitario."""

    def __init__(self, cliente, codigo, quantidade, valor_unitario, cidade, pais, observacao=""):
        self.cliente = cliente  # passa pelo setter → validado já na criação
        self.codigo = codigo  # passa pelo setter → validado já na criação
        self.quantidade = quantidade  # passa pelo setter → validado já na criação
        self.valor_unitario = valor_unitario  # passa pelo setter → validado já na criação
        self.cidade = cidade  # passa pelo setter → validado já na criação
        self.pais = pais  # passa pelo setter → validado já na criação
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
    def codigo(self):
        """Getter: lê `codigo` (o valor de verdade fica no atributo interno `_codigo`)."""
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — codigo: inteiro maior ou igual a 1."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("codigo deve ser um número inteiro")
        if valor < 1:
            raise ValueError("codigo deve ser no mínimo 1")
        self._codigo = valor

    @property
    def quantidade(self):
        """Getter: lê `quantidade` (o valor de verdade fica no atributo interno `_quantidade`)."""
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — quantidade: inteiro entre 1 e 100."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("quantidade deve ser um número inteiro")
        if not 1 <= valor <= 100:
            raise ValueError("quantidade deve estar entre 1 e 100")
        self._quantidade = valor

    @property
    def valor_unitario(self):
        """Getter: lê `valor_unitario` (o valor de verdade fica no atributo interno `_valor_unitario`)."""
        return self._valor_unitario

    @valor_unitario.setter
    def valor_unitario(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — valor_unitario: número maior ou igual a 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("valor_unitario deve ser um número")
        if valor < 0:
            raise ValueError("valor_unitario deve ser no mínimo 0")
        self._valor_unitario = valor

    @property
    def cidade(self):
        """Getter: lê `cidade` (o valor de verdade fica no atributo interno `_cidade`)."""
        return self._cidade

    @cidade.setter
    def cidade(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — cidade: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("cidade é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._cidade = valor

    @property
    def pais(self):
        """Getter: lê `pais` (o valor de verdade fica no atributo interno `_pais`)."""
        return self._pais

    @pais.setter
    def pais(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — pais: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("pais é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._pais = valor

    @property
    def total(self):
        """Valor total = quantidade × valor_unitario (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em quantidade ou valor_unitario.
        """
        return round(self.quantidade * self.valor_unitario, 2)

    def __repr__(self):
        return f"Destino(cliente={self.cliente!r}, total={self.total})"

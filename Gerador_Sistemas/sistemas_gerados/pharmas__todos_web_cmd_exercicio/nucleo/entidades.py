"""
Pharmas — entidade principal `Pharm` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - cliente: texto obrigatório (não pode ser vazio)
  - codigo: inteiro maior ou igual a 1
  - quantidade: inteiro entre 1 e 100
  - valor_unitario: número maior ou igual a 0
  - produto: texto obrigatório (não pode ser vazio)
  - idade: inteiro entre 0 e 130
  - categoria: texto obrigatório (não pode ser vazio)
  - cosmeticos: texto obrigatório (não pode ser vazio)
  - medicamentos: texto obrigatório (não pode ser vazio)
  - observacao: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class Pharm:
    """Pharm do sistema Pharmas: total = quantidade × valor_unitario."""

    def __init__(self, cliente, codigo, quantidade, valor_unitario, produto, idade, categoria, cosmeticos, medicamentos, observacao=""):
        self.cliente = cliente  # passa pelo setter → validado já na criação
        self.codigo = codigo  # passa pelo setter → validado já na criação
        self.quantidade = quantidade  # passa pelo setter → validado já na criação
        self.valor_unitario = valor_unitario  # passa pelo setter → validado já na criação
        self.produto = produto  # passa pelo setter → validado já na criação
        self.idade = idade  # passa pelo setter → validado já na criação
        self.categoria = categoria  # passa pelo setter → validado já na criação
        self.cosmeticos = cosmeticos  # passa pelo setter → validado já na criação
        self.medicamentos = medicamentos  # passa pelo setter → validado já na criação
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
    def produto(self):
        """Getter: lê `produto` (o valor de verdade fica no atributo interno `_produto`)."""
        return self._produto

    @produto.setter
    def produto(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — produto: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("produto é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._produto = valor

    @property
    def idade(self):
        """Getter: lê `idade` (o valor de verdade fica no atributo interno `_idade`)."""
        return self._idade

    @idade.setter
    def idade(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — idade: inteiro entre 0 e 130."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("idade deve ser um número inteiro")
        if not 0 <= valor <= 130:
            raise ValueError("idade deve estar entre 0 e 130")
        self._idade = valor

    @property
    def categoria(self):
        """Getter: lê `categoria` (o valor de verdade fica no atributo interno `_categoria`)."""
        return self._categoria

    @categoria.setter
    def categoria(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — categoria: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("categoria é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._categoria = valor

    @property
    def cosmeticos(self):
        """Getter: lê `cosmeticos` (o valor de verdade fica no atributo interno `_cosmeticos`)."""
        return self._cosmeticos

    @cosmeticos.setter
    def cosmeticos(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — cosmeticos: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("cosmeticos é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._cosmeticos = valor

    @property
    def medicamentos(self):
        """Getter: lê `medicamentos` (o valor de verdade fica no atributo interno `_medicamentos`)."""
        return self._medicamentos

    @medicamentos.setter
    def medicamentos(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — medicamentos: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("medicamentos é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._medicamentos = valor

    @property
    def total(self):
        """Valor total = quantidade × valor_unitario (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em quantidade ou valor_unitario.
        """
        return round(self.quantidade * self.valor_unitario, 2)

    def __repr__(self):
        return f"Pharm(cliente={self.cliente!r}, total={self.total})"

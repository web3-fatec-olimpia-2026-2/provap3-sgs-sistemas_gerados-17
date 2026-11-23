"""
Hotel Resort — entidade principal `Reserva` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - hospede: texto obrigatório (não pode ser vazio)
  - quarto: inteiro maior ou igual a 1
  - diarias: inteiro entre 1 e 30
  - valor_diaria: número maior ou igual a 0
  - observacao: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class Reserva:
    """Reserva do sistema Hotel Resort: total = diarias × valor_diaria."""

    def __init__(self, hospede, quarto, diarias, valor_diaria, observacao=""):
        self.hospede = hospede  # passa pelo setter → validado já na criação
        self.quarto = quarto  # passa pelo setter → validado já na criação
        self.diarias = diarias  # passa pelo setter → validado já na criação
        self.valor_diaria = valor_diaria  # passa pelo setter → validado já na criação
        self.observacao = observacao  # sem regra → atributo simples (antifachada)

    @property
    def hospede(self):
        """Getter: lê `hospede` (o valor de verdade fica no atributo interno `_hospede`)."""
        return self._hospede

    @hospede.setter
    def hospede(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — hospede: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("hospede é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._hospede = valor

    @property
    def quarto(self):
        """Getter: lê `quarto` (o valor de verdade fica no atributo interno `_quarto`)."""
        return self._quarto

    @quarto.setter
    def quarto(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — quarto: inteiro maior ou igual a 1."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("quarto deve ser um número inteiro")
        if valor < 1:
            raise ValueError("quarto deve ser no mínimo 1")
        self._quarto = valor

    @property
    def diarias(self):
        """Getter: lê `diarias` (o valor de verdade fica no atributo interno `_diarias`)."""
        return self._diarias

    @diarias.setter
    def diarias(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — diarias: inteiro entre 1 e 30."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("diarias deve ser um número inteiro")
        if not 1 <= valor <= 30:
            raise ValueError("diarias deve estar entre 1 e 30")
        self._diarias = valor

    @property
    def valor_diaria(self):
        """Getter: lê `valor_diaria` (o valor de verdade fica no atributo interno `_valor_diaria`)."""
        return self._valor_diaria

    @valor_diaria.setter
    def valor_diaria(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — valor_diaria: número maior ou igual a 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("valor_diaria deve ser um número")
        if valor < 0:
            raise ValueError("valor_diaria deve ser no mínimo 0")
        self._valor_diaria = valor

    @property
    def total(self):
        """Valor total = diarias × valor_diaria (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em diarias ou valor_diaria.
        """
        return round(self.diarias * self.valor_diaria, 2)

    def __repr__(self):
        return f"Reserva(hospede={self.hospede!r}, total={self.total})"

"""
ViagemCerta — entidade principal `Viagcert` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - viajante: texto obrigatório (não pode ser vazio)
  - voo: inteiro maior ou igual a 1
  - noites: inteiro entre 1 e 30
  - valor_noite: número maior ou igual a 0
  - observacao: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class Viagcert:
    """Viagcert do sistema ViagemCerta: total = noites × valor_noite."""

    def __init__(self, viajante, voo, noites, valor_noite, observacao=""):
        self.viajante = viajante  # passa pelo setter → validado já na criação
        self.voo = voo  # passa pelo setter → validado já na criação
        self.noites = noites  # passa pelo setter → validado já na criação
        self.valor_noite = valor_noite  # passa pelo setter → validado já na criação
        self.observacao = observacao  # sem regra → atributo simples (antifachada)

    @property
    def viajante(self):
        """Getter: lê `viajante` (o valor de verdade fica no atributo interno `_viajante`)."""
        return self._viajante

    @viajante.setter
    def viajante(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — viajante: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("viajante é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._viajante = valor

    @property
    def voo(self):
        """Getter: lê `voo` (o valor de verdade fica no atributo interno `_voo`)."""
        return self._voo

    @voo.setter
    def voo(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — voo: inteiro maior ou igual a 1."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("voo deve ser um número inteiro")
        if valor < 1:
            raise ValueError("voo deve ser no mínimo 1")
        self._voo = valor

    @property
    def noites(self):
        """Getter: lê `noites` (o valor de verdade fica no atributo interno `_noites`)."""
        return self._noites

    @noites.setter
    def noites(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — noites: inteiro entre 1 e 30."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("noites deve ser um número inteiro")
        if not 1 <= valor <= 30:
            raise ValueError("noites deve estar entre 1 e 30")
        self._noites = valor

    @property
    def valor_noite(self):
        """Getter: lê `valor_noite` (o valor de verdade fica no atributo interno `_valor_noite`)."""
        return self._valor_noite

    @valor_noite.setter
    def valor_noite(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — valor_noite: número maior ou igual a 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("valor_noite deve ser um número")
        if valor < 0:
            raise ValueError("valor_noite deve ser no mínimo 0")
        self._valor_noite = valor

    @property
    def total(self):
        """Valor total = noites × valor_noite (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em noites ou valor_noite.
        """
        return round(self.noites * self.valor_noite, 2)

    def __repr__(self):
        return f"Viagcert(viajante={self.viajante!r}, total={self.total})"

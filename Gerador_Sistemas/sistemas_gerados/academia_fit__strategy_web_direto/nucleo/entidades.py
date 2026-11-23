"""
Academia Fit — entidade principal `Matricula` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - aluno: texto obrigatório (não pode ser vazio)
  - turma: inteiro maior ou igual a 1
  - meses: inteiro entre 1 e 24
  - mensalidade: número maior ou igual a 0
  - objetivo: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class Matricula:
    """Matricula do sistema Academia Fit: total = meses × mensalidade."""

    def __init__(self, aluno, turma, meses, mensalidade, objetivo=""):
        self.aluno = aluno  # passa pelo setter → validado já na criação
        self.turma = turma  # passa pelo setter → validado já na criação
        self.meses = meses  # passa pelo setter → validado já na criação
        self.mensalidade = mensalidade  # passa pelo setter → validado já na criação
        self.objetivo = objetivo  # sem regra → atributo simples (antifachada)

    @property
    def aluno(self):
        """Getter: lê `aluno` (o valor de verdade fica no atributo interno `_aluno`)."""
        return self._aluno

    @aluno.setter
    def aluno(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — aluno: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("aluno é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._aluno = valor

    @property
    def turma(self):
        """Getter: lê `turma` (o valor de verdade fica no atributo interno `_turma`)."""
        return self._turma

    @turma.setter
    def turma(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — turma: inteiro maior ou igual a 1."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("turma deve ser um número inteiro")
        if valor < 1:
            raise ValueError("turma deve ser no mínimo 1")
        self._turma = valor

    @property
    def meses(self):
        """Getter: lê `meses` (o valor de verdade fica no atributo interno `_meses`)."""
        return self._meses

    @meses.setter
    def meses(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — meses: inteiro entre 1 e 24."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("meses deve ser um número inteiro")
        if not 1 <= valor <= 24:
            raise ValueError("meses deve estar entre 1 e 24")
        self._meses = valor

    @property
    def mensalidade(self):
        """Getter: lê `mensalidade` (o valor de verdade fica no atributo interno `_mensalidade`)."""
        return self._mensalidade

    @mensalidade.setter
    def mensalidade(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — mensalidade: número maior ou igual a 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("mensalidade deve ser um número")
        if valor < 0:
            raise ValueError("mensalidade deve ser no mínimo 0")
        self._mensalidade = valor

    @property
    def total(self):
        """Valor total = meses × mensalidade (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em meses ou mensalidade.
        """
        return round(self.meses * self.mensalidade, 2)

    def __repr__(self):
        return f"Matricula(aluno={self.aluno!r}, total={self.total})"

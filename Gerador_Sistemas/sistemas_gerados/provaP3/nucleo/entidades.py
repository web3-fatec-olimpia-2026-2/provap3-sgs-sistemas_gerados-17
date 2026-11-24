"""
Cooperativa Citrícola — entidade principal `LoteCitros` (ENCAPSULAMENTO com @property).

Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
  - cooperado: texto obrigatório (não pode ser vazio)
  - talhao: inteiro maior ou igual a 1
  - caixas: inteiro entre 1 e 5000
  - preco_caixa: número maior ou igual a 0
  - cidade: texto obrigatório (não pode ser vazio)
  - cpf_cnpj_provap3: texto obrigatório (não pode ser vazio)
  - observacao: texto livre, sem regra (atributo simples — proteger seria cerimônia)

Ideias das Aulas 02 e 03:
  * o objeto controla o acesso ao próprio estado (encapsulamento);
  * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
  * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
  * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
  * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
  * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
"""


class LoteCitros:
    """LoteCitros do sistema Cooperativa Citrícola: total = caixas × preco_caixa."""

    def __init__(self, cooperado, talhao, caixas, preco_caixa, cidade, cpf_cnpj_provap3, observacao=""):
        self.cooperado = cooperado  # passa pelo setter → validado já na criação
        self.talhao = talhao  # passa pelo setter → validado já na criação
        self.caixas = caixas  # passa pelo setter → validado já na criação
        self.preco_caixa = preco_caixa  # passa pelo setter → validado já na criação
        self.cidade = cidade  # passa pelo setter → validado já na criação
        self.cpf_cnpj_provap3 = cpf_cnpj_provap3  # passa pelo setter → validado já na criação
        self.observacao = observacao  # sem regra → atributo simples (antifachada)

    @property
    def cooperado(self):
        """Getter: lê `cooperado` (o valor de verdade fica no atributo interno `_cooperado`)."""
        return self._cooperado

    @cooperado.setter
    def cooperado(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — cooperado: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("cooperado é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._cooperado = valor

    @property
    def talhao(self):
        """Getter: lê `talhao` (o valor de verdade fica no atributo interno `_talhao`)."""
        return self._talhao

    @talhao.setter
    def talhao(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — talhao: inteiro maior ou igual a 1."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("talhao deve ser um número inteiro")
        if valor < 1:
            raise ValueError("talhao deve ser no mínimo 1")
        self._talhao = valor

    @property
    def caixas(self):
        """Getter: lê `caixas` (o valor de verdade fica no atributo interno `_caixas`)."""
        return self._caixas

    @caixas.setter
    def caixas(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — caixas: inteiro entre 1 e 5000."""
        # bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("caixas deve ser um número inteiro")
        if not 1 <= valor <= 5000:
            raise ValueError("caixas deve estar entre 1 e 5000")
        self._caixas = valor

    @property
    def preco_caixa(self):
        """Getter: lê `preco_caixa` (o valor de verdade fica no atributo interno `_preco_caixa`)."""
        return self._preco_caixa

    @preco_caixa.setter
    def preco_caixa(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — preco_caixa: número maior ou igual a 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("preco_caixa deve ser um número")
        if valor < 0:
            raise ValueError("preco_caixa deve ser no mínimo 0")
        self._preco_caixa = valor

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
    def cpf_cnpj_provap3(self):
        """Getter: lê `cpf_cnpj_provap3` (o valor de verdade fica no atributo interno `_cpf_cnpj_provap3`)."""
        return self._cpf_cnpj_provap3

    @cpf_cnpj_provap3.setter
    def cpf_cnpj_provap3(self, valor):
        """Setter (a "fechadura"): só grava se a regra for respeitada — cpf_cnpj_provap3: texto obrigatório (não pode ser vazio)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("cpf_cnpj_provap3 é obrigatório (texto não vazio)")
        valor = valor.strip()  # guarda sem espaços nas pontas
        self._cpf_cnpj_provap3 = valor

    @property
    def total(self):
        """Valor total = caixas × preco_caixa (2 casas).

        Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
        Calculada na hora, acompanha qualquer mudança em caixas ou preco_caixa.
        """
        return round(self.caixas * self.preco_caixa, 2)

    def __repr__(self):
        return f"LoteCitros(cooperado={self.cooperado!r}, total={self.total})"

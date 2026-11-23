"""
Pharmas — BUILDER (GoF · criação): montar a Pharm PASSO A PASSO, com nomes.

ANTES (nucleo/antes_construtor.py): nova_pharm_antiga(...) com todos os argumentos na ORDEM —
dois números trocados de lugar passam despercebidos e não há receitas prontas.
DEPOIS (aqui):
  * PharmBuilder tem um com_<campo>() por atributo; cada um devolve o próprio builder
    (interface FLUENTE: b.com_x(...).com_y(...));
  * construir() confere o que falta e só então cria a Pharm (os setters validam cada valor);
  * DiretorDePharm guarda "receitas" de montagem que se repetem.
Quando NÃO usar: poucos campos — em Python, argumentos NOMEADOS já resolvem a ordem.
"""
from nucleo.entidades import Pharm

OBRIGATORIOS = ['cliente', 'codigo', 'quantidade', 'valor_unitario', 'produto', 'idade', 'categoria', 'cosmeticos', 'medicamentos']


class PharmBuilder:
    """BUILDER: junta os valores aos poucos e cria a Pharm no final."""

    def __init__(self):
        self._valores = {}

    def com_cliente(self, valor):
        """Informa cliente e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["cliente"] = valor
        return self


    def com_codigo(self, valor):
        """Informa codigo e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["codigo"] = valor
        return self


    def com_quantidade(self, valor):
        """Informa quantidade e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["quantidade"] = valor
        return self


    def com_valor_unitario(self, valor):
        """Informa valor_unitario e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["valor_unitario"] = valor
        return self


    def com_produto(self, valor):
        """Informa produto e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["produto"] = valor
        return self


    def com_idade(self, valor):
        """Informa idade e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["idade"] = valor
        return self


    def com_categoria(self, valor):
        """Informa categoria e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["categoria"] = valor
        return self


    def com_cosmeticos(self, valor):
        """Informa cosmeticos e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["cosmeticos"] = valor
        return self


    def com_medicamentos(self, valor):
        """Informa medicamentos e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["medicamentos"] = valor
        return self


    def com_observacao(self, valor):
        """Informa observacao e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["observacao"] = valor
        return self

    def faltando(self):
        """Campos obrigatórios que ainda não foram informados."""
        return [campo for campo in OBRIGATORIOS if campo not in self._valores]

    def construir(self):
        """Cria a Pharm. Faltou campo → ValueError dizendo QUAL; valor inválido → o setter barra."""
        falta = self.faltando()
        if falta:
            raise ValueError(f"faltam campos: {', '.join(falta)}")
        return Pharm(**self._valores)


class DiretorDePharm:
    """DIRETOR: receitas de montagem que se repetem (o passo a passo fica num lugar só)."""

    PADRAO = {'codigo': 101, 'quantidade': 2, 'valor_unitario': 100.0, 'produto': 'Produto 1', 'idade': 0, 'categoria': 'Categoria 1', 'cosmeticos': 'Cosmeticos 1', 'medicamentos': 'Medicamentos 1'}

    def basico(self, cliente):
        builder = PharmBuilder().com_cliente(cliente)
        for campo, valor in self.PADRAO.items():
            getattr(builder, f"com_{campo}")(valor)
        return builder.construir()

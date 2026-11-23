"""
ViagemCerta — BUILDER (GoF · criação): montar a Destino PASSO A PASSO, com nomes.

ANTES (nucleo/antes_construtor.py): nova_destino_antiga(...) com todos os argumentos na ORDEM —
dois números trocados de lugar passam despercebidos e não há receitas prontas.
DEPOIS (aqui):
  * DestinoBuilder tem um com_<campo>() por atributo; cada um devolve o próprio builder
    (interface FLUENTE: b.com_x(...).com_y(...));
  * construir() confere o que falta e só então cria a Destino (os setters validam cada valor);
  * DiretorDeDestino guarda "receitas" de montagem que se repetem.
Quando NÃO usar: poucos campos — em Python, argumentos NOMEADOS já resolvem a ordem.
"""
from destinos.nucleo.entidades import Destino

OBRIGATORIOS = ['cliente', 'codigo', 'quantidade', 'valor_unitario', 'cidade', 'pais']


class DestinoBuilder:
    """BUILDER: junta os valores aos poucos e cria a Destino no final."""

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


    def com_cidade(self, valor):
        """Informa cidade e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["cidade"] = valor
        return self


    def com_pais(self, valor):
        """Informa pais e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["pais"] = valor
        return self


    def com_observacao(self, valor):
        """Informa observacao e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["observacao"] = valor
        return self

    def faltando(self):
        """Campos obrigatórios que ainda não foram informados."""
        return [campo for campo in OBRIGATORIOS if campo not in self._valores]

    def construir(self):
        """Cria a Destino. Faltou campo → ValueError dizendo QUAL; valor inválido → o setter barra."""
        falta = self.faltando()
        if falta:
            raise ValueError(f"faltam campos: {', '.join(falta)}")
        return Destino(**self._valores)


class DiretorDeDestino:
    """DIRETOR: receitas de montagem que se repetem (o passo a passo fica num lugar só)."""

    PADRAO = {'codigo': 101, 'quantidade': 2, 'valor_unitario': 100.0, 'cidade': 'Cidade 1', 'pais': 'Pais 1'}

    def basico(self, cliente):
        builder = DestinoBuilder().com_cliente(cliente)
        for campo, valor in self.PADRAO.items():
            getattr(builder, f"com_{campo}")(valor)
        return builder.construir()

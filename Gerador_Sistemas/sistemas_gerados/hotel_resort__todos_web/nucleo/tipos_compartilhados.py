"""
Hotel Resort — FLYWEIGHT (GoF · estrutural): COMPARTILHAR o que se repete em milhares de objetos.

ANTES (nucleo/antes_tipos_compartilhados.py): cada registro criava o SEU objeto de tipo de hóspede
(nome + fator) — 10 000 registros = 10 000 objetos iguais na memória.
DEPOIS (aqui):
  * TipoCompartilhado guarda só o estado INTRÍNSECO (nome, fator): igual para todos e IMUTÁVEL;
  * FabricaDeTipos.obter(chave) devolve SEMPRE o mesmo objeto para a mesma chave (cache);
  * o estado EXTRÍNSECO (a Reserva de cada registro) entra por parâmetro: tipo.valor(item).
Quando NÃO usar: poucos objetos, ou objetos que mudam — o ganho de memória não paga a complexidade.
"""

TIPOS = {"comum": ("Comum", 1.0), "fidelidade": ("Fidelidade", 0.9), "parceiro": ("Parceiro", 0.8), "vip": ("VIP", 0.5)}  # chave → (nome, fator)


class TipoCompartilhado:
    """FLYWEIGHT: estado intrínseco (nome, fator), compartilhado e IMUTÁVEL."""

    __slots__ = ("_nome", "_fator")  # sem __dict__: cada flyweight ocupa o mínimo

    def __init__(self, nome, fator):
        object.__setattr__(self, "_nome", nome)
        object.__setattr__(self, "_fator", fator)

    def __setattr__(self, campo, valor):
        raise AttributeError("flyweight é imutável: ele é compartilhado por todos")

    @property
    def nome(self):
        return self._nome

    @property
    def fator(self):
        return self._fator

    def valor(self, item):
        """Estado EXTRÍNSECO (o item) chega por parâmetro — o flyweight não guarda nada dele."""
        return round(item.total * self._fator, 2)


class FabricaDeTipos:
    """Entrega flyweights: cria na primeira vez, depois devolve o MESMO objeto."""

    def __init__(self):
        self._cache = {}

    def obter(self, chave):
        if chave not in self._cache:
            nome, fator = TIPOS[chave]  # KeyError se a chave não existir
            self._cache[chave] = TipoCompartilhado(nome, fator)
        return self._cache[chave]

    def quantidade(self):
        """Quantos flyweights existem de verdade na memória."""
        return len(self._cache)


class Registro:
    """Um lançamento: a Reserva (extrínseco) + uma REFERÊNCIA ao tipo compartilhado."""

    def __init__(self, item, tipo):
        self.item = item
        self.tipo = tipo

    def valor(self):
        return self.tipo.valor(self.item)

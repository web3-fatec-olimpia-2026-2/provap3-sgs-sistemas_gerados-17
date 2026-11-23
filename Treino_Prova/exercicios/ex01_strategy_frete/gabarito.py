"""ex01 — GABARITO comentado: Strategy no frete."""


# --- o smell, mantido igual (referência para provar que a refatoração não mudou nada) ---
class PedidoAntigo:
    def __init__(self, peso_kg, tipo_frete):
        self.peso_kg = peso_kg
        self.tipo_frete = tipo_frete

    def frete(self):
        if self.tipo_frete == "pac":
            return 10 + 2 * self.peso_kg
        elif self.tipo_frete == "sedex":
            return 20 + 4 * self.peso_kg
        elif self.tipo_frete == "retirada":
            return 0
        else:
            raise ValueError("tipo de frete desconhecido")


# --- ESTRATÉGIAS: uma família de algoritmos intercambiáveis, todas com calcular(peso_kg) ---
class FretePAC:
    TAXA_FIXA, POR_KG = 10, 2          # constantes nomeadas: a regra fica legível e num lugar só

    def calcular(self, peso_kg):
        return self.TAXA_FIXA + self.POR_KG * peso_kg


class FreteSedex:
    TAXA_FIXA, POR_KG = 20, 4

    def calcular(self, peso_kg):
        return self.TAXA_FIXA + self.POR_KG * peso_kg


class RetiradaNaLoja:
    def calcular(self, peso_kg):
        return 0                        # o peso não importa, mas a interface é a mesma


# --- CONTEXTO: recebe a estratégia (composição) e DELEGA — nenhum if ---
class Pedido:
    def __init__(self, peso_kg, frete):
        self.peso_kg = peso_kg
        self.frete_escolhido = frete    # TEM-UMA estratégia de frete

    def frete(self):
        # "Calcule isso para mim": o Pedido não sabe QUAL frete é, só que ele sabe calcular.
        return self.frete_escolhido.calcular(self.peso_kg)


# --- ESTRATÉGIA NOVA: o Pedido acima NÃO foi alterado (OCP) ---
class FreteMotoboy:
    VALOR, PESO_MAXIMO = 15, 5

    def calcular(self, peso_kg):
        # A regra própria (limite de peso) mora na própria estratégia, não no Pedido.
        if peso_kg > self.PESO_MAXIMO:
            raise ValueError("motoboy até 5 kg")
        return self.VALOR


# Para explicar na P3:
# - O Pedido depende só da interface calcular(peso_kg); qualquer frete novo é uma classe nova
#   → aberto para estender, fechado para modificar.
# - Seria exagero se a loja tivesse UM frete fixo que nunca muda: uma constante resolveria.
# - Em Python a estratégia poderia ser uma função: Pedido(3, lambda kg: 0) funcionaria se
#   frete() chamasse self.frete_escolhido(peso). Classes deixam o padrão explícito.

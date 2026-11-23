# LAB Aula 05 — Strategy (RESOLVIDO)
#
# Refatoração do if/elif de tarifa para o padrão STRATEGY:
#   - cada POLÍTICA de tarifa virou uma classe com o mesmo método aplicar(base);
#   - a Reserva (o "contexto") RECEBE uma estratégia e DELEGA o cálculo a ela.
# Resultado: tarifa nova = classe nova; a Reserva não muda (aberta p/ estender,
# fechada p/ modificar — o OCP da Aula 06).


# ---------------------------------------------------------------------------
# As ESTRATÉGIAS: uma família de algoritmos intercambiáveis.
# Todas respondem a aplicar(base) → polimorfismo (Aula 04) organizado num padrão.
# ---------------------------------------------------------------------------
class TarifaComum:
    def aplicar(self, base):
        return base                 # sem desconto


class TarifaFidelidade:
    def aplicar(self, base):
        return base * 0.90          # 10% off


class TarifaParceiro:
    def aplicar(self, base):
        return base * 0.80          # 20% off


# Passo 4 do roteiro: política NOVA, criada SEM tocar na classe Reserva.
class TarifaVIP:
    def aplicar(self, base):
        return base * 0.50          # 50% off


# ---------------------------------------------------------------------------
# O CONTEXTO: usa uma estratégia sem saber qual é.
# ---------------------------------------------------------------------------
class Reserva:
    def __init__(self, diarias, valor_diaria, tarifa):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        # Recebe um OBJETO-estratégia (não mais um texto "comum"/"parceiro").
        # Isso é COMPOSIÇÃO: a Reserva TEM-UMA tarifa.
        self.tarifa = tarifa

    def total(self):
        base = self.diarias * self.valor_diaria
        # DELEGA: "calcule isso para mim". Nenhum if — quem sabe a regra é a estratégia.
        return self.tarifa.aplicar(base)


# ---------------------------------------------------------------------------
# Variante "pythônica" (nota do roteiro / GIRIDHAR): em Python funções são objetos,
# então a estratégia pode ser só uma FUNÇÃO. Usamos classes no lab por clareza.
# ---------------------------------------------------------------------------
def tarifa_estudante(base):
    return base * 0.85


class ReservaComFuncao:
    """Mesma ideia, mas a estratégia é qualquer 'chamável' f(base) -> valor."""

    def __init__(self, diarias, valor_diaria, tarifa):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        self.tarifa = tarifa

    def total(self):
        return self.tarifa(self.diarias * self.valor_diaria)

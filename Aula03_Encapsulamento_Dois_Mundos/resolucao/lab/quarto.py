"""
ILP-037 — Aula 03 — Laboratório "Proteja a capacidade" (RESOLVIDO).

Ponto de partida: a diária já vinha protegida; a capacidade era guardada direto,
aceitando 0 ou negativo. Tarefa: proteger a capacidade com a regra "mínimo 1".
Desafio: property calculada `receita_maxima` (só leitura).

Extra (Parte 4 da aula — "a porta para herança"): classe Suite(Quarto) e um
exemplo de composição (Quarto TEM-UM Frigobar).
"""


class Quarto:
    def __init__(self, numero, diaria, capacidade):
        self.numero = numero            # sem regra nesta aula → atributo simples
        self.diaria = diaria            # passa pelo setter de diaria (valida)
        self.capacidade = capacidade    # AGORA também passa por um setter (valida)

    # --- diaria: já vinha protegida (o modelo a seguir) -------------------
    @property
    def diaria(self):
        return self._diaria

    @diaria.setter
    def diaria(self, valor):
        # Regra da DIÁRIA: barra só o negativo. Diária 0 (cortesia) é aceitável.
        if valor < 0:
            raise ValueError("diaria nao pode ser negativa")
        self._diaria = valor

    # --- capacidade: MINHA TAREFA -----------------------------------------
    @property
    def capacidade(self):
        """Getter: lê o valor guardado no atributo interno _capacidade."""
        return self._capacidade

    @capacidade.setter
    def capacidade(self, valor):
        # Regra da CAPACIDADE: "< 1" e não "< 0", porque ZERO também é inválido:
        # não existe quarto para zero pessoas. A regra vem do negócio, não do molde.
        if valor < 1:
            raise ValueError("capacidade minima e 1")
        self._capacidade = valor

    # --- desafio: dado calculado ------------------------------------------
    @property
    def receita_maxima(self):
        """Máximo que o quarto rende por noite = diaria × capacidade.

        Sem setter → só leitura. Nunca é guardado: se a diária ou a capacidade
        mudarem, a receita acompanha sozinha (a "conta do check-out" da Aula 02).
        """
        return self.diaria * self.capacidade


# ---------------------------------------------------------------------------
# Parte 4 da aula: herança (É-UM) × composição (TEM-UM)
# ---------------------------------------------------------------------------

class Suite(Quarto):
    """A suíte É-UM quarto, com algo a mais (tem sala). → HERANÇA."""

    def __init__(self, numero, diaria, capacidade, tem_sala=True):
        # super().__init__ chama o construtor do Quarto: a suíte ganha numero,
        # diaria e capacidade — inclusive as VALIDAÇÕES — sem copiar código.
        super().__init__(numero, diaria, capacidade)
        self.tem_sala = tem_sala        # só o que é dela


class Frigobar:
    """Um objeto separado, que o quarto CONTÉM."""

    def __init__(self, itens=None):
        self.itens = list(itens or [])


class QuartoComFrigobar(Quarto):
    """O quarto TEM-UM frigobar → COMPOSIÇÃO (atributo que guarda outro objeto).

    Teste do ouvido: "o quarto é um frigobar" soa errado → não é herança.
    """

    def __init__(self, numero, diaria, capacidade):
        super().__init__(numero, diaria, capacidade)
        self.frigobar = Frigobar(["água", "refrigerante"])

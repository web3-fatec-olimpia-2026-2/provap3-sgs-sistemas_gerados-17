"""
ILP-037 Tecnicas de Programacao II - Aula 03 - Laboratorio
Classe Quarto (Resort de Olimpia).

ESTE E O SEU PONTO DE PARTIDA.

A diaria JA esta protegida com @property e setter (leia e entenda).
A capacidade ja e recebida e guardada, mas AINDA NAO ESTA PROTEGIDA:
hoje ela aceita qualquer valor, ate zero ou negativo.

A sua tarefa (siga o ROTEIRO.md): proteger a capacidade do mesmo jeito
que a diaria, com a regra "capacidade minima e 1".

Nao apague o que ja existe. Voce vai TRANSFORMAR a capacidade publica
numa @property com setter.
"""


class Quarto:
    def __init__(self, numero, diaria, capacidade):
        self.numero = numero
        self.diaria = diaria             # usa o setter (protegido)
        self.capacidade = capacidade     # HOJE: guarda direto, sem proteger

    # --- diaria: JA PROTEGIDA (seu modelo a seguir) --------------------
    @property
    def diaria(self):
        return self._diaria

    @diaria.setter
    def diaria(self, valor):
        if valor < 0:
            raise ValueError("diaria nao pode ser negativa")
        self._diaria = valor

    # -------------------------------------------------------------------
    # SUA TAREFA (Passo 3 do roteiro):
    # Transforme a capacidade numa @property protegida.
    # Regra: capacidade minima e 1 (nao existe quarto para zero pessoas).
    #
    # Espelhe a diaria acima:
    #   - uma @property capacidade que retorna self._capacidade
    #   - um @capacidade.setter que, se valor < 1, levanta
    #     ValueError("capacidade minima e 1"); senao, guarda em self._capacidade
    #
    # Quando terminar, os 4 testes ficam verdes.
    # -------------------------------------------------------------------

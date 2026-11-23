"""
Painel de quartos do Resort de Olimpia.

>>> ESTE ARQUIVO TEM UM CHEIRO (code smell). <<<
A funcao tela_quartos() faz tudo ao mesmo tempo:
  - decide a REGRA DE NEGOCIO (quarto ocupado nao pode reservar, conta livres)
  - decide a APRESENTACAO (texto do status, rotulo do botao, "R$", LOTADO)
  - MONTA A TELA (junta as linhas numa string)

Resultado: para testar a regra "quando esta lotado?", o teste precisa
ler a string da tela e procurar a palavra "LOTADO" dentro dela.
A regra so existe DENTRO do desenho da tela. Nao da para testar a decisao
sem renderizar o texto.

Seu trabalho no laboratorio: separar as tres responsabilidades usando o
padrao MVVM. A camada ViewModel prepara os dados JA PRONTOS para a tela,
sem saber que e uma tela. A tela so le o que o ViewModel preparou.

As classes QuartoViewModel e PainelQuartosVM abaixo estao VAZIAS de proposito.
Os testes batem nelas e ficam VERMELHOS. Voce vai move a logica para ca.
"""

# ---------------------------------------------------------------------------
# DADOS (viriam do banco em Web III; aqui sao fixos para o laboratorio)
# ---------------------------------------------------------------------------
QUARTOS = [
    {"numero": 101, "categoria": "comum", "diaria": 200.0, "ocupado": False},
    {"numero": 201, "categoria": "suite", "diaria": 500.0, "ocupado": True},
    {"numero": 301, "categoria": "presidencial", "diaria": 1200.0, "ocupado": False},
]


# ---------------------------------------------------------------------------
# O SMELL: uma funcao de TELA que decide regra de negocio no meio do caminho
# ---------------------------------------------------------------------------
def tela_quartos(quartos):
    linhas = []
    livres = 0
    for q in quartos:
        if q["ocupado"]:
            status = "INDISPONIVEL"
            botao = "(ocupado)"
        else:
            status = "livre"
            botao = "Reservar"
            livres += 1
        preco = f"R$ {q['diaria']:.2f}"
        linhas.append(
            f"Quarto {q['numero']} [{q['categoria']}] - {preco} - {status} - {botao}"
        )
    if livres:
        rodape = f"{livres} quarto(s) livre(s)"
    else:
        rodape = "LOTADO - nenhum quarto livre"
    return "\n".join(linhas) + "\n" + rodape


# ---------------------------------------------------------------------------
# A CAMADA QUE VOCE VAI CONSTRUIR (ViewModel) -- hoje esta vazia (VERMELHO)
# ---------------------------------------------------------------------------
class QuartoViewModel:
    """
    Prepara UM quarto para exibicao. Nao sabe o que e uma tela:
    so entrega texto pronto (status, botao, preco) e a decisao (disponivel).

    TODO (voce): receber o dict do quarto e preencher os atributos abaixo.
    """

    def __init__(self, quarto):
        self.numero = None          # TODO
        self.categoria = None       # TODO
        self.disponivel = None      # TODO: True/False a partir de 'ocupado'
        self.status_label = None    # TODO: "livre" ou "INDISPONIVEL"
        self.botao_label = None     # TODO: "Reservar" ou "(ocupado)"
        self.preco_formatado = None # TODO: "R$ 200.00"


class PainelQuartosVM:
    """
    Prepara o PAINEL inteiro: a lista de QuartoViewModel, a contagem de
    livres e o texto do rodape. Continua sem saber desenhar a tela.

    TODO (voce): montar self.itens, self.livres e self.rodape.
    """

    def __init__(self, quartos):
        self.itens = []     # TODO: lista de QuartoViewModel
        self.livres = None  # TODO: quantos disponiveis
        self.rodape = None  # TODO: "N quarto(s) livre(s)" ou "LOTADO ..."

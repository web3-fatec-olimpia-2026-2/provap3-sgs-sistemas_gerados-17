"""
DOJO (Randori) - MVVM de novo, agora no painel de CHECK-IN do dia.
Resort de Olimpia.

Na Aula 08 o MVVM apareceu no painel de quartos. Hoje, no Coding Dojo, a gente
REPETE o movimento num cenario novo - a recepcao de manha, com as reservas que
fazem check-in hoje. Se o movimento ja esta no dedo, voce faz rapido.

>>> O MESMO CHEIRO DE SEMPRE <<<
A funcao painel_checkin() decide a APRESENTACAO no meio do laco (texto do status,
cor do selo, rotulo do botao) E a REGRA (so quem esta 'confirmada' e ja pagou pode
fazer check-in). Para testar "quem pode fazer check-in?" sou obrigado a ler a tela.

>>> O MOVIMENTO DO DOJO <<<
Extrair um CheckinViewModel que prepara UMA reserva para a tela, sem saber desenhar.
A classe esta vazia de proposito: os testes batem nela e ficam VERMELHOS.
"""

# dados crus (viriam do banco; aqui fixos para o kata)
RESERVAS = [
    {"hospede": "Ana",   "quarto": 101, "status": "confirmada", "pago": True},
    {"hospede": "Bruno", "quarto": 201, "status": "confirmada", "pago": False},
    {"hospede": "Carla", "quarto": 301, "status": "pendente",   "pago": False},
]


# ----- O SMELL: a tela decide apresentacao E regra -------------------------
def painel_checkin(reservas):
    linhas = []
    for r in reservas:
        if r["status"] == "confirmada" and r["pago"]:
            selo = "VERDE"; acao = "Fazer check-in"
        elif r["status"] == "confirmada" and not r["pago"]:
            selo = "AMARELO"; acao = "Aguardando pagamento"
        else:
            selo = "CINZA"; acao = "Nao disponivel"
        linhas.append(f"{r['hospede']} (q{r['quarto']}) [{selo}] - {acao}")
    return "\n".join(linhas)


# ----- A CAMADA QUE VOCE VAI CONSTRUIR (vazia = VERMELHO) -------------------
class CheckinViewModel:
    """
    Prepara UMA reserva para a tela. Nao sabe desenhar.

    TODO (dojo):
      - pode_checkin : True so se status 'confirmada' E pago
      - selo         : "VERDE" (pode), "AMARELO" (confirmada sem pagar), "CINZA" (resto)
      - acao_label   : "Fazer check-in" / "Aguardando pagamento" / "Nao disponivel"
      - hospede, quarto : preservados
    """

    def __init__(self, reserva):
        self.hospede = None       # TODO
        self.quarto = None        # TODO
        self.pode_checkin = None  # TODO
        self.selo = None          # TODO
        self.acao_label = None    # TODO

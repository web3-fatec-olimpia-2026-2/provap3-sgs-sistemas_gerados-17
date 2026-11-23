"""
Aula 09 — DOJO (Randori): MVVM de novo, no painel de CHECK-IN do dia (RESOLVIDO).

Mesmo cheiro da Aula 08: a tela painel_checkin() decidia o SELO, o RÓTULO do botão
e a REGRA "quem pode fazer check-in" no meio do laço.
Movimento: levar a decisão para um CheckinViewModel; a tela só lê.
"""

RESERVAS = [
    {"hospede": "Ana",   "quarto": 101, "status": "confirmada", "pago": True},
    {"hospede": "Bruno", "quarto": 201, "status": "confirmada", "pago": False},
    {"hospede": "Carla", "quarto": 301, "status": "pendente",   "pago": False},
]


# ----- ANTES (o smell) — mantido para provar que a tela final não mudou -----
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


# ----- VIEWMODEL -----------------------------------------------------------
class CheckinViewModel:
    """Prepara UMA reserva para a tela. Não sabe desenhar."""

    def __init__(self, reserva):
        self.hospede = reserva["hospede"]           # preservados
        self.quarto = reserva["quarto"]
        # Estado derivado: a REGRA de quem pode fazer check-in, num lugar só.
        # (Se ela ficasse mais complexa — p.ex. depender de horário — iria para um Service;
        #  o ViewModel continuaria só traduzindo o resultado em selo/rótulo.)
        self.pode_checkin = reserva["status"] == "confirmada" and reserva["pago"]

        # Decisão de exibição: selo e rótulo do botão.
        if self.pode_checkin:
            self.selo, self.acao_label = "VERDE", "Fazer check-in"
        elif reserva["status"] == "confirmada":     # confirmada, mas sem pagar
            self.selo, self.acao_label = "AMARELO", "Aguardando pagamento"
        else:                                       # pendente (ou qualquer outro status)
            self.selo, self.acao_label = "CINZA", "Nao disponivel"


# ----- VIEW "burra": só costura o que o ViewModel preparou ------------------
def painel_checkin_mvvm(reservas):
    itens = [CheckinViewModel(r) for r in reservas]
    return "\n".join(f"{i.hospede} (q{i.quarto}) [{i.selo}] - {i.acao_label}" for i in itens)


# Reflexão do guia do Dojo: "e se entrar o status 'em análise'?" → mexe-se SÓ no
# CheckinViewModel (cai no CINZA hoje); a tela nem fica sabendo.

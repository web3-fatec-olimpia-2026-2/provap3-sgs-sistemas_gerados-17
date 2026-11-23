"""SOLUCAO DO PROFESSOR - Dojo MVVM (CheckinViewModel). Nao distribuir antes."""
class CheckinViewModel:
    def __init__(self, reserva):
        self.hospede = reserva["hospede"]
        self.quarto = reserva["quarto"]
        self.pode_checkin = reserva["status"] == "confirmada" and reserva["pago"]
        if self.pode_checkin:
            self.selo = "VERDE"; self.acao_label = "Fazer check-in"
        elif reserva["status"] == "confirmada":
            self.selo = "AMARELO"; self.acao_label = "Aguardando pagamento"
        else:
            self.selo = "CINZA"; self.acao_label = "Nao disponivel"

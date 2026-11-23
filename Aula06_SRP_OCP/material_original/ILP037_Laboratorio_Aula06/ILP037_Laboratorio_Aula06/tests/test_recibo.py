import pytest
from recibo import Reserva

# Este teste fixa o comportamento atual (a rede de seguranca).
# Ele usa so a Reserva - vale antes e depois, porque total() continua nela.
def test_total():
    assert Reserva("Ana Souza", 3, 200).total() == 600

# Este teste comeca VERMELHO: ReciboFormatter ainda nao existe.
# Fica verde quando voce separar a apresentacao numa classe propria.
def test_recibo_formatado():
    from recibo import ReciboFormatter
    r = Reserva("Ana Souza", 3, 200)
    esperado = "RECIBO\nAna Souza\n3 diarias\nTotal: R$ 600"
    assert ReciboFormatter().formatar(r) == esperado

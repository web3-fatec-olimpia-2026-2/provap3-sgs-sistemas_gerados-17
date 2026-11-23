import pytest
from tarifa import Reserva

# Estes testes fixam o comportamento. A refatoracao NAO pode mudar nenhum.
def test_comum():
    assert Reserva(2, 200, "comum").total() == 400

def test_fidelidade():
    assert Reserva(2, 200, "fidelidade").total() == 360.0

def test_parceiro():
    assert Reserva(2, 200, "parceiro").total() == 320.0

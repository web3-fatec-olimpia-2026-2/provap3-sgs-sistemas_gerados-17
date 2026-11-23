import pytest
from relatorio import relatorio_reservas_view, RESERVAS

# Este fixa a SAIDA - vale antes e depois. A refatoracao nao pode muda-lo.
def test_saida_final():
    saida = relatorio_reservas_view(RESERVAS)
    assert "Ana: R$ 540.00" in saida
    assert "Bruno: R$ 300.00" in saida
    assert "TOTAL: R$ 840.00" in saida

# Este comeca VERMELHO: exige o RelatorioService testavel SEM http.
def test_service_sem_http():
    from relatorio import RelatorioService
    svc = RelatorioService([{"hospede": "X", "diarias": 2, "valor": 100, "tipo": "fidelidade"}])
    linhas, total = svc.calcular()
    assert total == 180.0
    assert linhas == [("X", 180.0)]

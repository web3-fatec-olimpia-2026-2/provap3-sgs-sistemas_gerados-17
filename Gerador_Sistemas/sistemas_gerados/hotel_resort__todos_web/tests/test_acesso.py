"""Testes do PROXY: cache transparente, proteção por perfil e proxies empilhados."""
import pytest

from nucleo import antes_acesso
from nucleo.acesso import ConsultaComCache, ConsultaDePreco, ConsultaProtegida
from tests.fabrica import criar, itens_exemplo


def test_cache_chama_o_real_uma_vez_so():
    real = ConsultaDePreco()
    proxy = ConsultaComCache(real)
    item = criar()
    assert [proxy.calcular(item) for _ in range(5)] == [item.total] * 5
    assert real.chamadas == 1


def test_cache_separa_itens_diferentes():
    real = ConsultaDePreco()
    proxy = ConsultaComCache(real)
    for item in itens_exemplo():
        proxy.calcular(item)
    assert real.chamadas == 4


@pytest.mark.parametrize("perfil", ["gerente", "atendente"])
def test_protecao_deixa_passar_quem_pode(perfil):
    item = criar()
    assert ConsultaProtegida(ConsultaDePreco(), perfil).calcular(item) == item.total


def test_protecao_barra_quem_nao_pode():
    with pytest.raises(PermissionError):
        ConsultaProtegida(ConsultaDePreco(), "visitante").calcular(criar())


def test_proxies_empilham_porque_tem_a_mesma_interface():
    real = ConsultaDePreco()
    consulta = ConsultaProtegida(ConsultaComCache(real), "gerente")
    item = criar()
    consulta.calcular(item)
    consulta.calcular(item)
    assert real.chamadas == 1


def test_igual_a_versao_feita_na_mao():
    antes_acesso.CACHE.clear()
    item = criar()
    real_antigo, real_novo = ConsultaDePreco(), ConsultaDePreco()
    proxy = ConsultaProtegida(ConsultaComCache(real_novo), "gerente")
    for _ in range(3):
        assert proxy.calcular(item) == antes_acesso.consultar_antigo(real_antigo, item, "gerente")
    assert real_antigo.chamadas == real_novo.chamadas == 1

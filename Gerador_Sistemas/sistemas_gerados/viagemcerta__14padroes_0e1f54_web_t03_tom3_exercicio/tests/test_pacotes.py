"""Testes do COMPOSITE: folha e pacote com a mesma interface; árvore de qualquer profundidade."""
from nucleo.antes_pacotes import total_antigo
from nucleo.pacotes import Componente, Pacote, Unitario
from tests.fabrica import itens_exemplo


def montar():
    a, b, c, d = itens_exemplo()
    interno = Pacote("interno").adicionar(Unitario(c)).adicionar(Unitario(d))
    externo = Pacote("externo").adicionar(Unitario(a)).adicionar(Unitario(b)).adicionar(interno)
    return externo, [a, b, [c, d]]


def test_folha_vale_o_total_da_entidade():
    item = itens_exemplo()[0]
    assert Unitario(item).preco() == item.total


def test_pacote_soma_os_filhos_em_qualquer_profundidade():
    pacote, lista = montar()
    assert pacote.preco() == total_antigo(lista)


def test_pacote_vazio_vale_zero():
    assert Pacote("vazio").preco() == 0


def test_desconto_do_pacote():
    a, b, _, _ = itens_exemplo()
    pacote = Pacote("promo", desconto=0.1).adicionar(Unitario(a)).adicionar(Unitario(b))
    assert pacote.preco() == round((a.total + b.total) * 0.9, 2)


def test_folha_e_pacote_tem_a_mesma_interface():
    pacote, _ = montar()
    for componente in [pacote, *pacote.filhos]:
        assert isinstance(componente, Componente)
        assert isinstance(componente.preco(), (int, float))


def test_descricao_mostra_a_arvore():
    pacote, _ = montar()
    linhas = pacote.descricao().splitlines()
    assert linhas[0].startswith("[externo]")
    assert any(linha.startswith("  [interno]") for linha in linhas)
    assert len(linhas) == 6

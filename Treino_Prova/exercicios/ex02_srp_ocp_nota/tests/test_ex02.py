import importlib
import os

m = importlib.import_module(os.environ.get("ALVO", "gabarito"))

ITENS = [("Café", 15.90, 2), ("Pão", 7.50, 1)]


def test_total():
    assert round(m.Pedido("Ana", ITENS).total(), 2) == 39.30


def test_nota_texto_identica_a_antiga():
    antiga = m.PedidoFazTudo("Ana", ITENS).gerar_nota()
    assert m.NotaTextoFormatter().formatar(m.Pedido("Ana", ITENS)) == antiga


def test_nota_csv():
    esperado = "item;qtd;subtotal\nCafé;2;31.80\nPão;1;7.50\nTOTAL;;39.30"
    assert m.NotaCsvFormatter().formatar(m.Pedido("Ana", ITENS)) == esperado


def test_repository_grava(tmp_path):
    caminho = tmp_path / "nota.txt"
    m.ArquivoRepository().salvar("conteúdo", caminho)
    assert caminho.read_text(encoding="utf-8") == "conteúdo"


def test_pedido_nao_formata_nem_grava():
    # SRP: o Pedido não deve ter métodos de apresentação/infra.
    p = m.Pedido("Ana", ITENS)
    assert not hasattr(p, "gerar_nota") and not hasattr(p, "salvar")

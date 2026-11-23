"""Modo exercício: o questionário exercicios.html existe e cada pergunta esconde a resposta."""
from pathlib import Path

PAGINA = Path(__file__).resolve().parent.parent / "exercicios.html"


def test_questionario_tem_uma_resposta_oculta_por_pergunta():
    html = PAGINA.read_text(encoding="utf-8")
    assert html.count("<details>") == 71
    assert html.count("<summary>Ver resposta</summary>") == 71


def test_questionario_nao_usa_javascript():
    assert "<script" not in PAGINA.read_text(encoding="utf-8")

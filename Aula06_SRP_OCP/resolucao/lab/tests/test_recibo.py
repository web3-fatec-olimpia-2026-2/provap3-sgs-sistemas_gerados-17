"""Aula 06 — os 2 testes originais + os meus (recibo idêntico, arquivo, novo layout)."""
import pytest

import recibo_antes
from recibo import (ArquivoRepository, ReciboFormatter, ReciboHtmlFormatter,
                    Reserva, emitir_recibo)


# --- originais ---
def test_total():
    assert Reserva("Ana Souza", 3, 200).total() == 600


def test_recibo_formatado():
    r = Reserva("Ana Souza", 3, 200)
    esperado = "RECIBO\nAna Souza\n3 diarias\nTotal: R$ 600"
    assert ReciboFormatter().formatar(r) == esperado


# --- meus ---
@pytest.mark.parametrize("hospede, diarias, valor", [
    ("Ana Souza", 3, 200), ("Bruno", 1, 99.9), ("Carla", 10, 0),
])
def test_recibo_identico_ao_da_versao_faz_tudo(hospede, diarias, valor):
    antes = recibo_antes.Reserva(hospede, diarias, valor).formatar_recibo()
    depois = ReciboFormatter().formatar(Reserva(hospede, diarias, valor))
    assert depois == antes


def test_repository_grava_o_texto(tmp_path):
    # tmp_path: pasta temporária do pytest → o teste não suja o projeto.
    caminho = tmp_path / "recibo_ana.txt"
    ArquivoRepository().salvar("conteudo", caminho)
    assert caminho.read_text(encoding="utf-8") == "conteudo"


def test_emitir_recibo_junta_as_pecas(tmp_path):
    caminho = tmp_path / "r.txt"
    texto = emitir_recibo(Reserva("Ana", 2, 100), ReciboFormatter(), ArquivoRepository(), caminho)
    assert caminho.read_text(encoding="utf-8") == texto


def test_layout_novo_sem_tocar_na_reserva():
    html = ReciboHtmlFormatter().formatar(Reserva("Ana", 2, 100))
    assert "<h1>RECIBO</h1>" in html and "Total: R$ 200" in html

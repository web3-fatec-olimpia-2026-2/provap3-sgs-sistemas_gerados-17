"""Testes do SRP: o recibo sai idêntico e cada classe tem uma só responsabilidade."""
import pytest

from nucleo.entidades import Atendimento
from nucleo.recibo import ArquivoRepository, ReciboCsvFormatter, ReciboFormatter, emitir_recibo
from tests.fabrica import dados


def test_formato_novo_por_extensao():
    item = Atendimento(**dados())
    linhas = ReciboCsvFormatter().formatar(item).split("\n")
    assert linhas[0] == "cliente;quantidade;total"
    assert linhas[1] == f"{item.cliente};{item.quantidade};{item.total:.2f}"


def test_repository_so_grava(tmp_path):
    caminho = tmp_path / "recibo.txt"
    ArquivoRepository().salvar("conteúdo", caminho)
    assert caminho.read_text(encoding="utf-8") == "conteúdo"


def test_emitir_junta_as_pecas(tmp_path):
    caminho = tmp_path / "recibo.txt"
    texto = emitir_recibo(Atendimento(**dados()), ReciboFormatter(), ArquivoRepository(), caminho)
    assert caminho.read_text(encoding="utf-8") == texto


def test_entidade_nao_formata_nem_salva():
    item = Atendimento(**dados())
    assert not hasattr(item, "formatar_recibo") and not hasattr(item, "salvar_em_arquivo")

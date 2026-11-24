"""Testes do SRP: o recibo sai idêntico e cada classe tem uma só responsabilidade."""
import pytest

from nucleo.antes_recibo import LoteCitrosFazTudo
from nucleo.entidades import LoteCitros
from nucleo.recibo import ArquivoRepository, ReciboCsvFormatter, ReciboFormatter, emitir_recibo
from tests.fabrica import dados


@pytest.mark.parametrize("indice", range(4))
def test_recibo_identico_ao_da_versao_faz_tudo(indice):
    antes = LoteCitrosFazTudo(**dados(indice)).formatar_recibo()
    depois = ReciboFormatter().formatar(LoteCitros(**dados(indice)))
    assert depois == antes


def test_formato_novo_por_extensao():
    item = LoteCitros(**dados())
    linhas = ReciboCsvFormatter().formatar(item).split("\n")
    assert linhas[0] == "cooperado;caixas;total"
    assert linhas[1] == f"{item.cooperado};{item.caixas};{item.total:.2f}"


def test_repository_so_grava(tmp_path):
    caminho = tmp_path / "recibo.txt"
    ArquivoRepository().salvar("conteúdo", caminho)
    assert caminho.read_text(encoding="utf-8") == "conteúdo"


def test_emitir_junta_as_pecas(tmp_path):
    caminho = tmp_path / "recibo.txt"
    texto = emitir_recibo(LoteCitros(**dados()), ReciboFormatter(), ArquivoRepository(), caminho)
    assert caminho.read_text(encoding="utf-8") == texto


def test_entidade_nao_formata_nem_salva():
    item = LoteCitros(**dados())
    assert not hasattr(item, "formatar_recibo") and not hasattr(item, "salvar_em_arquivo")

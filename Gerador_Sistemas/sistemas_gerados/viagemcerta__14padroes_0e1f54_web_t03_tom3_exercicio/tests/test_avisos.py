"""Testes do FACTORY METHOD: mesma mensagem da versão antiga; canal novo sem mexer no criador."""
import pytest

from nucleo.antes_avisos import avisar_antigo
from nucleo.avisos import (Avisador, AvisadorEmail, AvisadorSms, AvisadorWhatsapp, CanalEmail, CanalSms,
                           CanalWhatsapp)
from tests.fabrica import criar, itens_exemplo


@pytest.mark.parametrize("canal, avisador", [("email", AvisadorEmail), ("sms", AvisadorSms)])
@pytest.mark.parametrize("indice", range(4))
def test_refatoracao_preserva_a_mensagem(canal, avisador, indice):
    item = itens_exemplo()[indice]
    assert avisador().avisar(item) == avisar_antigo(item, canal)


@pytest.mark.parametrize("avisador, produto", [(AvisadorEmail, CanalEmail), (AvisadorSms, CanalSms),
                                               (AvisadorWhatsapp, CanalWhatsapp)])
def test_cada_criador_cria_o_seu_produto(avisador, produto):
    assert isinstance(avisador().criar_canal(), produto)


def test_criador_base_nao_escolhe_canal():
    with pytest.raises(NotImplementedError):
        Avisador().avisar(criar())


def test_canal_novo_sem_mudar_o_avisador():
    item = criar()
    assert AvisadorWhatsapp().avisar(item).startswith(f"[whatsapp] {item.viajante}:")


def test_versao_com_if_nao_conhece_o_canal_novo():
    with pytest.raises(ValueError):
        avisar_antigo(criar(), "whatsapp")


def test_mensagem_tem_o_total():
    item = criar()
    assert f"R$ {item.total:.2f}" in AvisadorEmail().avisar(item)

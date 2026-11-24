"""Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from citricultura.models import LoteCitros


def dados(**mudancas):
    copia = {"cooperado": 'Isabela', "talhao": 101, "caixas": 2, "preco_caixa": Decimal("38.00"), "cidade": 'Cidade 1', "cpf_cnpj_provap3": 'Cpf cnpj provap3 1', "tipo": "industria"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_cria_e_calcula_total():
    obj = LoteCitros.objects.create(**dados())
    assert obj.total == Decimal("76.00")


@pytest.mark.django_db
def test_dados_validos_passam_no_full_clean():
    LoteCitros(**dados()).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor", [("cooperado", ""), ("talhao", 0), ("caixas", 0), ("caixas", 5001), ("preco_caixa", Decimal("-1.00")), ("cidade", ""), ("cpf_cnpj_provap3", "")])
def test_full_clean_recusa_valor_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        LoteCitros(**dados(**{campo: valor})).full_clean()
    assert campo in erro.value.message_dict


@pytest.mark.django_db
def test_save_sozinho_nao_valida():
    """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
    LoteCitros(**dados(caixas=0)).save()
    assert LoteCitros.objects.count() == 1

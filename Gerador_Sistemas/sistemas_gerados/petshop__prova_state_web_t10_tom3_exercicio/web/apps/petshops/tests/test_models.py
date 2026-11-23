"""Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.petshops.models import Petshop


def dados(**mudancas):
    copia = {"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_cria_e_calcula_total():
    obj = Petshop.objects.create(**dados())
    assert obj.total == Decimal("200.00")


@pytest.mark.django_db
def test_dados_validos_passam_no_full_clean():
    Petshop(**dados()).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor", [("cliente", ""), ("codigo", 0), ("quantidade", 0), ("quantidade", 101), ("valor_unitario", Decimal("-1.00"))])
def test_full_clean_recusa_valor_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        Petshop(**dados(**{campo: valor})).full_clean()
    assert campo in erro.value.message_dict


@pytest.mark.django_db
def test_save_sozinho_nao_valida():
    """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
    Petshop(**dados(quantidade=0)).save()
    assert Petshop.objects.count() == 1

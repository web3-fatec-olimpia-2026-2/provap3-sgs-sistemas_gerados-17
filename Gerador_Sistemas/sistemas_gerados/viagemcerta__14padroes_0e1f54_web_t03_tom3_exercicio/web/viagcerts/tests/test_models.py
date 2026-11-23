"""Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from viagcerts.models import Viagcert


def dados(**mudancas):
    copia = {"viajante": 'Elisa', "voo": 101, "noites": 2, "valor_noite": Decimal("350.00"), "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_cria_e_calcula_total():
    obj = Viagcert.objects.create(**dados())
    assert obj.total == Decimal("700.00")


@pytest.mark.django_db
def test_dados_validos_passam_no_full_clean():
    Viagcert(**dados()).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor", [("viajante", ""), ("voo", 0), ("noites", 0), ("noites", 31), ("valor_noite", Decimal("-1.00"))])
def test_full_clean_recusa_valor_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        Viagcert(**dados(**{campo: valor})).full_clean()
    assert campo in erro.value.message_dict


@pytest.mark.django_db
def test_save_sozinho_nao_valida():
    """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
    Viagcert(**dados(noites=0)).save()
    assert Viagcert.objects.count() == 1

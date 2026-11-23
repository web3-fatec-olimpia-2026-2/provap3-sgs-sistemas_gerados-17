"""Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from reservas.models import Reserva


def dados(**mudancas):
    copia = {"hospede": 'Ana', "quarto": 101, "diarias": 2, "valor_diaria": Decimal("200.00"), "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_cria_e_calcula_total():
    obj = Reserva.objects.create(**dados())
    assert obj.total == Decimal("400.00")


@pytest.mark.django_db
def test_dados_validos_passam_no_full_clean():
    Reserva(**dados()).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor", [("hospede", ""), ("quarto", 0), ("diarias", 0), ("diarias", 31), ("valor_diaria", Decimal("-1.00"))])
def test_full_clean_recusa_valor_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        Reserva(**dados(**{campo: valor})).full_clean()
    assert campo in erro.value.message_dict


@pytest.mark.django_db
def test_save_sozinho_nao_valida():
    """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
    Reserva(**dados(diarias=0)).save()
    assert Reserva.objects.count() == 1

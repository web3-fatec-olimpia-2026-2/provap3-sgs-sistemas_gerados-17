"""Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from emprestimos.models import Emprestimo


def dados(**mudancas):
    copia = {"leitor": 'Beatriz', "exemplar": 101, "dias": 2, "taxa_dia": Decimal("2.50"), "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_cria_e_calcula_total():
    obj = Emprestimo.objects.create(**dados())
    assert obj.total == Decimal("5.00")


@pytest.mark.django_db
def test_dados_validos_passam_no_full_clean():
    Emprestimo(**dados()).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor", [("leitor", ""), ("exemplar", 0), ("dias", 0), ("dias", 31), ("taxa_dia", Decimal("-1.00"))])
def test_full_clean_recusa_valor_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        Emprestimo(**dados(**{campo: valor})).full_clean()
    assert campo in erro.value.message_dict


@pytest.mark.django_db
def test_save_sozinho_nao_valida():
    """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
    Emprestimo(**dados(dias=0)).save()
    assert Emprestimo.objects.count() == 1

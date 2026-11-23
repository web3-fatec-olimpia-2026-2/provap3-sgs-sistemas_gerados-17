"""Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from matriculas.models import Matricula


def dados(**mudancas):
    copia = {"aluno": 'Fernanda', "turma": 101, "meses": 2, "mensalidade": Decimal("100.00"), "tipo": "mensal"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_cria_e_calcula_total():
    obj = Matricula.objects.create(**dados())
    assert obj.total == Decimal("200.00")


@pytest.mark.django_db
def test_dados_validos_passam_no_full_clean():
    Matricula(**dados()).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor", [("aluno", ""), ("turma", 0), ("meses", 0), ("meses", 25), ("mensalidade", Decimal("-1.00"))])
def test_full_clean_recusa_valor_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        Matricula(**dados(**{campo: valor})).full_clean()
    assert campo in erro.value.message_dict


@pytest.mark.django_db
def test_save_sozinho_nao_valida():
    """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
    Matricula(**dados(meses=0)).save()
    assert Matricula.objects.count() == 1

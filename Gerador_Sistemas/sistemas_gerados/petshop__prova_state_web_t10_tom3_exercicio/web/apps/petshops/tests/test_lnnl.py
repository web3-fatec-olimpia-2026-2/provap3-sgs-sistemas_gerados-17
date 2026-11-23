"""Testes do ID interno LNNL (motor-id-interno): gerado no save(), válido, legível e único."""
import re
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.petshops import lnnl
from apps.petshops.models import TIPO_LNNL, Petshop, validar_codigo_lnnl


def novo(**mudancas):
    copia = {"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "tipo": "comum"}
    copia.update(mudancas)
    return Petshop.objects.create(**copia)


@pytest.mark.django_db
def test_id_interno_gerado_no_save_e_valido_do_tipo():
    obj = novo()
    assert lnnl.validar(obj.id_interno, TIPO_LNNL) and lnnl.extrair_tipo(obj.id_interno) == TIPO_LNNL


@pytest.mark.django_db
def test_id_interno_formatado_na_mascara_lnnl():
    mascara = r"[A-Z][1-9]{2}[A-Z]-[A-Z][1-9]{2}[A-Z]-[A-Z][1-9][A-Z]-[A-Z][1-9][A-Z]"   # LNNL-LNNL-LNL-LNL
    assert re.fullmatch(mascara, novo().id_interno_formatado)


@pytest.mark.django_db
def test_salvar_de_novo_nao_troca_o_id_interno():
    obj = novo()
    antes = obj.id_interno
    obj.save()
    assert obj.id_interno == antes


@pytest.mark.django_db
def test_colisao_insere_e_tenta_de_novo(monkeypatch):
    primeiro = novo()
    sorteios = iter([primeiro.id_interno, lnnl.gerar(TIPO_LNNL)])   # 1º sorteio repete um ID
    monkeypatch.setattr(lnnl, "gerar", lambda tipo: next(sorteios))
    assert novo().id_interno != primeiro.id_interno


def test_validador_recusa_codigo_invalido():
    codigo = lnnl.gerar(TIPO_LNNL)
    errado = codigo[:13] + ("A" if codigo[13] != "A" else "B")   # troca a última letra
    with pytest.raises(ValidationError):
        validar_codigo_lnnl(errado)


@pytest.mark.django_db
def test_api_mostra_o_codigo(client):
    obj = novo()
    from django.urls import reverse
    assert client.get(reverse("petshops:api")).json()["itens"][0]["codigo"] == obj.id_interno_formatado

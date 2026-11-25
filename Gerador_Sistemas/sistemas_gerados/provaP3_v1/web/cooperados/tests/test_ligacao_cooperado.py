"""Ligação Cooperado.cooperado → LoteCitros (sgs ligar): referência OPCIONAL entre classes de apps diferentes."""
import pytest

from cooperados.forms import CooperadoForm
from cooperados.models import Cooperado
from cooperados.tests.test_models import dados as dados_cooperados
from citricultura.models import LoteCitros
from citricultura.tests.test_models import dados as dados_citricultura

pytestmark = pytest.mark.django_db


def test_o_campo_e_opcional_e_aponta_para_a_classe():
    campo = Cooperado._meta.get_field("cooperado")
    assert campo.related_model is LoteCitros and campo.null and campo.blank
    assert "cooperado" in CooperadoForm().fields


def test_ligar_e_apagar_o_alvo_so_limpa_a_referencia():
    alvo = LoteCitros.objects.create(**dados_citricultura())
    obj = Cooperado.objects.create(**dados_cooperados(), cooperado=alvo)
    assert obj.cooperado == alvo and obj in alvo.cooperados_cooperado.all()
    alvo.delete()
    obj.refresh_from_db()
    assert obj.cooperado is None


def test_a_api_le_e_grava_a_referencia(client, settings):
    import json

    from django.urls import reverse

    setattr(settings, "COOPERADOS_API_CAMPOS", {})    # o padrão (o sgs api config pode ter ocultado)
    alvo = LoteCitros.objects.create(**dados_citricultura())
    obj = Cooperado.objects.create(**dados_cooperados())
    url = reverse("cooperados:api_item", args=[obj.pk])
    resposta = client.patch(url, data=json.dumps({"cooperado": str(alvo.pk)}), content_type="application/json")
    assert resposta.status_code == 200 and str(resposta.json()["cooperado"]) == str(alvo.pk)

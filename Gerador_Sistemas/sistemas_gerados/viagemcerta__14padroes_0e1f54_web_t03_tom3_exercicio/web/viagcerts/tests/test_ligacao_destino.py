"""Ligação Viagcert.destino → Destino (sgs ligar): referência OPCIONAL entre classes de apps diferentes."""
import pytest

from viagcerts.forms import ViagcertForm
from viagcerts.models import Viagcert
from viagcerts.tests.test_models import dados as dados_viagcerts
from destinos.models import Destino
from destinos.tests.test_models import dados as dados_destinos

pytestmark = pytest.mark.django_db


def test_o_campo_e_opcional_e_aponta_para_a_classe():
    campo = Viagcert._meta.get_field("destino")
    assert campo.related_model is Destino and campo.null and campo.blank
    assert "destino" in ViagcertForm().fields


def test_ligar_e_apagar_o_alvo_so_limpa_a_referencia():
    alvo = Destino.objects.create(**dados_destinos())
    obj = Viagcert.objects.create(**dados_viagcerts(), destino=alvo)
    assert obj.destino == alvo and obj in alvo.viagcerts_destino.all()
    alvo.delete()
    obj.refresh_from_db()
    assert obj.destino is None


def test_a_api_le_e_grava_a_referencia(client, settings):
    import json

    from django.urls import reverse

    setattr(settings, "VIAGCERTS_API_CAMPOS", {})    # o padrão (o sgs api config pode ter ocultado)
    alvo = Destino.objects.create(**dados_destinos())
    obj = Viagcert.objects.create(**dados_viagcerts())
    url = reverse("viagcerts:api_item", args=[obj.pk])
    resposta = client.patch(url, data=json.dumps({"destino": str(alvo.pk)}), content_type="application/json")
    assert resposta.status_code == 200 and str(resposta.json()["destino"]) == str(alvo.pk)

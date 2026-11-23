"""Teste do identificador UUIDv4 (Instruções §10.4)."""
import uuid
from decimal import Decimal

import pytest

from destinos.models import Destino


@pytest.mark.django_db
def test_chave_primaria_e_uuid4():
    obj = Destino.objects.create(**{"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "cidade": 'Cidade 1', "pais": 'Pais 1', "tipo": "comum"})
    assert isinstance(obj.pk, uuid.UUID) and obj.pk.version == 4

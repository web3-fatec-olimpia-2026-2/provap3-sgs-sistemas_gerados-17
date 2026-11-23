"""Teste do identificador UUIDv4 (Instruções §10.4)."""
import uuid
from decimal import Decimal

import pytest

from apps.petshops.models import Petshop


@pytest.mark.django_db
def test_chave_primaria_e_uuid4():
    obj = Petshop.objects.create(**{"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "tipo": "comum"})
    assert isinstance(obj.pk, uuid.UUID) and obj.pk.version == 4

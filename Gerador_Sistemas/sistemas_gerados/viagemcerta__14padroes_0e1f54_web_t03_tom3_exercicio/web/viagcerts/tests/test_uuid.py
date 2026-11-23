"""Teste do identificador UUIDv4 (Instruções §10.4)."""
import uuid
from decimal import Decimal

import pytest

from viagcerts.models import Viagcert


@pytest.mark.django_db
def test_chave_primaria_e_uuid4():
    obj = Viagcert.objects.create(**{"viajante": 'Elisa', "voo": 101, "noites": 2, "valor_noite": Decimal("350.00"), "tipo": "comum"})
    assert isinstance(obj.pk, uuid.UUID) and obj.pk.version == 4

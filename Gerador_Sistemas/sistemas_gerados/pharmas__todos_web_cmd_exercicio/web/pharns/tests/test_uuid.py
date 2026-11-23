"""Teste do identificador UUIDv4 (Instruções §10.4)."""
import uuid
from decimal import Decimal

import pytest

from pharns.models import Pharm


@pytest.mark.django_db
def test_chave_primaria_e_uuid4():
    obj = Pharm.objects.create(**{"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "produto": 'Produto 1', "idade": 0, "categoria": 'Categoria 1', "cosmeticos": 'Cosmeticos 1', "medicamentos": 'Medicamentos 1', "tipo": "comum"})
    assert isinstance(obj.pk, uuid.UUID) and obj.pk.version == 4

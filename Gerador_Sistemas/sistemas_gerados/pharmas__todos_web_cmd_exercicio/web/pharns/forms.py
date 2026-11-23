"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import Pharm


class PharmForm(forms.ModelForm):
    class Meta:
        model = Pharm
        fields = ["cliente", "codigo", "quantidade", "valor_unitario", "produto", "idade", "categoria", "cosmeticos", "medicamentos", "observacao", "tipo"]

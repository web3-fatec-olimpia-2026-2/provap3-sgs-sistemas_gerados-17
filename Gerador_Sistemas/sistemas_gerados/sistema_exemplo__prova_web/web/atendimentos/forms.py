"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import Atendimento


class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ["cliente", "codigo", "quantidade", "valor_unitario", "observacao", "tipo"]

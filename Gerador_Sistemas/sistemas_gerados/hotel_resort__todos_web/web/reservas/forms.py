"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["hospede", "quarto", "diarias", "valor_diaria", "observacao", "tipo"]

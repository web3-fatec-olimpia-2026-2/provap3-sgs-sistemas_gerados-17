"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import Destino


class DestinoForm(forms.ModelForm):
    class Meta:
        model = Destino
        fields = ["cliente", "codigo", "quantidade", "valor_unitario", "cidade", "pais", "observacao", "tipo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap: cada campo ganha a classe do componente (o HTML continua vindo do Django).
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"

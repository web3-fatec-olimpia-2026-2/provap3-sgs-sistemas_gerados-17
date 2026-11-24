"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import LoteCitros


class LoteCitrosForm(forms.ModelForm):
    class Meta:
        model = LoteCitros
        fields = ["cooperado", "talhao", "caixas", "preco_caixa", "cidade", "cpf_cnpj_provap3", "observacao", "tipo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap: cada campo ganha a classe do componente (o HTML continua vindo do Django).
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"

from django import forms

from .models import Pedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente", "produto", "quantidade", "preco_unitario", "observacao", "tipo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"

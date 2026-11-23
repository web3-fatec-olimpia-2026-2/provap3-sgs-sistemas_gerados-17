"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import Emprestimo


class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ["leitor", "exemplar", "dias", "taxa_dia", "observacao", "tipo"]

"""ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
from django import forms

from .models import Matricula


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ["aluno", "turma", "meses", "mensalidade", "objetivo", "tipo"]

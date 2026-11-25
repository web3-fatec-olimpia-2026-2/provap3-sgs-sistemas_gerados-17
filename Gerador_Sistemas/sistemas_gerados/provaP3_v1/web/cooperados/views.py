"""
VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
"""
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CooperadoForm
from .models import Cooperado
from .services import CooperadoService
from .viewmodels import DetalheVM, PainelVM


def lista(request):
    painel = PainelVM(Cooperado.objects.order_by("pk"), CooperadoService())
    return render(request, "cooperados/lista.html", {"painel": painel})


def criar(request):
    """CRUD · CREATE."""
    form = CooperadoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
        form.save()
        return redirect("cooperados:lista")
    return render(request, "cooperados/form.html", {"form": form})


def detalhe(request, pk):
    """CRUD · READ (um registro): o DetalheVM prepara o que a tela mostra."""
    obj = get_object_or_404(Cooperado, pk=pk)
    return render(request, "cooperados/detalhe.html", {"item": DetalheVM(obj, CooperadoService().valor_final(obj))})


def editar(request, pk):
    """CRUD · UPDATE: o MESMO ModelForm, preenchido com o registro (as validações continuam valendo)."""
    obj = get_object_or_404(Cooperado, pk=pk)
    form = CooperadoForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("cooperados:detalhe", pk=obj.pk)
    return render(request, "cooperados/form.html", {"form": form, "obj": obj})


def excluir(request, pk):
    """CRUD · DELETE: o GET só mostra a confirmação; apagar exige POST (GET nunca altera dados)."""
    obj = get_object_or_404(Cooperado, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("cooperados:lista")
    return render(request, "cooperados/confirmar_exclusao.html", {"obj": obj})

"""
VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
"""
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoteCitrosForm
from .models import LoteCitros
from .services import LoteCitrosService
from .viewmodels import DetalheVM, PainelVM


def lista(request):
    painel = PainelVM(LoteCitros.objects.order_by("pk"), LoteCitrosService())
    return render(request, "citricultura/lista.html", {"painel": painel})


def criar(request):
    """CRUD · CREATE."""
    form = LoteCitrosForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
        form.save()
        return redirect("citricultura:lista")
    return render(request, "citricultura/form.html", {"form": form})


def detalhe(request, pk):
    """CRUD · READ (um registro): o DetalheVM prepara o que a tela mostra."""
    obj = get_object_or_404(LoteCitros, pk=pk)
    return render(request, "citricultura/detalhe.html", {"item": DetalheVM(obj, LoteCitrosService().valor_final(obj))})


def editar(request, pk):
    """CRUD · UPDATE: o MESMO ModelForm, preenchido com o registro (as validações continuam valendo)."""
    obj = get_object_or_404(LoteCitros, pk=pk)
    form = LoteCitrosForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("citricultura:detalhe", pk=obj.pk)
    return render(request, "citricultura/form.html", {"form": form, "obj": obj})


def excluir(request, pk):
    """CRUD · DELETE: o GET só mostra a confirmação; apagar exige POST (GET nunca altera dados)."""
    obj = get_object_or_404(LoteCitros, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("citricultura:lista")
    return render(request, "citricultura/confirmar_exclusao.html", {"obj": obj})

"""
VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PetshopForm
from .models import Petshop
from .services import PetshopService
from .viewmodels import DetalheVM, PainelVM


def lista(request):
    painel = PainelVM(Petshop.objects.order_by("pk"), PetshopService())
    return render(request, "petshops/lista.html", {"painel": painel})


def criar(request):
    """CRUD · CREATE."""
    form = PetshopForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
        form.save()
        return redirect("petshops:lista")
    return render(request, "petshops/form.html", {"form": form})


def detalhe(request, pk):
    """CRUD · READ (um registro): o DetalheVM prepara o que a tela mostra."""
    obj = get_object_or_404(Petshop, pk=pk)
    return render(request, "petshops/detalhe.html", {"item": DetalheVM(obj, PetshopService().valor_final(obj))})


def editar(request, pk):
    """CRUD · UPDATE: o MESMO ModelForm, preenchido com o registro (as validações continuam valendo)."""
    obj = get_object_or_404(Petshop, pk=pk)
    form = PetshopForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("petshops:detalhe", pk=obj.pk)
    return render(request, "petshops/form.html", {"form": form, "obj": obj})


def excluir(request, pk):
    """CRUD · DELETE: o GET só mostra a confirmação; apagar exige POST (GET nunca altera dados)."""
    obj = get_object_or_404(Petshop, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("petshops:lista")
    return render(request, "petshops/confirmar_exclusao.html", {"obj": obj})


def api_lista(request):
    painel = PainelVM(Petshop.objects.order_by("pk"), PetshopService())
    itens = [{"id": str(i.id), "codigo": i.codigo, "titulo": i.titulo, "valor": i.valor_formatado}
             for i in painel.itens]
    return JsonResponse({"itens": itens, "total": painel.total_formatado})


def exercicios(request):
    """Questionário de revisão (modo exercício): só exibe — cada resposta fica oculta até "Ver resposta"."""
    return render(request, "petshops/exercicios.html")

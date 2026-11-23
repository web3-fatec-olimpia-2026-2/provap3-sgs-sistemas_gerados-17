"""
VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ViagcertForm
from .models import Viagcert
from .services import ViagcertService
from .viewmodels import DetalheVM, PainelVM


def lista(request):
    painel = PainelVM(Viagcert.objects.order_by("pk"), ViagcertService())
    return render(request, "viagcerts/lista.html", {"painel": painel})


def criar(request):
    """CRUD · CREATE."""
    form = ViagcertForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
        form.save()
        return redirect("viagcerts:lista")
    return render(request, "viagcerts/form.html", {"form": form})


def detalhe(request, pk):
    """CRUD · READ (um registro): o DetalheVM prepara o que a tela mostra."""
    obj = get_object_or_404(Viagcert, pk=pk)
    return render(request, "viagcerts/detalhe.html", {"item": DetalheVM(obj, ViagcertService().valor_final(obj))})


def editar(request, pk):
    """CRUD · UPDATE: o MESMO ModelForm, preenchido com o registro (as validações continuam valendo)."""
    obj = get_object_or_404(Viagcert, pk=pk)
    form = ViagcertForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("viagcerts:detalhe", pk=obj.pk)
    return render(request, "viagcerts/form.html", {"form": form, "obj": obj})


def excluir(request, pk):
    """CRUD · DELETE: o GET só mostra a confirmação; apagar exige POST (GET nunca altera dados)."""
    obj = get_object_or_404(Viagcert, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("viagcerts:lista")
    return render(request, "viagcerts/confirmar_exclusao.html", {"obj": obj})


def api_lista(request):
    painel = PainelVM(Viagcert.objects.order_by("pk"), ViagcertService())
    itens = [{"id": str(i.id), "codigo": i.codigo, "titulo": i.titulo, "valor": i.valor_formatado}
             for i in painel.itens]
    return JsonResponse({"itens": itens, "total": painel.total_formatado})


def exercicios(request):
    """Questionário de revisão (modo exercício): só exibe — cada resposta fica oculta até "Ver resposta"."""
    return render(request, "viagcerts/exercicios.html")

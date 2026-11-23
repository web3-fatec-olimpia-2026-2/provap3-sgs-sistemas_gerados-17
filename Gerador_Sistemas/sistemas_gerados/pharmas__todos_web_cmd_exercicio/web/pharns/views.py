"""
VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PharmForm
from .models import Pharm
from .services import PharmService
from .viewmodels import DetalheVM, PainelVM


def lista(request):
    painel = PainelVM(Pharm.objects.order_by("pk"), PharmService())
    return render(request, "pharns/lista.html", {"painel": painel})


def criar(request):
    """CRUD · CREATE."""
    form = PharmForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
        form.save()
        return redirect("pharns:lista")
    return render(request, "pharns/form.html", {"form": form})


def detalhe(request, pk):
    """CRUD · READ (um registro): o DetalheVM prepara o que a tela mostra."""
    obj = get_object_or_404(Pharm, pk=pk)
    return render(request, "pharns/detalhe.html", {"item": DetalheVM(obj, PharmService().valor_final(obj))})


def editar(request, pk):
    """CRUD · UPDATE: o MESMO ModelForm, preenchido com o registro (as validações continuam valendo)."""
    obj = get_object_or_404(Pharm, pk=pk)
    form = PharmForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("pharns:detalhe", pk=obj.pk)
    return render(request, "pharns/form.html", {"form": form, "obj": obj})


def excluir(request, pk):
    """CRUD · DELETE: o GET só mostra a confirmação; apagar exige POST (GET nunca altera dados)."""
    obj = get_object_or_404(Pharm, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("pharns:lista")
    return render(request, "pharns/confirmar_exclusao.html", {"obj": obj})


def api_lista(request):
    painel = PainelVM(Pharm.objects.order_by("pk"), PharmService())
    itens = [{"id": str(i.id), "codigo": i.codigo, "titulo": i.titulo, "valor": i.valor_formatado}
             for i in painel.itens]
    return JsonResponse({"itens": itens, "total": painel.total_formatado})


def exercicios(request):
    """Questionário de revisão (modo exercício): só exibe — cada resposta fica oculta até "Ver resposta"."""
    return render(request, "pharns/exercicios.html")

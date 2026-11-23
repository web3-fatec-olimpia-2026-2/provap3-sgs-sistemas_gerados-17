"""
VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
"""
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import ReservaForm
from .models import Reserva
from .services import ReservaService
from .viewmodels import PainelVM


def lista(request):
    painel = PainelVM(Reserva.objects.order_by("pk"), ReservaService())
    return render(request, "reservas/lista.html", {"painel": painel})


def criar(request):
    form = ReservaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
        form.save()
        return redirect("reservas:lista")
    return render(request, "reservas/form.html", {"form": form})


def api_lista(request):
    painel = PainelVM(Reserva.objects.order_by("pk"), ReservaService())
    return JsonResponse({"itens": [{"titulo": i.titulo, "valor": i.valor_formatado} for i in painel.itens],
                         "total": painel.total_formatado})

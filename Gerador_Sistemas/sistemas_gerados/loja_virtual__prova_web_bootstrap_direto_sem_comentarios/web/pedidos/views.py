from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PedidoForm
from .models import Pedido
from .services import PedidoService
from .viewmodels import DetalheVM, PainelVM


def lista(request):
    painel = PainelVM(Pedido.objects.order_by("pk"), PedidoService())
    return render(request, "pedidos/lista.html", {"painel": painel})


def criar(request):
    form = PedidoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("pedidos:lista")
    return render(request, "pedidos/form.html", {"form": form})


def detalhe(request, pk):
    obj = get_object_or_404(Pedido, pk=pk)
    return render(request, "pedidos/detalhe.html", {"item": DetalheVM(obj, PedidoService().valor_final(obj))})


def editar(request, pk):
    obj = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("pedidos:detalhe", pk=obj.pk)
    return render(request, "pedidos/form.html", {"form": form, "obj": obj})


def excluir(request, pk):
    obj = get_object_or_404(Pedido, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("pedidos:lista")
    return render(request, "pedidos/confirmar_exclusao.html", {"obj": obj})


def api_lista(request):
    painel = PainelVM(Pedido.objects.order_by("pk"), PedidoService())
    itens = [{"id": str(i.id), "codigo": i.codigo, "titulo": i.titulo, "valor": i.valor_formatado}
             for i in painel.itens]
    return JsonResponse({"itens": itens, "total": painel.total_formatado})

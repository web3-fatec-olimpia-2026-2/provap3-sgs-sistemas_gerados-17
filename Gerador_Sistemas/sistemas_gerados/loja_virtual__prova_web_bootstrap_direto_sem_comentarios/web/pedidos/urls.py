from django.urls import path

from . import views

app_name = "pedidos"
urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<int:pk>/", views.detalhe, name="detalhe"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/excluir/", views.excluir, name="excluir"),
    path("api/", views.api_lista, name="api"),
]

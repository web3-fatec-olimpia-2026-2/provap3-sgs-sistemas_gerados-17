from django.urls import path

from . import api, views

app_name = "viagcerts"
urlpatterns = [
    # CRUD básico: lista e detalhe (Read), criar (Create), editar (Update), excluir (Delete)
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<uuid:pk>/", views.detalhe, name="detalhe"),
    path("<uuid:pk>/editar/", views.editar, name="editar"),
    path("<uuid:pk>/excluir/", views.excluir, name="excluir"),
    # API REST (JSON): a coleção (GET lista, POST cria) e um registro (GET, PUT, PATCH, DELETE)
    path("api/v1/", api.colecao, name="api_colecao"),
    path("api/v1/<uuid:pk>/", api.item, name="api_item"),
    path("api/", views.api_lista, name="api"),  # resumo do painel (itens + total)
    path("exercicios/", views.exercicios, name="exercicios"),  # questionário (modo exercício)
]

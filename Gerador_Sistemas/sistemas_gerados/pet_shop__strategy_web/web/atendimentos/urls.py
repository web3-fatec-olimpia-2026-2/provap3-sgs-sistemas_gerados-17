from django.urls import path

from . import api, views

app_name = "atendimentos"
urlpatterns = [
    # CRUD básico: lista e detalhe (Read), criar (Create), editar (Update), excluir (Delete)
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<int:pk>/", views.detalhe, name="detalhe"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/excluir/", views.excluir, name="excluir"),
    # API REST (JSON): a coleção (GET lista, POST cria) e um registro (GET, PUT, PATCH, DELETE);
    # os campos de cada endpoint são configuráveis (sgs api config) e quem chama escolhe com ?campos=
    path("api/v1/", api.colecao, name="api_colecao"),
    path("api/v1/campos/", api.campos, name="api_campos"),
    path("api/v1/<int:pk>/", api.item, name="api_item"),
    path("api/", api.resumo, name="api"),  # resumo do painel (itens + total) — o link "API"
]

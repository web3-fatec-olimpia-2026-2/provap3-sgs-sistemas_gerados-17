from django.urls import path

from . import views

app_name = "petshops"
urlpatterns = [
    # CRUD básico: lista e detalhe (Read), criar (Create), editar (Update), excluir (Delete)
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<uuid:pk>/", views.detalhe, name="detalhe"),
    path("<uuid:pk>/editar/", views.editar, name="editar"),
    path("<uuid:pk>/excluir/", views.excluir, name="excluir"),
    path("api/", views.api_lista, name="api"),
    path("exercicios/", views.exercicios, name="exercicios"),  # questionário (modo exercício)
]

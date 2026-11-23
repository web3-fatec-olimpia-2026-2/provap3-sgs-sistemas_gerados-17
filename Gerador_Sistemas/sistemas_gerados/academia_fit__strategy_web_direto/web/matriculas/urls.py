from django.urls import path

from . import views

app_name = "matriculas"
urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("api/", views.api_lista, name="api"),
]

"""Uma rota só: todo caminho vai para a view da tela, que decide como o tela_prompt.py decide
(/, /comando, /config, /sugestoes, /tutorial, /referencias/…)."""
from django.urls import re_path

from sgs_web import views

urlpatterns = [re_path(r"^", views.tela)]

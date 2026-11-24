"""
API com o DRF (Django REST Framework) — compare com api.py (Django puro: JsonResponse e os métodos à mão).

Um ModelViewSet faz o CRUD REST inteiro e o router cria as rotas (incluídas em /api/ pelo projeto):
  GET    /api/lote-citroses/        lista            POST   /api/lote-citroses/        cria (201 / 400)
  GET    /api/lote-citroses/<pk>/   um registro      PUT    /api/lote-citroses/<pk>/   altera tudo
  PATCH  /api/lote-citroses/<pk>/   altera parte     DELETE /api/lote-citroses/<pk>/   exclui (204)
No navegador, /api/ abre a Browsable API do DRF (dá para testar os endpoints por ali).
"""
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from .models import LoteCitros
from .serializers import LoteCitrosSerializer


class LoteCitrosViewSet(viewsets.ModelViewSet):
    queryset = LoteCitros.objects.all().order_by("pk")
    serializer_class = LoteCitrosSerializer


router = DefaultRouter()
router.register("lote-citroses", LoteCitrosViewSet, basename="lote_citros")
urlpatterns = router.urls

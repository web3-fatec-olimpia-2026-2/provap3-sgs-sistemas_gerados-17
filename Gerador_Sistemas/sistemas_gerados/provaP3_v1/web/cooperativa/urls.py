from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from . import pwa

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # PWA: manifest e service worker ficam na RAIZ do site (o service worker só controla o que está abaixo dele)
    path("manifest.webmanifest", pwa.manifest, name="manifest"),
    path("sw.js", pwa.service_worker, name="service_worker"),
    path("cooperados/", include("cooperados.urls")),  # módulo (sgs app): antes da raiz
    path("api/", include("citricultura.api_drf")),  # API com o DRF (router + ViewSet): /api/…
    path("citricultura/", include("citricultura.urls")),
    path("", RedirectView.as_view(url="/citricultura/", permanent=False)),  # a raiz leva ao app
]

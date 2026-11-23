from django.contrib import admin
from django.urls import include, path

from . import pwa

urlpatterns = [
    path("admin/", admin.site.urls),
    # PWA: manifest e service worker ficam na RAIZ do site (o service worker só controla o que está abaixo dele)
    path("manifest.webmanifest", pwa.manifest, name="manifest"),
    path("sw.js", pwa.service_worker, name="service_worker"),
    path("", include("emprestimos.urls")),
]

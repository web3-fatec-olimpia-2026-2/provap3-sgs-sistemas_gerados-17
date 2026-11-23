import json

from django.http import HttpResponse
from django.templatetags.static import static

SERVICE_WORKER = """
const CACHE = "pwa-pedidos-v1";
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (evento) => evento.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (evento) => {
  if (evento.request.method !== "GET") return;
  evento.respondWith(
    fetch(evento.request)
      .then((resposta) => {
        const copia = resposta.clone();
        caches.open(CACHE).then((cache) => cache.put(evento.request, copia));
        return resposta;
      })
      .catch(() => caches.match(evento.request))
  );
});
"""


def manifest(request):
    dados = {
        "name": "Loja Virtual",
        "short_name": "Loja",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0c0c0c",
        "theme_color": "#0c0c0c",
        "icons": [{"src": static("pedidos/icone-192.png"), "sizes": "192x192", "type": "image/png"},
                  {"src": static("pedidos/icone-512.png"), "sizes": "512x512", "type": "image/png"}],
    }
    return HttpResponse(json.dumps(dados, ensure_ascii=False), content_type="application/manifest+json")


def service_worker(request):
    resposta = HttpResponse(SERVICE_WORKER, content_type="application/javascript")
    resposta["Service-Worker-Allowed"] = "/"
    return resposta

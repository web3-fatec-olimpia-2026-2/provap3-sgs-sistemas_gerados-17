"""
PWA (Progressive Web App): o site pode ser INSTALADO e abrir numa janela própria, isolada das abas.

Três peças, servidas pelo próprio Django (sem dependência extra):
  * /manifest.webmanifest — nome, cores, ícones e display "standalone" (janela de app);
  * /sw.js — o service worker (na RAIZ do site, para valer em todas as páginas): rede primeiro,
    e a última cópia de cada página quando a rede cair;
  * os ícones PNG em atendimentos/static/atendimentos/.
O iniciar.sh abre o site em modo app (Edge/Chrome --app=URL) quando PWA=1 no web/.env.
Em 127.0.0.1 o navegador já considera o site "seguro" (exigência do service worker).
"""
import json

from django.http import HttpResponse
from django.templatetags.static import static

SERVICE_WORKER = """
const CACHE = "pwa-atendimentos-v1";
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
    """O "RG" do app: o navegador lê isto para instalar e abrir em janela própria."""
    dados = {
        "name": "Sistema Exemplo",
        "short_name": "Sistema",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0c0c0c",
        "theme_color": "#0c0c0c",
        "icons": [{"src": static("atendimentos/icone-192.png"), "sizes": "192x192", "type": "image/png"},
                  {"src": static("atendimentos/icone-512.png"), "sizes": "512x512", "type": "image/png"}],
    }
    return HttpResponse(json.dumps(dados, ensure_ascii=False), content_type="application/manifest+json")


def service_worker(request):
    resposta = HttpResponse(SERVICE_WORKER, content_type="application/javascript")
    resposta["Service-Worker-Allowed"] = "/"
    return resposta

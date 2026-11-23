"""Configuração MÍNIMA do Django só para servir a tela do SGS (python manage.py runserver).

Sem banco, sem sessão, sem login, sem arquivos estáticos: a tela inteira (página, rotas, segurança, gzip) mora em
tela_prompt.py e é a mesma do `python tela_prompt.py`. Daqui só sai: quem pode chamar (127.0.0.1/localhost),
a view única (sgs_web.urls) e o log curto no terminal.
"""
import secrets
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent          # Gerador_Sistemas/
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))                        # tela_prompt, gerar_sistema… ficam ao lado

# Nada é assinado (sem sessões, cookies ou formulários do Django): uma chave nova a cada execução basta.
SECRET_KEY = secrets.token_urlsafe(50)
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]                  # a tela só atende a própria máquina

INSTALLED_APPS = ["sgs_web"]                                # o runserver do SGS (porta 6100, abre a janela)
MIDDLEWARE = []                                             # a segurança é a da tela: Host + POST só em JSON
ROOT_URLCONF = "sgs_web.urls"
WSGI_APPLICATION = "sgs_web.wsgi.application"
DATABASES = {}                                              # a tela não usa banco (os sistemas gerados usam o deles)

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = False
USE_TZ = True


def _so_o_que_importa(registro):
    """Uma linha por comando executado (POST /comando, /gerar) e os erros — como no tela_prompt.py
    (cada tecla busca sugestões: logar todo GET encheria o terminal)."""
    mensagem = registro.getMessage()
    return ('"POST /comando' in mensagem or '"POST /gerar' in mensagem
            or getattr(registro, "status_code", 200) >= 400)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"sgs": {"()": "django.utils.log.CallbackFilter", "callback": _so_o_que_importa}},
    "formatters": {"sgs": {"()": "django.utils.log.ServerFormatter", "format": "  [{server_time}] {message}",
                           "style": "{"}},
    "handlers": {"sgs": {"class": "logging.StreamHandler", "filters": ["sgs"], "formatter": "sgs"}},
    "loggers": {"django.server": {"handlers": ["sgs"], "level": "INFO", "propagate": False}},
}

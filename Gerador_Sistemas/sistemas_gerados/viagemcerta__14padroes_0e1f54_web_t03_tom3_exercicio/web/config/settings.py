"""Configuração do projeto Django (gerada). Valores sensíveis vêm do web/.env (modelo: web/.env.example)."""
import os
import sys
from pathlib import Path

from .env import carregar_env

BASE_DIR = Path(__file__).resolve().parent.parent
# O núcleo em Python puro (pasta ../nucleo) é usado pelo app: põe a pasta do sistema no path.
sys.path.insert(0, str(BASE_DIR.parent))
# Lê web/.env (se existir) para os.environ, sem sobrescrever o que já veio do ambiente.
carregar_env(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "somente-para-estudo-troque-no-env")
DEBUG = os.environ.get("DEBUG", "0") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
ADMIN_URL = os.environ.get("ADMIN_URL", "gestao/")  # endereço do Django Admin (lido em config/urls.py)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "viagcerts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino do `manage.py collectstatic` (publicação)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------------------------
# Segurança — baseline das Instruções de desenvolvimento DJANGO (§12.3, §13, §14, §16.1).
# Valores SEGUROS por padrão; o web/.env local relaxa o que precisa (DEBUG=1 → sem HTTPS forçado).
# ---------------------------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [origem for origem in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origem]
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "0" if DEBUG else "1") == "1"
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0" if DEBUG else "3600"))
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", "1048576"))  # 1 MiB
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ.get("DATA_UPLOAD_MAX_NUMBER_FIELDS", "500"))

# CSP nativa do Django 6 (§14): allowlist só com 'self' (o Bootstrap é servido daqui, sem CDN).
# Começa em Report-Only (§14.4); CSP_IMPOR=1 no web/.env passa a IMPOR a mesma política.
from django.utils.csp import CSP  # noqa: E402

_POLITICA_CSP = {
    "default-src": [CSP.SELF], "script-src": [CSP.SELF, CSP.NONCE], "style-src": [CSP.SELF, CSP.NONCE],
    "img-src": [CSP.SELF, "data:"], "font-src": [CSP.SELF], "connect-src": [CSP.SELF], "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF], "form-action": [CSP.SELF], "frame-ancestors": [CSP.NONE],
}
if os.environ.get("CSP_IMPOR") == "1":
    SECURE_CSP = _POLITICA_CSP
else:
    SECURE_CSP_REPORT_ONLY = _POLITICA_CSP
MIDDLEWARE.append("django.middleware.csp.ContentSecurityPolicyMiddleware")
TEMPLATES[0]["OPTIONS"]["context_processors"].append("django.template.context_processors.csp")

# Senhas com Argon2id (§16.1) quando o argon2-cffi estiver instalado (está no requirements.txt).
try:
    import argon2  # noqa: F401
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.Argon2PasswordHasher",
                        "django.contrib.auth.hashers.PBKDF2PasswordHasher"]
except ImportError:  # sem o pacote: fica o PBKDF2 do Django — rode: pip install -r requirements.txt
    pass

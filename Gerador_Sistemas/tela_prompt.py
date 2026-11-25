#!/usr/bin/env python3
"""
SGS - Sistema Gerador de Sistema · a TELA estilo terminal (ILP-037 · P3).

Sem IA e sem instalar nada: só a biblioteca padrão do Python (http.server).
O que a caixa aceita:
  * sgs gerar <pedido>      → GERA um sistema (único jeito de gerar: texto solto só é ANOTADO na tela);
  * sgs <comando>           → configura, lista, numera, testa, sobe/derruba sites, explica (sgs comand);
  * comandos do terminal    → cd, ls, pwd, source .venv/bin/activate, python manage.py migrate/runserver,
                              pytest, bash iniciar.sh… — com ou sem "sgs" na frente (módulo sgs_terminal.py).
Numeração FIXA: cada sistema recebe o seu número (01, 02, …) no momento da geração. O SGS (esta tela) é o 00
e roda na porta 6100; o sistema 01 roda na 6101, o 02 na 6102, e assim por diante.
EDIÇÃO × DUPLICAÇÃO: editar um sistema (sgs editar NN · sgs app NN · sgs ligar NN · sgs incrementar NN) altera
DIRETAMENTE o sistema NN indicado. Para criar uma CÓPIA versionada 01.1, 01.2 … 01.99 sem mexer no original, use
explicitamente `sgs duplicar NN`. A porta da cópia é a do sistema com o último dígito da versão no fim: 01.3 → 61013;
01.9, 01.19 … 01.99 → 61019 (por isso a base é 6100: 6199 + 1 dígito ainda cabe nas 65.535 portas).
PWA: a tela e os sites abrem numa janela de app isolada (Edge/Chrome --app); sgs pwa=false → aba comum.

Como rodar (no WSL, com o .venv ativado) — dois jeitos, a MESMA tela (as rotas moram em atender()):
    python manage.py runserver                           → Django (da raiz ou de Gerador_Sistemas): porta 6100, PWA
    python Gerador_Sistemas/tela_prompt.py              → biblioteca padrão (http.server), mesma porta
    … --sem-abrir                                        → nos dois: só sobe o servidor

Arquitetura (Aula 07): a tela é uma VIEW FINA. A geração mora em gerar_sistema.py, o terminal em
sgs_terminal.py e o help numerado em sgs_comand.py; aqui ficam o roteamento dos comandos e a página.
"""
import argparse
import atexit
import gzip
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, unquote, urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))  # os módulos do SGS estão ao lado deste arquivo
import gerar_sistema as gs  # noqa: E402
import sgs_comand  # noqa: E402
import sgs_dominios as modulo_dominios  # noqa: E402
import sgs_perguntas as perguntas  # noqa: E402
import sgs_terminal as terminal  # noqa: E402
import temas_web  # noqa: E402
import sgs_tutorial  # noqa: E402
import sgs_wysiwyg  # noqa: E402
import tipos_campos  # noqa: E402

NOME_SGS = "SGS - Sistema Gerador de Sistema"
RAIZ_PROJETO = AQUI.parent
PORTA_PADRAO = 6100            # o SGS é o "00": porta 6100; o sistema NN roda em porta_base + NN
PORTA_ANTIGA = 8100            # padrão anterior: um sgs_config.json salvo com ela passa para a 6100
MAX_VERSOES = 99               # 01.1 … 01.99
CONFIG_PADRAO = AQUI / "sgs_config.json"
REGISTRO = ".sgs_registro.json"  # números fixos dos sistemas e das versões (fica em sistemas_gerados/)
SERVIDORES = ".sgs_servidores.json"  # sites no ar (pid e porta): libera as portas se a tela cair sem limpar
IGNORAR_NA_COPIA = {".venv", "__pycache__", ".pytest_cache", "staticfiles", "servidor.log"}
REFERENCIA = AQUI / gs.REFERENCIA_GOF
# As cópias de referência (Wiki GoF e Django Study Hub) são servidas da PRÓPRIA pasta, como estão no disco: assim
# os caminhos relativos delas (CSS, imagens) funcionam. /referencia e /hub levam até elas.
PASTA_REFERENCIAS = AQUI / "referencias"
PAGINAS_REFERENCIA = {"/referencia": "wikipedia_padrao_de_projeto_de_software.html",
                      "/wiki": "wikipedia_padrao_de_projeto_de_software.html", "/hub": "django_study_hub.html"}
TIPOS_ESTATICOS = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                   ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
                   ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon"}
COMPRIMIR_ACIMA = 16_000                       # bytes: daí para cima, texto vai em gzip (se o navegador aceitar)
TIPOS_COMPRIMIVEIS = ("text/", "application/javascript", "application/json", "image/svg+xml")
LIMITE_PEDIDO = 600
LIMITE_CORPO = 10_000
LIMITE_ARQUIVO = 300_000
HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}
# Nunca listados nem abertos pelo visualizador de arquivos (o .env tem a senha do admin e a chave secreta).
IGNORAR = {"__pycache__", ".pytest_cache", ".venv", "staticfiles", gs.MARCADOR, "db.sqlite3", ".env",
           "servidor.log"}
NAVEGADORES = ["/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
               "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
               "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
               "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe"]
PERFIL_NAVEGADOR = r"SGS\navegador"        # dentro do %LOCALAPPDATA% do Windows: o perfil SÓ das janelas do SGS
OPCOES_CAIXA = ("django", "exercicio", "testar", "estudo", "comentarios", "comentarios_web", "perguntar")
OPCOES_WEB = tuple(gs.WEB_PADRAO)          # estilo, tema, tom, paleta, comentarios_web, id_publico…

# Um comando por vez: dois cliques no mesmo pedido gerariam a MESMA pasta ao mesmo tempo.
TRAVA = threading.Lock()


# =============================================================================
# 1. CONFIGURAÇÃO (o que "sgs config" mostra e altera; salva em JSON)
# =============================================================================
CONFIG_INICIAL = {
    "django": False, "exercicio": False, "testar": True, "estudo": True, "comentarios": True,
    "comentarios_web": False, "perguntar": False, "estilo": "web", "tema": "T01", "tom": "tom3", "paleta": "P02",
    "id_publico": "inteiro", "id_interno": False, "lnnl_tipo": "21", "estrutura": "plana", "seguranca": "basica",
    "banco": "sqlite3", "redis": False, "argon2": False, "fernet": False,
    "two_factor": False, "two_factor_expiracao": 10, "recuperacao_senha": False,
    "rbac": False, "antibot": False,
    "ratelimit": False, "anymail": False, "tinymce": False,
    "pwa": True, "porta_base": PORTA_PADRAO, "admin_usuario": "admin", "admin_email": "admin@exemplo.com",
    "admin_senha": "admin123", "visual": "cmd", "topo": True, "rodape": True,
}
# Valores fechados (listas): nada de texto livre vira CSS ou código.
ESCOLHAS = {"estilo": list(gs.ESTILOS), "tema": list(temas_web.TEMAS), "tom": temas_web.TONS,
            "paleta": list(temas_web.PALETAS), "id_publico": ["inteiro", "uuid"], "estrutura": ["plana", "apps"],
            "seguranca": ["basica", "baseline"], "banco": list(gs.BANCOS_DADOS), "visual": ["cmd", "sgs"]}
EXPLICA_CONFIG = {
    "django": "gerar também o site Django (caixa “+ Django”)",
    "exercicio": "modo exercício: questionário de revisão (exercicios.html, resposta oculta em “Ver resposta”); o código sai completo",
    "testar": "rodar os testes logo depois de gerar",
    "estudo": "sim = para estudo (antes_*.py, ADRs, README didático) · não = só gerar",
    "comentarios": "sim = comentários no CÓDIGO · não = apenas o código",
    "comentarios_web": "sim = notas de APRESENTAÇÃO nas páginas web (caixa “Notas na web”)",
    "perguntar": "sim = sgs gerar faz perguntas antes (rodadas de 10); sgs gerar -sp gera direto",
    "estilo": "formatação das páginas: simples · cmd (tela preta) · bootstrap · web (Bootstrap + temas)",
    "tema": "tema do estilo web: T01 a T10 (pasta temas/) — veja sgs tema",
    "tom": "variação do tema: claro, tom2, tom3, tom4, tom5, escuro",
    "paleta": "paleta do T10 Personalizado: P01 a P20 (Instruções §11.9)",
    "id_publico": "inteiro (padrão Django) · uuid (UUIDv4 — Instruções §10.4)",
    "id_interno": "sim = código LNNL legível em cada registro (motor-id-interno)",
    "lnnl_tipo": "código de tipo do LNNL: 2 dígitos de 1 a 9, nunca 93",
    "estrutura": "plana (web/<app>) · apps (apps/<app> + README — Instruções §9.2)",
    "seguranca": "basica · baseline (Instruções §12–14: cabeçalhos, cookies, CSP, ADMIN_URL)",
    "banco": "banco de dados principal: sqlite3 · postgresql · mongodb (com fallback local para SQLite3 nos testes)",
    "redis": "sim = configura cache distribuído com Redis (django-redis; fallback LocMemCache local)",
    "argon2": "sim = hash de senhas com Argon2id (argon2-cffi, §16.1)",
    "fernet": "sim = criptografia simétrica Fernet em repouso (config/crypto.py, §18.1)",
    "two_factor": "sim = autenticação em dois fatores 2FA com expiração configurável (config/twofactor.py)",
    "two_factor_expiracao": "tempo de expiração do código 2FA em minutos (1 a 60)",
    "recuperacao_senha": "sim = rotas de recuperação de usuário e senha (/conta/password_reset/)",
    "rbac": "sim = controle de acesso baseado em papéis RBAC (admin/gestor/operador/leitor, §17.4)",
    "antibot": "sim = proteção Anti-Bot com honeypot, tempo mínimo e gancho de provedor (config/antibot.py)",
    "ratelimit": "sim = limitação de taxa na aplicação (django-ratelimit, §19)",
    "anymail": "sim = envio transacional de e-mail via django-anymail",
    "tinymce": "sim = editor rich-text django-tinymce para campos de texto longo",
    "pwa": "sim = sites abrem em janela de app isolada (PWA) · não = aba comum (sgs pwa=false)",
    "porta_base": "o SGS é o 00 nesta porta; o sistema NN roda em porta_base + NN",
    "admin_usuario": "superusuário do Django criado pelo sgs rodar",
    "admin_email": "e-mail do superusuário",
    "admin_senha": "senha do superusuário (mín. 6 caracteres; vai para o web/.env do sistema)",
    "visual": "o estilo desta tela: cmd (o padrão ao abrir: como o Prompt de Comando do Windows — preto e cinza) · "
              "sgs (as cores do SGS, prompt verde) — mude com sgs cmd / sgs cmd sgs",
    "topo": "os comandos principais no topo da tela (sgs topo alterna; a tela abre com eles à mostra)",
    "rodape": "as caixas de seleção embaixo do prompt (sgs foot alterna; a tela abre com elas à mostra; a linha do comando "
              "sempre fica)",
}
SIM = {"sim", "s", "true", "1", "on", "yes", "y"}
NAO = {"nao", "não", "n", "false", "0", "off", "no"}


class Config:
    """Configuração da tela. Cada valor é validado antes de entrar (como um setter)."""

    def __init__(self, caminho=CONFIG_PADRAO):
        self.caminho = Path(caminho)
        self.valores = dict(CONFIG_INICIAL)
        try:
            salvos = json.loads(self.caminho.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            salvos = {}
        for chave, valor in (salvos.items() if isinstance(salvos, dict) else []):
            if chave in CONFIG_INICIAL and type(valor) is type(CONFIG_INICIAL[chave]):
                self.valores[chave] = valor
        if self.valores["porta_base"] == PORTA_ANTIGA:
            # A base mudou de 8100 para 6100: com 8100 as portas das versões (81011…) passariam de 65535.
            self.valores["porta_base"] = PORTA_PADRAO
        if self.valores["visual"] not in ESCOLHAS["visual"]:     # "powershell" (o nome antigo) → cmd
            self.valores["visual"] = CONFIG_INICIAL["visual"]

    def alterar(self, chave, valor):
        """Valida e troca UMA chave. O valor pode vir como texto (do sgs) ou já no tipo certo (da caixa)."""
        if chave not in CONFIG_INICIAL:
            raise ValueError(f"chave desconhecida: {chave!r} (veja: sgs config)")
        modelo = CONFIG_INICIAL[chave]
        if isinstance(modelo, bool):
            texto = str(valor).strip().lower()
            if isinstance(valor, bool):
                novo = valor
            elif texto in SIM:
                novo = True
            elif texto in NAO:
                novo = False
            else:
                raise ValueError(f"{chave}: use sim ou não (true/false)")
        elif isinstance(modelo, int):
            try:
                novo = int(valor)
            except (TypeError, ValueError):
                raise ValueError(f"{chave}: use um número inteiro") from None
            if chave == "two_factor_expiracao":
                if not 1 <= novo <= 60:
                    raise ValueError(f"{chave}: use um número entre 1 e 60 minutos")
            elif not 1024 <= novo <= 65000:
                raise ValueError(f"{chave}: use um número entre 1024 e 65000")
        elif chave in ESCOLHAS:
            novo = str(valor).strip()
            novo = novo.upper() if chave in ("tema", "paleta") else novo.lower()
            if novo not in ESCOLHAS[chave]:
                raise ValueError(f"{chave}: use {', '.join(ESCOLHAS[chave])}")
        elif chave == "lnnl_tipo":
            novo = str(valor).strip()
            if not re.fullmatch(r"[1-9]{2}", novo) or novo == "93":
                raise ValueError("lnnl_tipo: dois dígitos de 1 a 9 (11–99, sem zero), e nunca 93")
        else:
            novo = str(valor).strip()
            if not novo or any(ord(c) < 32 for c in novo):
                raise ValueError(f"{chave}: texto vazio ou com caractere inválido")
            if chave == "admin_senha" and len(novo) < 6:
                raise ValueError("admin_senha: use pelo menos 6 caracteres")
            if chave == "admin_usuario" and not re.fullmatch(r"[\w.@+-]{1,150}", novo):
                raise ValueError("admin_usuario: letras, números e . @ + - _ (sem espaço)")
            if chave == "admin_email" and not re.fullmatch(r"[^@\s]+@[^@\s]+", novo):
                raise ValueError("admin_email: e-mail inválido")
        self.valores[chave] = novo

    def salvar(self):
        self.caminho.write_text(json.dumps(self.valores, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def publica(self):
        """O que a página recebe: tudo, menos a senha."""
        return {k: v for k, v in self.valores.items() if k != "admin_senha"}


# =============================================================================
# 2. SISTEMAS GERADOS: NÚMERO FIXO (01, 02…) dado na geração → a porta também não muda
# =============================================================================
def pasta_saida(saida=None):
    return Path(saida or gs.PASTA_PADRAO)


class Num(tuple):
    """Número de um sistema: 01 (o gerado) ou 01.3 (a 3ª versão — cópia editada — do 01).

    Compara igual ao inteiro quando não é versão (Num(1) == 1), para quem só conhece 01, 02…
    """
    __slots__ = ()

    def __new__(cls, base, versao=0):
        return super().__new__(cls, (int(base), int(versao)))

    @property
    def base(self):
        return self[0]

    @property
    def versao(self):
        return self[1]

    def __str__(self):
        return f"{self[0]:02d}" + (f".{self[1]}" if self[1] else "")

    def __eq__(self, outro):
        if isinstance(outro, int) and not isinstance(outro, bool):
            return self[1] == 0 and self[0] == outro
        return tuple.__eq__(self, outro)

    def __ne__(self, outro):
        return not self == outro

    __hash__ = tuple.__hash__

    @classmethod
    def ler(cls, texto):
        """"01", "1", "01.3" ou "1.3" → Num; outra coisa → None."""
        m = re.fullmatch(r"(\d{1,3})(?:\.(\d{1,2}))?", str(texto).strip())
        return cls(int(m.group(1)), int(m.group(2) or 0)) if m else None


def nn(numero):
    return str(numero) if isinstance(numero, Num) else f"{numero:02d}"


def porta_de(numero, porta_base):
    """Porta do sistema: porta_base + NN (01 → 6101). Versão: a mesma com o ÚLTIMO dígito da versão no fim
    (01.3 → 61013; 01.9, 01.19 … 01.99 → 61019 — elas dividem a porta e a tela pergunta antes de trocar)."""
    numero = numero if isinstance(numero, Num) else Num(numero)
    principal = porta_base + numero.base
    if not numero.versao:
        return principal
    porta = int(f"{principal}{numero.versao % 10}")
    if porta > 65535:
        raise ValueError(f"a versão {numero} cairia na porta {porta}, acima de 65535 — com versões, a porta_base "
                         f"precisa ser no máximo {6552 - numero.base} (padrão {PORTA_PADRAO}: sgs config "
                         f"porta_base={PORTA_PADRAO})")
    return porta


def ler_registro(base):
    try:
        dados = json.loads((base / REGISTRO).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        dados = {}
    return dados if isinstance(dados, dict) else {}


def gravar_registro(base, dados):
    registro = {"proximo": dados["proximo"],
                "sistemas": dict(sorted(dados["sistemas"].items(), key=lambda par: par[1]))}
    if dados.get("versoes"):
        registro["versoes"] = dict(sorted(dados["versoes"].items(), key=lambda par: tuple(par[1])))
    (base / REGISTRO).write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def versoes_do_registro(dados):
    """{pasta: Num(base, versão)} das cópias versionadas (registradas por sgs duplicar)."""
    versoes = dados.get("versoes")
    if not isinstance(versoes, dict):
        return {}
    return {nome: Num(*par) for nome, par in versoes.items()
            if isinstance(par, list) and len(par) == 2 and all(isinstance(x, int) and x > 0 for x in par)}


def numerar(saida=None):
    """{pasta: número} dos sistemas GERADOS existentes (as versões ficam de fora: veja numeros()).

    O número é dado no momento da GERAÇÃO e nunca muda (nem é reaproveitado): por isso a porta do
    sistema (porta_base + número) também não muda quando aparece outro sistema. Pastas geradas fora da
    tela (pela linha de comando) ganham o próximo número na ordem em que foram criadas.
    """
    base = pasta_saida(saida)
    if not base.is_dir():
        return {}
    dados = ler_registro(base)
    versoes = versoes_do_registro(dados)
    pastas = [p for p in base.iterdir() if p.is_dir() and (p / gs.MARCADOR).exists() and p.name not in versoes]
    numeros = {k: v for k, v in (dados.get("sistemas") or {}).items() if isinstance(v, int) and v > 0}
    proximo = max([dados.get("proximo", 1) if isinstance(dados.get("proximo"), int) else 1]
                  + [n + 1 for n in numeros.values()])
    novas = sorted((p for p in pastas if p.name not in numeros),
                   key=lambda p: ((p / gs.MARCADOR).stat().st_mtime, p.name))
    for pasta in novas:
        numeros[pasta.name] = proximo
        proximo += 1
    if novas:
        gravar_registro(base, {"proximo": proximo, "sistemas": numeros, "versoes": dados.get("versoes")})
    existentes = {p.name for p in pastas}
    return {nome: n for nome, n in numeros.items() if nome in existentes}


def numeros(saida=None):
    """{pasta: Num} de TODOS os sistemas existentes: os gerados (01) e as versões (01.3)."""
    base = pasta_saida(saida)
    tudo = {nome: Num(n) for nome, n in numerar(saida).items()}
    if base.is_dir():
        for nome, numero in versoes_do_registro(ler_registro(base)).items():
            if (base / nome / gs.MARCADOR).exists():
                tudo[nome] = numero
    return tudo


def sistemas(saida=None):
    """[(Num, pasta)] em ordem de NÚMERO (01, 01.1, 01.2, 02…)."""
    base = pasta_saida(saida)
    return sorted(((n, base / nome) for nome, n in numeros(saida).items()), key=lambda par: tuple(par[0]))


def nova_versao(origem, porta_base, saida=None):
    """EDITAR = COPIAR: a pasta do sistema (01 ou 01.k) vira a próxima versão do 01 (<pasta do 01>_v<k>).

    O original não muda. Vão junto o banco (db.sqlite3) e o web/.env (com a PORTA da versão); ficam de fora
    o .venv, os caches e o log. Devolve (pasta nova, Num).
    """
    base = pasta_saida(saida)
    atual = numeros(saida).get(origem.name)
    if atual is None:
        raise ValueError(f"{origem.name} não é um sistema numerado (veja: sgs listar)")
    dados = ler_registro(base)
    usadas = [v.versao for v in versoes_do_registro(dados).values() if v.base == atual.base]
    versao = max(usadas, default=0) + 1                  # número de versão nunca é reaproveitado
    if versao > MAX_VERSOES:
        raise ValueError(f"o sistema {nn(atual.base)} já tem {MAX_VERSOES} versões (o limite é {atual.base:02d}.99)")
    numero = Num(atual.base, versao)
    porta = porta_de(numero, porta_base)                 # erro ANTES de copiar, se a porta não couber
    nome_base = re.sub(r"_v\d+$", "", origem.name) if atual.versao else origem.name
    destino = base / f"{nome_base}_v{versao}"
    if destino.exists():
        raise ValueError(f"a pasta {destino.name} já existe — apague-a ou renomeie antes de criar a versão")
    shutil.copytree(origem, destino, symlinks=True,
                    ignore=lambda _pasta, nomes: [n for n in nomes if n in IGNORAR_NA_COPIA])
    versoes = dados.get("versoes") if isinstance(dados.get("versoes"), dict) else {}
    versoes[destino.name] = [numero.base, numero.versao]
    numerados = {k: v for k, v in (dados.get("sistemas") or {}).items() if isinstance(v, int) and v > 0}
    gravar_registro(base, {"proximo": dados.get("proximo", max(numerados.values(), default=0) + 1),
                           "sistemas": numerados, "versoes": versoes})
    env = destino / "web" / ".env"
    if env.exists():
        texto_env = env.read_text(encoding="utf-8")
        if re.search(r"(?m)^PORTA=", texto_env):
            texto_env = re.sub(r"(?m)^PORTA=.*$", f"PORTA={porta}", texto_env)
        else:
            texto_env += ("" if texto_env.endswith("\n") or not texto_env else "\n") + f"PORTA={porta}\n"
        env.write_text(texto_env, encoding="utf-8")
    readme = destino / "README.md"
    if readme.exists():
        with open(readme, "a", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(f"\n\n## Versão {numero}\n\nCópia do sistema {atual} feita pelo SGS (`sgs duplicar`): o original "
                          f"não mudou. Esta versão roda na porta {porta} (a do {nn(atual.base)} é "
                          f"{porta_de(Num(atual.base), porta_base)}).\n")
    return destino, numero


def numero_de(destino, saida=None):
    """Num do sistema (01 ou 01.3) cuja pasta é `destino`, ou None."""
    return numeros(saida).get(Path(destino).name)


def caminho_exibido(destino):
    destino = Path(destino).resolve()
    return destino.relative_to(RAIZ_PROJETO).as_posix() if destino.is_relative_to(RAIZ_PROJETO) else str(destino)


def listar_arquivos(destino):
    """Arquivos do sistema (relativos à pasta), em ordem fixa, sem caches nem segredos."""
    return sorted(p.relative_to(destino).as_posix() for p in destino.rglob("*")
                  if p.is_file() and not IGNORAR.intersection(p.relative_to(destino).parts))


def ler_spec(destino):
    try:
        spec = json.loads((destino / "especificacao.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        spec = {}
    return spec if isinstance(spec, dict) else {}


def info_sistema(destino):
    """Resumo de um sistema já gerado, lido do disco (especificacao.json + pastas)."""
    spec = ler_spec(destino)
    return {"pasta": destino.name, "sistema": spec.get("sistema", destino.name), "entidade": spec.get("entidade", "?"),
            "padroes": [p for p in spec.get("padroes", []) if p in gs.PADROES],
            "django": (destino / "web" / "manage.py").exists(), "exercicio": (destino / "exercicios.html").exists(),
            "estudo": spec.get("estudo", True), "comentarios": spec.get("comentarios", True)}


def admin_url(destino):
    """Endereço do Django Admin do sistema (ADMIN_URL do web/.env, ou do .env.example)."""
    for nome in (".env", ".env.example"):
        try:
            for linha in (destino / "web" / nome).read_text(encoding="utf-8").splitlines():
                if linha.startswith("ADMIN_URL="):
                    return linha.split("=", 1)[1].strip() or "admin/"
        except FileNotFoundError:
            continue
    return "admin/"


def apps_django(destino):
    """Apps Django do sistema: a principal primeiro, depois os módulos criados por sgs app (na ordem)."""
    web = destino / "web"
    achadas = [p.parent.name for p in sorted(web.glob("*/apps.py"))] + \
              [p.parent.name for p in sorted(web.glob("apps/*/apps.py"))]
    modulos = [m["app"] for m in gs.ler_modulos(destino)]
    return [a for a in achadas if a not in modulos] + [m for m in modulos if m in achadas]


def app_django(destino):
    return next(iter(apps_django(destino)), "app")


def ler_arquivo(pasta, caminho, saida=None):
    """Texto de UM arquivo gerado. Só dentro de uma pasta criada pelo gerador; '..' e segredos são recusados."""
    base = pasta_saida(saida).resolve()
    sistema = (base / (pasta or "")).resolve()
    if not pasta or sistema.parent != base or not (sistema / gs.MARCADOR).exists():
        return {"ok": False, "erro": "Pasta não encontrada (só abro sistemas criados pelo gerador)."}
    alvo = (sistema / (caminho or "")).resolve()
    if not alvo.is_relative_to(sistema) or not alvo.is_file() or IGNORAR.intersection(alvo.relative_to(sistema).parts):
        return {"ok": False, "erro": "Arquivo não encontrado nesta pasta."}
    if alvo.stat().st_size > LIMITE_ARQUIVO:
        return {"ok": False, "erro": "Arquivo grande demais para mostrar aqui — abra no editor."}
    try:
        return {"ok": True, "conteudo": alvo.read_text(encoding="utf-8")}
    except UnicodeDecodeError:
        return {"ok": False, "erro": "Este arquivo não é texto."}


def cartao(destino, info, saida=None, porta_base=PORTA_PADRAO, **extra):
    """Dados que a página desenha como "cartão" de um sistema (gerado agora ou aberto com sgs info)."""
    numero = numero_de(destino, saida)
    try:
        porta = porta_de(numero, porta_base) if numero else None
    except ValueError:
        porta = None                                    # porta_base alta demais para a versão
    return {"ok": True, "pasta": destino.name, "numero": nn(numero) if numero else None,
            "porta": porta, "caminho": caminho_exibido(destino),
            "modulos": [m["app"] for m in gs.ler_modulos(destino)],
            "sistema": info["sistema"], "entidade": info["entidade"],
            "padroes": [{"chave": p, "titulo": gs.PADROES[p]["titulo"], "palavras": []} for p in info["padroes"]],
            "django": info["django"], "exercicio": info["exercicio"], "estudo": info["estudo"],
            "comentarios": info["comentarios"], "arquivos": listar_arquivos(destino), "testes": [], **extra}


# =============================================================================
# 3. GERAR (sgs gerar <pedido> · sgs gerar <domínio> <padrões…>)
# =============================================================================
def processar(texto=None, django=False, exercicio=False, testar=True, saida=None, estudo=True, comentarios=True,
              dominio=None, padroes=None, porta_base=PORTA_PADRAO, sistema=None, entidade=None, web=None,
              campos=None, regerar_fixa=False):
    """Gera e devolve o cartão do sistema (pronto para virar JSON). O número fixo é dado aqui.

    campos: campos a mais da entidade ([{"nome", "tipo"}] do questionário); sem eles, valem os que o pedido listar.

    Com `texto`: vira --assunto (domínio e padrões pelas palavras). Com `dominio`: escolha direta.
    forcar=True: a mesma entrada gera sempre os mesmos arquivos, e o gerador só substitui pastas que ELE criou.
    """
    texto = (texto or "").strip()
    if dominio is None:
        if not texto:
            return {"ok": False, "erro": "Diga o que gerar: sgs gerar loja com desconto por tipo de cliente"}
        if len(texto) > LIMITE_PEDIDO:
            return {"ok": False, "erro": f"Pedido longo demais ({len(texto)} caracteres; máximo {LIMITE_PEDIDO})."}
    try:
        destino, s = gs.gerar(assunto=texto or None, dominio=dominio, padroes=padroes, django=bool(django),
                              exercicio=bool(exercicio), saida=saida, forcar=True, estudo=bool(estudo),
                              comentarios=bool(comentarios), sistema=sistema, entidade=entidade, web=web,
                              campos=campos, regerar_fixa=regerar_fixa)
    except gs.ErroGerador as erro:
        return {"ok": False, "erro": str(erro)}
    o = s.origem
    info = {"sistema": s.sistema, "entidade": s.ent, "padroes": s.padroes, "django": s.django,
            "exercicio": s.exercicio, "estudo": s.estudo, "comentarios": s.comentarios}
    resposta = cartao(destino.resolve(), info, saida, porta_base)   # numera e lista ANTES dos testes
    motivos = o.get("padroes_palavras", {})
    for p in resposta["padroes"]:
        p["palavras"] = motivos.get(p["chave"], [])
    resposta["web"] = s.web if s.django else None
    resposta["campos"] = [{"nome": c["nome"], "tipo": c["tipo"], "rotulo": tipos_campos.rotulo(c["tipo"]),
                           "certeza": c["certeza"]} for c in o.get("campos", [])]
    resposta.update(dominio=o.get("dominio") or o.get("dominio_rotulo", ""), dominio_palavras=o.get("dominio_palavras", []),
                    por_assunto=bool(o.get("assunto")), sem_padrao=bool(o.get("sem_padrao")), notas=o.get("notas", []),
                    testes=gs.executar_testes(destino, s) if testar else [])
    return resposta


TERMINAL_SUGERIDOS = [   # comandos padrão (valem com e sem "sgs" na frente) — o que o intellisense oferece
    ("ls", "lista a pasta"), ("ls -la", "lista tudo, com detalhes"), ("cd ..", "sobe uma pasta"), ("cd ~", "volta à raiz"),
    ("cd -", "volta à pasta anterior"), ("pwd", "pasta atual"), ("tree -L 2", "árvore da pasta"),
    ("cat README.md", "mostra um arquivo"), ("head -n 20 ", "começo de um arquivo"), ("tail -n 20 ", "fim de um arquivo"),
    ("echo ", "imprime um texto"), ("whoami", "usuário"), ("date", "data e hora"), ("uname -a", "sistema operacional"),
    ("hostname", "nome da máquina"), ("which python", "qual python"), ("history", "histórico de comandos"),
    ("history -c", "limpa o histórico"), ("clear", "limpa a tela"), ("exit", "sai do módulo comand"),
    ("source .venv/bin/activate", "ativa o ambiente virtual"), ("deactivate", "desativa o ambiente virtual"),
    ("python --version", "versão do Python"), ("python -m pytest -q", "roda os testes da pasta"),
    ("python manage.py check", "confere o projeto Django"), ("python manage.py makemigrations", "cria as migrations"),
    ("python manage.py migrate", "aplica as migrations"), ("python manage.py showmigrations", "lista as migrations"),
    ("python manage.py garantir_admin", "cria/atualiza o superusuário"),
    ("python manage.py runserver", "sobe o site (porta do sistema)"), ("pip list", "pacotes instalados"),
    ("pip install -r requirements.txt", "confere as dependências"), ("bash iniciar.sh", "prepara e sobe o site"),
    ("bash rodar_testes.sh", "testes de todas as pastas"), ("git status", "o que mudou no git"),
    ("git log --oneline", "commits"),
]
POR_SISTEMA = [   # (comando, o que faz) para cada número de sistema: o intellisense já traz o número certo
    ("sgs info {n}", "detalhes"), ("sgs rodar {n}", "sobe o site"), ("sgs testar {n}", "roda os testes"),
    ("cd {n}", "entra na pasta"), ("sgs comandos {n}", "comandos de terminal"), ("sgs parar {n}", "derruba o site"),
    ("sgs editar {n}", "painel de edição (campos, ligações, módulos)"),
    ("sgs duplicar {n}", "duplica o sistema (cria cópia/versão)"),
    ("sgs app {n} ", "funcionalidade nova (módulo no próprio sistema)"),
    ("sgs ligar {n}", "ligar classes (campo de referência)"),
    ("sgs incrementar {n}", "incrementar/modificar campos"),
    ("sgs api config {n}", "campos de cada endpoint da API"),
]
SUGESTOES_FIXAS = [   # sempre as DUAS PRIMEIRAS do intellisense quando o que foi digitado é o começo delas (sgs…)
    ("sgs topo", "mostra/oculta os comandos principais no topo"),
    ("sgs foot", "mostra/oculta as caixas de seleção embaixo do prompt"),
]


def sugestoes(ctx, limite_historico=40):
    """Catálogo do INTELLISENSE da tela: {"cmd", "desc", "tipo"} em ordem de prioridade — histórico (mais recente
    primeiro), as pastas do cd, os comandos de cada sistema, os comandos sgs e os padrão (com e sem sgs).
    Quem filtra e ordena enquanto se digita é a página (até 5 sugestões, TAB completa)."""
    itens, vistos = [], set()

    def add(comando, descricao, tipo):
        if comando.strip() and comando not in vistos:
            vistos.add(comando)
            itens.append({"cmd": comando, "desc": descricao, "tipo": tipo})

    for comando, descricao in SUGESTOES_FIXAS:      # SEMPRE as duas primeiras ao digitar sgs (a página garante)
        add(comando, descricao, "fixo")
    for linha in reversed(ctx.historico.linhas()[-limite_historico:]):
        add(linha, "↺ do histórico", "historico")
    try:
        pastas = sorted(p.name for p in ctx.sessao.cwd.iterdir() if p.is_dir() and not p.name.startswith("."))
    except OSError:
        pastas = []
    for nome in pastas[:40]:
        add(f"cd {nome}", "entra na pasta", "pasta")
    for n, pasta in sistemas(ctx.saida):
        for modelo, descricao in POR_SISTEMA:
            add(modelo.format(n=nn(n)), f"{descricao} · {pasta.name}", "sistema")
    for rotulo, descricao, preencher in COMANDOS_SGS:
        base = re.split(r" \[| <| NN| \||  \(", rotulo)[0].strip()
        if "=" in base:
            base = base.split("=")[0] + "="
        add(base + (" " if preencher and not base.endswith("=") else ""), descricao, "sgs")
    for comando, descricao in (("sgs cmd sgs", "tela nas cores do SGS (prompt verde)"),
                               ("cmd", "tela no estilo do Prompt de Comando (= sgs cmd)"),
                               ("cmd sgs", "tela nas cores do SGS (= sgs cmd sgs)"),
                               ("sgs infra", "painel de Infra, Segurança & Bibliotecas (Passo 2)"),
                               ("sgs padroes arquitetura", "padrões no escopo Arquitetura (SRP, Service, MVVM)"),
                               ("sgs padroes classe", "padrões no escopo Classe (criação e comportamento)"),
                               ("sgs padroes campo", "padrões no escopo Campo (@property, Flyweight)"),
                               ("sgs padroes relacao", "padrões no escopo Ligação / FK (colaboração)"),
                               ("sgs config banco=postgresql", "usa PostgreSQL como banco principal"),
                               ("sgs config banco=mongodb", "usa MongoDB como banco principal"),
                               ("sgs config redis=sim", "ativa cache/sessões Redis (django-redis)"),
                               ("sgs config id_publico=uuid", "usa UUIDv4 na chave primária"),
                               ("sgs config id_interno=sim", "ativa motor-id-interno (LNNL)"),
                               ("sgs config estrutura=apps", "ativa estrutura modular apps/"),
                               ("sgs config seguranca=baseline", "ativa segurança baseline (§12–14: CSP, cookies, Argon2id)"),
                               ("sgs config argon2=sim", "ativa hash de senhas Argon2id"),
                               ("sgs config fernet=sim", "ativa criptografia Fernet em repouso"),
                               ("sgs config two_factor=sim", "ativa autenticação 2FA com expiração"),
                               ("sgs config recuperacao_senha=sim", "ativa rotas de recuperação de usuário/senha"),
                               ("sgs config rbac=sim", "ativa controle de acesso RBAC"),
                               ("sgs config antibot=sim", "ativa proteção Anti-Bot"),
                               ("sgs config ratelimit=sim", "ativa django-ratelimit (§19)"),
                               ("sgs config anymail=sim", "ativa envio transacional django-anymail"),
                               ("sgs config tinymce=sim", "ativa editor rich-text django-tinymce")):
        add(comando, descricao, "sgs")
    for comando, descricao in TERMINAL_SUGERIDOS:
        add(comando, descricao, "terminal")
        add(f"sgs {comando}", descricao + " (com sgs)", "terminal")
    return itens


def catalogo():
    """Domínios e padrões (por categoria) com as palavras que os ativam."""
    return {
        "dominios": [{"chave": c, "id": gs.INFO_DOMINIOS[c]["id"], "setor": gs.INFO_DOMINIOS[c]["setor"],
                      "sistema": d["sistema"], "entidade": d["entidade"], "palavras": d["palavras"][:8]}
                     for c, d in gs.DOMINIOS.items()],
        "categorias": [{"chave": cat, "nome": gs.NOMES_CATEGORIAS[cat],
                        "padroes": [{"chave": p, "titulo": gs.PADROES[p]["titulo"], "palavras": gs.PADROES[p]["palavras"][:6]}
                                    for p in membros]}
                       for cat, membros in gs.CATEGORIAS.items()],
    }


# =============================================================================
# 4. SITES NO AR (sgs rodar · python manage.py runserver · sgs parar) e o navegador (PWA)
# =============================================================================
def porta_livre(porta):
    """A porta aceita um servidor novo? SO_REUSEADDR = o mesmo teste que o runserver faz: as conexões em
    TIME_WAIT (os ~60 s depois de derrubar um site) NÃO contam como porta ocupada — só quem escuta nela."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", porta))
            return True
        except OSError:
            return False


def linha_de_comando(pid):
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip()
    except OSError:
        return ""


def vivo(pid):
    """O processo existe e não é zumbi (zumbi já soltou a porta; só falta o pai recolher)."""
    try:
        estado = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return False
    return estado != "Z"


def processo_na_porta(porta):
    """Quem ESCUTA na porta (Linux/WSL: /proc/net/tcp → inode do socket → /proc/<pid>/fd).

    Devolve None (ninguém escuta), {"pid": None, "cmd": ""} (escuta, mas o processo não é visível — outro
    usuário) ou {"pid": n, "cmd": "python manage.py runserver …"}.
    """
    inodes = set()
    for tabela in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            linhas = Path(tabela).read_text().splitlines()[1:]
        except OSError:
            continue
        for linha in linhas:
            campos = linha.split()
            if len(campos) > 9 and campos[3] == "0A" and int(campos[1].rsplit(":", 1)[1], 16) == porta:   # 0A = LISTEN
                inodes.add(f"socket:[{campos[9]}]")
    if not inodes:
        return None
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            for fd in (proc / "fd").iterdir():
                if os.readlink(fd) in inodes:
                    return {"pid": int(proc.name), "cmd": linha_de_comando(proc.name)}
        except OSError:
            continue
    return {"pid": None, "cmd": ""}


def encerrar_pid(pid, porta=None, segundos=8):
    """Encerra o processo que segura a porta (o GRUPO dele, se ele for o líder e não for o grupo do SGS).
    SIGTERM, espera a porta soltar e, se preciso, SIGKILL. Nunca encerra o próprio SGS. Devolve se liberou."""
    if not pid or pid in (1, os.getpid()):
        return False
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return True
    grupo = pgid == pid and pgid != os.getpgrp()

    def sinal(numero):
        try:
            if grupo:
                os.killpg(pgid, numero)
            else:
                os.kill(pid, numero)
        except ProcessLookupError:
            pass

    def soltou(limite):
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            if not vivo(pid) and (porta is None or porta_livre(porta)):
                return True
            time.sleep(0.2)
        return False

    try:
        sinal(signal.SIGTERM)
    except PermissionError:
        return False
    if soltou(segundos):
        return True
    sinal(signal.SIGKILL)
    return soltou(4)


def esperar_porta(porta, processo, segundos=40):
    """Espera o servidor aceitar conexões (ou o processo morrer)."""
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        if processo.poll() is not None:
            return False
        try:
            with socket.create_connection(("127.0.0.1", porta), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def ajustar_env(destino, cfg):
    """Escreve no web/.env do sistema o superusuário definido no sgs config (o resto do .env fica igual)."""
    arquivo = destino / "web" / ".env"
    novos = {"DJANGO_SUPERUSER_USERNAME": cfg["admin_usuario"], "DJANGO_SUPERUSER_EMAIL": cfg["admin_email"],
             "DJANGO_SUPERUSER_PASSWORD": cfg["admin_senha"]}
    linhas = arquivo.read_text(encoding="utf-8").splitlines() if arquivo.exists() else []
    feitos = set()
    for i, linha in enumerate(linhas):
        chave = linha.split("=", 1)[0].strip()
        if "=" in linha and chave in novos:
            linhas[i] = f"{chave}={novos[chave]}"
            feitos.add(chave)
    linhas += [f"{chave}={valor}" for chave, valor in novos.items() if chave not in feitos]
    arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def cauda(texto, n=12):
    return texto.strip().splitlines()[-n:]


def encerrar(processo):
    """Derruba o processo e os filhos dele (cada site roda num grupo de processos próprio)."""
    if processo.poll() is not None:
        return
    try:
        os.killpg(processo.pid, signal.SIGTERM)
    except (AttributeError, ProcessLookupError, PermissionError):
        processo.terminate()
    try:
        processo.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(processo.pid, signal.SIGKILL)
        except (AttributeError, ProcessLookupError, PermissionError):
            processo.kill()
        processo.wait(timeout=5)


_PERFIL = []


def perfil_do_navegador():
    """A pasta (Windows) do perfil só das janelas do SGS: %LOCALAPPDATA%\\SGS\\navegador.

    Num perfil próprio, sem extensões e sem o SGS instalado como app, a janela --app abre LIMPA: só o título e
    os botões da janela — sem o ícone de extensão e sem o menu ⋮ que o Chrome põe nos apps instalados.
    Sem o Windows por perto (cmd.exe), devolve "" e a janela abre no perfil de sempre."""
    if not _PERFIL:
        pasta = ""
        cmd = Path("/mnt/c/Windows/System32/cmd.exe")
        if cmd.exists():
            try:
                saida = subprocess.run([str(cmd), "/c", "echo %LOCALAPPDATA%"], cwd="/mnt/c", capture_output=True,
                                       text=True, timeout=10).stdout.strip()
            except (OSError, subprocess.SubprocessError):
                saida = ""
            if re.fullmatch(r"[A-Za-z]:\\[^%\r\n\"]+", saida):
                pasta = saida.rstrip("\\") + "\\" + PERFIL_NAVEGADOR
        _PERFIL.append(pasta)
    return _PERFIL[0]


def comando_janela_app(exe, url, perfil):
    """A linha que abre a janela de app: perfil próprio (sem extensões) quando há um; sem ele, só o --app (o
    --disable-extensions no perfil de sempre desligaria as extensões do navegador inteiro)."""
    if not perfil:
        return [exe, f"--app={url}"]
    return [exe, f"--user-data-dir={perfil}", "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            f"--app={url}"]


def abrir_no_navegador(url, pwa=True):
    """PWA: janela de app isolada das abas (Chrome/Edge --app, num perfil só do SGS). Sem PWA: aba comum.
    Devolve o que fez (ou None)."""
    exe = next((p for p in NAVEGADORES if os.access(p, os.X_OK)), None)
    quieto = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "stdin": subprocess.DEVNULL,
              "start_new_session": True}
    try:
        if pwa and exe:
            subprocess.Popen(comando_janela_app(exe, url, perfil_do_navegador()), cwd="/mnt/c", **quieto)
            return "aberto em modo PWA (janela de app isolada)"
        if shutil.which("wslview"):
            subprocess.Popen(["wslview", url], **quieto)
            return "aberto numa aba do navegador"
        cmd = Path("/mnt/c/Windows/System32/cmd.exe")
        if cmd.exists():
            subprocess.Popen([str(cmd), "/c", "start", "", url], cwd="/mnt/c", **quieto)
            return "aberto numa aba do navegador"
        if webbrowser.open(url):
            return "aberto no navegador"
    except OSError:
        pass
    return None


class Servidores:
    """Sites que a tela subiu (sgs rodar ou python manage.py runserver). Caem junto com a tela.

    Cada site é anotado em sistemas_gerados/.sgs_servidores.json (pid e porta): se a tela cair sem derrubar
    os sites (terminal fechado, processo morto), a PRÓXIMA tela encerra esses órfãos e as portas voltam a ficar livres.
    """

    def __init__(self, arquivo=None):
        self._ativos = {}   # chave (pasta do sistema) → {"processo", "porta", "destino"}
        self._trava = threading.Lock()
        self.arquivo = Path(arquivo) if arquivo else None

    def _anotar(self):
        """Grava os sites no ar (chamar com a trava). Sem nenhum, o arquivo some."""
        if self.arquivo is None or not self.arquivo.parent.is_dir():
            return
        dados = {c: {"pid": a["processo"].pid, "porta": a["porta"], "pasta": str(a["destino"])}
                 for c, a in self._ativos.items()}
        try:
            if dados:
                self.arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            else:
                self.arquivo.unlink(missing_ok=True)
        except OSError:
            pass

    def encerrar_orfaos(self):
        """Sites que uma tela ANTERIOR subiu e não derrubou: encerra e devolve [(chave, porta)] liberadas.
        Só encerra quem ainda é o mesmo runserver (pid reaproveitado por outro programa não é tocado)."""
        if self.arquivo is None or not self.arquivo.exists():
            return []
        try:
            dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            dados = {}
        liberadas = []
        for chave, info in (dados.items() if isinstance(dados, dict) else []):
            pid, porta = (info or {}).get("pid"), (info or {}).get("porta")
            if not (isinstance(pid, int) and isinstance(porta, int)) or not vivo(pid):
                continue
            comando = linha_de_comando(pid)
            if ("runserver" in comando or "iniciar.sh" in comando) and str(porta) in comando:
                if encerrar_pid(pid, porta):
                    liberadas.append((chave, porta))
        with self._trava:
            self._anotar()
        return liberadas

    def ativos(self):
        with self._trava:
            mortos = [c for c, a in self._ativos.items() if a["processo"].poll() is not None]
            for chave in mortos:
                del self._ativos[chave]          # terminou sozinho (erro ou Ctrl+C): a porta já está solta
            if mortos:
                self._anotar()
            return dict(self._ativos)

    def ambiente(self):
        """Usa o Python da tela se ele já tem Django (rápido, sem internet); senão o iniciar.sh cria um .venv.
        ABRIR=0: quem abre o navegador é a tela (conforme sgs pwa), não o script."""
        env = dict(os.environ, RUNSERVER_OPCOES="--noreload", ABRIR="0")
        env.pop("DJANGO_SETTINGS_MODULE", None)
        if importlib.util.find_spec("django") and importlib.util.find_spec("pytest_django"):
            env["PY"] = sys.executable
        return env

    def _registrar(self, chave, processo, porta, destino, log):
        with self._trava:
            self._ativos[chave] = {"processo": processo, "porta": porta, "destino": destino}
            self._anotar()
        if not esperar_porta(porta, processo):
            self.parar(chave)
            return False, ["o servidor não respondeu — final do log:"] + cauda(log.read_text(encoding="utf-8"))
        return True, []

    def preparar(self, destino, cfg):
        """bash iniciar.sh env → o admin do sgs config no web/.env → bash iniciar.sh preparar (.venv/dependências,
        migrations, admin) — sem subir o servidor. Devolve (pronto?, linhas: o que cada passo disse ou o erro)."""
        env = self.ambiente()
        feitos = []
        for passo in ("env", "preparar"):
            if passo == "preparar":
                ajustar_env(destino, cfg)
            r = subprocess.run(["bash", "iniciar.sh", passo], cwd=destino, env=env, capture_output=True, text=True,
                               timeout=600)
            if r.returncode:
                return False, [f"falhou em: bash iniciar.sh {passo}"] + cauda(r.stdout + r.stderr)
            feitos += [linha.strip() for linha in r.stdout.splitlines() if linha.strip()]
        return True, feitos

    def iniciar(self, destino, porta, cfg, preparar=True):
        """sgs rodar: bash iniciar.sh env → admin do sgs config no .env → preparar → rodar (em segundo plano)."""
        if destino.name in self.ativos():
            return False, [f"já está rodando na porta {self._ativos[destino.name]['porta']}"]
        if not (destino / "web" / "manage.py").exists():
            return False, ["este sistema não tem o site Django — gere de novo com a caixa “+ Django” marcada"]
        if not (destino / "iniciar.sh").exists():
            return False, ["este sistema Django veio de uma versão antiga do gerador (sem iniciar.sh) — "
                           "faça o mesmo pedido de novo para ele ganhar o iniciar.sh, o .env e o admin"]
        if not porta_livre(porta):
            return False, [f"a porta {porta} está ocupada (veja quem usa: sgs servidores) — ou suba em outra: "
                           "sgs rodar NN <porta>"]
        env = self.ambiente()
        if preparar:
            pronto, mensagens = self.preparar(destino, cfg)
            if not pronto:
                return False, mensagens
        log = destino / "web" / "servidor.log"
        with open(log, "w", encoding="utf-8") as arquivo_log:
            processo = subprocess.Popen(["bash", "iniciar.sh", "rodar", str(porta)], cwd=destino, env=env,
                                        stdout=arquivo_log, stderr=subprocess.STDOUT, start_new_session=True)
        return self._registrar(destino.name, processo, porta, destino, log)

    def runserver(self, web, porta, chave, python):
        """python manage.py runserver, em segundo plano (sem preparar nada: igual ao comando do Django)."""
        if chave in self.ativos():
            return False, [f"já está rodando na porta {self._ativos[chave]['porta']} (sgs parar antes)"]
        if not porta_livre(porta):
            return False, [f"Error: That port is already in use. ({porta})"]
        log = web / "servidor.log"
        # Quando o SGS sobe via `python manage.py runserver`, o processo herda DJANGO_SETTINGS_MODULE=sgs_web.settings.
        # Removemos antes de lançar o runserver do sistema gerado para o manage.py dele carregar o próprio settings.
        env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
        with open(log, "w", encoding="utf-8") as arquivo_log:
            processo = subprocess.Popen([python, "manage.py", "runserver", f"127.0.0.1:{porta}", "--noreload"],
                                        cwd=web, env=env, stdout=arquivo_log, stderr=subprocess.STDOUT,
                                        start_new_session=True, stdin=subprocess.DEVNULL)
        return self._registrar(chave, processo, porta, web.parent, log)

    def parar(self, chave):
        with self._trava:
            ativo = self._ativos.pop(chave, None)
            self._anotar()
        if not ativo:
            return False
        encerrar(ativo["processo"])
        return True

    def parar_porta(self, porta):
        chave = next((c for c, a in self.ativos().items() if a["porta"] == porta), None)
        return self.parar(chave) if chave else False

    def parar_todos(self):
        for chave in list(self.ativos()):
            self.parar(chave)


# =============================================================================
# 5. CONTEXTO: o que os comandos (sgs e terminal) precisam
# =============================================================================
class Contexto:
    """Pasta dos sistemas, configuração, sites no ar e a sessão do terminal (pasta atual, .venv)."""

    def __init__(self, saida=None, config=None, raiz=RAIZ_PROJETO, porta_tela=PORTA_PADRAO, abrir_janelas=False,
                 caminho_dominios_extras=None):
        self.saida = pasta_saida(saida)
        self.config = config if isinstance(config, Config) else Config(config or CONFIG_PADRAO)
        self.servidores = Servidores(self.saida / SERVIDORES)
        self.sessao = terminal.Sessao(raiz)
        # Histórico GLOBAL de comandos (como o ~/.bash_history): fica ao lado do sgs_config.json e sobrevive ao F5.
        self.historico = terminal.Historico(self.config.caminho.parent / terminal.HISTORICO)
        self.porta_tela = porta_tela
        self.abrir_janelas = abrir_janelas      # False nos testes: nada de janelas abrindo sozinhas
        self.caminho_dominios_extras = caminho_dominios_extras
        self.questionario = None                # perguntas em andamento (sgs gerar com "perguntar" ligado)
        self.confirmacao = None                 # pergunta s/N pendente (ex.: forçar a porta ocupada)

    def porta_do(self, numero):
        """Porta do sistema 01 (porta_base + 1) ou da versão 01.3 (porta do 01 + último dígito da versão)."""
        return porta_de(numero, self.config.valores["porta_base"])

    def pasta_do_numero(self, numero):
        alvo = numero if isinstance(numero, Num) else (Num.ler(numero) if isinstance(numero, str) else Num(numero))
        return next((pasta for n, pasta in sistemas(self.saida) if n == alvo), None)

    def rotulo_de(self, destino):
        n = numero_de(destino, self.saida)
        return f"o sistema {nn(n)}" if n else Path(destino).name

    # ------------------------------------------------------------ porta ocupada: quem é e como liberar
    def dono_da_porta(self, porta):
        """None se a porta está livre; senão {"descricao", "encerrar"} (encerrar=None: a tela não consegue)."""
        if porta_livre(porta):
            return None
        for chave, a in self.servidores.ativos().items():
            if a["porta"] == porta:
                return {"descricao": f"{self.rotulo_de(a['destino'])} (site que a tela subiu)",
                        "encerrar": lambda c=chave: self.servidores.parar(c)}
        dono = processo_na_porta(porta)
        if dono is None or dono["pid"] is None:
            return {"descricao": "um processo que a tela não enxerga (outro usuário ou o Windows)", "encerrar": None}
        if dono["pid"] == os.getpid():
            return {"descricao": "o próprio SGS", "encerrar": None}
        comando = dono["cmd"] if len(dono["cmd"]) <= 160 else dono["cmd"][:157] + "…"
        return {"descricao": f"o processo {dono['pid']} ({comando or 'sem linha de comando'})",
                "encerrar": lambda pid=dono["pid"]: encerrar_pid(pid, porta)}

    def perguntar_forcar(self, porta, dono, rotulo_novo, subir):
        """Porta ocupada: pergunta (s/N) se encerra quem está nela e sobe o atual. `subir()` devolve a resposta."""
        if dono["encerrar"] is None:
            return falha(f"a porta {porta} está em uso por {dono['descricao']} — encerre por fora ou use outra "
                         "porta: sgs rodar NN <porta>")

        def confirmar():
            if not dono["encerrar"]():
                return falha(f"não consegui liberar a porta {porta} (sem permissão para encerrar {dono['descricao']})")
            resposta = subir()
            resposta.setdefault("blocos", []).insert(0, texto(f"✓ porta {porta} liberada ({dono['descricao']} "
                                                              "encerrado)", "ok"))
            return resposta

        self.confirmacao = {"rotulo": "forçar? s/N", "acao": confirmar,
                            "dica": f"s = encerra quem está na porta {porta} e sobe {rotulo_novo} · n (ou Enter) = deixa como está"}
        return ok(texto(f"A porta {porta} está em uso por {dono['descricao']}.", "aviso"),
                  texto(f"Forçar o encerramento e subir {rotulo_novo} no lugar? (s/N)", "destaque"),
                  bloco("botoes", itens=[cmd("s — encerrar e subir", "s"), cmd("n — deixar como está", "n")]))

    def reiniciar_site(self, destino, n):
        """Depois de MUDAR o sistema (api config, incrementar, ligar, app sem versão): se o site dele está no ar pela
        tela, derruba e sobe de novo na MESMA porta (preparando: migrations) — o servidor não recarrega sozinho.
        No ar por FORA da tela: só avisa. Fora do ar: nada."""
        destino = Path(destino)
        ativo = self.servidores.ativos().get(destino.name)
        if ativo:
            porta = ativo["porta"]
            self.servidores.parar(destino.name)
            sucesso, linhas = self.servidores.iniciar(destino, porta, self.config.valores, preparar=True)
            if sucesso:
                url = f"http://127.0.0.1:{porta}/"
                return [texto(f"↻ o site do {n} estava no ar: foi reiniciado na porta {porta} para a mudança valer "
                              "(migrations aplicadas) — recarregue a página no navegador (F5)", "ok"),
                        bloco("link", texto=url, href=url)]
            return [texto(f"o site do {n} foi derrubado mas não voltou: {linhas[0]}", "erro"),
                    *[texto(linha, "suave") for linha in linhas[1:]]]
        try:
            porta = self.porta_do(numero_de(destino, self.saida))
        except (ValueError, TypeError):
            return []
        dono = processo_na_porta(porta)
        if dono and dono["pid"] and "runserver" in dono["cmd"]:
            return [texto(f"um site está no ar na porta {porta} FORA da tela (processo {dono['pid']}), ainda com o código "
                          f"antigo — reinicie-o, ou rode sgs rodar {n} e responda s para a tela assumir", "aviso")]
        return []

    def ja_no_ar(self, chave, porta):
        """O mesmo sistema já está no ar: na porta pedida → só reabre a janela; em outra → explica."""
        ativo = self.servidores.ativos().get(chave)
        if ativo is None:
            return None
        url = f"http://127.0.0.1:{ativo['porta']}/"
        if ativo["porta"] != porta:
            return falha(f"já está no ar na porta {ativo['porta']} — derrube antes (sgs parar {ativo['porta']}) "
                         f"para subir na {porta}", bloco("link", texto=url, href=url))
        return ok(texto(f"já estava no ar na porta {porta} — nada foi reiniciado (reabri o endereço)", "ok"),
                  bloco("link", texto=url, href=url), *self.janela(url))

    def sistema_de(self, caminho):
        """(número, pasta do sistema) que contém o caminho, ou (None, None)."""
        caminho = Path(caminho).resolve()
        for n, pasta in sistemas(self.saida):
            if caminho == pasta.resolve() or caminho.is_relative_to(pasta.resolve()):
                return n, pasta
        return None, None

    def python_padrao(self):
        return sys.executable

    def janela(self, url):
        """Abre o site conforme sgs pwa (janela de app isolada ou aba). Devolve blocos para a tela."""
        if not self.abrir_janelas:
            return []
        feito = abrir_no_navegador(url, self.config.valores["pwa"])
        return [texto(f"↗ {feito}", "suave")] if feito else [texto("não consegui abrir o navegador — use o link", "aviso")]

    def runserver(self, web, args, python):
        """python manage.py runserver [porta] → em segundo plano, na porta do sistema (6100 + NN; versão 01.3 → 61013).
        Porta ocupada por outro site (ex.: a versão 01.9 na porta do 01.19) → pergunta se força."""
        n, pasta = self.sistema_de(web)
        porta = None
        for a in args:
            m = re.fullmatch(r"(?:[\w.]+:)?(\d{2,5})", a)
            if m:
                porta = int(m.group(1))
        if porta is None:                                  # sem porta no comando: a do sistema (ou a 8000 do Django)
            porta = self.porta_do(n) if n else 8000
        chave = pasta.name if pasta else caminho_exibido(web)
        rotulo = f"o sistema {nn(n)}" if n else chave

        def subir():
            sucesso, linhas = self.servidores.runserver(web, porta, chave, python)
            if not sucesso:
                return falha(linhas[0], *[terminal.saida(linha, "erro") for linha in linhas[1:]])
            url = f"http://127.0.0.1:{porta}/"
            parar = f"sgs parar {nn(n)}" if n else f"sgs parar {porta}"
            blocos = [terminal.saida(f"Starting development server at {url}\nQuit the server with CONTROL-C. "
                                     f"(na tela: {parar})"),
                      bloco("link", texto=url, href=url)]
            if not (web / "db.sqlite3").exists():
                blocos.append(texto("atenção: ainda não há banco (db.sqlite3) — rode python manage.py migrate", "aviso"))
            return ok(*blocos, *self.janela(url))

        resposta = self.ja_no_ar(chave, porta) or self._subir_ou_perguntar(porta, rotulo, subir)
        return resposta["blocos"]

    def _subir_ou_perguntar(self, porta, rotulo, subir):
        dono = self.dono_da_porta(porta)
        return self.perguntar_forcar(porta, dono, rotulo, subir) if dono else subir()

    def subir_sistema(self, destino, porta, preparar=True):
        """sgs rodar / bash iniciar.sh tudo|rodar: prepara e sobe; porta ocupada → pergunta se força."""
        n = numero_de(destino, self.saida)

        def subir():
            sucesso, linhas = self.servidores.iniciar(destino, porta, self.config.valores, preparar=preparar)
            if not sucesso:
                return falha(f"não subiu {self.rotulo_de(destino)}: {linhas[0]}",
                             *[texto(linha, "suave") for linha in linhas[1:]])
            url = f"http://127.0.0.1:{porta}/"
            return ok(texto(f"✓ no ar: {self.rotulo_de(destino)} ({destino.name})", "ok"),
                      bloco("link", texto=f"site: {url}", href=url),
                      bloco("link", texto=f"admin: {url}{admin_url(destino)}", href=f"{url}{admin_url(destino)}"),
                      *[bloco("link", texto=f"módulo {m}: {url}{m}/  ·  API REST: {url}{m}/api/v1/",
                              href=f"{url}{m}/") for m in apps_django(destino)[1:]],
                      texto(f"login do admin: usuário {self.config.valores['admin_usuario']} · senha: a do sgs config "
                            "(admin_senha) — também gravada em web/.env do sistema"),
                      texto(f"log: {caminho_exibido(destino / 'web' / 'servidor.log')} · para derrubar: sgs parar "
                            f"{nn(n) if n else porta}", "suave"),
                      *self.janela(url))

        if not (destino / "web" / "manage.py").exists():
            return falha(f"não subiu {self.rotulo_de(destino)}: este sistema não tem o site Django — gere de novo "
                         "com a caixa “+ Django” marcada")
        return self.ja_no_ar(destino.name, porta) or self._subir_ou_perguntar(porta, self.rotulo_de(destino), subir)

    def iniciar_sh(self, destino, args):
        """bash iniciar.sh [passo] na tela: tudo/rodar sobem em segundo plano; os outros passos rodam de verdade."""
        passo = args[0] if args else "tudo"
        if passo in ("tudo", "rodar"):
            n = numero_de(destino, self.saida)
            porta = int(args[1]) if len(args) > 1 and args[1].isdigit() else (self.porta_do(n) if n else 8000)
            return self.subir_sistema(destino, porta, preparar=passo == "tudo")["blocos"]
        env = self.servidores.ambiente()
        if passo in ("admin", "preparar") and (destino / "web" / ".env").exists():
            ajustar_env(destino, self.config.valores)       # o admin do sgs config vai para o .env
        blocos = terminal.rodar(["bash", "iniciar.sh", *args], destino, env)
        if passo == "env" and (destino / "web" / ".env").exists():
            ajustar_env(destino, self.config.valores)
            blocos.append(texto("(o superusuário do sgs config foi gravado no web/.env)", "suave"))
        return blocos


# =============================================================================
# 6. COMANDOS "sgs" (cada um devolve blocos que a página desenha)
# =============================================================================
COMANDOS_SGS = [
    ("sgs", "ajuda: como usar, comandos e configuração", False),
    ("sgs gerar <pedido>", "GERA um sistema (texto solto só é anotado); com “Perguntar” ligado, pergunta antes", True),
    ("sgs gerar -sp <pedido>", "gera SEM perguntar · sozinho (sgs gerar -sp) encerra as perguntas e gera", True),
    ("sgs gerar <domínio> <padrões…>", "gera escolhendo direto (ex.: sgs gerar hotel criacao)", True),
    ("sgs provap3", "PROVA PRÁTICA P3: gera o sistema do domínio 101 (citricultura) como no guia da prova — pasta "
                    "provaP3, projeto cooperativa, app citricultura, rotas /citricultura/, DRF em /api/ — e prepara "
                    "o ambiente (.venv, .env, migrations, admin); se já existe, pergunta antes de gerar do zero", False),
    ("sgs cancelar", "desiste das perguntas em andamento (nada é gerado)", False),
    ("sgs estilo [simples|cmd|bootstrap|web]", "formatação das páginas web geradas", True),
    ("sgs tema [T01…T10] [tom] [P01…P20]", "tema do estilo web (pasta temas/) e paleta do T10", True),
    ("sgs tipos <campos>", "identificador de tipos: o tipo de cada campo pelo nome (os duvidosos viram pergunta)", True),
    ("sgs listar", "sistemas pelo número fixo (01, 02…) e as versões (01.1, 01.2…), com a porta de cada um", False),
    ("sgs info NN", "detalhes e arquivos do sistema NN (ou da versão NN.k)", True),
    ("sgs testar NN", "roda os testes do sistema NN (ou da versão NN.k)", True),
    ("sgs editar NN", "EDITAR o sistema NN: abre o painel guiado do próprio NN (incrementar campos, ligar classes, "
                      "nova funcionalidade/app, API) — nunca duplica", True),
    ("sgs duplicar NN", "DUPLICAR = COPIAR: cria uma cópia versionada NN.k (01.1 … 01.99) — o original NN não muda "
                        "(único comando que cria cópia)", True),
    ("sgs app NN <pedido>", "FUNCIONALIDADE NOVA no próprio NN: mais uma app Django (form, CRUD, API REST, padrões, "
                            "settings, models, views, testes). Com “Perguntar”, conduz nome, ligação, campos e padrões "
                            "· entidade=Nome · padroes=a,b · ligar=Classe.campo", True),
    ("sgs ligar NN Classe.campo Alvo", "LIGAR CLASSES no próprio NN: campo de REFERÊNCIA opcional (ForeignKey) entre "
                                       "duas classes (ex.: sgs ligar 16 Viagcert.destino Destino) · sozinho conduz "
                                       "passo a passo ou lista as classes", True),
    ("sgs api config NN", "CAMPOS DA API: o que cada endpoint (/api/v1/, /api/, /destinos/api/v1/…) expõe — "
                          "sgs api config NN <endpoint> campo=sim|nao · quem chama escolhe com ?campos=a,b", True),
    ("sgs incrementar NN Classe.campo <padrão>", "INCREMENTAR CAMPOS no próprio NN: cria campo novo ou modifica a "
                                                 "regra de um campo existente (inteiro>=0, inteiro:1..30, lista:a,b,c, "
                                                 "texto…) — vale no @property e no Django · sozinho conduz passo a "
                                                 "passo ou lista os campos", True),
    ("sgs rodar NN [porta]", "prepara o Django do sistema NN (.env, migrations, admin) e sobe o site (6100+NN; "
                             "versão 01.3 → 61013)", True),
    ("sgs servidores", "sites no ar", False),
    ("sgs parar NN | porta | todos", "derruba um site (ou todos) e libera a porta", True),
    ("sgs comandos NN", "comandos de terminal para rodar o sistema NN fora da tela", True),
    ("sgs comand [n]", "módulo de ajuda: a lista numerada dos comandos da esteira (sgs exit volta)", False),
    ("sgs padroes [categoria|escopo]", "os 28 padrões por categoria ou escopo (arquitetura, classe, campo, relacao)", False),
    ("sgs infra", "PAINEL DE INFRA, SEGURANÇA & BIBLIOTECAS (Passo 2): banco, Redis, UUID, LNNL, baseline, Argon2id, "
                  "Fernet, 2FA, RBAC, Anti-Bot, ratelimit, anymail e tinymce", False),
    ("sgs dominios [termo | novo | remover]", "os 300 domínios (100 palavras cada; 101 = Prova P3) + domínios "
                                              "personalizados · sgs dominios novo cadastra um novo domínio · "
                                              "sgs dominios saude filtra", True),
    ("sgs config [chave=valor]", "mostra/altera a configuração (infra, segurança, bibliotecas, tema, porta, admin, pwa)", False),
    ("sgs pwa=true | sgs pwa=false", "PWA isolado (padrão: janela de app) ou aba comum do navegador", True),
    ("sgs tutorial", "TUTORIAL prático: classe nova, ligar, campos, o padrão do campo (@property), padrões de "
                     "projeto, API (abre ao lado da Wiki e do Study Hub)", False),
    ("sgs wiki", "abre a cópia da Wikipédia (lista GoF), com o layout da Wikipédia", False),
    ("sgs hub", "abre a cópia do Django Study Hub (estudo de Django: models, views, ORM, forms, DRF, P3)", False),
    ("sgs cmd [sgs]", "estilo da tela: sgs cmd = como o Prompt de Comando do Windows (o padrão ao abrir) · "
                      "sgs cmd sgs = as cores do SGS · sem o sgs também vale: cmd · cmd sgs", False),
    ("sgs wysiwyg [NN]", "MODO WYSIWYG (bancada Kanban de blocos): monta Domínio, Classes, Campos, Ligações, API e "
                         "Padrões de Projeto com exclusão mútua visual (CMD ↔ WYSIWYG)", False),
    ("sgs topo", "mostra/oculta os comandos principais no topo (a tela abre com eles à mostra)", False),
    ("sgs foot", "mostra/oculta as caixas de seleção embaixo do prompt (a tela abre com elas à mostra; a linha "
                 "do comando sempre fica)", False),
    ("sgs clear  (ou clear)", "limpa a tela — ficam só as duas linhas do topo", False),
    ("sgs history  (ou history)", "histórico de comandos (arquivo .sgs_historico: sobrevive ao F5) · history N · "
                                  "history -c limpa · history -d N apaga um", False),
    ("sgs exit  (ou exit)", "sai do módulo comand e volta para a tela principal", False),
]


def bloco(tipo, **campos):
    return {"t": tipo, **campos}


def texto(conteudo, cor=None):
    return bloco("texto", texto=conteudo, cor=cor)


def ok(*blocos, **extra):
    return {"ok": True, "blocos": list(blocos), **extra}


def falha(mensagem, *blocos, **extra):
    return {"ok": False, "blocos": [texto(mensagem, "erro"), *blocos], **extra}


def cmd(rotulo, comando=None, preencher=False):
    """Célula clicável: executa o comando (ou só o escreve no prompt, se ainda faltar algo)."""
    return {"texto": rotulo, "cmd": comando or rotulo, "preencher": preencher}


def tabela_comandos(itens=COMANDOS_SGS):
    linhas = []
    for rotulo, descricao, preencher in itens:
        base = re.split(r" \[| <| NN| \||  \(", rotulo)[0].strip()
        if "=" in base:                                   # sgs pwa=true → escreve "sgs pwa=" para completar
            base = base.split("=")[0] + "="
        linhas.append([cmd(rotulo, base + (" " if preencher and not base.endswith("=") else ""), preencher), descricao])
    return bloco("tabela", colunas=["comando", "o que faz"], linhas=linhas)


def tabela_config(cfg):
    linhas = []
    for chave, valor in cfg.valores.items():
        if isinstance(valor, bool):
            mostrado = "sim" if valor else "não"
        elif chave == "admin_senha":
            mostrado = "•" * len(valor)
        else:
            mostrado = str(valor)
        linhas.append([cmd(chave, f"sgs config {chave}=", True), mostrado, EXPLICA_CONFIG[chave]])
    return bloco("tabela", colunas=["chave", "valor", "o que é"], linhas=linhas)


def escolher(ctx, argumento):
    """"01", "1" ou a versão "01.3" → (pasta do sistema, Num). ValueError com a explicação se não existir."""
    lista = sistemas(ctx.saida)
    if not lista:
        raise ValueError("ainda não há sistemas gerados — gere um com: sgs gerar <pedido>")
    numero = Num.ler(argumento) if argumento is not None else None
    if numero is None:
        raise ValueError(f"diga o número do sistema, ex.: {nn(lista[0][0])} ou a versão {nn(lista[0][0])}.1 "
                         "(veja: sgs listar)")
    pasta = next((p for n, p in lista if n == numero), None)
    if pasta is None:
        raise ValueError(f"não existe o sistema {nn(numero)} (veja: sgs listar)")
    return pasta, numero


def sgs_ajuda(ctx, _args, _opcoes=None):
    base = ctx.config.valores["porta_base"]
    return ok(
        bloco("titulo", texto=f"{NOME_SGS} — ajuda"),
        texto("1) GERAR: sgs gerar <pedido>. Ex.: sgs gerar biblioteca onde a multa varia conforme o tipo de leitor. "
              "Texto escrito sem “sgs gerar” só é ANOTADO na tela (nada é gerado por engano). As caixas embaixo "
              "(+ Django, exercício, testes, estudo, comentários) valem para a geração."),
        texto("2) TERMINAL: cd, ls, pwd, tree, cat, source .venv/bin/activate, python manage.py migrate/runserver, "
              "pytest, bash iniciar.sh… funcionam com ou sem sgs na frente. A lista completa, explicada: sgs comand."),
        texto(f"3) NÚMEROS, EDIÇÃO E DUPLICAÇÃO: cada sistema recebe um número fixo na geração (01, 02…). O SGS é o 00 "
              f"(porta {base}); o sistema 01 roda na {base + 1}, o 02 na {base + 2}… Por padrão, EDITAR (sgs editar NN, "
              f"sgs app NN, sgs ligar NN, sgs incrementar NN) altera DIRETAMENTE o sistema NN indicado. Para criar uma "
              f"CÓPIA versionada 01.1 … 01.99 sem mexer no original, use `sgs duplicar NN` (porta = porta do sistema + "
              f"último dígito da versão: {base + 1}1 para a 01.1; a 01.9, 01.19 … 01.99 dividem a {base + 1}9 — se uma "
              "estiver no ar, a tela pergunta se encerra a anterior). Porta presa? A tela libera ao parar, fechar e reabrir."),
        texto("4) PWA: os sites (e o SGS) abrem numa janela de app isolada. sgs pwa=false → aba comum do navegador."),
        texto("5) PERGUNTAS: com a caixa “Perguntar antes de gerar”, sgs gerar faz rodadas de 10 perguntas (estilo, "
              "arquitetura, padrões…) e só gera com sgs gerar -sp — que também funciona no meio de qualquer pergunta. "
              "O que está MARCADO nas caixas não é perguntado; o que não se aplica também não (sem Django, nada de "
              "estilo). Ao abrir o SGS, todas as caixas começam marcadas. sgs gerar -sp <pedido> gera direto."),
        texto("7) CAMPOS E TIPOS: “… com os campos nome, idade, peso, vacinado” acrescenta campos à entidade. O "
              "identificador de tipos deduz pelo nome (nome → texto, idade → inteiro, peso → decimal, vacinado → "
              "sim/não, data_… → data); só os que NÃO são óbvios (codigo, status…) viram pergunta. Teste: sgs tipos."),
        texto("6) ESTILO das páginas: sgs estilo (simples · cmd · bootstrap · web) e sgs tema (10 temas × 6 tons). "
              "“Notas na web” liga as notas de apresentação nas páginas (diferente dos comentários no código)."),
        texto("8) EDITAR, NOVA CLASSE E LIGAR CLASSES: sgs editar NN abre o painel guiado do próprio NN. sgs app NN "
              "<pedido> acrescenta mais uma app Django (form, CRUD, API REST, padrões, settings, models, views e testes) "
              "diretamente no NN. Ligar duas classes que já existem: sgs ligar NN Classe.campo Alvo (sozinho conduz "
              "passo a passo). Direto: sgs app 16 -sp destinos de viagem ligar=Viagcert.destino padroes=state."),
        texto("9) INCREMENTAR CAMPOS: sgs incrementar NN Classe.campo <padrão> — altera diretamente o sistema NN "
              "(campo que existe muda de regra; nome novo entra na classe). Padrões: inteiro>=0, inteiro:1..30, "
              "decimal>=0, lista:janela,meio,corredor, texto, texto-livre, simnao, data. Vale no @property do núcleo e "
              "no model/form/API do Django; os testes acompanham. Ex.: sgs incrementar 16 Viagcert.voo inteiro>=1 · "
              "sgs incrementar 16 sozinho conduz passo a passo ou lista os campos."),
        tabela_comandos(),
        bloco("titulo", texto="Configuração atual"),
        tabela_config(ctx.config),
        bloco("link", texto="Referência dos padrões GoF: cópia da Wikipédia (abre em outra aba)", href="/referencia"),
        texto("Atalhos: Enter executa · Shift+Enter quebra linha · com a caixa de sugestões aberta: ↑/↓ andam entre as "
              "opções e TAB (ou →, com o cursor no fim da linha) escolhe a marcada — o trecho em cinza na linha é ela · "
              "clique também escolhe · Esc fecha a caixa · com a caixa fechada, ↑/↓ são o histórico (guardado em "
              "arquivo: sobrevive ao F5) · Ctrl+L limpa · history · history -c", "suave"),
    )


SEM_PERGUNTAR = ("-sp", "--sem-perguntar")


def sgs_gerar(ctx, args, opcoes=None):
    """sgs gerar <pedido> · sgs gerar -sp <pedido> (sem perguntas) · sgs gerar -sp (encerra as perguntas e gera)."""
    sem_perguntar = any(a.lower() in SEM_PERGUNTAR for a in args)
    args = [a for a in args if a.lower() not in SEM_PERGUNTAR]
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    if sem_perguntar and not args:
        if ctx.questionario is None:
            return falha("não há pedido em andamento — use: sgs gerar -sp <pedido>")
        if isinstance(ctx.questionario, perguntas.QuestionarioModulo):     # as perguntas eram de um sgs app
            return _concluir_modulo(ctx, opcoes)
        if isinstance(ctx.questionario, perguntas.QuestionarioIncremento):  # … ou de um sgs incrementar
            return sgs_incrementar(ctx, ["-sp"], opcoes)
        if isinstance(ctx.questionario, perguntas.QuestionarioLigar):      # … ou de um sgs ligar
            return sgs_ligar(ctx, ["-sp"], opcoes)
        if isinstance(ctx.questionario, perguntas.QuestionarioDominio):    # … ou de um sgs dominios novo
            return sgs_dominios(ctx, ["novo", "-sp"], opcoes)
        q, ctx.questionario = ctx.questionario, None
        resposta = processar(saida=ctx.saida, porta_base=c["porta_base"], **q.argumentos())
        if not resposta["ok"]:
            return falha(resposta["erro"])
        return ok(texto(f"✓ perguntas encerradas ({q.respostas} resposta(s)) — gerando com as decisões tomadas", "ok"),
                  cartao=resposta)
    if not args:
        return falha("diga o que gerar: sgs gerar <pedido>  (ex.: sgs gerar loja com extras opcionais) · "
                     "ou direto: sgs gerar <domínio> <padrões…> · sgs gerar -sp <pedido> gera sem perguntar")
    if c["perguntar"] and not sem_perguntar:
        pedido = " ".join(args)
        if len(pedido) > LIMITE_PEDIDO:
            return falha(f"pedido longo demais (máximo {LIMITE_PEDIDO} caracteres)")
        marcadas = [caixa for caixa in perguntas.CAIXAS if c[caixa]]       # caixa marcada não vira pergunta
        q = perguntas.Questionario(pedido, c, marcadas=marcadas)
        if not q.esgotado:
            ctx.questionario = q
            aviso = f" · marcadas na tela (não serão perguntadas): {', '.join(marcadas)}" if marcadas else ""
            return ok(texto(f"Antes de gerar, algumas perguntas (rodadas de 10). Pedido: {pedido}{aviso}", "destaque"),
                      *perguntas.blocos(q))
        resposta = processar(saida=ctx.saida, porta_base=c["porta_base"], **q.argumentos())   # nada a perguntar
        return ok(cartao=resposta) if resposta["ok"] else falha(resposta["erro"])
    ctx.questionario = None
    comum = dict(django=c["django"], exercicio=c["exercicio"], testar=c["testar"], saida=ctx.saida, estudo=c["estudo"],
                 comentarios=c["comentarios"], porta_base=c["porta_base"], web={k: c[k] for k in OPCOES_WEB})
    # Escolha DIRETA: 1ª palavra é um domínio e as demais são padrões/grupos conhecidos. Senão: pedido livre.
    direto = args[0].lower() in gs.DOMINIOS and all(gs.APELIDOS.get(gs.normalizar(a).replace("-", "_"))
                                                    for a in args[1:])
    if direto:
        resposta = processar(dominio=args[0].lower(), padroes=args[1:] or ["prova"], **comum)
    else:
        resposta = processar(" ".join(args), **comum)
    if not resposta["ok"]:
        return falha(resposta["erro"])
    return ok(cartao=resposta)


PROVA_P3 = "citricultura"          # o domínio 101: tem o perfil da Prova Prática P3 (dominios.PERFIS)


def sgs_provap3(ctx, args, opcoes=None):
    """sgs provap3 — a Prova Prática P3 num comando: gera o sistema do domínio 101 (citricultura) com o perfil da
    prova (pasta provaP3, projeto Django cooperativa, app citricultura, rotas /citricultura/, DRF em /api/) e
    PREPARA o ambiente dele (.venv/dependências, web/.env, migrations, admin). A pasta já existe? Não apaga: é onde
    se trabalha — mostra o sistema e pergunta (s/N) antes de gerar do zero."""
    perfil = gs.DOMINIOS[PROVA_P3]["perfil"]
    destino = Path(ctx.saida) / perfil["pasta"]
    if destino.exists():
        n = numero_de(destino, ctx.saida)
        ctx.confirmacao = {"rotulo": "gerar do zero? s/N",
                           "dica": f"s = APAGA {perfil['pasta']} e gera de novo · n (ou Enter) = deixa como está",
                           "acao": lambda: _gerar_provap3(ctx, opcoes, regerar=True)}
        botoes = ([cmd(f"sgs rodar {nn(n)}"), cmd(f"sgs editar {nn(n)}"), cmd(f"sgs incrementar {nn(n)}"),
                   cmd(f"sgs ligar {nn(n)}"), cmd(f"sgs duplicar {nn(n)}"), cmd(f"sgs testar {nn(n)}")] if n else [])
        return ok(texto(f"{perfil['pasta']} já existe" + (f" (sistema {nn(n)})" if n else "") + " — é a pasta de "
                        "trabalho da prova: não apago sem perguntar.", "aviso"),
                  bloco("botoes", itens=botoes),
                  texto(f"Gerar do zero APAGA o que foi feito em {perfil['pasta']}. Gerar de novo? (s/N)", "aviso"))
    return _gerar_provap3(ctx, opcoes, regerar=False)


def _gerar_provap3(ctx, opcoes, regerar):
    perfil = gs.DOMINIOS[PROVA_P3]["perfil"]
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    ctx.questionario = None
    resposta = processar(dominio=PROVA_P3, padroes=["prova"], django=True, exercicio=False, testar=c["testar"],
                         saida=ctx.saida, estudo=c["estudo"], comentarios=c["comentarios"], porta_base=c["porta_base"],
                         web={k: c[k] for k in OPCOES_WEB}, regerar_fixa=regerar)
    if not resposta["ok"]:
        return falha(resposta["erro"])
    destino = Path(ctx.saida) / perfil["pasta"]
    n = numero_de(destino, ctx.saida)
    pronto, mensagens = ctx.servidores.preparar(destino, ctx.config.valores)
    blocos = [bloco("titulo", texto=f"{perfil['nome']} — sistema {nn(n)} gerado e PREPARADO em "
                                    f"sistemas_gerados/{perfil['pasta']}"),
              bloco("tabela", colunas=["no guia da prova", "aqui"], linhas=[
                  ["~/provaP3", f"sistemas_gerados/{perfil['pasta']}/web (caminho relativo)"],
                  [f"startproject {perfil['projeto']} .", f"web/{perfil['projeto']}/ (settings, urls, wsgi)"],
                  [f"startapp {perfil['app']}", f"web/{perfil['app']}/ (models, views, api.py, serializers.py, api_drf.py)"],
                  ['INSTALLED_APPS: "rest_framework", "' + perfil["app"] + '"', f"web/{perfil['projeto']}/settings.py"],
                  [f"pytest.ini → {perfil['projeto']}.settings · {perfil['pytest_arquivos']}", "web/pytest.ini"],
                  ["pip install django djangorestframework pytest pytest-django", "requirements.txt (já instalado)"]]),
              texto(f"Rotas: / → /{perfil['rota']} (telas do CRUD) · /{perfil['rota']}api/v1/ (API em Django puro) · "
                    "/api/ (API com o DRF: Serializer + ViewSet + router) · /admin/", "suave")]
    if pronto:
        blocos.append(texto("✓ ambiente preparado: .venv/dependências, web/.env, migrations e superusuário (admin do "
                            "sgs config)", "ok"))
    else:
        blocos += [texto("o sistema foi gerado, mas o preparo parou:", "erro"), *[texto(m, "suave") for m in mensagens]]
    blocos.append(bloco("botoes", itens=[cmd(f"sgs rodar {nn(n)}"), cmd(f"sgs editar {nn(n)}"),
                                         cmd(f"sgs incrementar {nn(n)}"), cmd(f"sgs ligar {nn(n)}"),
                                         cmd(f"sgs duplicar {nn(n)}"), cmd(f"sgs testar {nn(n)}")]))
    return ok(*blocos, cartao=resposta)


def sgs_tipos(ctx, args, _opcoes=None):
    """sgs tipos nome, idade, status — mostra o tipo que o identificador deduz (e o que vira pergunta)."""
    texto_campos = " ".join(args)
    if not texto_campos.strip():
        exemplos = [[tipos_campos.rotulo(tipo), tipos_campos.TIPOS[tipo][0], exemplo] for tipo, exemplo in (
            ("str", "nome, raca, email, telefone, cpf, placa"), ("int", "idade, ano, dias, quantidade, andar"),
            ("float", "preco, valor_*, peso, altura, salario, taxa"), ("bool", "ativo, vacinado, pago, tem_*, e_*"),
            ("data", "data_*, nascimento, vencimento, validade, *_em"))]
        return ok(texto("Identificador de tipos: deduz o tipo de cada campo pelo nome. Ex.: sgs tipos nome, idade, status"),
                  bloco("tabela", colunas=["tipo", "sigla", "nomes que já são óbvios"], linhas=exemplos),
                  texto("Nomes ambíguos (codigo, numero, tamanho, status, nota…) ou desconhecidos viram PERGUNTA em "
                        "sgs gerar. O tipo também pode ir junto no pedido: idade:int, peso (decimal).", "suave"))
    campos = tipos_campos.analisar(texto_campos)
    if not campos:
        return falha("nenhum campo reconhecido — separe por vírgula: sgs tipos nome, idade, vacinado")
    certeza = {"obvio": "óbvio", "duvida": "DÚVIDA → vira pergunta", "informado": "informado"}
    linhas = [[c["nome"], tipos_campos.rotulo(c["tipo"]), gs.descrever_regra(c).split(": ", 1)[1],
               certeza[c["certeza"]], c["motivo"]] for c in campos]
    return ok(bloco("tabela", colunas=["campo", "tipo", "regra", "certeza", "por quê"], linhas=linhas),
              texto(f"forma curta para o gerador: {tipos_campos.como_texto(campos)}", "suave"))


def sgs_cancelar(ctx, _args, _opcoes=None):
    if ctx.questionario is None:
        return ok(texto("não há perguntas em andamento", "suave"))
    ctx.questionario = None
    return ok(texto("perguntas canceladas — nada foi gerado", "aviso"))


def sgs_estilo(ctx, args, _opcoes=None):
    """sgs estilo · sgs estilo simples|cmd|bootstrap|web"""
    if args:
        ctx.config.alterar("estilo", args[0])
        ctx.config.salvar()
    atual = ctx.config.valores["estilo"]
    linhas = [[cmd(e, f"sgs estilo {e}"), descricao, "← atual" if e == atual else ""] for e, descricao in gs.ESTILOS.items()]
    return ok(texto(f"✓ estilo: {atual}", "ok") if args else texto(f"estilo atual: {atual}"),
              bloco("tabela", colunas=["estilo", "como fica", ""], linhas=linhas),
              texto("vale para os próximos sgs gerar com Django · o tema do estilo web: sgs tema", "suave"),
              config=ctx.config.publica())


def sgs_tema(ctx, args, _opcoes=None):
    """sgs tema · sgs tema T04 · sgs tema T04 escuro · sgs tema T10 P12"""
    for arg in args:
        valor = arg.upper()
        if valor in temas_web.TEMAS:
            ctx.config.alterar("tema", valor)
        elif valor in temas_web.PALETAS:
            ctx.config.alterar("paleta", valor)
        else:
            ctx.config.alterar("tom", arg)
    if args:
        ctx.config.salvar()
    v = ctx.config.valores
    linhas = []
    for chave, info in temas_web.TEMAS.items():
        t = temas_web.resolver(chave, v["tom"], v["paleta"])
        linhas.append([cmd(chave, f"sgs tema {chave}"), info["nome"], info["descricao"],
                       f"fundo {t['fundo']} · destaque {t['destaque']}", "← atual" if chave == v["tema"] else ""])
    tons = " · ".join(f"{t}" for t in temas_web.TONS)
    return ok(texto(f"tema atual: {v['tema']} {temas_web.TEMAS[v['tema']]['nome']} · {temas_web.NOMES_TONS[v['tom']]}"
                    + (f" · paleta {v['paleta']} {temas_web.PALETAS[v['paleta']][0]}" if v["tema"] == "T10" else ""), "ok"),
              bloco("tabela", colunas=["tema", "nome", "personalidade", f"cores no {temas_web.NOMES_TONS[v['tom']]}", ""],
                    linhas=linhas),
              texto(f"tons: {tons} · paletas do T10: P01 a P20 · ex.: sgs tema T04 escuro · sgs tema T10 P12", "suave"),
              texto("cores da pasta temas/ (10 temas × 6 tons), com contraste WCAG conferido; vale para o estilo web", "suave"),
              config=ctx.config.publica())


def sgs_listar(ctx, args, _opcoes=None):
    lista = sistemas(ctx.saida)
    rodando = ctx.servidores.ativos()
    linhas = [[{"texto": "00", "cor": "ok"}, "SGS (esta tela)", "—", "—", "—", str(ctx.porta_tela),
               {"texto": "no ar", "cor": "ok"}]]
    if args and args[0] == "recentes":
        lista = sorted(lista, key=lambda par: (par[1] / gs.MARCADOR).stat().st_mtime, reverse=True)
    for n, destino in lista:
        info = info_sistema(destino)
        modo = ("estudo" if info["estudo"] else "só gerar") + ("" if info["comentarios"] else " · sem coment.")
        modo += " · exercício" if info["exercicio"] else ""
        modulos = gs.ler_modulos(destino)
        modo += f" · +{len(modulos)} módulo(s)" if modulos else ""
        no_ar = rodando.get(destino.name)
        try:
            porta = no_ar["porta"] if no_ar else ctx.porta_do(n)
        except ValueError:
            porta = "—"                                      # porta_base alta demais para a versão
        situacao = {"texto": "no ar", "href": f"http://127.0.0.1:{porta}/", "cor": "ok"} if no_ar else \
            (cmd("parado · rodar", f"sgs rodar {nn(n)}") if info["django"] else "—")
        linhas.append([cmd(nn(n), f"sgs info {nn(n)}"), destino.name, str(len(info["padroes"])),
                       "sim" if info["django"] else "—", modo, str(porta), situacao])
    blocos = [bloco("titulo", texto=f"{len(lista)} sistema(s) em {caminho_exibido(ctx.saida)}"),
              bloco("tabela", colunas=["nº", "pasta", "padrões", "Django", "modo", "porta", "site"], linhas=linhas),
              texto("O número é dado na geração e não muda (por isso a porta também não). 01.1, 01.2… são CÓPIAS "
                    "(criadas com sgs duplicar NN). Editar (sgs editar / app / ligar / incrementar) altera o próprio "
                    "sistema indicado. Clique no número para os detalhes; cd NN entra na pasta.", "suave")]
    if not lista:
        blocos.insert(1, texto("Nenhum sistema gerado ainda. Gere um: sgs gerar loja com extras opcionais", "aviso"))
    return ok(*blocos)


def _resumo_infra_web(w):
    """Lista [(grupo, valor)] com as decisões de Infra, Segurança & Bibliotecas gravadas no sistema."""
    w = {**gs.WEB_PADRAO, **(w or {})}
    extras_seg = [rot for flag, rot in (
        (w["argon2"] or w["seguranca"] == "baseline", "Argon2id"),
        (w["fernet"], "Fernet"), (w["antibot"], "Anti-Bot"),
    ) if flag]
    acesso = [rot for flag, rot in (
        (w["rbac"], "RBAC"),
        (w["recuperacao_senha"], "Recup. Usuário/Senha"),
        (w["two_factor"], f"2FA ({w['two_factor_expiracao']} min)"),
    ) if flag]
    libs = [rot for flag, rot in (
        (w["ratelimit"], "django-ratelimit"),
        (w["anymail"], "django-anymail"),
        (w["tinymce"], "django-tinymce"),
    ) if flag]
    return [
        ["Estrutura & IDs", f"{w['estrutura']} · PK {w['id_publico']}"
         + (f" · LNNL ({w['lnnl_tipo']})" if w["id_interno"] else "")],
        ["Banco & Cache", f"{w['banco']}" + (" + Redis" if w["redis"] else "")],
        ["Segurança & Cripto", f"{w['seguranca']}" + (f" · {', '.join(extras_seg)}" if extras_seg else "")],
        ["Acesso & Identidade", ", ".join(acesso) or "padrão Django"],
        ["Bibliotecas", ", ".join(libs) or "nenhuma extra"],
    ]


def sgs_info(ctx, args, _opcoes=None):
    destino, n = escolher(ctx, args[0] if args else None)
    info = info_sistema(destino)
    spec = ler_spec(destino) or {}
    sugestoes = [cmd(f"sgs editar {nn(n)}"), cmd(f"sgs incrementar {nn(n)}"), cmd(f"sgs ligar {nn(n)}"),
                 cmd(f"sgs duplicar {nn(n)}"), cmd(f"sgs testar {nn(n)}"), cmd(f"cd {nn(n)}")]
    sugestoes += [cmd(f"sgs rodar {nn(n)}"), cmd(f"sgs app {nn(n)} …", f"sgs app {nn(n)} ", True)] if info["django"] else []
    blocos = []
    if info["django"]:
        blocos.append(bloco("tabela", colunas=["Infra, Segurança & Bibliotecas", "ativo neste sistema"],
                            linhas=_resumo_infra_web(spec.get("web"))))
    blocos.append(bloco("tabela", colunas=["próximos passos"] + [""] * (len(sugestoes) - 1), linhas=[sugestoes]))
    return ok(*blocos, cartao=cartao(destino, info, ctx.saida, ctx.config.valores["porta_base"]))


def sgs_infra(ctx, _args=None, _opcoes=None):
    """sgs infra (ou sgs seguranca) — Passo 2 no modo CMD: Infraestrutura, Segurança & Bibliotecas com comandos clicáveis."""
    c = ctx.config.valores

    def tog(chave, ativo):
        prox = "nao" if ativo else "sim"
        return cmd(f"{'ativo' if ativo else 'desligado'} → {prox}", f"sgs config {chave}={prox}")

    linhas = [
        ["1 · Estrutura", c["estrutura"], cmd("plana", "sgs config estrutura=plana"),
         cmd("apps/", "sgs config estrutura=apps")],
        ["1 · Chave Pública", c["id_publico"], cmd("inteiro", "sgs config id_publico=inteiro"),
         cmd("uuid", "sgs config id_publico=uuid")],
        ["1 · ID Interno LNNL", f"sim ({c['lnnl_tipo']})" if c["id_interno"] else "não",
         tog("id_interno", c["id_interno"]), cmd("lnnl_tipo=21", "sgs config lnnl_tipo=", True)],
        ["2 · Banco Principal", c["banco"],
         cmd("sqlite3", "sgs config banco=sqlite3"),
         cmd("postgresql / mongodb", "sgs config banco=postgresql" if c["banco"] != "postgresql" else "sgs config banco=mongodb")],
        ["2 · Cache Redis", "sim" if c["redis"] else "não", tog("redis", c["redis"]), "django-redis"],
        ["3 · Hardening HTTP/CSP", c["seguranca"], cmd("basica", "sgs config seguranca=basica"),
         cmd("baseline (§12–14)", "sgs config seguranca=baseline")],
        ["3 · Argon2id", "sim (Baseline)" if c["seguranca"] == "baseline" else ("sim" if c["argon2"] else "não"),
         tog("argon2", c["argon2"]), "hash de senhas §16.1"],
        ["3 · Fernet", "sim" if c["fernet"] else "não", tog("fernet", c["fernet"]), "criptografia em repouso §18.1"],
        ["3 · Anti-Bot", "sim" if c["antibot"] else "não", tog("antibot", c["antibot"]), "honeypot + tempo mínimo"],
        ["4 · RBAC", "sim" if c["rbac"] else "não", tog("rbac", c["rbac"]), "papéis admin/gestor/operador/leitor"],
        ["4 · Recup. Senha", "sim" if c["recuperacao_senha"] else "não",
         tog("recuperacao_senha", c["recuperacao_senha"]), "/conta/password_reset/"],
        ["4 · Two-Factor (2FA)", f"sim ({c['two_factor_expiracao']} min)" if c["two_factor"] else "não",
         tog("two_factor", c["two_factor"]), cmd("expiração (min)", "sgs config two_factor_expiracao=", True)],
        ["5 · django-ratelimit", "sim" if c["ratelimit"] else "não", tog("ratelimit", c["ratelimit"]), "taxa de requisições §19"],
        ["5 · django-anymail", "sim" if c["anymail"] else "não", tog("anymail", c["anymail"]), "e-mail transacional"],
        ["5 · django-tinymce", "sim" if c["tinymce"] else "não", tog("tinymce", c["tinymce"]), "rich-text em texto-longo"],
    ]
    blocos = [
        bloco("titulo", texto="Passo 2 · Infra, Segurança & Bibliotecas (para os próximos sgs gerar com Django)"),
        bloco("tabela", colunas=["bloco", "atual", "alternar / escolher", "opção / efeito"], linhas=linhas),
    ]
    if c["ratelimit"] and not c["redis"]:
        blocos.append(texto("Aviso: django-ratelimit ativo sem Redis — em produção recomenda-se ativar: sgs config redis=sim", "aviso"))
    if (c["recuperacao_senha"] or c["two_factor"]) and not c["anymail"]:
        blocos.append(texto("Dica: recuperação de senha / 2FA ativos — para envio transacional, considere: sgs config anymail=sim", "suave"))
    blocos.append(texto("Altere várias chaves de uma vez com: sgs config banco=postgresql redis=sim fernet=sim rbac=sim", "suave"))
    return ok(*blocos, config=ctx.config.publica())


def sgs_testar(ctx, args, _opcoes=None):
    destino, n = escolher(ctx, args[0] if args else None)
    info = info_sistema(destino)
    resultados = gs.executar_testes(destino, SimpleNamespace(exercicio=info["exercicio"], django=info["django"]))
    linhas = []
    for r in resultados:
        if r["codigo"] == 0:
            situacao = {"texto": "✓ passou", "cor": "ok"}
        elif r["conta"]:
            situacao = {"texto": "✗ falhou", "cor": "erro"}
        else:
            situacao = {"texto": "• esperado (a sua parte começa vermelha)", "cor": "suave"}
        linhas.append([r["rotulo"], situacao, r["resumo"]])
    return ok(bloco("titulo", texto=f"Testes do sistema {nn(n)} — {destino.name}"),
              bloco("tabela", colunas=["parte", "resultado", "pytest"], linhas=linhas))


def sgs_rodar(ctx, args, _opcoes=None):
    """sgs rodar NN [porta]: prepara e sobe. Já no ar → reabre. Porta ocupada (ex.: 01.9 na porta do 01.19) → pergunta."""
    destino, n = escolher(ctx, args[0] if args else None)
    if len(args) > 1:
        if not args[1].isdigit() or not 1024 <= int(args[1]) <= 65535:
            return falha("porta inválida: use um número entre 1024 e 65535")
        porta = int(args[1])
    else:
        porta = ctx.porta_do(n)
    return ctx.subir_sistema(destino, porta)


def sgs_parar(ctx, args, _opcoes=None):
    if not args:
        raise ValueError("diga qual: sgs parar NN, sgs parar <porta> ou sgs parar todos")
    if args[0] == "todos":
        quantos = len(ctx.servidores.ativos())
        ctx.servidores.parar_todos()
        return ok(texto(f"{quantos} site(s) derrubado(s)", "ok"))
    if args[0].isdigit() and int(args[0]) >= 1024:
        if ctx.servidores.parar_porta(int(args[0])):
            return ok(texto(f"site da porta {args[0]} derrubado", "ok"))
        return falha(f"nada rodando na porta {args[0]} (veja: sgs servidores)")
    destino, n = escolher(ctx, args[0])
    if ctx.servidores.parar(destino.name):
        return ok(texto(f"site do sistema {nn(n)} derrubado — porta liberada", "ok"))
    return falha(f"o sistema {nn(n)} não está rodando (veja: sgs servidores)")


def sgs_servidores(ctx, _args, _opcoes=None):
    ativos = ctx.servidores.ativos()
    if not ativos:
        return ok(texto("Nenhum site no ar além do SGS. Suba um com: sgs rodar NN (ou python manage.py runserver)",
                        "aviso"))
    linhas = []
    for chave, a in sorted(ativos.items(), key=lambda par: par[1]["porta"]):
        n = numero_de(a["destino"], ctx.saida)
        url = f"http://127.0.0.1:{a['porta']}/"
        linhas.append([nn(n) if n else "—", chave, {"texto": url, "href": url},
                       cmd("parar", f"sgs parar {nn(n) if n else a['porta']}")])
    return ok(bloco("tabela", colunas=["nº", "sistema", "endereço", ""], linhas=linhas))


def sgs_comandos(ctx, args, _opcoes=None):
    destino, n = escolher(ctx, args[0] if args else None)
    info = info_sistema(destino)
    pasta = str(destino.resolve())
    venv = f"{AQUI}/.venv"                          # o .venv do projeto mora em Gerador_Sistemas/
    porta = ctx.porta_do(n)
    blocos = [bloco("titulo", texto=f"Rodar o sistema {nn(n)} fora da tela (terminal do WSL) — porta {porta}"),
              texto("Entrar na pasta:"), bloco("codigo", texto=f'cd "{pasta}"')]
    teste = "python -m pytest -q"
    if info["django"]:
        app = " ".join(apps_django(destino)) or "app"
        blocos += [
            texto("Tudo de uma vez (cria .venv, instala o requirements.txt, .env, migrations, admin e sobe em PWA):"),
            bloco("codigo", texto=f"bash iniciar.sh tudo {porta}"),
            texto("Reaproveitando o .venv do projeto (já tem Django — não precisa de internet):"),
            bloco("codigo", texto=f'VENV="{venv}" bash iniciar.sh tudo {porta}'),
            texto("Separado, passo a passo (cada um pode ser repetido):"),
            bloco("codigo", texto="bash iniciar.sh venv\nbash iniciar.sh deps\nbash iniciar.sh env\nbash iniciar.sh migrar\n"
                                  f"bash iniciar.sh admin\nbash iniciar.sh testar\nbash iniciar.sh rodar {porta}"),
            texto("Concatenado numa linha, só com comandos do Python/Django (sem o script):"),
            bloco("codigo", texto=f'cd "{pasta}" && source "{venv}/bin/activate" && cp -n web/.env.example web/.env && '
                                  f"cd web && python manage.py makemigrations {app} && python manage.py migrate && "
                                  f"python manage.py garantir_admin && python manage.py runserver 127.0.0.1:{porta}"),
            texto(f"Site: http://127.0.0.1:{porta}/ · admin: http://127.0.0.1:{porta}/{admin_url(destino)} (usuário e senha no "
                  "web/.env). PWA=0 no web/.env abre numa aba comum.", "suave"),
        ]
    blocos += [texto("Testes:"),
               bloco("codigo", texto=f'source "{venv}/bin/activate"\n{teste}' + ("\ncd web && python -m pytest -q"
                                                                                  if info["django"] else ""))]
    if info["exercicio"]:
        blocos += [texto("Questionário de revisão (resposta oculta em “Ver resposta”) — abre no navegador do Windows:"),
                   bloco("codigo", texto="explorer.exe exercicios.html"),
                   texto("Com o site no ar, o mesmo questionário está em /exercicios/.", "suave")]
    return ok(*blocos)


def sgs_padroes(ctx, args, _opcoes=None):
    arg = gs.normalizar(args[0]) if args else None
    mapa_escopo = {"arquitetura": "arquitetura", "arq": "arquitetura", "classe": "classe", "entidade": "classe",
                   "campo": "campo", "atributo": "campo", "relacao": "relacao", "ligacao": "relacao", "fk": "relacao"}
    escopo_filtro = mapa_escopo.get(arg) if arg else None
    filtro = gs.APELIDOS.get(arg) if (arg and not escopo_filtro) else None
    if args and not escopo_filtro and filtro not in ("gof", "criacao", "estrutural", "comportamental", "fundamentos"):
        return falha("filtro desconhecido: use categoria (criacao, estrutural, comportamental, fundamentos, gof) "
                     "ou escopo (arquitetura, classe, campo, relacao)")
    blocos = []
    nomes_esc = {e["id"]: e["nome"] for e in sgs_wysiwyg.ESCOPOS_PADRAO}
    for c in catalogo()["categorias"]:
        if filtro and not (filtro == c["chave"] or (filtro == "gof" and c["chave"] != "fundamentos")):
            continue
        itens = [p for p in c["padroes"]
                 if not escopo_filtro or sgs_wysiwyg.ESCOPO_DO_PADRAO.get(p["chave"], "classe") == escopo_filtro]
        if not itens:
            continue
        blocos.append(bloco("titulo", texto=f"{c['nome']} ({len(itens)})"))
        blocos.append(bloco("tabela", colunas=["chave", "escopo", "padrão", "palavras que ativam"],
                            linhas=[[cmd(p["chave"], f"sgs gerar generico {p['chave']}", True),
                                     nomes_esc.get(sgs_wysiwyg.ESCOPO_DO_PADRAO.get(p["chave"], "classe"), "Classe"),
                                     p["titulo"], ", ".join(p["palavras"])] for p in itens]))
    blocos.append(texto("Filtros por escopo: sgs padroes arquitetura · classe · campo · relacao", "suave"))
    blocos.append(bloco("link", texto="Referência: cópia da Wikipédia com a lista GoF", href="/referencia"))
    return ok(*blocos)


def _opcoes_novo_dominio(args):
    """Separa argumentos de `sgs dominios novo [chave] sistema=... entidade=... palavras=... [setor=...] ...`."""
    dados = {"chave": "", "sistema": "", "entidade": "", "palavras": "", "setor": modulo_dominios.SETOR_PADRAO,
             "ident": "cliente", "recurso": "codigo", "quantidade": "quantidade", "preco": "valor_unitario",
             "unidade": "unidade(s)"}
    sem_perguntar = False
    pos = []
    for arg in args:
        if arg.lower() in SEM_PERGUNTAR:
            sem_perguntar = True
        elif "=" in arg:
            k, v = arg.split("=", 1)
            k = gs.normalizar(k)
            if k in dados:
                dados[k] = v.strip()
        else:
            pos.append(arg)
    if pos and not dados["chave"]:
        dados["chave"] = pos[0]
    return dados, sem_perguntar


def _salvar_dominio(ctx, dados):
    try:
        novo = modulo_dominios.cadastrar_dominio(
            dados["chave"], dados["sistema"], dados["entidade"], dados["palavras"],
            setor=dados.get("setor") or modulo_dominios.SETOR_PADRAO,
            ident=dados.get("ident") or "cliente",
            recurso=dados.get("recurso") or "codigo",
            quantidade=dados.get("quantidade") or "quantidade",
            preco=dados.get("preco") or "valor_unitario",
            unidade=dados.get("unidade") or "unidade(s)",
            caminho=ctx.caminho_dominios_extras,
        )
    except ValueError as erro:
        return falha(str(erro))
    gs.recarregar_dominios(ctx.caminho_dominios_extras)
    return ok(
        texto(f"✓ domínio {int(novo['id']):03d} ({novo['chave']} · {novo['sistema']} · {novo['entidade']}) "
              f"cadastrado com {len(novo['palavras'])} palavra(s)!", "ok"),
        bloco("tabela", colunas=["campo", "valor"], linhas=[
            ["ID / chave", f"{int(novo['id']):03d} · {novo['chave']}"],
            ["sistema / entidade", f"{novo['sistema']} · {novo['entidade']}"],
            ["setor", novo["setor"]],
            ["palavras", ", ".join(novo["palavras"])],
            ["campos básicos", f"{novo['ident']} · {novo['recurso']} · {novo['quantidade']} ({novo['unidade']}) · {novo['preco']}"],
        ]),
        bloco("botoes", itens=[
            cmd(f"sgs gerar {novo['chave']} prova", f"sgs gerar {novo['chave']} prova"),
            cmd(f"sgs dominios {novo['chave']}", f"sgs dominios {novo['chave']}"),
            cmd("sgs dominios", "sgs dominios"),
        ]),
        texto(f"Salvo em dominios_extras.json e já ativo no SGS! Para remover depois: sgs dominios remover {novo['chave']}",
              "suave"),
    )


def sgs_dominios(ctx, args, _opcoes=None):
    """sgs dominios → setores · sgs dominios <termo> → filtra · sgs dominios novo → adiciona domínio ·
    sgs dominios remover <chave|id> → remove domínio personalizado."""
    sub = args[0].lower() if args else ""
    if sub in ("novo", "adicionar", "add", "criar"):
        resto = args[1:]
        if resto and all(a.lower() in SEM_PERGUNTAR for a in resto):
            q = ctx.questionario
            if not isinstance(q, perguntas.QuestionarioDominio):
                return falha("não há cadastro de domínio em andamento — use: sgs dominios novo")
            ctx.questionario = None
            resposta = _salvar_dominio(ctx, q.argumentos())
            if resposta["ok"]:
                resposta["blocos"].insert(0, texto(f"✓ cadastro concluído ({q.respostas} resposta(s))", "ok"))
            return resposta
        dados, sem_perguntar = _opcoes_novo_dominio(resto)
        completo = all(dados[k] for k in ("chave", "sistema", "entidade", "palavras"))
        if completo:
            ctx.questionario = None
            return _salvar_dominio(ctx, dados)
        if sem_perguntar:
            return falha('para cadastrar direto numa linha, informe chave, sistema=, entidade= e palavras=: '
                         'sgs dominios novo energia_maremotriz sistema="Maré Energia" entidade=TurbinaMare '
                         'palavras="maremotriz, turbina submarina, energia das mares, oceano"')
        q = perguntas.QuestionarioDominio(
            chave=dados["chave"], sistema=dados["sistema"], entidade=dados["entidade"],
            palavras=dados["palavras"], setor=dados["setor"], caminho_extras=ctx.caminho_dominios_extras,
        )
        ctx.questionario = q
        return ok(texto("Cadastrar novo domínio personalizado (além dos 300 nativos): responda os dados básicos e "
                        "as palavras-chave (conclua com `sgs dominios novo -sp`).", "destaque"),
                  *perguntas.blocos(q))
    if sub in ("remover", "excluir", "apagar", "del"):
        if len(args) < 2:
            return falha("informe a chave ou ID do domínio personalizado: sgs dominios remover <chave|id>")
        try:
            removido = modulo_dominios.remover_dominio(args[1], caminho=ctx.caminho_dominios_extras)
        except ValueError as erro:
            return falha(str(erro))
        gs.recarregar_dominios(ctx.caminho_dominios_extras)
        return ok(texto(f"✓ domínio personalizado {int(removido['id']):03d} ({removido['chave']}) removido.", "ok"))
    termo = " ".join(args).strip()
    if not termo:
        setores = {}
        for chave, _d, info, _ in gs.filtrar_dominios():
            setores.setdefault(info["setor"], []).append((info["id"], chave))
        linhas = [[f"{itens[0][0]}–{itens[-1][0]}", cmd(nome, f"sgs dominios {nome.split(',')[0].split()[0]}"),
                   " · ".join(chave for _, chave in itens)] for nome, itens in setores.items()]
        return ok(texto(f"{len(gs.DOMINIOS)} domínios em {len(setores)} setores. Para ver os detalhes sem encher a tela: "
                        "sgs dominios <termo> (ex.: sgs dominios saude · sgs dominios pet · sgs dominios 045)."),
                  bloco("tabela", colunas=["IDs", "setor", "domínios"], linhas=linhas),
                  bloco("botoes", itens=[cmd("sgs dominios novo", "sgs dominios novo")]),
                  texto("O pedido escolhe o domínio por PONTOS: cada palavra do domínio que aparece vale 1 e o nome do "
                        "domínio vale +3; o genérico só entra quando nenhum outro bate. Para adicionar um novo domínio: "
                        "sgs dominios novo.", "suave"))
    achados = gs.filtrar_dominios(termo)
    if not achados:
        return falha(f"nenhum domínio com “{termo}” — veja os setores com: sgs dominios (ou cadastre com: sgs dominios novo)")
    linhas = [[info["id"], cmd(chave, f"sgs gerar {chave} ", True), d["sistema"], d["entidade"], info["setor"],
               f"{len(d['palavras'])} palavras · " + (", ".join((bateram or d["palavras"])[:6]) or "(padrão)")]
              for chave, d, info, bateram in achados]
    return ok(texto(f"{len(achados)} domínio(s) com “{termo}”:"),
              bloco("tabela", colunas=["ID", "domínio", "sistema", "entidade", "setor", "palavras"], linhas=linhas))


def sgs_config(ctx, args, _opcoes=None):
    if not args:
        return ok(bloco("titulo", texto="Configuração (sgs config chave=valor para mudar)"), tabela_config(ctx.config),
                  config=ctx.config.publica())
    erros, mudou = [], []
    for par in args:
        if "=" not in par:
            erros.append(f"{par}: use chave=valor")
            continue
        chave, valor = par.split("=", 1)
        try:
            ctx.config.alterar(chave.strip(), valor)
            mudou.append(chave.strip())
        except ValueError as erro:
            erros.append(str(erro))
    if mudou:
        ctx.config.salvar()
    blocos = [texto(f"✓ alterado: {', '.join(mudou)}", "ok")] if mudou else []
    blocos += [texto(e, "erro") for e in erros]
    blocos.append(tabela_config(ctx.config))
    return {"ok": not erros, "blocos": blocos, "config": ctx.config.publica()}


def sgs_pwa(ctx, args, _opcoes=None):
    """sgs pwa · sgs pwa=true · sgs pwa=false (também: sgs pwa false)."""
    valor = None
    if args and "=" in args[0]:
        valor = args[0].split("=", 1)[1]
    elif len(args) > 1:
        valor = args[1]
    if valor is not None:
        ctx.config.alterar("pwa", valor)
        ctx.config.salvar()
    if ctx.config.valores["pwa"]:
        msg = "PWA ligado (padrão): os sites abrem numa janela de app isolada — sem abas nem barra de endereço"
    else:
        msg = "PWA desligado: os sites abrem numa aba comum do navegador (sgs pwa=true volta ao padrão)"
    return ok(texto(("✓ " if valor is not None else "") + msg, "ok"),
              texto("sgs pwa=true · sgs pwa=false · vale para o sgs rodar, python manage.py runserver e bash "
                    "iniciar.sh pela tela", "suave"), config=ctx.config.publica())


def sgs_comand_cmd(ctx, args, _opcoes=None):
    if not args:
        return ok(*sgs_comand.listar(), tela="comand")
    if not args[0].isdigit():
        return falha("use: sgs comand (a lista) ou sgs comand n (ex.: sgs comand 11)", tela="comand")
    return ok(*sgs_comand.detalhe(int(args[0])), tela="comand")


def sgs_exit(ctx, _args, _opcoes=None):
    return ok(texto("(já está na tela principal)", "suave"), tela="principal")


def _paginas_de_estudo():
    """As três páginas de estudo lado a lado (a mesma barra fica no topo de cada uma)."""
    return bloco("botoes", itens=[{"texto": "Tutorial", "href": "/tutorial"},
                                  {"texto": "Wiki · padrões GoF", "href": "/referencia"},
                                  {"texto": "Django Study Hub", "href": "/hub"}])


def sgs_wiki(ctx, _args, _opcoes=None):
    return ok(bloco("link", texto="Padrão de projeto de software — cópia estática da Wikipédia", href="/referencia"),
              texto(f"arquivo: Gerador_Sistemas/{gs.REFERENCIA_GOF} (com o layout e o CSS da própria Wikipédia)",
                    "suave"), _paginas_de_estudo(), abrir="/referencia")


def sgs_hub(ctx, _args, _opcoes=None):
    return ok(bloco("link", texto="Django Study Hub — cópia estática (mrsautchuk.github.io/django-study-hub)", href="/hub"),
              texto("arquivo: Gerador_Sistemas/referencias/django_study_hub.html (origem e data no rodapé do site)",
                    "suave"), _paginas_de_estudo(), abrir="/hub")


def sgs_tutorial_cmd(ctx, _args, _opcoes=None):
    """sgs tutorial: o passo a passo prático (abre a página /tutorial) e um resumo aqui mesmo."""
    return ok(bloco("titulo", texto="sgs tutorial — o SGS em 9 passos (a página abriu em outra janela)"),
              bloco("tabela", colunas=["passo", "comando"],
                    linhas=[[passo, comando] for passo, comando in sgs_tutorial.resumo()]),
              bloco("link", texto="abrir o tutorial completo: /tutorial", href="/tutorial"),
              _paginas_de_estudo(), abrir="/tutorial")


def sgs_wysiwyg_cmd(ctx, args, _opcoes=None):
    """sgs wysiwyg [NN] — abre o Modo WYSIWYG (bancada Kanban de encaixe de blocos) no navegador."""
    href = "/wysiwyg"
    if args:
        try:
            _, n = escolher(ctx, args[0])
            href = f"/wysiwyg?projeto={n}"
        except ValueError as erro:
            return falha(str(erro))
    return ok(bloco("titulo", texto="Modo WYSIWYG — bancada Kanban de blocos (CMD ↔ WYSIWYG)"),
              bloco("link", texto=f"abrir o Modo WYSIWYG: {href}", href=href),
              texto("Monte Domínio, Classes, Campos (arrastar-e-soltar), Ligações FK, API REST e Padrões de Projeto "
                    "com bloqueio automático de padrões mutuamente excludentes.", "suave"),
              abrir=href)


def sgs_cmd(ctx, args, _opcoes=None):
    """sgs cmd [sgs] — o estilo desta tela. sgs cmd = como o Prompt de Comando do Windows (preto e cinza, o padrão
    ao abrir) · sgs cmd sgs = as cores do SGS (prompt verde). Sem o "sgs" na frente também vale: cmd · cmd sgs."""
    escolha = args[0].split("=", 1)[-1].strip().lower() if args else "cmd"
    escolha = "cmd" if escolha in ("cmd", "ps", "powershell", "windows") else escolha
    try:
        ctx.config.alterar("visual", escolha)
    except ValueError:
        return falha(f"estilo desconhecido: {args[0]} — use sgs cmd (Prompt de Comando) ou sgs cmd sgs (cores do SGS)",
                     config=ctx.config.publica())
    ctx.config.salvar()
    if escolha == "cmd":
        return ok(texto("tela no estilo do Prompt de Comando · para as cores do SGS: sgs cmd sgs", "suave"),
                  config=ctx.config.publica())
    return ok(texto("tela nas cores do SGS · para voltar ao estilo do Prompt de Comando: sgs cmd", "suave"),
              config=ctx.config.publica())


def _alternar(ctx, chave, args):
    """Liga/desliga uma chave booleana do config (sem argumento: inverte · com sim/não: fixa) e grava."""
    ctx.config.alterar(chave, args[0] if args else not ctx.config.valores[chave])
    ctx.config.salvar()
    return ctx.config.valores[chave]


def sgs_topo(ctx, args, _opcoes=None):
    """sgs topo — mostra os comandos principais no topo; de novo, oculta (alterna). sgs topo sim|nao fixa."""
    if _alternar(ctx, "topo", args):
        msg = "comandos do topo à mostra · sgs topo de novo oculta"
    else:
        msg = "comandos do topo ocultos · sgs topo de novo mostra"
    return ok(texto(msg, "suave"), config=ctx.config.publica())


def sgs_foot(ctx, args, _opcoes=None):
    """sgs foot — mostra as caixas de seleção do rodapé; de novo, oculta (alterna; a linha do comando sempre fica)."""
    if _alternar(ctx, "rodape", args):
        msg = "caixas de seleção à mostra · sgs foot de novo oculta"
    else:
        msg = "caixas de seleção ocultas (a linha do comando fica) · sgs foot de novo mostra"
    return ok(texto(msg, "suave"), config=ctx.config.publica())


def sgs_limpar(ctx, _args, _opcoes=None):
    return {"ok": True, "blocos": [], "limpar": True}


def sgs_duplicar(ctx, args, opcoes=None):
    """sgs duplicar NN → CÓPIA versionada NN.k (01.1 … 01.99) — o original NN não muda (único comando que duplica)."""
    destino, n = escolher(ctx, args[0] if args else None)
    nova, numero = nova_versao(destino, ctx.config.valores["porta_base"], ctx.saida)
    c = cartao(nova, info_sistema(nova), ctx.saida, ctx.config.valores["porta_base"])
    return ok(texto(f"✓ cópia (versão {numero}) criada a partir do {n} ({nova.name}) — o original {n} não mudou", "ok"),
              bloco("botoes", itens=[cmd(f"sgs editar {numero}"), cmd(f"sgs incrementar {numero}"),
                                     cmd(f"sgs ligar {numero}"), cmd(f"sgs rodar {numero}"), cmd(f"cd {numero}")]),
              texto(f"Para alterar a cópia: sgs editar {numero} · porta da cópia: {c['porta']}", "suave"),
              cartao=c)


def sgs_editar(ctx, args, opcoes=None):
    """sgs editar NN → painel guiado de edição do PRÓPRIO sistema NN (nunca duplica).
    Atalhos: sgs editar NN app|ligar|incrementar|api …  ·  Para criar cópia antes, use sgs duplicar NN."""
    if len(args) > 1:
        sub = args[1].lower()
        if sub in ("app", "modulo", "módulo"):
            return sgs_app(ctx, [args[0]] + args[2:], opcoes)
        if sub == "ligar":
            return sgs_ligar(ctx, [args[0]] + args[2:], opcoes)
        if sub in ("incrementar", "campo", "campos", "modificar"):
            return sgs_incrementar(ctx, [args[0]] + args[2:], opcoes)
        if sub == "api":
            resto = args[2:]
            if resto and resto[0].lower() == "config":
                return sgs_api(ctx, ["config", args[0]] + resto[1:], opcoes)
            return sgs_api(ctx, ["config", args[0]] + resto, opcoes)
    destino, n = escolher(ctx, args[0] if args else None)
    info = info_sistema(destino)
    classes = gs.classes_do_projeto(destino)
    entidades = gs.entidades_do_projeto(destino)
    uma = sorted(classes)[0] if classes else (sorted(entidades)[0] if entidades else "Classe")
    blocos = [bloco("titulo", texto=f"Editar o sistema {n} — {info['sistema']} ({destino.name})"),
              texto(f"Todas as edições abaixo alteram DIRETAMENTE o sistema {n} (nenhuma cópia é criada). "
                    f"Se quiser preservar antes de mexer, use sgs duplicar {n}.", "destaque")]
    if classes:
        resumo_classes = [[nome, "principal" if dados["principal"] else f"módulo {dados['app']}",
                           ", ".join(a["nome"] for a in dados["atributos"])]
                          for nome, dados in sorted(classes.items())]
        blocos.append(bloco("tabela", colunas=["classe", "onde", "campos atuais"], linhas=resumo_classes))
    acoes = [
        ["Incrementar Campos", cmd(f"sgs incrementar {n}"),
         f"criar campo novo ou mudar regra/@property em {uma} (ex.: sgs incrementar {n} {uma}.cidade texto)"],
        ["Ligar Classes", cmd(f"sgs ligar {n}"),
         f"criar relacionamento ForeignKey entre classes do {n} (conduz passo a passo ou explica como criar a 2ª classe)"],
    ]
    if info["django"]:
        acoes.append(["Nova Classe / App", cmd(f"sgs app {n} ", f"sgs app {n} ", True),
                      f"acrescentar nova funcionalidade (model, form, CRUD, API REST e testes) no próprio {n}"])
        acoes.append(["Configurar API", cmd(f"sgs api config {n}"),
                      f"escolher quais campos cada endpoint da API do {n} expõe"])
    acoes.append(["Abrir pasta", cmd(f"cd {n}"), f"entrar na pasta do {n} para editar arquivos pelo terminal"])
    acoes.append(["Duplicar (cópia)", cmd(f"sgs duplicar {n}"),
                  f"criar cópia versionada {n}.k sem alterar o original {n}"])
    blocos.append(bloco("titulo", texto="O que você deseja fazer neste sistema?"))
    blocos.append(bloco("tabela", colunas=["ação", "comando (clique)", "o que faz"], linhas=acoes))
    blocos.append(texto(f"Atalhos rápidos: sgs editar {n} incrementar · sgs editar {n} ligar · sgs editar {n} app <pedido>",
                        "suave"))
    return ok(*blocos)


SEM_VERSAO = ("-sv", "--sem-versao", "--sem-versão")


def _opcoes_do_app(args):
    """Separa do pedido as opções do sgs app: entidade=, padroes=, ligar=, -sp (sem perguntar); -sv aceito por compatibilidade."""
    o = {"entidade": None, "padroes": None, "ligar": None, "sem_perguntar": False}
    resto = []
    for arg in args:
        baixo = arg.lower()
        if baixo in SEM_VERSAO:
            continue
        elif baixo in SEM_PERGUNTAR:
            o["sem_perguntar"] = True
        elif baixo.startswith("entidade="):
            o["entidade"] = arg.split("=", 1)[1].strip() or None
        elif baixo.split("=", 1)[0] in ("padroes", "padrões", "padrao", "padrão") and "=" in baixo:
            o["padroes"] = [p for p in re.split(r"[,;\s]+", arg.split("=", 1)[1]) if p] or None
        elif baixo.startswith("ligar="):
            o["ligar"] = arg.split("=", 1)[1].strip() or None
        else:
            resto.append(arg)
    return " ".join(resto).strip(), o


def _ler_ligar(texto, nova):
    """"Viagcert.destino" → ("Viagcert", "destino", <a classe nova>) · "Voo.destino:Destino" → ("Voo", "destino", "Destino")."""
    m = re.fullmatch(r"(\w+)\.(\w+)(?::(\w+))?", texto or "")
    if not m:
        raise ValueError("use ligar=Classe.campo (a Classe ganha o campo apontando para a classe nova; ex.: "
                         "ligar=Viagcert.destino) ou ligar=Classe.campo:Alvo")
    return m.group(1), m.group(2), m.group(3) or nova


def sgs_app(ctx, args, opcoes=None):
    """sgs app NN <pedido> [entidade=Nome] [padroes=a,b] [ligar=Classe.campo] [-sp]

    Acrescenta DIRETAMENTE ao sistema NN MAIS UMA app Django (a funcionalidade nova): form (ModelForm), CRUD completo,
    API REST, os padrões pedidos (núcleo dentro da app), settings, models, views e testes. Com "Perguntar antes de
    gerar", conduz: nome pelo contexto, ligação com classes existentes, campos e padrões. Para criar cópia antes, use
    sgs duplicar NN.
    """
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    if args and all(a.lower() in SEM_PERGUNTAR for a in args):         # sgs app -sp: encerra as perguntas e aplica
        if not isinstance(ctx.questionario, perguntas.QuestionarioModulo):
            return falha("não há perguntas de módulo em andamento — use: sgs app NN <pedido>")
        return _concluir_modulo(ctx, opcoes)
    if not args:
        raise ValueError("use: sgs app NN <pedido> — ex.: sgs app 16 destinos de viagem ligar=Viagcert.destino")
    destino, n = escolher(ctx, args[0])
    pedido, o = _opcoes_do_app(args[1:])
    if not pedido:
        raise ValueError(f"diga que funcionalidade acrescentar: sgs app {n} <pedido> (ex.: sgs app {n} destinos de "
                         "viagem com os campos cidade e pais)")
    if len(pedido) > LIMITE_PEDIDO:
        return falha(f"pedido longo demais (máximo {LIMITE_PEDIDO} caracteres)")
    if not info_sistema(destino)["django"]:
        return falha(f"o sistema {n} não tem o site Django — um módulo é uma app Django: gere o sistema com a "
                     "caixa “+ Django” marcada")
    if c["perguntar"] and not o["sem_perguntar"]:
        q = perguntas.QuestionarioModulo(pedido, c, destino, n, marcadas=["testar"] if c["testar"] else [],
                                         entidade=o["entidade"], padroes=o["padroes"], ligar=o["ligar"])
        ctx.questionario = q
        return ok(texto(f"Antes de acrescentar a funcionalidade no sistema {n}, algumas perguntas (o nome dela depende "
                        f"do contexto). Pedido: {pedido}", "destaque"), *perguntas.blocos(q))
    ctx.questionario = None
    return _aplicar_modulo(ctx, destino, n, pedido, entidade=o["entidade"], padroes=o["padroes"], ligar=o["ligar"],
                           testar=c["testar"])


def _concluir_modulo(ctx, opcoes=None):
    q, ctx.questionario = ctx.questionario, None
    a = q.argumentos()
    resposta = _aplicar_modulo(ctx, q.projeto, q.numero, a["pedido"], entidade=a["entidade"], padroes=a["padroes"],
                               ligar=a["ligar"], testar=a["testar"], dominio=a["dominio"], campos=a["campos"])
    if resposta["ok"]:
        resposta["blocos"].insert(0, texto(f"✓ perguntas encerradas ({q.respostas} resposta(s)) — aplicando no sistema "
                                           f"{q.numero} com as decisões tomadas", "ok"))
    return resposta


def _aplicar_modulo(ctx, destino, n, pedido, entidade=None, padroes=None, ligar=None, testar=True,
                    dominio=None, campos=None):
    """Planeja TUDO (módulo e ligação) antes de mexer em qualquer arquivo; aplica diretamente no sistema NN."""
    if not Path(destino).is_dir():
        return falha(f"o sistema {n} não existe mais no disco — rode sgs listar")
    info = info_sistema(destino)
    try:
        plano = gs.preparar_modulo(destino, pedido, entidade=entidade, campos=campos, padroes=padroes, dominio=dominio)
        m = plano["modulo"]
        lig = None
        if ligar:
            origem, campo, alvo = ligar if isinstance(ligar, tuple) else _ler_ligar(ligar, m["entidade"])
            novas = {m["entidade"]: {"app": m["app"], "pacote": m["pacote"], "caminho": m["caminho"]}}
            lig = gs.planejar_ligacao(destino, origem, campo, alvo, novas=novas)
    except (gs.ErroGerador, ValueError) as erro:
        return falha(str(erro))
    alvo_dir, numero = destino, n
    gs.aplicar_modulo(alvo_dir, plano)
    linhas = [["app", m["pacote"]], ["classe", m["entidade"]], ["padrões", ", ".join(m["padroes"])],
              ["telas (CRUD)", f"/{m['app']}/  ·  /{m['app']}/novo/  ·  /{m['app']}/<id>/  ·  editar/  ·  excluir/"],
              ["API REST", f"/{m['app']}/api/v1/  (GET, POST)  ·  /{m['app']}/api/v1/<id>/  (GET, PUT, PATCH, DELETE)"],
              ["arquivos", f"web/{m['caminho']}/  (settings · models · forms · views · api · urls · nucleo/ · tests/)"]]
    if lig:
        try:
            lig = gs.ligar_classes(alvo_dir, lig["origem"], lig["campo"], lig["alvo"], comentarios=info["comentarios"])
        except gs.ErroGerador as erro:
            return falha(f"o módulo {m['app']} entrou em {numero}, mas a ligação falhou: {erro}")
        linhas.append(["ligação", f"{lig['origem']}.{lig['campo']} → {lig['alvo']}  (opcional; no form e na API)"])
    linhas.append(["migrations", (lig or plano).get("migrations") or "—"])
    return _resposta_da_edicao(ctx, alvo_dir, numero, testar, info, linhas, f"o módulo {m['app']} ({m['entidade']})")


def _resposta_da_edicao(ctx, alvo_dir, numero, testar, info, linhas, o_que):
    resposta = cartao(alvo_dir, info_sistema(alvo_dir), ctx.saida, ctx.config.valores["porta_base"])
    if testar:
        resposta["testes"] = gs.executar_testes(alvo_dir, SimpleNamespace(exercicio=info["exercicio"],
                                                                          django=info["django"]))
    titulo = f"✓ {o_que}: aplicado no sistema {numero}"
    blocos = [texto(titulo, "ok"), bloco("tabela", colunas=["", ""], linhas=linhas)]
    reinicio = ctx.reiniciar_site(alvo_dir, numero) if info["django"] else []   # no ar: volta com o código novo
    if reinicio:
        blocos += reinicio
    elif info["django"]:
        blocos.append(texto(f"suba com: sgs rodar {numero} (porta {resposta['porta']}) · para criar cópia antes de "
                            f"novas mudanças: sgs duplicar {numero}", "suave"))
    return ok(*blocos, cartao=resposta)


def sgs_incrementar(ctx, args, opcoes=None):
    """sgs incrementar NN Classe.campo <padrão> [-sp] — acrescenta (campo novo) ou MODIFICA um campo de uma classe do
    PRÓPRIO sistema NN, com o padrão (a regra) dele: inteiro>=0, inteiro:1..30, decimal>=0, lista:a,b,c, texto,
    texto-livre, simnao, data.

    A classe é refeita pelo gerador: a regra vale no @property do núcleo (o setter recusa negativo, letras, valor
    fora da lista…) e no model/form/API do Django; os testes acompanham. Com "Perguntar", conduz passo a passo:
    classe, campo, padrão e valor. sgs incrementar NN sozinho mostra as classes, os campos e os padrões.
    """
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    if args and all(a.lower() in SEM_PERGUNTAR for a in args):       # sgs incrementar -sp: aplica as respostas
        q = ctx.questionario
        if not isinstance(q, perguntas.QuestionarioIncremento):
            return falha("não há perguntas de incremento em andamento — use: sgs incrementar NN")
        ctx.questionario = None
        a = q.argumentos()
        resposta = _aplicar_incremento(ctx, q.projeto, q.numero, a["classe"], a["campo"], a["regra"], c["testar"])
        if resposta["ok"]:
            resposta["blocos"].insert(0, texto(f"✓ perguntas encerradas ({q.respostas} resposta(s))", "ok"))
        return resposta
    sem_perguntar = any(a.lower() in SEM_PERGUNTAR for a in args)
    resto = [a for a in args if a.lower() not in SEM_VERSAO + SEM_PERGUNTAR]
    destino, n = escolher(ctx, resto[0] if resto else None)
    classes = gs.classes_do_projeto(destino)
    if not classes:
        return falha(f"o sistema {n} não tem classes que o SGS saiba refazer (falta o especificacao.json?)")
    alvo = re.fullmatch(r"(\w+)\.(\w+)", resto[1]) if len(resto) > 1 else None
    if len(resto) > 1 and alvo is None:
        raise ValueError(f"use: sgs incrementar {n} Classe.campo <padrão> (ex.: sgs incrementar {n} "
                         f"{sorted(classes)[0]}.assento lista:janela,meio,corredor)")
    classe, campo = (alvo.group(1), alvo.group(2)) if alvo else (None, None)
    regra = " ".join(resto[2:]) or None
    if c["perguntar"] and not sem_perguntar:
        q = perguntas.QuestionarioIncremento(destino, n, classes, classe, campo, regra)
        ctx.questionario = q
        return ok(texto(f"Incrementar Campos no sistema {n} (altera diretamente o {n}; para cópia antes, use sgs "
                        f"duplicar {n}): escolha a classe, o campo e o padrão.", "destaque"),
                  *perguntas.blocos(q))
    if classe and not regra:                                   # só faltou o padrão: mostra o campo e exemplos prontos
        return _como_incrementar_o_campo(n, classes, classe, campo)
    if not (classe and regra):
        linhas = [[cmd(f"{nome}.{a['nome']}", f"sgs incrementar {n} {nome}.{a['nome']} ", True), gs.regra_em_texto(a),
                   gs.descrever_regra(a).split(": ", 1)[1]]
                  for nome, info in sorted(classes.items()) for a in info["atributos"]]
        uma = sorted(classes)[0]
        campo_um = classes[uma]["atributos"][0]["nome"]
        return ok(texto(f"INCREMENTAR CAMPOS no sistema {n}: define o PADRÃO (a regra) de um campo — cria um campo "
                        f"novo ou altera a regra de um campo existente diretamente no {n}. Campos atuais (clique para "
                        f"escolher):"),
                  bloco("tabela", colunas=["classe.campo", "padrão hoje", "o que aceita"], linhas=linhas),
                  bloco("titulo", texto="Como usar"),
                  bloco("tabela", colunas=["", "comando", "o que faz"], linhas=[
                      ["modificar", cmd(f"sgs incrementar {n} {uma}.{campo_um} texto",
                                        f"sgs incrementar {n} {uma}.{campo_um} ", True),
                       f"o campo {campo_um} (que já existe) passa a seguir o padrão dado"],
                      ["incrementar", cmd(f"sgs incrementar {n} {uma}.assento lista:janela,meio,corredor",
                                          f"sgs incrementar {n} {uma}.assento lista:janela,meio,corredor", True),
                       f"a {uma} GANHA o campo assento, que só aceita esses 3 valores"]]),
                  bloco("titulo", texto="Padrões que um campo pode seguir"),
                  bloco("tabela", colunas=["padrão", "o que faz"], linhas=[[p, o] for p, o in gs.REGRAS_DE_CAMPO]),
                  texto(f"Formato: sgs incrementar {n} Classe.campo <padrão> · altera diretamente o sistema {n} "
                        f"(para criar cópia antes, use sgs duplicar {n}). Vale no @property do núcleo e no "
                        f"model/form/API do Django.", "suave"))
    return _aplicar_incremento(ctx, destino, n, classe, campo, regra, c["testar"])


def _como_incrementar_o_campo(n, classes, classe, campo):
    """sgs incrementar NN Classe.campo (sem o padrão): como o campo está hoje e comandos prontos para ele."""
    nome_classe = gs.achar_classe(classes, classe)
    if nome_classe is None:
        return falha(f"a classe {gs.camel(classe)} não existe no sistema {n} (ele tem: {', '.join(sorted(classes))})")
    campo = gs.camel_para_snake(gs.camel(campo))
    atual = next((a for a in classes[nome_classe]["atributos"] if a["nome"] == campo), None)
    base = f"sgs incrementar {n} {nome_classe}.{campo}"
    exemplos = ["inteiro>=0", "inteiro:1..30", "decimal>=0", "lista:janela,meio,corredor", "texto", "simnao", "data"]
    if atual:
        situacao = texto(f"{nome_classe}.{campo} hoje: {gs.regra_em_texto(atual)} — "
                         f"{gs.descrever_regra(atual).split(': ', 1)[1]}. Diga o padrão NOVO:")
    else:
        situacao = texto(f"A {nome_classe} ainda não tem o campo {campo}: ele será CRIADO diretamente no sistema {n} "
                         f"com o padrão que você der:")
    explica = dict(gs.REGRAS_DE_CAMPO)
    return ok(situacao,
              bloco("tabela", colunas=["comando (clique para escrever)", "o que o campo passa a aceitar"],
                    linhas=[[cmd(f"{base} {e}", f"{base} {e}", True), explica[e]] for e in exemplos]),
              texto(f"Altera diretamente o sistema {n}. Se quiser preservar antes, use sgs duplicar {n}.", "suave"))


def _aplicar_incremento(ctx, destino, n, classe, campo, regra, testar):
    if not Path(destino).is_dir():
        return falha(f"o sistema {n} não existe mais no disco — rode sgs listar")
    info = info_sistema(destino)
    try:
        plano = gs.planejar_incremento(destino, classe, campo, regra)       # tudo conferido ANTES de escrever
    except gs.ErroGerador as erro:
        return falha(str(erro))
    alvo_dir, numero = destino, n
    plano = gs.aplicar_incremento(alvo_dir, plano, comentarios=info["comentarios"])
    linhas = [["campo", f"{plano['classe']}.{plano['campo']} ({plano['acao']})"],
              ["padrão", f"{plano['regra']} — {plano['descricao'].split(': ', 1)[1]}"],
              ["onde vale", "@property do núcleo (o setter recusa o que não segue o padrão)"
               + (" · model (validators/choices) · form · API REST" if info["django"] else "")],
              ["testes", "os da classe foram refeitos com o padrão novo"],
              ["migrations", plano["migrations"]]]
    return _resposta_da_edicao(ctx, alvo_dir, numero, testar, info, linhas,
                               f"o campo {plano['classe']}.{plano['campo']} ({plano['acao']})")


def _achar_endpoint(endpoints, alvo):
    """"/api/v1/", "/destinos/api/v1/", "destinos", "destinos.resumo", "v1" ou "resumo" (da app principal)."""
    alvo = alvo.strip()
    rota = alvo.strip("/")
    for ep in endpoints:
        if rota and rota == ep["rota"].strip("/"):
            return ep
    app, _, endpoint = alvo.replace(":", ".").partition(".")
    if app in ("v1", "resumo") and not endpoint:
        app, endpoint = endpoints[0]["app"] if endpoints else "", app
    endpoint = endpoint or "v1"
    return next((ep for ep in endpoints if ep["app"] == app.lower() and ep["endpoint"] == endpoint), None)


def _tabela_api(ctx, destino, n, endpoints, so=None):
    linhas = []
    for ep in endpoints:
        if so is not None and ep is not so:
            continue
        for campo, exposto, mudado in ep["campos"]:
            linhas.append([ep["rota"], campo,
                           {"texto": ("sim" if exposto else "não") + (" · mudado" if mudado else ""),
                            "cor": "ok" if exposto else "suave"},
                           cmd("ocultar" if exposto else "expor",
                               f"sgs api config {n} {ep['rota']} {campo}={'nao' if exposto else 'sim'}")])
    try:
        porta = ctx.porta_do(numero_de(destino, ctx.saida))
    except (ValueError, TypeError):
        porta = "PORTA"
    antigas = sorted({ep["app"] for ep in endpoints if not ep["suporta"]})
    blocos = [texto(f"Campos de cada endpoint da API do sistema {n} — clique em ocultar/expor (o padrão: o v1 mostra o "
                    "registro inteiro + total e valor_final; o resumo, que é o link “API” do site, mostra id, codigo, "
                    "titulo e valor):"),
              bloco("tabela", colunas=["endpoint", "campo", "exposto", ""], linhas=linhas),
              texto(f"Formato: sgs api config {n} <endpoint> campo=sim|nao [campo=sim|nao…] · todos=sim|nao · padrao "
                    "(volta ao padrão). Quem chama ainda escolhe entre os expostos: "
                    f"http://127.0.0.1:{porta}/api/v1/?campos=id,total · os campos de cada endpoint: "
                    f"http://127.0.0.1:{porta}/api/v1/campos/", "suave")]
    if antigas:
        blocos.append(texto(f"a(s) app(s) {', '.join(antigas)} vieram de uma versão anterior do gerador: a primeira "
                            "mudança refaz a classe (mesmas regras, campos configuráveis na API) — determinístico, as "
                            "ligações continuam", "aviso"))
    return blocos


def sgs_api(ctx, args, opcoes=None):
    """sgs api config NN [<endpoint> campo=sim|nao …] — que campos cada endpoint da API expõe.

    Endpoints de cada app: o v1 (REST: /api/v1/ e /api/v1/<id>/) e o resumo (/api/, o link "API" do site); nos
    módulos, com o nome da app na frente (/destinos/api/v1/). A escolha vai para o config/settings.py do sistema
    (<APP>_API_CAMPOS). É configuração: vale no próprio sistema (para testar numa cópia: sgs duplicar NN antes)."""
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    if args and args[0].lower() in ("config", "configurar"):
        args = args[1:]
    destino, n = escolher(ctx, args[0] if args else None)
    info = info_sistema(destino)
    if not info["django"]:
        return falha(f"o sistema {n} não tem o site Django — não há API para configurar")
    endpoints = gs.endpoints_do_projeto(destino)
    if len(args) < 2:
        return ok(*_tabela_api(ctx, destino, n, endpoints))
    if "=" in args[1] or args[1].lower() == "padrao":          # sem endpoint: vale para TODOS os do sistema
        alvos, pares = endpoints, args[1:]
    else:
        ep = _achar_endpoint(endpoints, args[1])
        if ep is None:
            return falha(f"endpoint {args[1]!r} não existe no sistema {n} — use um destes: "
                         + ", ".join(e["rota"] for e in endpoints) + f" (ou nenhum: sgs api config {n} todos=sim vale "
                         "para todos)", *_tabela_api(ctx, destino, n, endpoints))
        if len(args) < 3:
            return ok(*_tabela_api(ctx, destino, n, endpoints, so=ep))
        alvos, pares = [ep], args[2:]
    todos_os_campos = {campo for ep in alvos for campo, _, _ in ep["campos"]}
    ordens, erros = [], []
    for par in pares:
        chave, sinal, valor = par.partition("=")
        chave = chave.strip().lower()
        if chave == "padrao" and not sinal:
            ordens.append(("padrao", None))                     # volta ao padrão
        elif not sinal or valor.strip().lower() not in SIM | NAO:
            erros.append(f"{par}: use campo=sim ou campo=nao")
        elif chave != "todos" and chave not in todos_os_campos:
            erros.append(f"{chave}: não é campo de {', '.join(ep['rota'] for ep in alvos)} "
                         f"(campos: {', '.join(sorted(todos_os_campos))})")
        else:
            ordens.append((chave, valor.strip().lower() in SIM))
    if erros:
        return falha(" · ".join(erros), *_tabela_api(ctx, destino, n, endpoints, so=alvos[0] if len(alvos) == 1 else None))
    refeitas = {}
    for ep in alvos:                                            # app de antes: ganha os campos configuráveis
        if not ep["suporta"] and ep["classe"] not in refeitas:
            refeitas[ep["classe"]] = gs.refazer_classe(destino, ep["classe"], comentarios=info["comentarios"])
    escolhas = gs.ler_api_campos(destino)
    for ep in alvos:
        nomes = [campo for campo, _, _ in ep["campos"]]
        do_endpoint = escolhas.setdefault(ep["app"], {}).setdefault(ep["endpoint"], {})
        for chave, exposto in ordens:
            if chave == "padrao":
                do_endpoint.clear()
                continue
            for campo in (nomes if chave == "todos" else [chave] if chave in nomes else []):
                if exposto == gs.exposto_por_padrao(ep["endpoint"], campo):
                    do_endpoint.pop(campo, None)                # igual ao padrão: não precisa anotar
                else:
                    do_endpoint[campo] = exposto
    gs.gravar_api_campos(destino, escolhas)
    endpoints = gs.endpoints_do_projeto(destino)
    rotas = {ep["rota"] for ep in alvos}
    blocos = [texto(f"✓ {ep['rota']}: expostos agora — {', '.join(c for c, e, _ in ep['campos'] if e) or 'nenhum'}", "ok")
              for ep in endpoints if ep["rota"] in rotas]
    for classe, mudaram in refeitas.items():
        blocos.append(texto(f"a classe {classe} foi refeita pelo gerador de hoje para ter os campos configuráveis "
                            f"({len(mudaram)} arquivo(s) atualizado(s); as regras e as ligações são as mesmas)", "aviso"))
    if refeitas and c["testar"]:
        testes = gs.executar_testes(destino, SimpleNamespace(exercicio=info["exercicio"], django=True))
        blocos.append(bloco("tabela", colunas=["testes", "resultado"], linhas=[[t["rotulo"], t["resumo"]] for t in testes]))
    blocos += ctx.reiniciar_site(destino, n)                    # no ar: reinicia para a escolha valer já
    blocos += _tabela_api(ctx, destino, n, endpoints, so=_achar_endpoint(endpoints, alvos[0]["rota"]) if len(alvos) == 1
                          else None)
    return ok(*blocos)


def _como_ligar(n, entidades):
    """O passo a passo do sgs ligar (Ligar Classes), com as classes do sistema e exemplos prontos no próprio NN."""
    classes = sorted(entidades)
    uma = classes[0] if classes else "Classe"
    linhas = [[classe, i["app"], f"web/{i['caminho']}/"] for classe, i in sorted(entidades.items())]
    blocos = [texto(f"LIGAR CLASSES no sistema {n}: cria um campo de REFERÊNCIA (ForeignKey opcional) numa classe "
                    f"apontando para OUTRA classe do mesmo sistema (vira lista de escolha no formulário e campo na API "
                    f"REST). Classes atuais do sistema {n}:"),
              bloco("tabela", colunas=["classe", "app", "pasta"], linhas=linhas)]
    if len(classes) < 2:
        blocos.append(texto(f"O sistema {n} só tem a classe {uma}: para ligar duas classes, crie a outra classe "
                            f"primeiro (passo 1 ou o atalho abaixo).", "aviso"))
        passos = [
            ["1", cmd(f"sgs app {n} destinos de viagem", f"sgs app {n} destinos de viagem", True),
             f"cria a 2ª classe (ex.: Destino) diretamente no sistema {n}"],
            ["2", cmd(f"sgs ligar {n} {uma}.destino Destino", f"sgs ligar {n} {uma}.destino Destino", True),
             f"a {uma} ganha o campo destino → Destino diretamente no sistema {n}"],
            ["atalho", cmd(f"sgs app {n} destinos de viagem ligar={uma}.destino",
                           f"sgs app {n} destinos de viagem ligar={uma}.destino", True),
             "faz os passos 1 e 2 de uma vez"],
        ]
    else:
        segunda = classes[1]
        campo_ex = gs.camel_para_snake(segunda)
        passos = [
            ["ligar agora", cmd(f"sgs ligar {n} {uma}.{campo_ex} {segunda}",
                                f"sgs ligar {n} {uma}.{campo_ex} {segunda}", True),
             f"a {uma} ganha o campo {campo_ex} → {segunda} diretamente no sistema {n}"],
            ["inverso", cmd(f"sgs ligar {n} {segunda}.{gs.camel_para_snake(uma)} {uma}",
                            f"sgs ligar {n} {segunda}.{gs.camel_para_snake(uma)} {uma}", True),
             f"a {segunda} ganha o campo {gs.camel_para_snake(uma)} → {uma} diretamente no sistema {n}"],
            ["nova + ligar", cmd(f"sgs app {n} destinos de viagem ligar={uma}.destino",
                                 f"sgs app {n} destinos de viagem ligar={uma}.destino", True),
             "cria mais uma classe e já liga à existente de uma vez"],
        ]
    blocos += [bloco("titulo", texto="Como usar"),
               bloco("tabela", colunas=["passo", "comando (clique)", "o que faz"], linhas=passos),
               texto(f"Formato: sgs ligar {n} Classe.campo Alvo — Classe = quem GANHA o campo · campo = nome do campo "
                     f"· Alvo = classe para onde aponta (sem o Alvo, vale o nome do campo: destino → Destino). "
                     f"Altera diretamente o sistema {n} (para cópia antes, use sgs duplicar {n}). Apagar o Alvo só "
                     f"limpa o campo (SET_NULL).", "suave")]
    return ok(*blocos)


def _aplicar_ligacao(ctx, destino, n, origem, campo, alvo, testar):
    if not Path(destino).is_dir():
        return falha(f"o sistema {n} não existe mais no disco — rode sgs listar")
    info = info_sistema(destino)
    try:
        lig = gs.planejar_ligacao(destino, origem, campo, alvo)
    except gs.ErroGerador as erro:
        return falha(str(erro))
    alvo_dir, numero = destino, n
    try:
        lig = gs.ligar_classes(alvo_dir, lig["origem"], lig["campo"], lig["alvo"], comentarios=info["comentarios"])
    except gs.ErroGerador as erro:
        return falha(str(erro))
    linhas = [["ligação", f"{lig['origem']}.{lig['campo']} → {lig['alvo']}  (opcional; no form e na API)"],
              ["teste", f"tests/test_ligacao_{lig['campo']}.py (na app de {lig['origem']})"],
              ["migrations", lig["migrations"]]]
    return _resposta_da_edicao(ctx, alvo_dir, numero, testar, info, linhas,
                               f"a ligação {lig['origem']}.{lig['campo']} → {lig['alvo']}")


def sgs_ligar(ctx, args, opcoes=None):
    """sgs ligar NN Classe.campo Alvo [-sp] — LIGAR CLASSES: cria campo de referência (ForeignKey opcional) entre duas
    classes do PRÓPRIO sistema NN (ex.: sgs ligar 16 Viagcert.destino Destino). Com "Perguntar" ligado e ≥ 2 classes,
    conduz passo a passo (origem → alvo → nome do campo). Para criar cópia antes, use sgs duplicar NN."""
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    if args and all(a.lower() in SEM_PERGUNTAR for a in args):          # sgs ligar -sp: aplica o questionário
        q = ctx.questionario
        if not isinstance(q, perguntas.QuestionarioLigar):
            return falha("não há perguntas de ligação em andamento — use: sgs ligar NN")
        ctx.questionario = None
        a = q.argumentos()
        resposta = _aplicar_ligacao(ctx, q.projeto, q.numero, a["origem"], a["campo"], a["alvo"], c["testar"])
        if resposta["ok"]:
            resposta["blocos"].insert(0, texto(f"✓ perguntas encerradas ({q.respostas} resposta(s))", "ok"))
        return resposta
    sem_perguntar = any(a.lower() in SEM_PERGUNTAR for a in args)
    args = [a for a in args if a.lower() not in SEM_VERSAO + SEM_PERGUNTAR]
    destino, n = escolher(ctx, args[0] if args else None)
    entidades = gs.entidades_do_projeto(destino)
    if len(args) < 2:
        if c["perguntar"] and not sem_perguntar and len(entidades) >= 2:
            q = perguntas.QuestionarioLigar(destino, n, entidades)
            ctx.questionario = q
            return ok(texto(f"Ligar Classes no sistema {n} (altera diretamente o {n}; para cópia antes, use sgs "
                            f"duplicar {n}): escolha a classe de origem, a classe alvo e o nome do campo.", "destaque"),
                      *perguntas.blocos(q))
        return _como_ligar(n, entidades)
    m = re.fullmatch(r"(\w+)\.(\w+)", args[1])
    if not m:
        return falha(f"escreva a classe e o campo com um ponto: sgs ligar {n} Classe.campo Alvo",
                     *_como_ligar(n, entidades)["blocos"])
    origem, campo = m.group(1), m.group(2)
    alvo = args[2] if len(args) > 2 else gs.camel(campo)    # sem o Alvo: o nome do campo diz (destino → Destino)
    existentes = ", ".join(sorted(entidades)) or "nenhuma"
    if gs.achar_classe(entidades, origem) is None:
        return falha(f"a classe {gs.camel(origem)} não existe no sistema {n} (ele tem: {existentes}) — a classe que "
                     "GANHA o campo vem antes do ponto", *_como_ligar(n, entidades)["blocos"])
    if gs.achar_classe(entidades, alvo) is None:
        nova = gs.camel(alvo)
        pedido = gs.plural(gs.camel_para_snake(nova)).replace("_", " ")
        atalho = f"sgs app {n} {pedido} ligar={gs.achar_classe(entidades, origem)}.{campo}"
        return falha(f"a classe {nova} ainda não existe no sistema {n} (ele tem: {existentes}). O ligar conecta duas "
                     "classes que JÁ existem — crie a nova e ligue numa linha só (no próprio sistema):",
                     bloco("codigo", texto=atalho),
                     texto(f"(altera diretamente o sistema {n}; se quiser preservar antes, use sgs duplicar {n})", "suave"),
                     texto("Ou em dois passos:", "suave"),
                     bloco("codigo", texto=f"sgs app {n} {pedido}\nsgs ligar {n} {gs.achar_classe(entidades, origem)}."
                                           f"{campo} {nova}"),
                     bloco("botoes", itens=[cmd(f"escrever: {atalho}", atalho + " ", True)]))
    return _aplicar_ligacao(ctx, destino, n, origem, campo, alvo, c["testar"])


SGS = {"ajuda": sgs_ajuda, "help": sgs_ajuda, "gerar": sgs_gerar, "listar": sgs_listar, "lista": sgs_listar,
       "info": sgs_info, "testar": sgs_testar, "rodar": sgs_rodar, "parar": sgs_parar, "servidores": sgs_servidores,
       "comandos": sgs_comandos, "comand": sgs_comand_cmd, "padroes": sgs_padroes, "padrões": sgs_padroes,
       "dominios": sgs_dominios, "domínios": sgs_dominios, "dominio": sgs_dominios, "domínio": sgs_dominios,
       "infra": sgs_infra, "seguranca": sgs_infra, "segurança": sgs_infra, "stack": sgs_infra,
       "config": sgs_config, "pwa": sgs_pwa, "wiki": sgs_wiki,
       "clear": sgs_limpar, "cls": sgs_limpar, "limpar": sgs_limpar, "exit": sgs_exit, "sair": sgs_exit,
       "cancelar": sgs_cancelar, "estilo": sgs_estilo, "tema": sgs_tema, "temas": sgs_tema, "tipos": sgs_tipos,
       "tipo": sgs_tipos, "editar": sgs_editar, "duplicar": sgs_duplicar, "copiar": sgs_duplicar,
       "versao": sgs_duplicar, "versão": sgs_duplicar, "app": sgs_app, "modulo": sgs_app, "módulo": sgs_app,
       "ligar": sgs_ligar, "incrementar": sgs_incrementar, "modificar": sgs_incrementar, "api": sgs_api,
       "tutorial": sgs_tutorial_cmd, "hub": sgs_hub, "cmd": sgs_cmd, "visual": sgs_cmd, "cor": sgs_cmd,
       "wysiwyg": sgs_wysiwyg_cmd, "blocos": sgs_wysiwyg_cmd, "kanban": sgs_wysiwyg_cmd,
       "topo": sgs_topo, "foot": sgs_foot, "rodape": sgs_foot, "rodapé": sgs_foot, "provap3": sgs_provap3}


def executar_linha(linha, ctx, opcoes=None):
    """Roteia UMA linha digitada: sgs <comando> · comando de terminal · ou texto solto (só anotado).

    Toda linha vai para o histórico global (.sgs_historico) — menos as RESPOSTAS de pergunta (como o `read`
    do bash, que não entra no ~/.bash_history)."""
    linha = (linha or "").strip()
    q = ctx.questionario
    primeira = linha.split(None, 1)[0].lower() if linha else ""
    confirmacao, ctx.confirmacao = ctx.confirmacao, None
    resposta = None
    if confirmacao is not None:                        # pergunta s/N pendente (ex.: forçar a porta)
        escolha = linha.lower()
        if escolha in SIM:
            resposta = confirmacao["acao"]()
        elif escolha in NAO or not escolha:
            resposta = ok(texto("ok — nada foi encerrado nem reiniciado", "suave"))
    if resposta is None and q is not None and primeira not in ("sgs", "clear", "cls", "exit", "history"):
        erro = q.responder(linha)                      # é a RESPOSTA da pergunta (Enter vazio = padrão)
        resposta = ok(*perguntas.blocos(q, erro))
    gravado = None
    if resposta is None:
        if linha:
            gravado = ctx.historico.acrescentar(linha)
        resposta = _executar(linha, ctx, opcoes or {}) if linha else ok()
        if confirmacao is not None:
            resposta.setdefault("blocos", []).insert(0, texto("(a pergunta anterior ficou sem resposta: nada foi "
                                                              "encerrado)", "suave"))
        if q is not None and ctx.questionario is q and not resposta.get("limpar"):
            resposta.setdefault("blocos", []).append(
                texto(f"(pergunta pendente — {q.rotulo()}: responda, ou {q.comando} -sp para gerar, ou sgs cancelar)",
                      "aviso"))
    resposta.setdefault("ok", True)
    resposta["prompt"] = ctx.sessao.prompt()
    if ctx.confirmacao is not None:
        resposta["pergunta"], resposta["dica"] = ctx.confirmacao["rotulo"], ctx.confirmacao["dica"]
    else:
        resposta["pergunta"] = ctx.questionario.rotulo() if ctx.questionario else None
        if ctx.questionario is not None:
            resposta["dica"] = f"sua resposta (Enter = padrão) · {ctx.questionario.comando} -sp aplica agora"
    resposta["gravado"] = gravado                      # o que entrou no histórico (a página acrescenta na lista dela)
    if ctx.historico.mudou:                            # history -c / -d: a página troca a lista dela
        resposta["historico"] = ctx.historico.linhas()
        resposta["gravado"] = None
        ctx.historico.mudou = False
    return resposta


def _executar(linha, ctx, opcoes):
    try:
        partes = shlex.split(linha)
    except ValueError:
        partes = linha.split()
    primeira = partes[0].lower() if partes else ""
    if primeira in ("clear", "cls"):
        return sgs_limpar(ctx, [])
    if primeira == "exit":
        return sgs_exit(ctx, [])
    if primeira == "cmd":                                 # o estilo da tela, sem o sgs: cmd · cmd sgs
        return sgs_cmd(ctx, partes[1:])
    if primeira == "sgs":
        if len(partes) == 1:
            return sgs_ajuda(ctx, [])
        nome = partes[1].lower()
        chave = nome.split("=", 1)[0]                     # sgs pwa=false
        funcao = SGS.get(chave)
        if funcao is not None:
            try:
                return funcao(ctx, ([nome] if chave == "pwa" else []) + partes[2:], opcoes)
            except ValueError as erro:
                return falha(str(erro))
        blocos = terminal.executar(linha.split(None, 1)[1], ctx)   # sgs cd web, sgs ls, sgs python manage.py…
        if blocos is not None:
            return ok(*blocos)
        return falha(f"comando desconhecido: sgs {nome}", texto("a lista completa, explicada: sgs comand", "suave"))
    blocos = terminal.executar(linha, ctx)
    if blocos is not None:
        return ok(*blocos)
    # Texto solto: só ANOTA na tela. Gerar é sempre explícito (sgs gerar), para não gerar sistema por engano.
    return ok(bloco("acao", prefixo="↳ anotado (nada foi gerado) · para gerar: ",
                    rotulo=f"sgs gerar {linha[:60]}{'…' if len(linha) > 60 else ''}",
                    cmd=f"sgs gerar {linha}", preencher=True), nota=True)


def executar_sgs(linha, ctx, opcoes=None):
    """Compatibilidade: o mesmo roteador (usado pelos testes antigos e pela rota /comando)."""
    return executar_linha(linha, ctx, opcoes)


# =============================================================================
# 7. SERVIDOR HTTP (só costura: lê a requisição, chama a regra, devolve JSON/HTML)
# =============================================================================
MANIFEST = json.dumps({
    "name": "SGS", "short_name": "SGS", "description": NOME_SGS, "start_url": "/", "scope": "/", "display": "standalone",
    "background_color": "#0c0c0c", "theme_color": "#0c0c0c",
    "icons": [{"src": "/icone-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/icone-512.png", "sizes": "512x512", "type": "image/png"}],
}, ensure_ascii=False)
SERVICE_WORKER = """
// Service worker do SGS: a página principal funciona como app (PWA); os comandos sempre vão ao servidor.
const CACHE = "sgs-v13";
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/"]))); self.skipWaiting(); });
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.pathname !== "/") return;
  e.respondWith(fetch(e.request).then((r) => { const c = r.clone(); caches.open(CACHE).then((k) => k.put("/", c)); return r; })
                                .catch(() => caches.match("/")));
});
"""


# -----------------------------------------------------------------------------
# ATENDER UM PEDIDO — o MESMO caminho para os dois servidores da tela:
#   * python Gerador_Sistemas/tela_prompt.py        → http.server (classe Tela, abaixo)
#   * python Gerador_Sistemas/manage.py runserver   → Django (sgs_web/views.py)
# Recebe o método, o caminho (com a query), os cabeçalhos (qualquer objeto com .get) e uma função que lê N bytes
# do corpo; devolve Resposta(status, cabecalhos, corpo). Nada aqui sabe qual servidor está rodando.
# -----------------------------------------------------------------------------
def _resposta(status, corpo, tipo, extras=None, aceita=""):
    dados = corpo.encode("utf-8") if isinstance(corpo, str) else corpo
    # Texto grande vai COMPRIMIDO (gzip) quando o navegador aceita: pelo repasse localhost do WSL2
    # (Windows → Linux), respostas de ~200 KB (o CSS da Wiki, o Study Hub) travavam no fim e a página não
    # terminava de carregar; comprimidas (~25–50 KB) passam inteiras.
    comprimir = len(dados) > COMPRIMIR_ACIMA and "gzip" in aceita and tipo.startswith(TIPOS_COMPRIMIVEIS)
    if comprimir:
        dados = gzip.compress(dados, 6)
    cabecalhos = [("Content-Type", tipo), ("Content-Length", str(len(dados))), ("Cache-Control", "no-store")]
    if comprimir:
        cabecalhos += [("Content-Encoding", "gzip"), ("Vary", "Accept-Encoding")]
    cabecalhos += list((extras or {}).items())
    return SimpleNamespace(status=status, cabecalhos=cabecalhos, corpo=dados)


def atender(ctx, metodo, alvo, cabecalhos, ler_corpo):
    """Um pedido HTTP à tela → Resposta. Só atende quem chama por 127.0.0.1/localhost (bloqueia outro site
    tentando usar a tela) e só aceita POST em JSON (um formulário de OUTRO site não dispara ações aqui)."""
    aceita = cabecalhos.get("Accept-Encoding") or ""

    def responder(status, corpo, tipo, extras=None):
        return _resposta(status, corpo, tipo, extras, aceita)

    def responder_json(status, dados):
        return responder(status, json.dumps(dados, ensure_ascii=False), "application/json; charset=utf-8")

    if (cabecalhos.get("Host") or "").rsplit(":", 1)[0] not in HOSTS_PERMITIDOS:
        return responder_json(403, {"ok": False, "erro": "Acesse por http://127.0.0.1"})
    url = urlparse(alvo)
    if metodo == "GET":
        return _atender_get(ctx, url, responder, responder_json)
    if metodo == "POST":
        return _atender_post(ctx, url.path, cabecalhos, ler_corpo, responder_json)
    return responder_json(405, {"ok": False, "erro": "Método não permitido."})


def _atender_get(ctx, url, responder, responder_json):
    rotas = {
        "/": lambda: responder(200, sgs_wysiwyg.pagina(), "text/html; charset=utf-8"),
        "/cmd": lambda: responder(200, PAGINA, "text/html; charset=utf-8"),
        "/config": lambda: responder_json(200, {"ok": True, "config": ctx.config.publica(),
                                                "prompt": ctx.sessao.prompt(),
                                                "historico": ctx.historico.linhas()}),   # ↑/↓ depois do F5
        "/catalogo": lambda: responder_json(200, catalogo()),
        "/sugestoes": lambda: responder_json(200, {"ok": True, "itens": sugestoes(ctx)}),   # intellisense
        "/manifest.webmanifest": lambda: responder(200, MANIFEST, "application/manifest+json"),
        "/sw.js": lambda: responder(200, SERVICE_WORKER, "application/javascript", {"Service-Worker-Allowed": "/"}),
        "/icone-192.png": lambda: responder(200, gs.icone_png(192), "image/png"),
        "/icone-512.png": lambda: responder(200, gs.icone_png(512), "image/png"),
        "/tutorial": lambda: responder(200, sgs_tutorial.pagina(), "text/html; charset=utf-8"),
        "/wysiwyg": lambda: responder(200, sgs_wysiwyg.pagina(), "text/html; charset=utf-8"),
        "/wysiwyg/estado": lambda: responder_json(200, sgs_wysiwyg.estado_completo(ctx)),
    }
    if url.path in rotas:
        return rotas[url.path]()
    if url.path == "/wysiwyg/tema":
        q = parse_qs(url.query)
        r = sgs_wysiwyg.resolver_tema_wysiwyg(
            q.get("tema", ["T09"])[0], q.get("tom", ["escuro"])[0], q.get("paleta", ["P01"])[0]
        )
        return responder_json(200, r)
    if url.path == "/wysiwyg/projeto":
        q = parse_qs(url.query)
        r = sgs_wysiwyg.detalhe_projeto(ctx, q.get("numero", [""])[0])
        return responder_json(200 if r["ok"] else 404, r)
    if url.path == "/arquivo":
        q = parse_qs(url.query)
        r = ler_arquivo(q.get("pasta", [""])[0], q.get("caminho", [""])[0], ctx.saida)
        return responder_json(200 if r["ok"] else 404, r)
    if url.path in PAGINAS_REFERENCIA:              # a cópia é servida da pasta dela (os caminhos relativos valem)
        return responder(302, b"", "text/plain; charset=utf-8",
                         {"Location": "/referencias/" + PAGINAS_REFERENCIA[url.path]})
    if url.path.startswith("/referencias/"):
        return _servir_referencia(url.path[len("/referencias/"):], responder, responder_json)
    return responder_json(404, {"ok": False, "erro": "Página não encontrada."})


def _servir_referencia(relativo, responder, responder_json):
    """Um arquivo da pasta referencias/ (página, estilo, script, dado ou imagem) — nada fora dela. As páginas
    ganham a barra Tutorial | Wiki | Django Study Hub | SGS no topo (só na resposta; o arquivo não muda)."""
    alvo = (PASTA_REFERENCIAS / unquote(relativo)).resolve()
    tipo = TIPOS_ESTATICOS.get(alvo.suffix.lower())
    if tipo is None or not alvo.is_relative_to(PASTA_REFERENCIAS.resolve()) or not alvo.is_file():
        return responder_json(404, {"ok": False, "erro": "Arquivo de referência não encontrado."})
    dados = alvo.read_bytes()
    if alvo.suffix.lower() == ".html":
        atual = "/hub" if "study_hub" in alvo.name else "/referencia"
        dados = sgs_tutorial.com_barra(dados.decode("utf-8", "replace"), atual)
    return responder(200, dados, tipo)


def _atender_post(ctx, caminho, cabecalhos, ler_corpo, responder_json):
    if caminho not in ("/gerar", "/comando", "/config"):
        return responder_json(404, {"ok": False, "erro": "Página não encontrada."})
    # Exigir JSON impede que um formulário de OUTRO site dispare ações aqui.
    if not (cabecalhos.get("Content-Type") or "").startswith("application/json"):
        return responder_json(415, {"ok": False, "erro": "Envie JSON."})
    try:
        tamanho = int(cabecalhos.get("Content-Length") or 0)
    except ValueError:
        tamanho = -1
    if not 0 <= tamanho <= LIMITE_CORPO:
        return responder_json(413, {"ok": False, "erro": "Pedido grande demais."})
    try:
        pedido = json.loads(ler_corpo(tamanho) or b"{}")
        if not isinstance(pedido, dict):
            raise ValueError
    except ValueError:
        return responder_json(400, {"ok": False, "erro": "JSON inválido."})
    try:
        if caminho == "/config":
            return responder_json(200, salvar_config(ctx, pedido))
        if caminho == "/comando":
            opcoes = pedido.get("opcoes") if isinstance(pedido.get("opcoes"), dict) else {}
            with TRAVA:
                return responder_json(200, executar_linha(str(pedido.get("linha", "")), ctx, opcoes))
        c = ctx.config.valores                       # /gerar: API direta (a página usa "sgs gerar" pelo /comando)
        with TRAVA:
            r = processar(pedido.get("texto"), pedido.get("django", c["django"]),
                          pedido.get("exercicio", c["exercicio"]), pedido.get("testar", c["testar"]),
                          ctx.saida, pedido.get("estudo", c["estudo"]), pedido.get("comentarios", c["comentarios"]),
                          porta_base=c["porta_base"])
        return responder_json(200, r)
    except Exception as erro:  # erro inesperado: mostra na tela em vez de derrubar o servidor
        return responder_json(500, {"ok": False, "erro": f"Erro interno: {erro!r}", "prompt": ctx.sessao.prompt()})


def salvar_config(ctx, pedido):
    """POST /config: as caixas e o sgs config da página (tudo ou nada: um valor ruim não grava os outros)."""
    config = ctx.config
    try:
        for chave, valor in pedido.items():
            config.alterar(chave, valor)
    except ValueError as erro:
        return {"ok": False, "erro": str(erro), "config": config.publica()}
    config.salvar()
    return {"ok": True, "config": config.publica()}


class Tela(BaseHTTPRequestHandler):
    """O servidor da biblioteca padrão (python tela_prompt.py): só repassa o pedido para atender()."""
    server_version = "SGS/3.0"

    def _atender(self, metodo):
        r = atender(self.server.ctx, metodo, self.path, self.headers, self.rfile.read)
        self.send_response(r.status)
        for chave, valor in r.cabecalhos:
            self.send_header(chave, valor)
        self.end_headers()
        self.wfile.write(r.corpo)

    def do_GET(self):  # noqa: N802 (nome exigido pelo http.server)
        self._atender("GET")

    def do_POST(self):  # noqa: N802
        self._atender("POST")

    def log_message(self, formato, *args):
        # Uma linha curta por pedido no terminal (o padrão do http.server é bem poluído).
        if self.path.startswith(("/comando", "/gerar")):
            print(f"  {self.command} {self.path.split('?')[0]}  {args[1] if len(args) > 1 else ''}")


def criar_servidor(porta=PORTA_PADRAO, saida=None, config=None, raiz=RAIZ_PROJETO, abrir_janelas=False):
    """Servidor SÓ no 127.0.0.1 (ninguém de fora da sua máquina acessa). porta=0 → qualquer livre."""
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Tela)
    servidor.daemon_threads = True
    servidor.ctx = Contexto(saida, config, raiz, servidor.server_address[1], abrir_janelas)
    # atalhos (compatibilidade com quem usava servidor.saida/config/servidores)
    servidor.saida, servidor.config, servidor.servidores = servidor.ctx.saida, servidor.ctx.config, servidor.ctx.servidores
    return servidor


MARCA_TELA = "SGS_TELA_ABERTA"      # no ambiente da tela que está servindo (e dos comandos que ela roda)


def marcar_tela_aberta(porta):
    """Os comandos que a tela roda herdam a marca: um `python manage.py runserver` digitado DENTRO da tela, na
    pasta Gerador_Sistemas, não abre um segundo SGS (que encerraria os sites deste e trocaria o config)."""
    os.environ[MARCA_TELA] = str(porta)


AO_ABRIR = (("visual", "cmd"),      # sempre no estilo do Prompt de Comando (sgs cmd),
            ("pwa", True),          # em janela de app (PWA),
            ("topo", True),         # comandos principais no topo à mostra (sgs topo oculta)
            ("rodape", True))       # caixas de seleção no rodapé à mostra (sgs foot oculta)


def preparar_inicio(ctx):
    """O que a tela faz ao abrir — igual no tela_prompt.py e no python manage.py runserver: todas as caixas
    marcadas (desmarque na tela), o estilo de AO_ABRIR e os sites de uma tela anterior que caiu sem limpar
    encerrados. Devolve as linhas para o terminal."""
    for caixa in OPCOES_CAIXA:
        ctx.config.alterar(caixa, True)
    for chave, valor in AO_ABRIR:
        ctx.config.alterar(chave, valor)
    ctx.config.salvar()
    return [f"  porta {porta} liberada (site {chave} que ficou no ar de uma sessão anterior)"
            for chave, porta in ctx.servidores.encerrar_orfaos()]


def principal(argv=None):
    p = argparse.ArgumentParser(description=f"{NOME_SGS} — a tela estilo terminal (sem IA).")
    p.add_argument("--porta", type=int, default=PORTA_PADRAO, help=f"porta do SGS (padrão {PORTA_PADRAO} = o 00)")
    p.add_argument("--sem-abrir", action="store_true", help="não abre o navegador (só sobe o servidor)")
    a = p.parse_args(argv)
    try:
        servidor = criar_servidor(a.porta, abrir_janelas=not a.sem_abrir)
    except OSError as erro:
        print(f"ERRO: a porta {a.porta} não está livre ({erro.strerror}). Já tem um SGS aberto? "
              f"Outra porta: --porta {a.porta + 50}", file=sys.stderr)
        return 2
    ctx = servidor.ctx
    marcar_tela_aberta(servidor.server_address[1])
    for linha in preparar_inicio(ctx):
        print(linha)
    atexit.register(ctx.servidores.parar_todos)   # sites que a tela subiu caem junto com ela

    def ao_receber_sinal(_numero, _quadro):
        # Terminal fechado (SIGHUP) ou kill (SIGTERM): sai pelo mesmo caminho do Ctrl+C, que derruba os sites
        # e libera as portas (sem isto, o Python sairia direto e os sites ficariam no ar segurando as portas).
        raise KeyboardInterrupt

    for sinal in (signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if sinal is not None:
            signal.signal(sinal, ao_receber_sinal)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    print(f"{NOME_SGS} no ar: {url}   (Ctrl+C para parar)")
    print(f"Sistemas gerados em: {ctx.saida}")
    print(f"Configuração (sgs config): {ctx.config.caminho}")
    if not a.sem_abrir:
        threading.Timer(0.8, lambda: print("  " + (abrir_no_navegador(url, ctx.config.valores["pwa"])
                                                  or f"abra no navegador: {url}"))).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando (derrubando os sites que a tela subiu)…")
    finally:
        ctx.servidores.parar_todos()
        servidor.server_close()
    return 0


# =============================================================================
# 8. A PÁGINA (HTML + CSS + JS num texto só; nada é baixado da internet)
#    Texto que vem do servidor entra com textContent (nunca innerHTML).
# =============================================================================
PAGINA = r"""<!doctype html>
<html lang="pt-br" data-visual="cmd" data-topo="1" data-rodape="1">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0c0c0c">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icone-192.png">
<title>SGS</title>
<style>
  :root {
    --fundo: #0c0c0c; --painel: #151515; --texto: #cccccc; --forte: #f2f2f2; --suave: #7c7c7c;
    --verde: #16c60c; --ciano: #61d6d6; --amarelo: #e5c07b; --vermelho: #f14c4c; --azul: #6ea8fe;
    --borda: #2c2c2c; --selecao: #264f78;
    --prompt: var(--verde); --prompt-dir: var(--azul); --prompt-peso: 700; --cursor: var(--verde);
    --topo: var(--ciano); --marca: var(--verde); --rotulo: var(--suave); --sug-ativa: #1f2a1f; --sug-letra: var(--verde);
    --mono: "Cascadia Mono", "Cascadia Code", Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace;
  }
  /* estilo "cmd" (o padrão ao abrir · sgs cmd): o Prompt de Comando do Windows — fundo #0c0c0c e TUDO em cinza
     #cccccc (prompt "~\pasta>" numa linha só, comandos do topo, caixas e botão); cor só no que o comando responde */
  :root[data-visual="cmd"] {
    --painel: #0c0c0c; --borda: #242424; --forte: #cccccc; --suave: #767676; --amarelo: #f9f1a5;
    --vermelho: #e74856; --azul: #3a96dd; --selecao: #3a3a3a;
    --prompt: #cccccc; --prompt-dir: #cccccc; --prompt-peso: normal; --cursor: #cccccc;
    --topo: #cccccc; --marca: #cccccc; --rotulo: #cccccc; --sug-ativa: #262626; --sug-letra: #ffffff;
  }
  :root[data-visual="cmd"] #caixa.focado { border-color: var(--borda); }
  :root[data-visual="cmd"] .linha-prompt { display: flex; flex-wrap: wrap; align-items: flex-start; }
  :root[data-visual="cmd"] .linha-comando { flex: 1 1 240px; gap: 0; }
  .eco-cmd.em-linha .ps1 { display: inline; }   /* o eco guarda o formato de quando foi digitado */
  * { box-sizing: border-box; }
  html, body { margin: 0; background: var(--fundo); color: var(--texto); font: 14px/1.55 var(--mono); }
  ::selection { background: var(--selecao); color: #fff; }
  main { padding: 10px 14px 190px; }
  /* barra superior fixa na esquerda com o alternador WYSIWYG | CMD na mesma posição do modo WYSIWYG */
  .barra-modo { position: sticky; top: 0; z-index: 10; display: flex; align-items: flex-start; gap: 12px;
                padding: 5px 14px; min-height: 34px; background: var(--painel);
                border-bottom: 1px solid var(--borda); }
  .modo-stack { display: flex; flex-direction: column; gap: 4px; flex: none; }
  .switch-modo { display: inline-flex; flex: none; background: var(--fundo); border: 1px solid var(--borda);
                 border-radius: 5px; padding: 2px; gap: 2px; font-family: var(--mono); }
  .switch-modo span, .switch-modo a { padding: 2px 9px; border-radius: 3px; text-decoration: none;
                                      font-size: 11px; line-height: 1.45; font-weight: 700; }
  .switch-modo .on { background: #1c1c1c; color: var(--forte); border: 1px solid #3e3e3e; }
  .switch-modo a { color: var(--suave); border: 1px solid transparent; }
  .switch-modo a:hover { background: #181818; color: #ffffff; }
  .btn-tutorial-cmd {
    width: 100%; background: #161616; color: var(--forte); border: 1px solid #3e3e3e;
    border-radius: 4px; padding: 2px 8px; font: 700 11px/1.45 var(--mono); cursor: pointer;
    text-align: center;
  }
  .btn-tutorial-cmd:hover { border-color: var(--azul); color: #ffffff; background: #1c2430; }
  /* os comandos principais (sem o "sgs" na frente): fonte menor, separados por "|", até o fim da tela */
  .principais { margin: 2px 0 0; flex: 1; font-size: 12px; line-height: 1.5; color: var(--suave); overflow-wrap: anywhere; }
  .principais .cmd { color: var(--topo); text-decoration: none; white-space: nowrap; }   /* "api config" não parte */
  .principais .cmd:hover { color: #ffffff; text-decoration: underline; }
  :root[data-topo="0"] #principais { display: none; }      /* sgs topo oculta/mostra (abre à mostra) */
  :root[data-rodape="0"] .opcoes { display: none; }        /* sgs foot oculta/mostra as caixas; o prompt fica */
  .eco-cmd { margin-top: 14px; color: var(--forte); white-space: pre-wrap; overflow-wrap: anywhere; }
  .eco-cmd .ps1 { display: block; }
  .seta { color: var(--prompt); font-weight: var(--prompt-peso); white-space: nowrap; }
  .botoes { display: flex; flex-wrap: wrap; gap: 4px 18px; margin: 4px 0 8px; }
  .ps1 { color: var(--prompt); font-weight: var(--prompt-peso); }
  .ps1 .dir { color: var(--prompt-dir); }
  .ps1 .venv { color: var(--suave); font-weight: normal; }
  .resp p { margin: 2px 0; overflow-wrap: anywhere; }
  .ok { color: var(--verde); } .erro { color: var(--vermelho); } .aviso { color: var(--amarelo); }
  .suave { color: var(--suave); } .destaque { color: var(--ciano); }
  .titulo { color: var(--amarelo); margin: 10px 0 2px !important; font-weight: 700; }
  table { border-collapse: collapse; margin: 4px 0 8px; display: block; overflow-x: auto; max-width: 100%; }
  th { color: var(--ciano); text-align: left; font-weight: normal; border-bottom: 1px dashed var(--borda); }
  th, td { padding: 1px 18px 1px 0; vertical-align: top; }
  pre.codigo, pre.visor { background: var(--painel); border-left: 3px solid var(--verde); padding: 8px 12px;
                          margin: 6px 0; overflow: auto; white-space: pre; font: inherit; }
  pre.visor { max-height: 460px; border-left-color: var(--azul); }
  pre.saida { margin: 2px 0; white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; color: var(--texto); }
  pre.saida.erro { color: var(--vermelho); } pre.saida.aviso { color: var(--amarelo); }
  a { color: var(--azul); }
  .cmd { color: var(--ciano); cursor: pointer; text-decoration: underline dotted; }
  .cmd:hover { color: var(--forte); }
  .arquivos { display: flex; flex-wrap: wrap; gap: 0 16px; margin: 2px 0 4px; }
  .arq { all: unset; cursor: pointer; }
  .arq:hover, .arq.ativo { color: var(--verde); text-decoration: underline; }
  details summary { cursor: pointer; color: var(--suave); }
  .espera::after { content: "▌"; color: var(--verde); animation: sumir 1s steps(1) infinite; }
  @keyframes sumir { 50% { opacity: 0; } }
  /* ---- caixa do prompt (fixa embaixo) ---- */
  #prompt { position: fixed; left: 0; right: 0; bottom: 0; padding: 18px 16px 14px;
            background: linear-gradient(to bottom, transparent, var(--fundo) 18px); }
  #caixa { position: relative; margin: 0; background: var(--painel); border: 1px solid var(--borda);
           border-radius: 6px; padding: 8px 10px 7px; }
  /* ---- INTELLISENSE: até 5 sugestões acima do prompt (clique escolhe) e a sugestão "fantasma" na linha (TAB) ---- */
  #sugestoes { position: absolute; left: 12px; right: 12px; bottom: calc(100% + 4px); z-index: 5; background: var(--painel);
               border: 1px solid #3d3d3d; border-radius: 6px; padding: 4px 0; box-shadow: 0 -6px 18px rgba(0, 0, 0, .55); }
  .sug { display: flex; gap: 14px; align-items: baseline; padding: 2px 12px; cursor: pointer; }
  .sug.ativa { background: var(--sug-ativa); }
  .sug:hover { background: var(--selecao); }
  .sug-cmd { color: var(--texto); white-space: pre; }
  .sug-cmd b { color: var(--sug-letra); font-weight: 700; }
  .sug-desc { margin-left: auto; color: var(--suave); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
              font-size: 12.5px; }
  .sug-tab { color: var(--suave); font-size: 11.5px; border: 1px solid var(--borda); border-radius: 3px; padding: 0 4px; }
  #fantasma { color: #5f6b5f; }
  #caixa.focado { border-color: #3d3d3d; }
  /* PS1 em DUAS linhas: em cima "sgs@ilp037:~/caminho" (quebra se for comprido); embaixo "$>" e o comando */
  .linha-prompt { cursor: text; }
  .ps1-linha { overflow-wrap: anywhere; word-break: break-all; }
  .linha-comando { display: flex; gap: 8px; align-items: flex-start; }
  #modo { color: var(--amarelo); }
  .entrada { position: relative; flex: 1; min-width: 0; }
  #eco { margin: 0; min-height: 1.55em; white-space: pre-wrap; word-break: break-all; color: var(--forte); font: inherit; }
  /* o textarea de verdade fica INVISÍVEL por cima do eco: recebe o teclado, o eco desenha o cursor de bloco */
  #texto { position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; padding: 0; border: 0; outline: none;
           resize: none; overflow: hidden; background: transparent; color: transparent; caret-color: transparent;
           font: inherit; white-space: pre-wrap; word-break: break-all; }
  #caixa.focado #cursor { background: var(--cursor); color: var(--fundo); animation: piscar 1.05s steps(1) infinite; }
  #caixa:not(.focado) #cursor { outline: 1px solid var(--cursor); outline-offset: -1px; }
  @keyframes piscar { 50% { background: transparent; color: var(--forte); } }
  #dica { color: var(--suave); }
  /* rodapé: as caixas numa linha só (se faltar largura, rola de lado); no estilo cmd, só preto e cinza */
  .opcoes { display: flex; flex-wrap: nowrap; gap: 10px; align-items: center; margin-top: 6px; color: var(--rotulo);
            font-size: 11.5px; white-space: nowrap; overflow-x: auto; scrollbar-width: none; }
  .opcoes label { display: inline-flex; gap: 5px; align-items: center; cursor: pointer; flex: none; }
  .opcoes input { appearance: none; flex: none; width: 11px; height: 11px; margin: 0; cursor: pointer;
                  border: 1px solid var(--marca); border-radius: 1px; background: var(--fundo); }
  .opcoes input:checked { background: var(--marca); box-shadow: inset 0 0 0 2px var(--fundo); }
  .opcoes input:focus-visible { outline: 1px solid #ffffff; outline-offset: 1px; }
  /* ---- TOUR INTERATIVO DO MODO CMD ---- */
  .tour-layer[hidden] { display: none; }
  .tour-backdrop { position: fixed; inset: 0; z-index: 90; background: transparent; }
  .tour-ring {
    position: fixed; z-index: 91; pointer-events: none;
    border: 2px solid var(--azul); border-radius: 6px;
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, .65);
    transition: left .18s ease, top .18s ease, width .18s ease, height .18s ease;
  }
  .tour-card {
    position: fixed; z-index: 95; width: 410px; max-width: calc(100vw - 24px);
    background: #121212; border: 1px solid var(--azul); border-radius: 6px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, .65); overflow: hidden;
    font: 12.5px/1.45 "Segoe UI", system-ui, sans-serif; color: var(--texto);
  }
  .tour-head {
    padding: 9px 12px; border-bottom: 1px solid var(--borda); background: #181818;
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
  }
  .tour-badge {
    font: 700 10.5px var(--mono); color: var(--azul);
    border: 1px solid var(--azul); padding: 1px 6px; border-radius: 4px; flex-shrink: 0;
  }
  .tour-title { font-weight: 700; color: #f2f2f2; font-size: 12.5px; }
  .tour-body { padding: 10px 12px; display: flex; flex-direction: column; gap: 7px; }
  .tour-text { margin: 0; font-size: 12px; color: #d4d4d4; line-height: 1.48; }
  .tour-tip {
    font: 11px/1.45 var(--mono); color: #f2f2f2; background: #0a0a0a;
    border: 1px solid var(--borda); border-left: 3px solid var(--azul);
    padding: 6px 8px; border-radius: 4px; white-space: pre-wrap;
  }
  .tour-foot {
    padding: 8px 12px; border-top: 1px solid var(--borda); background: #181818;
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
  }
  .tour-dots { display: flex; align-items: center; gap: 4px; }
  .tour-dot {
    width: 7px; height: 7px; border-radius: 50%; border: 0; padding: 0;
    background: #444; cursor: pointer;
  }
  .tour-dot.on { background: var(--azul); width: 16px; border-radius: 4px; }
  .tour-nav { display: flex; align-items: center; gap: 6px; }
  .tour-btn {
    border: 1px solid #3e3e3e; background: #1c1c1c; color: #f2f2f2;
    padding: 3px 9px; border-radius: 4px; cursor: pointer; font: 600 11.5px var(--mono);
  }
  .tour-btn:hover:not(:disabled) { border-color: var(--azul); background: #1c2430; }
  .tour-btn:disabled { opacity: .4; cursor: not-allowed; }
  .tour-btn.prim { border-color: var(--azul); background: rgba(58, 150, 221, .2); }
  .tour-link { font-size: 11px; color: var(--suave); text-decoration: none; }
  .tour-link:hover { color: #ffffff; text-decoration: underline; }
</style>
</head>
<body>
<header class="barra-modo">
  <div class="modo-stack">
    <nav class="switch-modo" aria-label="Alternar WYSIWYG e CMD">
      <a href="/" title="Abrir bancada visual WYSIWYG (tela inicial)">WYSIWYG</a>
      <span class="on">CMD</span>
    </nav>
    <button class="btn-tutorial-cmd" id="btn-tutorial-cmd" type="button" title="Iniciar tour interativo do Modo CMD">Tutorial</button>
  </div>
  <p class="principais" id="principais"></p>
</header>
<main>
  <section id="saida"></section>
</main>
<div id="prompt">
  <div id="caixa">
    <div id="sugestoes" role="listbox" aria-label="sugestões (clique para escolher · TAB completa)" hidden></div>
    <div class="linha-prompt" id="linha">
      <div class="ps1-linha"><span id="modo"></span><span class="ps1" id="ps1"></span></div>
      <div class="linha-comando"><span class="seta" id="seta">&gt;</span>
      <div class="entrada">
        <pre id="eco"><span id="antes"></span><span id="cursor"> </span><span id="fantasma"></span><span id="depois"></span><span id="dica">sgs gerar &lt;pedido&gt; · cd · ls · python manage.py … · ou sgs para ajuda</span></pre>
        <textarea id="texto" rows="1" spellcheck="false" autocomplete="off" maxlength="600"
                  aria-label="Comando: sgs, terminal ou anotação"></textarea>
      </div>
      </div>
    </div>
    <div class="opcoes" title="as caixas valem para o sgs gerar (e ficam salvas)">
      <label><input type="checkbox" data-opcao="django"> + Django (site)</label>
      <label><input type="checkbox" data-opcao="exercicio"> Modo exercício</label>
      <label><input type="checkbox" data-opcao="testar"> Rodar testes</label>
      <label><input type="checkbox" data-opcao="estudo"> Para estudo</label>
      <label><input type="checkbox" data-opcao="comentarios"> Comentários no código</label>
      <label><input type="checkbox" data-opcao="comentarios_web"> Notas na web</label>
      <label><input type="checkbox" data-opcao="perguntar"> Perguntar antes de gerar</label>
    </div>
  </div>
</div>
<div class="tour-layer" id="tour-cmd-layer" hidden role="dialog" aria-modal="true" aria-label="Tutorial interativo do Modo CMD">
  <div class="tour-backdrop" id="tour-cmd-backdrop"></div>
  <div class="tour-ring" id="tour-cmd-ring"></div>
  <div class="tour-card" id="tour-cmd-card">
    <div class="tour-head">
      <span class="tour-badge" id="tour-cmd-badge">1 / 7</span>
      <span class="tour-title" id="tour-cmd-title"></span>
      <button class="tour-btn" id="tour-cmd-close" type="button" title="Fechar tutorial (Esc)">Fechar</button>
    </div>
    <div class="tour-body">
      <p class="tour-text" id="tour-cmd-text"></p>
      <div class="tour-tip" id="tour-cmd-tip"></div>
      <a class="tour-link" href="/tutorial" target="_blank" rel="noopener">Abrir guia completo em nova aba (/tutorial)</a>
    </div>
    <div class="tour-foot">
      <div class="tour-dots" id="tour-cmd-dots"></div>
      <div class="tour-nav">
        <button class="tour-btn" id="tour-cmd-prev" type="button">&lt; Voltar</button>
        <button class="tour-btn prim" id="tour-cmd-next" type="button">Avançar &gt;</button>
      </div>
    </div>
  </div>
</div>
<script>
const $ = (id) => document.getElementById(id);
const saida = $("saida"), ta = $("texto"), caixa = $("caixa");
// As 3 linhas de comandos principais: [comando, preencher?] — preencher = só escreve no prompt (falta o NN…).
// A 1ª linha começa pela cor da janela (CMD/PowerShell ou SGS).
// Os comandos principais do topo, mostrados SEM o "sgs" na frente (o clique manda o comando inteiro).
// [comando, preencher?] — preencher = só escreve no prompt (falta o NN…). O "sgs" sozinho aparece como "ajuda".
const PRINCIPAIS = [
  ["sgs", false], ["sgs gerar ", true], ["sgs listar", false], ["sgs comand", false],
  ["sgs rodar ", true],
  ["sgs estilo", false], ["sgs infra", false], ["sgs padroes", false], ["sgs config", false], ["clear", false],
  ["sgs info ", true], ["sgs testar ", true], ["sgs servidores", false], ["sgs parar ", true], ["sgs editar ", true],
  ["sgs duplicar ", true], ["sgs app ", true], ["sgs ligar ", true], ["sgs incrementar ", true], ["sgs api config ", true], ["history", false],
  ["sgs dominios", false], ["sgs tipos ", true], ["sgs tema", false], ["sgs comandos ", true], ["sgs cancelar", false],
  ["sgs tutorial", false], ["sgs wiki", false], ["sgs hub", false], ["sgs wysiwyg", false], ["sgs cmd ", true],
  ["sgs topo", false], ["sgs foot", false]
];
const historico = [];             // cópia do arquivo .sgs_historico (vem do servidor: sobrevive ao F5)
let posHist = 0;
let prompt = { cwd: "~", venv: "" };
let telaGuardada = null;          // a tela principal, guardada enquanto o módulo sgs comand está aberto
let pergunta = null;              // rótulo da pergunta em andamento (sgs gerar com "Perguntar" ligado, forçar porta…)
let dicaPergunta = null;          // dica da pergunta em andamento (quando o servidor manda uma)

// Cria um elemento com filhos. Texto vira nó de texto (seguro: nada é interpretado como HTML).
function el(tag, props = {}, ...filhos) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const f of filhos.flat()) {
    if (f === null || f === undefined || f === false) continue;
    n.append(f instanceof Node ? f : String(f));
  }
  return n;
}
function rolar() { window.scrollTo({ top: document.body.scrollHeight }); }

/* ---------- prompt (PS1) e cursor de bloco ---------- */
// Linha 1 do prompt: "(venv) sgs@ilp037:~/caminho" — a linha 2 é o "$>" com o comando (caminho longo não espreme nada).
// No estilo cmd (sgs cmd): como o Prompt de Comando, numa linha só — "(venv) ~\caminho>comando".
function modoCmd() { return document.documentElement.dataset.visual !== "sgs"; }
function seta() { return modoCmd() ? ">" : "$>"; }
function ps1(p) {
  const venv = p.venv ? el("span", { class: "venv" }, `(${p.venv}) `) : null;
  if (modoCmd()) return [venv, el("span", { class: "dir" }, p.cwd.replaceAll("/", "\\"))];
  return [venv, "sgs@ilp037:", el("span", { class: "dir" }, p.cwd)];
}
function desenharPrompt() {
  $("ps1").replaceChildren(...ps1(prompt).filter(Boolean));   // sem .venv ativo não há o "(.venv) "
  $("seta").textContent = seta();
  $("modo").textContent = pergunta ? `[${pergunta}] ` : (telaGuardada ? "[comand] " : "");
  $("dica").textContent = pergunta ? (dicaPergunta || "sua resposta (Enter = padrão) · sgs gerar -sp gera agora")
                                   : "sgs gerar <pedido> · cd · ls · python manage.py … · ou sgs para ajuda";
}
function trocarHistorico(linhas) {
  historico.splice(0, historico.length, ...linhas);
  posHist = historico.length;
}
/* ---------- INTELLISENSE: até 5 sugestões que se atualizam a cada tecla (clique escolhe) + a "fantasma" (TAB) ----
   O catálogo vem do servidor (/sugestoes): histórico, pastas do cd, comandos de cada sistema, sgs e os padrão
   (com e sem sgs). Ordem: começa com o que foi digitado → palavra que começa com ele → contém → letras na ordem. */
const MAX_SUG = 5;
let catalogoSug = [];             // [{cmd, desc, tipo}]
let sugAtuais = [];               // as mostradas agora
let sugSel = 0;                   // a MARCADA: ↑/↓ andam entre elas; TAB ou → (no fim da linha) escolhem
let sugFechadas = false;          // Esc fecha até a próxima tecla
let viaHistorico = false;         // ↑/↓ escreveu o comando: a caixa fica fechada
function carregarSugestoes() {
  fetch("/sugestoes").then((r) => r.json()).then((d) => { catalogoSug = d.itens || []; atualizarSugestoes(); })
    .catch(() => {});
}
function pontuar(cmd, t) {
  const c = cmd.toLowerCase();
  if (c === t) return null;                                   // já está escrito: não sugere de novo
  if (c.startsWith(t)) return 0;
  if (c.includes(" " + t) || c.includes("/" + t) || c.includes("." + t)) return 1;
  if (c.includes(t)) return 2;
  if (t.length < 2) return null;
  let i = 0;
  for (const letra of c) { if (letra === t[i]) i += 1; if (i === t.length) return 3; }
  return null;
}
function buscarSugestoes(texto) {
  const t = texto.toLowerCase();
  if (!t.trim() || t.includes("\n")) return [];
  const achados = [];
  catalogoSug.forEach((s, ordem) => {
    // sgs topo e sgs foot: SEMPRE as duas primeiras quando o digitado é o começo delas (s, sg, sgs, sgs …)
    const fixa = s.tipo === "fixo" && s.cmd.toLowerCase() !== t && s.cmd.toLowerCase().startsWith(t);
    const p = fixa ? -1 : pontuar(s.cmd, t);
    if (p !== null) achados.push([p, ordem, s]);
  });
  achados.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return achados.slice(0, MAX_SUG).map((a) => a[2]);
}
function cmdDestacado(cmd, t) {               // o trecho já digitado aparece em destaque dentro da sugestão
  const i = t ? cmd.toLowerCase().indexOf(t.toLowerCase()) : -1;
  return i < 0 ? [cmd] : [cmd.slice(0, i), el("b", {}, cmd.slice(i, i + t.length)), cmd.slice(i + t.length)];
}
function atualizarSugestoes() {             // recalcula (a cada tecla): a marcada volta a ser a 1ª
  const v = ta.value;
  sugAtuais = (pergunta || sugFechadas || viaHistorico || document.activeElement !== ta) ? [] : buscarSugestoes(v);
  sugSel = 0;
  desenharSugestoes();
}
function desenharSugestoes() {
  const v = ta.value;
  $("sugestoes").replaceChildren(...sugAtuais.map((s, i) => {
    const item = el("div", { class: "sug" + (i === sugSel ? " ativa" : ""), role: "option",
                             "aria-selected": i === sugSel ? "true" : "false", title: "clique para escolher" },
                    el("span", { class: "sug-cmd" }, ...cmdDestacado(s.cmd, v)), el("span", { class: "sug-desc" }, s.desc),
                    i === sugSel ? el("span", { class: "sug-tab" }, "TAB · →") : null);
    item.addEventListener("mousedown", (ev) => { ev.preventDefault(); escolherSugestao(s.cmd); });  // sem perder o foco
    return item;
  }));
  $("sugestoes").hidden = sugAtuais.length === 0;
  atualizarEco();
}
function caixaAberta() { return sugAtuais.length > 0 && !$("sugestoes").hidden; }
function fantasmaDe(s, v) {
  return s && s.cmd.toLowerCase().startsWith(v.toLowerCase()) ? s.cmd.slice(v.length) : "";
}
function escolherSugestao(cmd) {
  viaHistorico = sugFechadas = false;
  escrever(cmd);
  atualizarSugestoes();
}
function atualizarEco() {
  const v = ta.value, pos = Math.min(ta.selectionStart ?? v.length, v.length), ch = v[pos];
  const fim = ch === undefined || ch === "\n";
  // Fantasma: o resto da sugestão MARCADA, em outra cor, logo depois do que foi digitado (só com o cursor no fim).
  const resto = pos === v.length && document.activeElement === ta ? fantasmaDe(sugAtuais[sugSel], v) : "";
  $("antes").textContent = v.slice(0, pos);
  $("cursor").textContent = fim ? (resto ? resto[0] : " ") : ch;
  $("fantasma").textContent = resto.slice(1);
  $("depois").textContent = v.slice(fim ? pos : pos + 1);
  $("dica").hidden = v.length > 0;
}
ta.addEventListener("input", () => { viaHistorico = sugFechadas = false; atualizarSugestoes(); });
for (const ev of ["keyup", "click", "select"]) ta.addEventListener(ev, atualizarEco);
document.addEventListener("selectionchange", () => { if (document.activeElement === ta) atualizarEco(); });
ta.addEventListener("focus", () => { caixa.classList.add("focado"); atualizarSugestoes(); });
ta.addEventListener("blur", () => { caixa.classList.remove("focado"); $("sugestoes").hidden = true; atualizarEco(); });
$("linha").addEventListener("mousedown", (ev) => { if (ev.target !== ta) { ev.preventDefault(); ta.focus(); } });

function escrever(comando) {
  ta.value = comando;
  ta.focus();
  ta.setSelectionRange(comando.length, comando.length);
  atualizarEco();
}
/* ---------- Alt+Enter: maximiza a janela; de novo, volta ao tamanho de antes (como no Prompt de Comando) ----------
   Na janela de app (PWA) o SGS ocupa a área útil da tela com moveTo/resizeTo e guarda onde estava; numa aba comum
   (o navegador não deixa a página mexer na janela) vira tela cheia. */
let antesDeMaximizar = null;      // [x, y, largura, altura] da janela antes do Alt+Enter
function alternarMaximizar() {
  const s = window.screen;
  const area = [s.availLeft ?? 0, s.availTop ?? 0, s.availWidth, s.availHeight];
  const agora = [window.screenX, window.screenY, window.outerWidth, window.outerHeight];
  const maximizada = Math.abs(agora[2] - area[2]) <= 16 && Math.abs(agora[3] - area[3]) <= 16;
  let alvo;
  if (!maximizada) {
    antesDeMaximizar = agora;
    alvo = area;
  } else {
    alvo = antesDeMaximizar || [area[0] + area[2] * 0.1, area[1] + area[3] * 0.1, area[2] * 0.8, area[3] * 0.8];
    antesDeMaximizar = null;
  }
  window.moveTo(Math.round(alvo[0]), Math.round(alvo[1]));
  window.resizeTo(Math.round(alvo[2]), Math.round(alvo[3]));
  setTimeout(() => {                                          // nada mudou: aba comum → tela cheia (liga/desliga)
    if (window.outerWidth !== agora[2] || window.outerHeight !== agora[3]) return;
    antesDeMaximizar = null;
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    else document.documentElement.requestFullscreen?.().catch(() => {});
  }, 150);
}
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter" && ev.altKey) { ev.preventDefault(); ev.stopPropagation(); alternarMaximizar(); }
}, true);                                                     // antes do Enter do prompt (que executaria)

ta.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter" && ev.altKey) return;                // Alt+Enter: só a janela (acima)
  if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); executar(); return; }
  if (ev.key === "Tab" && !ev.shiftKey) {                    // TAB completa com a sugestão marcada
    if (sugAtuais.length) { ev.preventDefault(); escolherSugestao(sugAtuais[sugSel].cmd); return; }
    if (ta.value) ev.preventDefault();                       // sem sugestão: o foco não sai do prompt
  }
  const noFim = ta.selectionStart === ta.value.length && ta.selectionEnd === ta.value.length;
  if (ev.key === "ArrowRight" && caixaAberta() && noFim && !ev.shiftKey) {   // → no fim da linha = igual ao TAB
    ev.preventDefault();
    escolherSugestao(sugAtuais[sugSel].cmd);
    return;
  }
  if ((ev.key === "ArrowUp" || ev.key === "ArrowDown") && caixaAberta()) {   // caixa aberta: ↑/↓ andam nas opções
    ev.preventDefault();
    sugSel = (sugSel + (ev.key === "ArrowDown" ? 1 : -1) + sugAtuais.length) % sugAtuais.length;
    desenharSugestoes();
    return;
  }
  if (ev.key === "Escape" && sugAtuais.length) { ev.preventDefault(); sugFechadas = true; atualizarSugestoes(); return; }
  if ((ev.key === "ArrowUp" || ev.key === "ArrowDown") && !ta.value.includes("\n") && historico.length) {
    ev.preventDefault();
    posHist = Math.max(0, Math.min(historico.length, posHist + (ev.key === "ArrowUp" ? -1 : 1)));
    viaHistorico = true;                                     // comando do histórico: a caixa de sugestões fecha
    escrever(historico[posHist] ?? "");
    atualizarSugestoes();
  }
  if (ev.key.toLowerCase() === "l" && ev.ctrlKey) { ev.preventDefault(); limpar(); }
});

/* ---------- comandos clicáveis ---------- */
function comandoClicavel(rotulo, comando, preencher) {
  const s = el("span", { class: "cmd", title: preencher ? "clique para escrever no prompt" : "clique para executar" }, rotulo);
  s.addEventListener("click", () => (preencher ? escrever(comando) : executar(comando)));
  return s;
}
$("principais").append(...PRINCIPAIS.flatMap(([c, preencher], i) => {
  const item = comandoClicavel(c.trim() === "sgs" ? "ajuda" : c.trim().replace(/^sgs /, ""), c, preencher);
  item.title = `${c.trim()} — ${item.title}`;                       // o comando inteiro aparece ao passar o mouse
  return [i ? "|" : "", item];
}));

/* ---------- desenhar as respostas ---------- */
function celula(c) {
  if (c === null || c === undefined) return "";
  if (typeof c !== "object") return String(c);
  if (c.cmd) return comandoClicavel(c.texto, c.cmd, c.preencher);
  if (c.href) return el("a", { href: c.href, target: "_blank", rel: "noopener", class: c.cor || "" }, c.texto);
  return el("span", { class: c.cor || "" }, c.texto);
}
function desenharBloco(b) {
  if (b.t === "titulo") return el("p", { class: "titulo" }, b.texto);
  if (b.t === "texto") return el("p", { class: b.cor || "" }, b.texto);
  if (b.t === "saida") return el("pre", { class: "saida " + (b.cor || "") }, b.texto);
  if (b.t === "codigo") return el("pre", { class: "codigo" }, b.texto);
  if (b.t === "link") return el("p", {}, el("a", { href: b.href, target: "_blank", rel: "noopener" }, b.texto));
  if (b.t === "acao") return el("p", { class: "suave" }, b.prefixo || "", comandoClicavel(b.rotulo, b.cmd, b.preencher));
  if (b.t === "botoes") return el("div", { class: "botoes" }, b.itens.map(celula));     // comando ou link
  if (b.t === "tabela") {
    return el("table", {}, el("thead", {}, el("tr", {}, b.colunas.map((c) => el("th", {}, c)))),
      el("tbody", {}, b.linhas.map((linha) => el("tr", {}, linha.map((c) => el("td", {}, celula(c)))))));
  }
  return el("p", { class: "suave" }, JSON.stringify(b));
}

function montarSistema(d) {
  const partes = [];
  const modo = [d.estudo ? "estudo" : "só gerar", d.comentarios ? "comentado" : "apenas o código",
                d.django && "+ Django", d.exercicio && "exercício"].filter(Boolean).join(" · ");
  partes.push(el("p", { class: "ok" }, `✔ ${d.numero ? d.numero + " · " : ""}${d.sistema} · entidade ${d.entidade}`,
                  el("span", { class: "suave" }, `   (${modo})`)));
  if (d.por_assunto) {
    partes.push(el("p", {}, el("span", { class: "destaque" }, "domínio: "), d.dominio,
      el("span", { class: "suave" }, d.dominio_palavras.length ? `  ← ${d.dominio_palavras.join(", ")}`
                                                               : "  ← nenhuma palavra de domínio: genérico")));
  }
  const motivo = (p) => {
    if (p.palavras.length) return `  ← ${p.palavras.join(", ")}`;
    if (p.chave === "encapsulamento") return "  (sempre entra: é a base)";
    if (d.sem_padrao) return "  (nenhum padrão citado: os 9 da prova)";
    return "";
  };
  partes.push(el("p", {}, el("span", { class: "destaque" }, `padrões (${d.padroes.length}):`)));
  if (d.padroes.length <= 12) {
    for (const p of d.padroes) partes.push(el("p", {}, "  • ", p.titulo, el("span", { class: "suave" }, motivo(p))));
  } else {
    partes.push(el("p", {}, "  " + d.padroes.map((p) => p.titulo).join(" · ")));
    const motivos = [...new Set(d.padroes.flatMap((p) => p.palavras))];
    if (motivos.length) partes.push(el("p", { class: "suave" }, "  ← " + motivos.join(", ")));
  }
  if (d.web) {
    const w = d.web;
    const detalhes = [w.estilo === "web" ? `${w.estilo} · ${w.tema} · ${w.tom}` + (w.tema === "T10" ? ` · ${w.paleta}` : "") : w.estilo,
                      w.comentarios_web && "notas de apresentação", w.id_publico === "uuid" && "UUIDv4",
                      w.id_interno && `LNNL ${w.lnnl_tipo}`, w.estrutura === "apps" && "apps/", w.seguranca === "baseline" && "baseline de segurança"];
    partes.push(el("p", {}, el("span", { class: "destaque" }, "web: "), detalhes.filter(Boolean).join(" · ")));
  }
  if (d.campos && d.campos.length) {
    partes.push(el("p", {}, el("span", { class: "destaque" }, "campos a mais: "),
                   d.campos.map((c) => `${c.nome} (${c.rotulo})`).join(" · ")));
  }
  if (d.modulos && d.modulos.length) {
    partes.push(el("p", {}, el("span", { class: "destaque" }, "módulos (apps a mais): "),
                   d.modulos.map((m) => `${m}  (/${m}/ · API /${m}/api/v1/)`).join(" · ")));
  }
  for (const n of d.notas || []) partes.push(el("p", { class: "suave" }, "nota: " + n));
  if (d.testes && d.testes.length) {
    partes.push(el("p", {}, el("span", { class: "destaque" }, "testes:")));
    for (const t of d.testes) {
      const passou = t.codigo === 0;
      partes.push(el("p", {}, el("span", { class: passou ? "ok" : (t.conta ? "erro" : "suave") }, passou ? "  ✓ " : (t.conta ? "  ✗ " : "  • ")),
        t.rotulo, "  ", el("span", { class: "suave" }, t.resumo + (!t.conta && !passou ? "  (esperado: é a sua parte)" : ""))));
    }
  }
  partes.push(el("p", {}, el("span", { class: "destaque" }, "pasta: "), d.caminho,
                  d.numero ? el("span", { class: "suave" }, `   (sistema ${d.numero} · porta ${d.porta})`) : null));
  if (d.numero) {
    const sug = (d.django ? [`sgs rodar ${d.numero}`] : []).concat([`sgs testar ${d.numero}`, `cd ${d.numero}`, `sgs comandos ${d.numero}`]);
    partes.push(el("p", {}, el("span", { class: "suave" }, "executar: "), sug.flatMap((c, i) => [i ? "  ·  " : "", comandoClicavel(c, c)])));
    const evol = [
      [`sgs editar ${d.numero}`, `sgs editar ${d.numero}`, false],
      [`sgs incrementar ${d.numero}`, `sgs incrementar ${d.numero}`, false],
      [`sgs ligar ${d.numero}`, `sgs ligar ${d.numero}`, false],
    ];
    if (d.django) evol.push([`sgs app ${d.numero} `, `sgs app ${d.numero} `, true]);
    evol.push([`sgs duplicar ${d.numero}`, `sgs duplicar ${d.numero}`, false]);
    partes.push(el("p", {}, el("span", { class: "suave" }, `editar este sistema (${d.numero}): `),
      evol.flatMap(([rot, cmdStr, pre], i) => [i ? "  ·  " : "", comandoClicavel(rot.trim(), cmdStr, pre)])));
  }
  const visor = el("pre", { class: "visor", hidden: true });
  const lista = el("div", { class: "arquivos" });
  for (const a of d.arquivos) {
    const botao = el("button", { type: "button", class: "arq" }, a);
    botao.addEventListener("click", () => abrirArquivo(d.pasta, a, visor, lista, botao));
    lista.append(botao);
  }
  partes.push(el("details", { open: d.arquivos.length <= 30 },
    el("summary", {}, `arquivos (${d.arquivos.length}) — clique para ler; comece pelo README.md`), lista), visor);
  return partes;
}

async function abrirArquivo(pasta, caminho, visor, lista, botao) {
  for (const b of lista.children) b.classList.remove("ativo");
  botao.classList.add("ativo");
  visor.hidden = false;
  visor.textContent = "carregando…";
  try {
    const r = await fetch(`/arquivo?pasta=${encodeURIComponent(pasta)}&caminho=${encodeURIComponent(caminho)}`);
    const d = await r.json();
    visor.textContent = d.ok ? `── ${caminho} ──\n\n${d.conteudo}` : "erro: " + d.erro;
  } catch (e) {
    visor.textContent = "sem resposta do servidor: " + e;
  }
}

function desenhar(d) {
  const partes = (d.blocos || []).map(desenharBloco);
  if (d.cartao) partes.push(...montarSistema(d.cartao));
  if (!d.ok && d.erro) partes.push(el("p", { class: "erro" }, "erro: " + d.erro));
  return partes;
}

/* ---------- tela: limpar · módulo comand · voltar ---------- */
function limpar() { saida.replaceChildren(); telaGuardada = null; desenharPrompt(); }
function entrarComand(manter) {          // guarda a tela principal e mostra só o módulo
  if (telaGuardada) { saida.replaceChildren(...manter); return; }
  telaGuardada = [...saida.childNodes].filter((n) => !manter.includes(n));
  saida.replaceChildren(...manter);
}
function voltarPrincipal() {
  if (!telaGuardada) return false;
  saida.replaceChildren(...telaGuardada);
  telaGuardada = null;
  return true;
}

/* ---------- opções da caixa (sincronizadas com o sgs config) ---------- */
const caixas = [...document.querySelectorAll("[data-opcao]")];
function aplicarConfig(c) {
  for (const cx of caixas) cx.checked = !!c[cx.dataset.opcao];
  const raiz = document.documentElement.dataset;
  if ("topo" in c) raiz.topo = c.topo ? "1" : "0";            // sgs topo
  if ("rodape" in c) raiz.rodape = c.rodape ? "1" : "0";      // sgs foot
  if (c.visual && c.visual !== raiz.visual) {                 // sgs cmd · sgs cmd sgs
    raiz.visual = c.visual;
    desenharPrompt();
  }
}
function lerOpcoes() { return Object.fromEntries(caixas.map((cx) => [cx.dataset.opcao, cx.checked])); }
for (const cx of caixas) {
  cx.addEventListener("change", async () => {
    try {
      const r = await fetch("/config", { method: "POST", headers: { "Content-Type": "application/json" },
                                         body: JSON.stringify({ [cx.dataset.opcao]: cx.checked }) });
      aplicarConfig((await r.json()).config);
    } catch (e) { /* sem servidor: a caixa vale só para esta página */ }
  });
}

/* ---------- executar: tudo vai para /comando (o servidor decide: sgs, terminal ou anotação) ---------- */
let executando = false;           // um comando por vez (Enter durante a execução não manda outro)
async function executar(forcado) {
  let texto = (forcado ?? ta.value).trim();
  if ((!texto && !pergunta) || executando) return;                // numa pergunta, Enter vazio = padrão
  posHist = historico.length;
  ta.value = "";
  atualizarSugestoes();                                         // linha vazia: a caixa de sugestões fecha
  // O eco como o prompt: no sgs, o caminho em cima e "$> comando" embaixo; no cmd, "~\caminho>comando".
  const eco = el("div", { class: modoCmd() ? "eco-cmd em-linha" : "eco-cmd" }, el("span", { class: "ps1" }, ps1(prompt)),
                 el("span", { class: "seta" }, modoCmd() ? seta() : seta() + " "),
                 texto || el("span", { class: "suave" }, "(Enter: padrão)"));
  saida.append(eco);
  if (telaGuardada && !pergunta && /^\d{1,2}$/.test(texto)) texto = "sgs comand " + texto;   // no módulo: só o número
  const resposta = el("div", { class: "resp" }, el("p", { class: "suave espera" }, "executando "));
  saida.append(resposta);
  rolar();
  executando = true;
  try {
    const r = await fetch("/comando", { method: "POST", headers: { "Content-Type": "application/json" },
                                       body: JSON.stringify({ linha: texto, opcoes: lerOpcoes() }) });
    const d = await r.json();
    if (d.prompt) prompt = d.prompt;
    pergunta = d.pergunta || null;
    dicaPergunta = d.dica || null;
    // O servidor diz o que entrou no arquivo de histórico (resposta de pergunta não entra; senha sai mascarada).
    if (d.gravado && historico[historico.length - 1] !== d.gravado) historico.push(d.gravado);
    if (Array.isArray(d.historico)) trocarHistorico(d.historico);      // history -c / history -d N
    posHist = historico.length;
    if (d.limpar) limpar();
    else if (d.tela === "principal" && voltarPrincipal()) { /* a tela principal voltou como estava */ }
    else {
      resposta.replaceChildren(...desenhar(d));
      if (d.tela === "comand") entrarComand([eco, resposta]);
    }
    if (d.config) aplicarConfig(d.config);
    if (d.abrir) window.open(d.abrir, "_blank", "noopener");
  } catch (e) {
    resposta.replaceChildren(el("p", { class: "erro" }, "sem resposta do servidor (o SGS ainda está rodando no terminal?): " + e));
  }
  desenharPrompt();
  executando = false;
  ta.focus();
  rolar();
  carregarSugestoes();                  // pasta, sistemas e histórico podem ter mudado: o intellisense acompanha
}

/* ---------- tour interativo de apresentação do Modo CMD ---------- */
const TOUR_CMD = [
  {
    alvo: ".modo-stack",
    titulo: "Alternador WYSIWYG / CMD e Tutorial",
    texto: "Você está no terminal CMD do SGS. Clique em 'WYSIWYG' para abrir a bancada visual de 5 colunas na mesma posição do canto esquerdo, ou clique em 'Tutorial' sempre que quiser rever este passo a passo.",
    dica: "Atalhos no tutorial: <- Voltar · -> Avançar · Esc para fechar.",
  },
  {
    alvo: "#principais",
    titulo: "Barra de Comandos Principais",
    texto: "Todos os comandos essenciais do SGS aparecem aqui como atalhos clicáveis (sem precisar digitar 'sgs'). Comandos diretos executam na hora; comandos que pedem argumentos são preenchidos no prompt.",
    dica: "Use 'sgs topo' para ocultar/mostrar esta barra · 'sgs comand' abre o guia numerado.",
  },
  {
    alvo: "#principais",
    titulo: "Passo 2 · Infra, Segurança & Bibliotecas (sgs infra)",
    texto: "O comando 'sgs infra' (ou 'sgs seguranca') exibe o painel completo de arquitetura: estrutura apps/, UUIDv4, motor-id-interno (LNNL), banco (SQLite3/PostgreSQL/MongoDB), Redis, Baseline (§12–14), Argon2id, Fernet, 2FA com expiração, Recuperação de Senha, RBAC, Anti-Bot, ratelimit, anymail e tinymce.",
    dica: "Ex.: sgs infra\n     sgs config banco=postgresql redis=sim fernet=sim rbac=sim",
  },
  {
    alvo: "#saida",
    titulo: "300 Domínios e 28 Padrões por Escopo",
    texto: "Explore os 300 domínios nativos (+ cadastro próprio em 'sgs dominios novo') e filtre os 28 padrões de projeto por categoria GoF ou por escopo arquitetural (arquitetura, classe, campo, relacao).",
    dica: "Ex.: sgs dominios saude\n     sgs padroes relacao  (mostra padrões de colaboração/FK)",
  },
  {
    alvo: "#saida",
    titulo: "Gerar, Criar Classes, Ligar e Incrementar Campos",
    texto: "Gere o sistema com 'sgs gerar', adicione novas classes com padrões próprios em 'sgs app', conecte ForeignKeys em 'sgs ligar' e incremente campos categorizados (Primitivos, Seleção, Negócio e Estruturados) em 'sgs incrementar'.",
    dica: "Ex.: sgs gerar -sp hotel strategy\n     sgs incrementar 01 Reserva.agendado_em data-hora\n     sgs incrementar 01 Reserva.cpf_hospede cpf",
  },
  {
    alvo: "#caixa",
    titulo: "Prompt com Intellisense e Histórico Persistente",
    texto: "Digite qualquer comando 'sgs ...' ou comando de terminal (ls, cd 01, python manage.py check, pytest). O Intellisense sugere comandos e chaves de configuração; TAB completa e as setas ↑/↓ navegam pelo histórico salvo.",
    dica: "Texto livre sem 'sgs' é apenas anotado na tela. Use 'sgs info 01' para ver infra e arquivos.",
  },
  {
    alvo: ".opcoes",
    titulo: "Caixas Rápidas de Geração",
    texto: "Marque '+ Django', 'Modo exercício', 'Rodar testes', 'Para estudo', 'Comentários' ou 'Perguntar antes de gerar' (que conduz o questionário completo incluindo Infra & Segurança). As escolhas ficam salvas automaticamente.",
    dica: "Use 'sgs foot' para ocultar/mostrar estas caixas · 'sgs rodar 01' sobe o site gerado.",
  },
];

let tourCmdIdx = -1;
function posicionarTourCmd() {
  if (tourCmdIdx < 0) return;
  const passo = TOUR_CMD[tourCmdIdx];
  const alvo = document.querySelector(passo.alvo);
  const ring = $("tour-cmd-ring"), card = $("tour-cmd-card");
  const r = alvo ? alvo.getBoundingClientRect() : null;
  const valido = r && r.width > 10 && r.height > 10;
  if (!valido) {
    ring.style.left = "-9999px"; ring.style.top = "-9999px";
    ring.style.width = "0px"; ring.style.height = "0px";
    card.style.left = Math.max(12, (window.innerWidth - card.offsetWidth) / 2) + "px";
    card.style.top = Math.max(12, (window.innerHeight - card.offsetHeight) / 2) + "px";
    return;
  }
  const pad = 4;
  ring.style.left = Math.max(2, r.left - pad) + "px";
  ring.style.top = Math.max(2, r.top - pad) + "px";
  ring.style.width = Math.min(window.innerWidth - 4, r.width + pad * 2) + "px";
  ring.style.height = Math.min(window.innerHeight - 4, r.height + pad * 2) + "px";
  const cw = card.offsetWidth || 410, ch = card.offsetHeight || 220;
  let left = r.left;
  let top = r.bottom + 12;
  if (top + ch > window.innerHeight - 12) top = r.top - ch - 12;
  top = Math.max(12, Math.min(window.innerHeight - ch - 12, top));
  left = Math.max(12, Math.min(window.innerWidth - cw - 12, left));
  card.style.left = left + "px";
  card.style.top = top + "px";
}

function renderTourCmd() {
  const layer = $("tour-cmd-layer");
  if (tourCmdIdx < 0 || tourCmdIdx >= TOUR_CMD.length) {
    layer.hidden = true;
    ta.focus();
    return;
  }
  const passo = TOUR_CMD[tourCmdIdx];
  layer.hidden = false;
  $("tour-cmd-badge").textContent = `${tourCmdIdx + 1} / ${TOUR_CMD.length}`;
  $("tour-cmd-title").textContent = passo.titulo;
  $("tour-cmd-text").textContent = passo.texto;
  $("tour-cmd-tip").textContent = passo.dica;
  $("tour-cmd-prev").disabled = tourCmdIdx === 0;
  $("tour-cmd-next").textContent = tourCmdIdx === TOUR_CMD.length - 1 ? "Concluir" : "Avançar >";
  $("tour-cmd-dots").replaceChildren(...TOUR_CMD.map((_, i) =>
    el("button", {
      class: "tour-dot" + (i === tourCmdIdx ? " on" : ""),
      type: "button", title: `Passo ${i + 1}`,
      onclick: () => { tourCmdIdx = i; renderTourCmd(); },
    })
  ));
  requestAnimationFrame(posicionarTourCmd);
}

function abrirTourCmd(i = 0) { tourCmdIdx = i; ta.blur(); renderTourCmd(); }
function fecharTourCmd() { tourCmdIdx = -1; renderTourCmd(); }

$("btn-tutorial-cmd").onclick = () => abrirTourCmd(0);
$("tour-cmd-close").onclick = fecharTourCmd;
$("tour-cmd-backdrop").onclick = fecharTourCmd;
$("tour-cmd-prev").onclick = () => { if (tourCmdIdx > 0) { tourCmdIdx -= 1; renderTourCmd(); } };
$("tour-cmd-next").onclick = () => {
  if (tourCmdIdx < TOUR_CMD.length - 1) { tourCmdIdx += 1; renderTourCmd(); }
  else fecharTourCmd();
};
window.addEventListener("resize", posicionarTourCmd);
window.addEventListener("keydown", (e) => {
  if (tourCmdIdx < 0) return;
  if (e.key === "Escape") { e.preventDefault(); fecharTourCmd(); }
  else if (e.key === "ArrowRight") { e.preventDefault(); $("tour-cmd-next").click(); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); $("tour-cmd-prev").click(); }
});

/* ---------- início: só as duas linhas do topo ---------- */
fetch("/config").then((r) => r.json()).then((d) => {
  aplicarConfig(d.config);
  if (d.prompt) prompt = d.prompt;
  if (Array.isArray(d.historico)) trocarHistorico(d.historico);       // ↑/↓ continuam funcionando depois do F5
  desenharPrompt();
}).catch(() => {});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
carregarSugestoes();                    // o catálogo do intellisense
desenharPrompt();
atualizarEco();
ta.focus();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(principal())

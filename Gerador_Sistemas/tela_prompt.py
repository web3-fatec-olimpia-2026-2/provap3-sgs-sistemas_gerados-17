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
VERSÕES: editar um sistema (sgs editar NN · sgs app NN <pedido>) gera uma CÓPIA numerada 01.1, 01.2 … 01.99.
A porta da versão é a do sistema com o último dígito da versão no fim: 01.3 → 61013; 01.9, 01.19 … 01.99 →
61019 (por isso a base é 6100: 6199 + 1 dígito ainda cabe nas 65.535 portas).
PWA: a tela e os sites abrem numa janela de app isolada (Edge/Chrome --app); sgs pwa=false → aba comum.

Como rodar (no WSL, na raiz do projeto, com o .venv ativado):
    python Gerador_Sistemas/tela_prompt.py              → abre http://127.0.0.1:6100 (em modo PWA)
    python Gerador_Sistemas/tela_prompt.py --sem-abrir  → só sobe o servidor

Arquitetura (Aula 07): a tela é uma VIEW FINA. A geração mora em gerar_sistema.py, o terminal em
sgs_terminal.py e o help numerado em sgs_comand.py; aqui ficam o roteamento dos comandos e a página.
"""
import argparse
import atexit
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
from urllib.parse import parse_qs, urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))  # os módulos do SGS estão ao lado deste arquivo
import gerar_sistema as gs  # noqa: E402
import sgs_comand  # noqa: E402
import sgs_perguntas as perguntas  # noqa: E402
import sgs_terminal as terminal  # noqa: E402
import temas_web  # noqa: E402
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
LIMITE_PEDIDO = 600
LIMITE_CORPO = 10_000
LIMITE_ARQUIVO = 300_000
HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}
# Nunca listados nem abertos pelo visualizador de arquivos (o .env tem a senha do admin e a chave secreta).
IGNORAR = {"__pycache__", ".pytest_cache", ".venv", "staticfiles", gs.MARCADOR, "db.sqlite3", ".env",
           "servidor.log"}
NAVEGADORES = ["/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
               "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe",
               "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
               "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"]
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
    "pwa": True, "porta_base": PORTA_PADRAO, "admin_usuario": "admin", "admin_email": "admin@exemplo.com",
    "admin_senha": "admin123",
}
# Valores fechados (listas): nada de texto livre vira CSS ou código.
ESCOLHAS = {"estilo": list(gs.ESTILOS), "tema": list(temas_web.TEMAS), "tom": temas_web.TONS,
            "paleta": list(temas_web.PALETAS), "id_publico": ["inteiro", "uuid"], "estrutura": ["plana", "apps"],
            "seguranca": ["basica", "baseline"]}
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
    "pwa": "sim = sites abrem em janela de app isolada (PWA) · não = aba comum (sgs pwa=false)",
    "porta_base": "o SGS é o 00 nesta porta; o sistema NN roda em porta_base + NN",
    "admin_usuario": "superusuário do Django criado pelo sgs rodar",
    "admin_email": "e-mail do superusuário",
    "admin_senha": "senha do superusuário (mín. 6 caracteres; vai para o web/.env do sistema)",
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
            if not 1024 <= novo <= 65000:
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
    """{pasta: Num(base, versão)} das cópias versionadas (registradas por sgs editar / sgs app)."""
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
            arquivo.write(f"\n\n## Versão {numero}\n\nCópia do sistema {atual} feita pelo SGS (`sgs editar`): o original "
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
              campos=None):
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
                              campos=campos)
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


def abrir_no_navegador(url, pwa=True):
    """PWA: janela de app isolada das abas (Edge/Chrome --app). Sem PWA: aba comum. Devolve o que fez (ou None)."""
    exe = next((p for p in NAVEGADORES if os.access(p, os.X_OK)), None)
    quieto = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "stdin": subprocess.DEVNULL,
              "start_new_session": True}
    try:
        if pwa and exe:
            subprocess.Popen([exe, f"--app={url}"], cwd="/mnt/c", **quieto)
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
        for passo in (("env", "preparar") if preparar else ()):
            if passo == "preparar":
                ajustar_env(destino, cfg)
            r = subprocess.run(["bash", "iniciar.sh", passo], cwd=destino, env=env, capture_output=True, text=True,
                               timeout=600)
            if r.returncode:
                return False, [f"falhou em: bash iniciar.sh {passo}"] + cauda(r.stdout + r.stderr)
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
        with open(log, "w", encoding="utf-8") as arquivo_log:
            processo = subprocess.Popen([python, "manage.py", "runserver", f"127.0.0.1:{porta}", "--noreload"],
                                        cwd=web, stdout=arquivo_log, stderr=subprocess.STDOUT, start_new_session=True,
                                        stdin=subprocess.DEVNULL)
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

    def __init__(self, saida=None, config=None, raiz=RAIZ_PROJETO, porta_tela=PORTA_PADRAO, abrir_janelas=False):
        self.saida = pasta_saida(saida)
        self.config = config if isinstance(config, Config) else Config(config or CONFIG_PADRAO)
        self.servidores = Servidores(self.saida / SERVIDORES)
        self.sessao = terminal.Sessao(raiz)
        # Histórico GLOBAL de comandos (como o ~/.bash_history): fica ao lado do sgs_config.json e sobrevive ao F5.
        self.historico = terminal.Historico(self.config.caminho.parent / terminal.HISTORICO)
        self.porta_tela = porta_tela
        self.abrir_janelas = abrir_janelas      # False nos testes: nada de janelas abrindo sozinhas
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
PRINCIPAIS = ["sgs", "sgs gerar", "sgs listar", "sgs comand", "sgs rodar", "sgs padroes", "sgs config", "clear"]
COMANDOS_SGS = [
    ("sgs", "ajuda: como usar, comandos e configuração", False),
    ("sgs gerar <pedido>", "GERA um sistema (texto solto só é anotado); com “Perguntar” ligado, pergunta antes", True),
    ("sgs gerar -sp <pedido>", "gera SEM perguntar · sozinho (sgs gerar -sp) encerra as perguntas e gera", True),
    ("sgs gerar <domínio> <padrões…>", "gera escolhendo direto (ex.: sgs gerar hotel criacao)", True),
    ("sgs cancelar", "desiste das perguntas em andamento (nada é gerado)", False),
    ("sgs estilo [simples|cmd|bootstrap|web]", "formatação das páginas web geradas", True),
    ("sgs tema [T01…T10] [tom] [P01…P20]", "tema do estilo web (pasta temas/) e paleta do T10", True),
    ("sgs tipos <campos>", "identificador de tipos: o tipo de cada campo pelo nome (os duvidosos viram pergunta)", True),
    ("sgs listar", "sistemas pelo número fixo (01, 02…) e as versões (01.1, 01.2…), com a porta de cada um", False),
    ("sgs info NN", "detalhes e arquivos do sistema NN (ou da versão NN.k)", True),
    ("sgs testar NN", "roda os testes do sistema NN (ou da versão NN.k)", True),
    ("sgs editar NN", "EDITAR = COPIAR: cria a versão NN.k (01.1 … 01.99) — o original não muda", True),
    ("sgs app NN <pedido>", "MÓDULO: nova versão de NN com mais uma app Django (form, CRUD, API REST, padrões, "
                            "settings, models, views, testes) · entidade=Nome escolhe o nome", True),
    ("sgs rodar NN [porta]", "prepara o Django do sistema NN (.env, migrations, admin) e sobe o site (6100+NN; "
                             "versão 01.3 → 61013)", True),
    ("sgs servidores", "sites no ar", False),
    ("sgs parar NN | porta | todos", "derruba um site (ou todos) e libera a porta", True),
    ("sgs comandos NN", "comandos de terminal para rodar o sistema NN fora da tela", True),
    ("sgs comand [n]", "módulo de ajuda: a lista numerada dos comandos da esteira (sgs exit volta)", False),
    ("sgs padroes [categoria]", "os 28 padrões por categoria e as palavras que os ativam", False),
    ("sgs dominios [termo]", "os 100 domínios por setor; com termo, só os que batem (sgs dominios saude)", True),
    ("sgs config [chave=valor]", "mostra/altera a configuração (caixas, porta base, admin, pwa)", False),
    ("sgs pwa=true | sgs pwa=false", "PWA isolado (padrão: janela de app) ou aba comum do navegador", True),
    ("sgs wiki", "abre a cópia da Wikipédia (lista GoF)", False),
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
        texto(f"3) NÚMEROS E PORTAS: cada sistema recebe um número fixo na geração (01, 02…). O SGS é o 00 (porta "
              f"{base}); o sistema 01 roda na {base + 1}, o 02 na {base + 2}… Editar (sgs editar NN, sgs app NN "
              f"<pedido>) cria uma CÓPIA versionada 01.1 … 01.99, com a porta do sistema + o último dígito da versão "
              f"({base + 1}1 para a 01.1; a 01.9, a 01.19 … a 01.99 dividem a {base + 1}9 — se uma estiver no ar, a "
              "tela pergunta se encerra a anterior). Porta presa? A tela libera ao parar, ao fechar e ao reabrir."),
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
        texto("8) MÓDULOS: sgs app NN <pedido> cria a versão NN.k com mais uma app Django: form (ModelForm), CRUD "
              "completo, API REST (/<app>/api/v1/), os padrões do pedido (núcleo dentro da app), settings, models, "
              "views e testes. Ex.: sgs app 01 vacinas com desconto por convênio entidade=Vacina."),
        tabela_comandos(),
        bloco("titulo", texto="Configuração atual"),
        tabela_config(ctx.config),
        bloco("link", texto="Referência dos padrões GoF: cópia da Wikipédia (abre em outra aba)", href="/referencia"),
        texto("Atalhos: Enter executa · Shift+Enter quebra linha · ↑/↓ histórico (guardado em arquivo: sobrevive ao "
              "F5) · Ctrl+L limpa · history · history -c", "suave"),
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
              texto("O número é dado na geração e não muda (por isso a porta também não). 01.1, 01.2… são VERSÕES "
                    "(cópias editadas: sgs editar NN · sgs app NN <pedido>). Clique no número para os detalhes; "
                    "cd NN (ou cd 01.2) entra na pasta.", "suave")]
    if not lista:
        blocos.insert(1, texto("Nenhum sistema gerado ainda. Gere um: sgs gerar loja com extras opcionais", "aviso"))
    return ok(*blocos)


def sgs_info(ctx, args, _opcoes=None):
    destino, n = escolher(ctx, args[0] if args else None)
    info = info_sistema(destino)
    sugestoes = [cmd(f"sgs testar {nn(n)}"), cmd(f"cd {nn(n)}"), cmd(f"sgs comandos {nn(n)}"),
                 cmd(f"sgs editar {nn(n)}")]
    sugestoes += [cmd(f"sgs rodar {nn(n)}"), cmd(f"sgs app {nn(n)} …", f"sgs app {nn(n)} ", True)] if info["django"] else []
    return ok(bloco("tabela", colunas=["próximos passos"] + [""] * (len(sugestoes) - 1), linhas=[sugestoes]),
              cartao=cartao(destino, info, ctx.saida, ctx.config.valores["porta_base"]))


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
    venv = f"{RAIZ_PROJETO}/.venv"
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
    filtro = gs.APELIDOS.get(gs.normalizar(args[0])) if args else None
    if args and filtro not in ("gof", "criacao", "estrutural", "comportamental", "fundamentos"):
        return falha("categoria desconhecida: use criacao, estrutural, comportamental, fundamentos ou gof")
    blocos = []
    for c in catalogo()["categorias"]:
        if filtro and not (filtro == c["chave"] or (filtro == "gof" and c["chave"] != "fundamentos")):
            continue
        blocos.append(bloco("titulo", texto=f"{c['nome']} ({len(c['padroes'])})"))
        blocos.append(bloco("tabela", colunas=["chave", "padrão", "palavras que ativam"],
                            linhas=[[cmd(p["chave"], f"sgs gerar generico {p['chave']}", True), p["titulo"],
                                     ", ".join(p["palavras"])] for p in c["padroes"]]))
    blocos.append(bloco("link", texto="Referência: cópia da Wikipédia com a lista GoF", href="/referencia"))
    return ok(*blocos)


def sgs_dominios(ctx, args, _opcoes=None):
    """sgs dominios → os 10 setores (100 domínios) · sgs dominios <termo> → só os que batem (saude, pet, 045…)."""
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
                  texto("O pedido escolhe o domínio por PONTOS: cada palavra do domínio que aparece vale 1 e o nome do "
                        "domínio vale +3; o genérico só entra quando nenhum outro bate.", "suave"))
    achados = gs.filtrar_dominios(termo)
    if not achados:
        return falha(f"nenhum domínio com “{termo}” — veja os setores com: sgs dominios")
    linhas = [[info["id"], cmd(chave, f"sgs gerar {chave} ", True), d["sistema"], d["entidade"], info["setor"],
               ", ".join((bateram or d["palavras"])[:8]) or "(quando nenhum outro bate)"]
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


def sgs_wiki(ctx, _args, _opcoes=None):
    return ok(bloco("link", texto="Padrão de projeto de software — cópia estática da Wikipédia", href="/referencia"),
              texto(f"arquivo: Gerador_Sistemas/{gs.REFERENCIA_GOF}", "suave"), abrir="/referencia")


def sgs_limpar(ctx, _args, _opcoes=None):
    return {"ok": True, "blocos": [], "limpar": True}


def sgs_editar(ctx, args, opcoes=None):
    """sgs editar NN → CÓPIA versionada NN.k (o original não muda) · sgs editar NN app <pedido> = sgs app NN <pedido>."""
    if len(args) > 1 and args[1].lower() in ("app", "modulo", "módulo"):
        return sgs_app(ctx, [args[0]] + args[2:], opcoes)
    destino, n = escolher(ctx, args[0] if args else None)
    nova, numero = nova_versao(destino, ctx.config.valores["porta_base"], ctx.saida)
    c = cartao(nova, info_sistema(nova), ctx.saida, ctx.config.valores["porta_base"])
    return ok(texto(f"✓ versão {numero} criada: cópia do {n} ({nova.name}) — o original não mudou", "ok"),
              texto(f"edite os arquivos dela (cd {numero}) ou acrescente um módulo: sgs app {numero} <pedido> · "
                    f"porta da versão: {c['porta']}", "suave"),
              cartao=c)


def _pedido_e_entidade(args):
    """["vacinas", "com", "desconto", "entidade=Vacina"] → ("vacinas com desconto", "Vacina")."""
    entidade, resto = None, []
    for arg in args:
        if arg.lower().startswith("entidade="):
            entidade = arg.split("=", 1)[1].strip() or None
        else:
            resto.append(arg)
    return " ".join(resto).strip(), entidade


def sgs_app(ctx, args, opcoes=None):
    """sgs app NN <pedido> [entidade=Nome]: cria a versão NN.k com MAIS UMA app Django (o módulo do pedido).

    O módulo tem o seu form (ModelForm), o CRUD completo, a API REST, os padrões que o pedido pedir (núcleo
    dentro da app), o settings da app, models, views e testes. O original não muda (editar = copiar)."""
    if not args:
        raise ValueError("use: sgs app NN <pedido> — ex.: sgs app 01 vacinas com desconto por convênio")
    destino, n = escolher(ctx, args[0])
    pedido, entidade = _pedido_e_entidade(args[1:])
    if not pedido:
        raise ValueError(f"diga o que o módulo faz: sgs app {n} <pedido> (ex.: sgs app {n} estoque com extras "
                         "opcionais entidade=Produto)")
    if len(pedido) > LIMITE_PEDIDO:
        return falha(f"pedido longo demais (máximo {LIMITE_PEDIDO} caracteres)")
    info = info_sistema(destino)
    if not info["django"]:
        return falha(f"o sistema {n} não tem o site Django — um módulo é uma app Django: gere o sistema com a "
                     "caixa “+ Django” marcada")
    try:
        plano = gs.preparar_modulo(destino, pedido, entidade=entidade)     # valida tudo ANTES de copiar
    except gs.ErroGerador as erro:
        return falha(str(erro))
    nova, numero = nova_versao(destino, ctx.config.valores["porta_base"], ctx.saida)
    gs.aplicar_modulo(nova, plano)
    c = dict(ctx.config.valores)
    c.update({k: bool(v) for k, v in (opcoes or {}).items() if k in OPCOES_CAIXA})
    resposta = cartao(nova, info_sistema(nova), ctx.saida, c["porta_base"])
    if c["testar"]:
        resposta["testes"] = gs.executar_testes(nova, SimpleNamespace(exercicio=info["exercicio"], django=True))
    m = plano["modulo"]
    porta = resposta["porta"]
    linhas = [["app", m["pacote"]], ["entidade", m["entidade"]], ["padrões", ", ".join(m["padroes"])],
              ["telas (CRUD)", f"/{m['app']}/  ·  /{m['app']}/novo/  ·  /{m['app']}/<id>/  ·  editar/  ·  excluir/"],
              ["API REST", f"/{m['app']}/api/v1/  (GET, POST)  ·  /{m['app']}/api/v1/<id>/  (GET, PUT, PATCH, DELETE)"],
              ["arquivos", f"web/{m['caminho']}/  (settings · models · forms · views · api · urls · nucleo/ · tests/)"]]
    return ok(texto(f"✓ versão {numero} criada com o módulo {m['app']} — cópia do {n} + a app nova; o {n} não mudou",
                    "ok"),
              bloco("tabela", colunas=["módulo", ""], linhas=linhas),
              texto(f"suba com: sgs rodar {numero} (porta {porta}) · o banco ganha a tabela nova no migrate", "suave"),
              cartao=resposta)


SGS = {"ajuda": sgs_ajuda, "help": sgs_ajuda, "gerar": sgs_gerar, "listar": sgs_listar, "lista": sgs_listar,
       "info": sgs_info, "testar": sgs_testar, "rodar": sgs_rodar, "parar": sgs_parar, "servidores": sgs_servidores,
       "comandos": sgs_comandos, "comand": sgs_comand_cmd, "padroes": sgs_padroes, "padrões": sgs_padroes,
       "dominios": sgs_dominios, "domínios": sgs_dominios, "config": sgs_config, "pwa": sgs_pwa, "wiki": sgs_wiki,
       "clear": sgs_limpar, "cls": sgs_limpar, "limpar": sgs_limpar, "exit": sgs_exit, "sair": sgs_exit,
       "cancelar": sgs_cancelar, "estilo": sgs_estilo, "tema": sgs_tema, "temas": sgs_tema, "tipos": sgs_tipos,
       "tipo": sgs_tipos, "editar": sgs_editar, "versao": sgs_editar, "versão": sgs_editar, "app": sgs_app,
       "modulo": sgs_app, "módulo": sgs_app}


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
                texto(f"(pergunta pendente — {q.rotulo()}: responda, ou sgs gerar -sp para gerar, ou sgs cancelar)", "aviso"))
    resposta.setdefault("ok", True)
    resposta["prompt"] = ctx.sessao.prompt()
    if ctx.confirmacao is not None:
        resposta["pergunta"], resposta["dica"] = ctx.confirmacao["rotulo"], ctx.confirmacao["dica"]
    else:
        resposta["pergunta"] = ctx.questionario.rotulo() if ctx.questionario else None
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
    "name": NOME_SGS, "short_name": "SGS", "start_url": "/", "scope": "/", "display": "standalone",
    "background_color": "#0c0c0c", "theme_color": "#0c0c0c",
    "icons": [{"src": "/icone-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/icone-512.png", "sizes": "512x512", "type": "image/png"}],
}, ensure_ascii=False)
SERVICE_WORKER = """
// Service worker do SGS: a página principal funciona como app (PWA); os comandos sempre vão ao servidor.
const CACHE = "sgs-v2";
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/"]))); self.skipWaiting(); });
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.pathname !== "/") return;
  e.respondWith(fetch(e.request).then((r) => { const c = r.clone(); caches.open(CACHE).then((k) => k.put("/", c)); return r; })
                                .catch(() => caches.match("/")));
});
"""


class Tela(BaseHTTPRequestHandler):
    server_version = "SGS/3.0"

    def _responder(self, status, corpo, tipo, extras=None):
        dados = corpo.encode("utf-8") if isinstance(corpo, str) else corpo
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        for chave, valor in (extras or {}).items():
            self.send_header(chave, valor)
        self.end_headers()
        self.wfile.write(dados)

    def _json(self, status, dados):
        self._responder(status, json.dumps(dados, ensure_ascii=False), "application/json; charset=utf-8")

    def _host_ok(self):
        # Só atende quem chama por 127.0.0.1/localhost (bloqueia outro site tentando usar a tela).
        if self.headers.get("Host", "").rsplit(":", 1)[0] in HOSTS_PERMITIDOS:
            return True
        self._json(403, {"ok": False, "erro": "Acesse por http://127.0.0.1"})
        return False

    def _ler_json(self):
        """Corpo JSON do POST, ou None (já respondido com o erro)."""
        # Exigir JSON impede que um formulário de OUTRO site dispare ações aqui.
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            self._json(415, {"ok": False, "erro": "Envie JSON."})
            return None
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho > LIMITE_CORPO:
            self._json(413, {"ok": False, "erro": "Pedido grande demais."})
            return None
        try:
            dados = json.loads(self.rfile.read(tamanho) or b"{}")
            if not isinstance(dados, dict):
                raise ValueError
            return dados
        except ValueError:
            self._json(400, {"ok": False, "erro": "JSON inválido."})
            return None

    def do_GET(self):  # noqa: N802 (nome exigido pelo http.server)
        if not self._host_ok():
            return
        ctx = self.server.ctx
        url = urlparse(self.path)
        rotas = {
            "/": lambda: self._responder(200, PAGINA, "text/html; charset=utf-8"),
            "/config": lambda: self._json(200, {"ok": True, "config": ctx.config.publica(),
                                                "prompt": ctx.sessao.prompt(),
                                                "historico": ctx.historico.linhas()}),   # ↑/↓ depois do F5
            "/catalogo": lambda: self._json(200, catalogo()),
            "/manifest.webmanifest": lambda: self._responder(200, MANIFEST, "application/manifest+json"),
            "/sw.js": lambda: self._responder(200, SERVICE_WORKER, "application/javascript",
                                              {"Service-Worker-Allowed": "/"}),
            "/icone-192.png": lambda: self._responder(200, gs.icone_png(192), "image/png"),
            "/icone-512.png": lambda: self._responder(200, gs.icone_png(512), "image/png"),
        }
        if url.path in rotas:
            rotas[url.path]()
        elif url.path == "/arquivo":
            q = parse_qs(url.query)
            r = ler_arquivo(q.get("pasta", [""])[0], q.get("caminho", [""])[0], ctx.saida)
            self._json(200 if r["ok"] else 404, r)
        elif url.path == "/referencia" and REFERENCIA.exists():
            self._responder(200, REFERENCIA.read_bytes(), "text/html; charset=utf-8")
        else:
            self._json(404, {"ok": False, "erro": "Página não encontrada."})

    def do_POST(self):  # noqa: N802
        if not self._host_ok():
            return
        ctx = self.server.ctx
        caminho = urlparse(self.path).path
        if caminho not in ("/gerar", "/comando", "/config"):
            self._json(404, {"ok": False, "erro": "Página não encontrada."})
            return
        pedido = self._ler_json()
        if pedido is None:
            return
        try:
            if caminho == "/config":
                self._json(200, self._salvar_config(pedido))
            elif caminho == "/comando":
                opcoes = pedido.get("opcoes") if isinstance(pedido.get("opcoes"), dict) else {}
                with TRAVA:
                    self._json(200, executar_linha(str(pedido.get("linha", "")), ctx, opcoes))
            else:   # /gerar: API direta (a página usa "sgs gerar" pelo /comando)
                c = ctx.config.valores
                with TRAVA:
                    r = processar(pedido.get("texto"), pedido.get("django", c["django"]),
                                  pedido.get("exercicio", c["exercicio"]), pedido.get("testar", c["testar"]),
                                  ctx.saida, pedido.get("estudo", c["estudo"]), pedido.get("comentarios", c["comentarios"]),
                                  porta_base=c["porta_base"])
                self._json(200, r)
        except Exception as erro:  # erro inesperado: mostra na tela em vez de derrubar o servidor
            self._json(500, {"ok": False, "erro": f"Erro interno: {erro!r}", "prompt": ctx.sessao.prompt()})

    def _salvar_config(self, pedido):
        config = self.server.ctx.config
        try:
            for chave, valor in pedido.items():
                config.alterar(chave, valor)
        except ValueError as erro:
            return {"ok": False, "erro": str(erro), "config": config.publica()}
        config.salvar()
        return {"ok": True, "config": config.publica()}

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
    for caixa in OPCOES_CAIXA:                    # ao abrir, TODAS as caixas começam marcadas (desmarque na tela)
        ctx.config.alterar(caixa, True)
    ctx.config.salvar()
    for chave, porta in ctx.servidores.encerrar_orfaos():   # sites de uma tela anterior que caiu sem limpar
        print(f"  porta {porta} liberada (site {chave} que ficou no ar de uma sessão anterior)")
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
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0c0c0c">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icone-192.png">
<title>SGS - Sistema Gerador de Sistema</title>
<style>
  :root {
    --fundo: #0c0c0c; --painel: #151515; --texto: #cccccc; --forte: #f2f2f2; --suave: #7c7c7c;
    --verde: #16c60c; --ciano: #61d6d6; --amarelo: #e5c07b; --vermelho: #f14c4c; --azul: #6ea8fe;
    --borda: #2c2c2c; --selecao: #264f78;
    --mono: "Cascadia Mono", "Cascadia Code", Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: var(--fundo); color: var(--texto); font: 14px/1.55 var(--mono); }
  ::selection { background: var(--selecao); color: #fff; }
  main { max-width: 1100px; margin: 0 auto; padding: 18px 16px 230px; }
  .banner { color: var(--verde); font-weight: 700; margin: 0; }
  .cmds { color: var(--suave); margin: 2px 0 6px; }
  .eco-cmd { margin-top: 14px; color: var(--forte); white-space: pre-wrap; overflow-wrap: anywhere; }
  .eco-cmd .ps1 { display: block; }
  .seta { color: var(--verde); font-weight: 700; white-space: nowrap; }
  .botoes { display: flex; flex-wrap: wrap; gap: 4px 18px; margin: 4px 0 8px; }
  .ps1 { color: var(--verde); font-weight: 700; }
  .ps1 .dir { color: var(--azul); }
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
  #caixa { max-width: 1100px; margin: 0 auto; background: var(--painel); border: 1px solid var(--borda);
           border-radius: 6px; padding: 10px 12px 8px; }
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
  #caixa.focado #cursor { background: var(--verde); color: var(--fundo); animation: piscar 1.05s steps(1) infinite; }
  #caixa:not(.focado) #cursor { outline: 1px solid var(--verde); outline-offset: -1px; }
  @keyframes piscar { 50% { background: transparent; color: var(--forte); } }
  #dica { color: var(--suave); }
  .opcoes { display: flex; flex-wrap: wrap; gap: 4px 16px; align-items: center; margin-top: 8px; color: var(--suave);
            font-size: 12.5px; }
  .opcoes label { display: inline-flex; gap: 6px; align-items: center; cursor: pointer; }
  .opcoes input { accent-color: var(--verde); margin: 0; }
  #enviar { margin-left: auto; font: inherit; background: transparent; color: var(--verde); border: 1px solid var(--verde);
            border-radius: 4px; padding: 3px 12px; cursor: pointer; }
  #enviar:hover { background: var(--verde); color: var(--fundo); }
  #enviar:disabled { opacity: .4; cursor: wait; }
</style>
</head>
<body>
<main>
  <p class="banner">SGS - Sistema Gerador de Sistema</p>
  <p class="cmds" id="principais">comandos: </p>
  <section id="saida"></section>
</main>
<div id="prompt">
  <div id="caixa">
    <div class="linha-prompt" id="linha">
      <div class="ps1-linha"><span id="modo"></span><span class="ps1" id="ps1"></span></div>
      <div class="linha-comando"><span class="seta" id="seta">$&gt;</span>
      <div class="entrada">
        <pre id="eco"><span id="antes"></span><span id="cursor"> </span><span id="depois"></span><span id="dica">sgs gerar &lt;pedido&gt; · cd · ls · python manage.py … · ou sgs para ajuda</span></pre>
        <textarea id="texto" rows="1" spellcheck="false" autocomplete="off" maxlength="600"
                  aria-label="Comando: sgs, terminal ou anotação"></textarea>
      </div>
      </div>
    </div>
    <div class="opcoes">
      <label><input type="checkbox" data-opcao="django"> + Django (site)</label>
      <label><input type="checkbox" data-opcao="exercicio"> Modo exercício</label>
      <label><input type="checkbox" data-opcao="testar"> Rodar testes</label>
      <label><input type="checkbox" data-opcao="estudo"> Para estudo</label>
      <label><input type="checkbox" data-opcao="comentarios"> Comentários no código</label>
      <label><input type="checkbox" data-opcao="comentarios_web"> Notas na web</label>
      <label><input type="checkbox" data-opcao="perguntar"> Perguntar antes de gerar</label>
      <span class="suave">(valem para o sgs gerar)</span>
      <button id="enviar" type="button">Executar ⏎</button>
    </div>
  </div>
</div>
<script>
const $ = (id) => document.getElementById(id);
const saida = $("saida"), ta = $("texto"), caixa = $("caixa");
const PRINCIPAIS = [["sgs", false], ["sgs gerar ", true], ["sgs listar", false], ["sgs comand", false],
                    ["sgs rodar ", true], ["sgs estilo", false], ["sgs padroes", false], ["sgs config", false],
                    ["clear", false]];
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
function ps1(p) {
  return [p.venv ? el("span", { class: "venv" }, `(${p.venv}) `) : null, "sgs@ilp037:", el("span", { class: "dir" }, p.cwd)];
}
function desenharPrompt() {
  $("ps1").replaceChildren(...ps1(prompt).filter(Boolean));   // sem .venv ativo não há o "(.venv) "
  $("modo").textContent = pergunta ? `[${pergunta}] ` : (telaGuardada ? "[comand] " : "");
  $("dica").textContent = pergunta ? (dicaPergunta || "sua resposta (Enter = padrão) · sgs gerar -sp gera agora")
                                   : "sgs gerar <pedido> · cd · ls · python manage.py … · ou sgs para ajuda";
}
function trocarHistorico(linhas) {
  historico.splice(0, historico.length, ...linhas);
  posHist = historico.length;
}
function atualizarEco() {
  const v = ta.value, pos = Math.min(ta.selectionStart ?? v.length, v.length), ch = v[pos];
  const fim = ch === undefined || ch === "\n";
  $("antes").textContent = v.slice(0, pos);
  $("cursor").textContent = fim ? " " : ch;
  $("depois").textContent = v.slice(fim ? pos : pos + 1);
  $("dica").hidden = v.length > 0;
}
for (const ev of ["input", "keyup", "click", "select", "focus"]) ta.addEventListener(ev, atualizarEco);
document.addEventListener("selectionchange", () => { if (document.activeElement === ta) atualizarEco(); });
ta.addEventListener("focus", () => caixa.classList.add("focado"));
ta.addEventListener("blur", () => caixa.classList.remove("focado"));
$("linha").addEventListener("mousedown", (ev) => { if (ev.target !== ta) { ev.preventDefault(); ta.focus(); } });

function escrever(comando) {
  ta.value = comando;
  ta.focus();
  ta.setSelectionRange(comando.length, comando.length);
  atualizarEco();
}
ta.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); executar(); return; }
  if ((ev.key === "ArrowUp" || ev.key === "ArrowDown") && !ta.value.includes("\n") && historico.length) {
    ev.preventDefault();
    posHist = Math.max(0, Math.min(historico.length, posHist + (ev.key === "ArrowUp" ? -1 : 1)));
    escrever(historico[posHist] ?? "");
  }
  if (ev.key.toLowerCase() === "l" && ev.ctrlKey) { ev.preventDefault(); limpar(); }
});

/* ---------- comandos clicáveis ---------- */
function comandoClicavel(rotulo, comando, preencher) {
  const s = el("span", { class: "cmd", title: preencher ? "clique para escrever no prompt" : "clique para executar" }, rotulo);
  s.addEventListener("click", () => (preencher ? escrever(comando) : executar(comando)));
  return s;
}
$("principais").append(...PRINCIPAIS.flatMap(([c, preencher], i) => [i ? " · " : "", comandoClicavel(c.trim(), c, preencher)]));

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
  if (b.t === "botoes") return el("div", { class: "botoes" }, b.itens.map((c) => comandoClicavel(c.texto, c.cmd, c.preencher)));
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
    const sug = [`sgs testar ${d.numero}`, `cd ${d.numero}`, `sgs comandos ${d.numero}`].concat(d.django ? [`sgs rodar ${d.numero}`] : []);
    partes.push(el("p", {}, el("span", { class: "suave" }, "próximo: "), sug.flatMap((c, i) => [i ? "  ·  " : "", comandoClicavel(c, c)])));
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
function aplicarConfig(c) { for (const cx of caixas) cx.checked = !!c[cx.dataset.opcao]; }
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
async function executar(forcado) {
  let texto = (forcado ?? ta.value).trim();
  if ((!texto && !pergunta) || $("enviar").disabled) return;      // numa pergunta, Enter vazio = padrão
  posHist = historico.length;
  ta.value = "";
  atualizarEco();
  // O eco também em duas linhas: o caminho em cima, "$> comando" embaixo.
  const eco = el("div", { class: "eco-cmd" }, el("span", { class: "ps1" }, ps1(prompt)),
                 el("span", { class: "seta" }, "$> "), texto || el("span", { class: "suave" }, "(Enter: padrão)"));
  saida.append(eco);
  if (telaGuardada && !pergunta && /^\d{1,2}$/.test(texto)) texto = "sgs comand " + texto;   // no módulo: só o número
  const resposta = el("div", { class: "resp" }, el("p", { class: "suave espera" }, "executando "));
  saida.append(resposta);
  rolar();
  $("enviar").disabled = true;
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
  $("enviar").disabled = false;
  ta.focus();
  rolar();
}
$("enviar").addEventListener("click", () => executar());

/* ---------- início: só as duas linhas do topo ---------- */
fetch("/config").then((r) => r.json()).then((d) => {
  aplicarConfig(d.config);
  if (d.prompt) prompt = d.prompt;
  if (Array.isArray(d.historico)) trocarHistorico(d.historico);       // ↑/↓ continuam funcionando depois do F5
  desenharPrompt();
}).catch(() => {});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
desenharPrompt();
atualizarEco();
ta.focus();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(principal())

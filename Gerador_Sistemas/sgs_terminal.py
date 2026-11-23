"""
SGS · TERMINAL — os comandos do WSL mais usados na esteira de desenvolvimento, dentro da tela.
Funcionam com ou sem "sgs" na frente (cd web  ==  sgs cd web).

DE VERDADE:  pwd · ls · cd · tree · cat/head/tail · echo · whoami · date · uname · hostname · python --version ·
             python -m pytest · python manage.py <check|makemigrations|migrate|showmigrations|garantir_admin|
             runserver…> · python script.py · pip list/freeze/show · bash <script>.sh (iniciar.sh, rodar_testes.sh) ·
             git (só leitura) · cp de um .env.example para .env ·
             history (history N · history -c · history -d N) — o histórico fica no ARQUIVO .sgs_historico
             (como o ~/.bash_history), por isso sobrevive ao F5 e ao reiniciar a tela
SIMULADOS:   source …/bin/activate e deactivate (marcam o prompt com "(.venv)") · which ·
             pip install -r requirements.txt (confere o que já está instalado; instalar baixa da internet)
RECUSADOS:   rm, mv, mkdir, touch, sudo, apt, nano, vim… (apagam/mudam arquivos ou pedem senha) e tudo
             que é interativo (python sem argumentos, manage.py shell, createsuperuser sem --noinput)

Segurança: a navegação fica DENTRO da raiz do projeto ("~" na tela) e os segredos do .env aparecem
mascarados no cat. O servidor da tela só atende 127.0.0.1.
"""
import getpass
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

LIMITE_ARQUIVO = 300_000
LIMITE_LINHAS = 200
TEMPO_PADRAO = 600
OCULTAR_NA_ARVORE = {".venv", "__pycache__", ".pytest_cache", "node_modules", ".git", "staticfiles"}
RECUSADOS = {"rm", "rmdir", "mv", "mkdir", "touch", "sudo", "su", "apt", "apt-get", "nano", "vim", "vi", "chmod",
             "chown", "kill", "pkill", "dd", "curl", "wget", "ssh", "scp", "shutdown", "reboot", "code"}
SEGREDO = re.compile(r"^(\s*[A-Za-z0-9_]*(?:SECRET|PASSWORD|SENHA|TOKEN|KEY)[A-Za-z0-9_]*\s*=\s*).+$", re.M | re.I)
DJANGO_PERMITIDOS = {"check", "makemigrations", "migrate", "showmigrations", "sqlmigrate", "garantir_admin",
                     "collectstatic", "diffsettings", "version", "help", "test", "dumpdata", "runserver"}
DJANGO_INTERATIVOS = {"createsuperuser", "shell", "dbshell", "changepassword"}
GIT_LEITURA = {"status", "log", "diff", "branch", "show", "remote", "--version"}
DICA_VENV = "dica: no WSL, ative o ambiente antes (source ~/.venv/bin/activate) — aqui a tela usou o Python do SGS"
HISTORICO = ".sgs_historico"        # o "~/.bash_history" da tela (fica ao lado do sgs_config.json)
LIMITE_HISTORICO = 1000             # como o HISTFILESIZE do bash: guarda só os últimos
SEGREDO_NA_LINHA = re.compile(r"(\b\w*(?:senha|password|secret|token|key)\w*\s*=\s*)\S+", re.I)


class Historico:
    """Histórico GLOBAL de comandos num arquivo de texto (um comando por linha, o mais novo no fim).

    Como o bash: não repete o mesmo comando seguido (ignoredups), guarda os últimos 1000 e `history -c` limpa.
    Senha digitada num comando (sgs config admin_senha=…) entra MASCARADA.
    """

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.mudou = False              # history -c / -d: a página precisa trocar a lista inteira

    def linhas(self):
        try:
            return [linha for linha in self.caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]
        except (OSError, UnicodeDecodeError):
            return []

    def acrescentar(self, comando):
        """Guarda o comando (quebra de linha vira espaço). Devolve a linha como ficou no arquivo."""
        linha = SEGREDO_NA_LINHA.sub(r"\1********", " ".join(str(comando).split()))
        if not linha:
            return None
        atuais = self.linhas()
        if not atuais or atuais[-1] != linha:
            self._gravar((atuais + [linha])[-LIMITE_HISTORICO:])
        return linha

    def limpar(self):
        self._gravar([])
        self.mudou = True

    def apagar(self, numero):
        atuais = self.linhas()
        if not 1 <= numero <= len(atuais):
            raise ValueError(f"bash: history: {numero}: history position out of range")
        del atuais[numero - 1]
        self._gravar(atuais)
        self.mudou = True

    def _gravar(self, linhas):
        try:
            self.caminho.write_text("".join(linha + "\n" for linha in linhas), encoding="utf-8")
        except OSError:
            pass


class Sessao:
    """Estado do terminal da tela: pasta atual, pasta anterior (cd -) e o .venv "ativado"."""

    def __init__(self, raiz):
        self.raiz = Path(raiz).resolve()
        self.cwd = self.raiz
        self.anterior = self.raiz
        self.venv = None

    def mostrar(self, caminho=None):
        """Caminho como o prompt mostra: ~ é a raiz do projeto."""
        relativo = (caminho or self.cwd).relative_to(self.raiz).as_posix()
        return "~" if relativo == "." else "~/" + relativo

    def resolver(self, alvo):
        """'~', '..', relativo ou absoluto → caminho absoluto. Fora da raiz do projeto → PermissionError."""
        if alvo in ("", "~"):
            caminho = self.raiz
        elif alvo.startswith("~/"):
            caminho = self.raiz / alvo[2:]
        else:
            caminho = self.cwd / alvo                   # alvo absoluto: o / do pathlib usa o próprio alvo
        caminho = caminho.resolve()
        if not caminho.is_relative_to(self.raiz):
            raise PermissionError(alvo)
        return caminho

    def prompt(self):
        return {"cwd": self.mostrar(), "venv": self.venv.name if self.venv else ""}


# ----------------------------------------------------------------- blocos de saída
def saida(texto, cor=None):
    return {"t": "saida", "texto": texto, "cor": cor}


def nota(texto):
    return {"t": "texto", "texto": texto, "cor": "suave"}


def rodar(argv, cwd, env_extra=None, tempo=TEMPO_PADRAO):
    """Executa DE VERDADE (sem teclado: stdin fechado) e devolve a saída como blocos."""
    env = dict(os.environ, **(env_extra or {}))
    try:
        r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=tempo,
                           stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return [saida(f"(interrompido: passou de {tempo}s)", "erro")]
    except FileNotFoundError:
        return [saida(f"{Path(argv[0]).name}: command not found", "erro")]
    linhas = (r.stdout + r.stderr).rstrip().splitlines()
    if len(linhas) > LIMITE_LINHAS:
        linhas = [f"… ({len(linhas) - LIMITE_LINHAS} linhas antes)"] + linhas[-LIMITE_LINHAS:]
    blocos = [saida("\n".join(linhas) or "(sem saída)", None if r.returncode == 0 else "erro")]
    if r.returncode:
        blocos.append(nota(f"código de saída {r.returncode}"))
    return blocos


def python_da_sessao(ctx):
    """Com um .venv "ativado", usa o python dele; senão, o Python que roda a tela."""
    venv = ctx.sessao.venv
    if venv and (venv / "bin" / "python").exists():
        return str(venv / "bin" / "python")
    return ctx.python_padrao()


def dica_venv(ctx):
    return [] if ctx.sessao.venv else [nota(DICA_VENV)]


# ----------------------------------------------------------------- navegar
def cmd_pwd(args, ctx, env):
    return [saida(str(ctx.sessao.cwd))]


def cmd_ls(args, ctx, env):
    opcoes = "".join(a[1:] for a in args if a.startswith("-"))
    alvos = [a for a in args if not a.startswith("-")] or ["."]
    blocos = []
    for alvo in alvos:
        caminho = ctx.sessao.resolver(alvo)
        if not caminho.exists():
            blocos.append(saida(f"ls: cannot access '{alvo}': No such file or directory", "erro"))
            continue
        itens = [caminho] if caminho.is_file() else sorted(caminho.iterdir(), key=lambda p: p.name.lower())
        if "a" not in opcoes:
            itens = [p for p in itens if not p.name.startswith(".")]
        nomes = [p.name + ("/" if p.is_dir() else "") for p in itens]
        if "l" in opcoes:
            texto = "\n".join(f"{'d' if p.is_dir() else '-'} {(p.stat().st_size if p.is_file() else 0):>9}  {nome}"
                              for p, nome in zip(itens, nomes))
        else:
            texto = "  ".join(nomes)
        blocos.append(saida((f"{alvo}:\n" if len(alvos) > 1 else "") + (texto or "(pasta vazia)")))
    return blocos


def cmd_ll(args, ctx, env):
    return cmd_ls(["-l"] + args, ctx, env)


def cmd_cd(args, ctx, env):
    sessao = ctx.sessao
    alvo = args[0] if args else "~"
    if alvo == "-":
        sessao.anterior, sessao.cwd = sessao.cwd, sessao.anterior
        return [saida(str(sessao.cwd))]
    destino = sessao.resolver(alvo)
    if not destino.exists() and re.fullmatch(r"\d{1,3}(\.\d{1,2})?", alvo):   # atalho: cd 01 = sistema 01; cd 01.2 = versão
        pasta = ctx.pasta_do_numero(alvo)
        if pasta is not None:
            destino = sessao.resolver(str(pasta))
    if not destino.exists():
        return [saida(f"bash: cd: {alvo}: No such file or directory", "erro")]
    if not destino.is_dir():
        return [saida(f"bash: cd: {alvo}: Not a directory", "erro")]
    sessao.anterior, sessao.cwd = sessao.cwd, destino
    return []                                                    # cd não imprime nada: só o prompt muda


def cmd_tree(args, ctx, env):
    nivel, alvo, i = 3, ".", 0
    while i < len(args):
        if args[i] == "-L" and i + 1 < len(args) and args[i + 1].isdigit():
            nivel, i = int(args[i + 1]), i + 2
        else:
            alvo, i = args[i], i + 1
    raiz = ctx.sessao.resolver(alvo)
    if not raiz.is_dir():
        return [saida(f"{alvo} [error opening dir]", "erro")]
    linhas, contagem = [alvo], [0, 0]

    def descer(pasta, prefixo, profundidade):
        filhos = sorted((p for p in pasta.iterdir() if p.name not in OCULTAR_NA_ARVORE and not p.name.startswith(".")),
                        key=lambda p: (not p.is_dir(), p.name.lower()))
        for k, filho in enumerate(filhos):
            ultimo = k == len(filhos) - 1
            linhas.append(prefixo + ("└── " if ultimo else "├── ") + filho.name + ("/" if filho.is_dir() else ""))
            if filho.is_dir():
                contagem[0] += 1
                if profundidade < nivel and len(linhas) < 500:
                    descer(filho, prefixo + ("    " if ultimo else "│   "), profundidade + 1)
            else:
                contagem[1] += 1

    descer(raiz, "", 1)
    return [saida("\n".join(linhas) + f"\n\n{contagem[0]} directories, {contagem[1]} files")]


def ler_texto(alvo, ctx, comando):
    caminho = ctx.sessao.resolver(alvo)
    if not caminho.exists():
        raise FileNotFoundError(f"{comando}: {alvo}: No such file or directory")
    if caminho.is_dir():
        raise IsADirectoryError(f"{comando}: {alvo}: Is a directory")
    if caminho.stat().st_size > LIMITE_ARQUIVO:
        raise ValueError(f"{comando}: {alvo}: grande demais para a tela — abra no editor")
    try:
        texto = caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{comando}: {alvo}: arquivo binário (não é texto)") from None
    if caminho.name == ".env" or caminho.name.endswith(".env"):
        texto = SEGREDO.sub(lambda m: m.group(1) + "********  (oculto pela tela)", texto)
    return texto


def cmd_cat(args, ctx, env):
    if not args:
        return [saida("cat: diga o arquivo (ex.: cat requirements.txt)", "aviso")]
    return [saida(ler_texto(alvo, ctx, "cat").rstrip("\n") or "(arquivo vazio)") for alvo in args]


def _head_tail(args, ctx, comando):
    n, arquivos, i = 10, [], 0
    while i < len(args):
        if args[i] == "-n" and i + 1 < len(args) and args[i + 1].isdigit():
            n, i = int(args[i + 1]), i + 2
        elif re.fullmatch(r"-\d+", args[i]):
            n, i = int(args[i][1:]), i + 1
        else:
            arquivos.append(args[i])
            i += 1
    if not arquivos:
        return [saida(f"{comando}: diga o arquivo (ex.: {comando} -n 20 web/servidor.log)", "aviso")]
    blocos = []
    for alvo in arquivos:
        linhas = ler_texto(alvo, ctx, comando).splitlines()
        blocos.append(saida("\n".join(linhas[:n] if comando == "head" else linhas[-n:]) or "(vazio)"))
    return blocos


def cmd_head(args, ctx, env):
    return _head_tail(args, ctx, "head")


def cmd_tail(args, ctx, env):
    return _head_tail(args, ctx, "tail")


def cmd_echo(args, ctx, env):
    valores = {"$PWD": str(ctx.sessao.cwd), "$HOME": str(ctx.sessao.raiz),
               "$VIRTUAL_ENV": str(ctx.sessao.venv or ""), "$USER": getpass.getuser()}
    texto = " ".join(args)
    for chave, valor in valores.items():
        texto = texto.replace(chave, valor)
    return [saida(texto)]


def cmd_whoami(args, ctx, env):
    return [saida(getpass.getuser())]


def cmd_date(args, ctx, env):
    if any(a in ("-s", "--set") or a.startswith("--set=") for a in args):
        return [saida("date: a tela não muda o relógio (pede senha) — só mostra a data", "aviso")]
    return rodar(["date", *args], ctx.sessao.cwd, env, tempo=10)


def cmd_uname(args, ctx, env):
    return rodar(["uname", *args], ctx.sessao.cwd, env, tempo=10)


def cmd_hostname(args, ctx, env):
    if any(not a.startswith("-") for a in args):
        return [saida("hostname: a tela só mostra o nome da máquina (trocar pede senha)", "aviso")]
    return rodar(["hostname", *args], ctx.sessao.cwd, env, tempo=10)


def cmd_history(args, ctx, env):
    """history · history N (os últimos N) · history -c (limpa) · history -d N (apaga o N) — numerado como no bash."""
    hist = ctx.historico
    if args and args[0] == "-c":
        hist.limpar()
        return []                                                   # como no bash: não imprime nada
    if args and args[0] == "-d":
        if len(args) < 2 or not args[1].lstrip("-").isdigit():
            return [saida("bash: history: -d: option requires an argument", "erro")]
        hist.apagar(int(args[1]))
        return []
    linhas = hist.linhas()
    numeradas = [f"{i:5d}  {linha}" for i, linha in enumerate(linhas, 1)]
    if args:
        if not args[0].isdigit():
            return [saida(f"bash: history: {args[0]}: numeric argument required (use: history, history N, "
                          "history -c ou history -d N)", "erro")]
        numeradas = numeradas[-int(args[0]):] if int(args[0]) else []
    return [saida("\n".join(numeradas) or "(histórico vazio)")]


# ----------------------------------------------------------------- ambiente python
def cmd_source(args, ctx, env):
    if not args:
        return [saida("bash: source: filename argument required", "erro")]
    caminho = ctx.sessao.resolver(args[0])
    if not caminho.is_file():
        return [saida(f"bash: {args[0]}: No such file or directory", "erro"),
                nota("o .venv do projeto fica na raiz: source ~/.venv/bin/activate")]
    if caminho.name != "activate" or caminho.parent.name != "bin":
        return [saida("source: a tela só ativa ambientes virtuais (…/.venv/bin/activate)", "aviso")]
    ctx.sessao.venv = caminho.parent.parent
    return []                                                     # como no bash: só o prompt muda


def cmd_deactivate(args, ctx, env):
    if ctx.sessao.venv is None:
        return [saida("deactivate: command not found", "erro")]
    ctx.sessao.venv = None
    return []


def cmd_which(args, ctx, env):
    linhas = []
    for nome in args or ["python"]:
        if nome in ("python", "python3", "pip", "pip3") and ctx.sessao.venv:
            linhas.append(str(ctx.sessao.venv / "bin" / nome))
        else:
            linhas.append(shutil.which(nome) or f"{nome} not found")
    return [saida("\n".join(linhas))]


def cmd_pip(args, ctx, env):
    py = python_da_sessao(ctx)
    if not args:
        return [saida("Usage: pip <command> [options]  (na tela: install -r, list, freeze, show)", "aviso")]
    if args[0] in ("list", "freeze", "show", "check", "--version", "-V"):
        return dica_venv(ctx) + rodar([py, "-m", "pip", *args], ctx.sessao.cwd, env, tempo=120)
    if args[0] == "install" and "-r" in args:
        k = args.index("-r")
        if k + 1 >= len(args):
            return [saida("ERROR: -r option requires 1 argument", "erro")]
        texto = ler_texto(args[k + 1], ctx, "pip")
        requisitos = [linha.strip() for linha in texto.splitlines() if linha.strip() and not linha.startswith("#")]
        nomes = [re.split(r"[<>=!~\[; ]", r, maxsplit=1)[0] for r in requisitos]
        verificador = ("import sys, importlib.metadata as m\nfor n in sys.argv[1:]:\n"
                       "    try:\n        print(m.version(n))\n    except m.PackageNotFoundError:\n        print('-')\n")
        r = subprocess.run([py, "-c", verificador, *nomes], capture_output=True, text=True, timeout=60)
        versoes = r.stdout.split()
        linhas, faltando = [], []
        for requisito, versao in zip(requisitos, versoes):
            if versao == "-":
                faltando.append(requisito)
            else:
                linhas.append(f"Requirement already satisfied: {requisito} ({versao})")
        blocos = dica_venv(ctx) + [saida("\n".join(linhas) or "(nada instalado ainda)")]
        if faltando:
            blocos.append(saida("faltando: " + ", ".join(faltando) + "\ninstalar baixa da internet — no terminal do "
                                "WSL: pip install -r " + args[k + 1], "aviso"))
        else:
            blocos.append(nota("(simulado: tudo já estava instalado, nada foi baixado)"))
        return blocos
    return [saida("pip: a tela não instala pacotes novos (baixa da internet) — use o terminal do WSL", "aviso")]


def cmd_python(args, ctx, env):
    py = python_da_sessao(ctx)
    if not args:
        return [saida("python: o modo interativo (REPL) não funciona na tela — use o terminal do WSL", "aviso")]
    if args[0] in ("--version", "-V"):
        return rodar([py, "--version"], ctx.sessao.cwd, env)
    if args[0] == "-m" and len(args) > 1:
        if args[1] == "pytest":
            return dica_venv(ctx) + cmd_pytest(args[2:], ctx, env, py)
        if args[1] == "pip":
            return cmd_pip(args[2:], ctx, env)
        return [saida(f"python -m {args[1]}: não executado pela tela (use pytest ou pip)", "aviso")]
    if args[0] == "manage.py" or args[0].endswith("/manage.py"):
        return dica_venv(ctx) + cmd_manage(args, ctx, env, py)
    if args[0].endswith(".py"):
        script = ctx.sessao.resolver(args[0])
        if not script.is_file():
            return [saida(f"python: can't open file '{script}': [Errno 2] No such file or directory", "erro")]
        return dica_venv(ctx) + rodar([py, str(script), *args[1:]], ctx.sessao.cwd, env, tempo=120)
    return [saida(f"python: opção não suportada pela tela: {args[0]}", "aviso")]


def cmd_pytest(args, ctx, env, py=None):
    return rodar([py or python_da_sessao(ctx), "-m", "pytest", "-p", "no:cacheprovider", *args], ctx.sessao.cwd, env)


# ----------------------------------------------------------------- django
def localizar_manage(arg, ctx):
    """Acha o manage.py. Na pasta do sistema (ou em config/), AJUSTA para o web/manage.py e avisa."""
    cwd = ctx.sessao.cwd
    pedido = ctx.sessao.resolver(arg)
    if pedido.is_file():
        return pedido, None
    if arg == "manage.py":
        for alternativo, motivo in ((cwd / "web" / "manage.py", "o manage.py deste sistema fica em web/ — rodei de lá"),
                                    (cwd.parent / "manage.py", "o manage.py fica na pasta de cima — rodei de lá")):
            if alternativo.is_file() and alternativo.resolve().is_relative_to(ctx.sessao.raiz):
                return alternativo, motivo
    return None, None


def cmd_manage(args, ctx, env, py):
    manage, ajuste = localizar_manage(args[0], ctx)
    if manage is None:
        return [saida(f"python: can't open file '{ctx.sessao.cwd / args[0]}': [Errno 2] No such file or directory",
                      "erro"),
                nota("entre na pasta de um sistema com Django (sgs listar → cd NN) — a tela acha o web/manage.py")]
    blocos = [nota("ajuste: " + ajuste)] if ajuste else []
    sub = args[1] if len(args) > 1 else "help"
    web = manage.parent
    if sub == "runserver":
        return blocos + ctx.runserver(web, args[2:], py)
    if sub in DJANGO_INTERATIVOS and "--noinput" not in args:
        dica = "python manage.py garantir_admin (usa o usuário e a senha do web/.env)" if sub == "createsuperuser" \
            else "o terminal do WSL"
        return blocos + [saida(f"manage.py {sub}: é interativo (faz perguntas) e a tela não responde — use {dica}",
                               "aviso")]
    if sub not in DJANGO_PERMITIDOS | DJANGO_INTERATIVOS:
        return blocos + [saida(f"manage.py {sub}: não executado pela tela — rode no terminal do WSL", "aviso")]
    extra = ["--noinput"] if sub == "collectstatic" and "--noinput" not in args else []
    return blocos + rodar([py, "manage.py", *args[1:], *extra], web, env)


# ----------------------------------------------------------------- scripts, git e cópia do .env
def cmd_bash(args, ctx, env):
    if not args:
        return [saida("bash: o modo interativo não funciona na tela — rode um script: bash iniciar.sh", "aviso")]
    if not args[0].endswith(".sh"):
        return [saida("bash: a tela só roda scripts .sh (ex.: bash iniciar.sh, bash rodar_testes.sh)", "aviso")]
    script = ctx.sessao.resolver(args[0])
    if not script.is_file() and args[0] == "iniciar.sh" and (ctx.sessao.cwd.parent / "iniciar.sh").is_file():
        script = ctx.sessao.cwd.parent / "iniciar.sh"           # estava em web/: o script fica na pasta de cima
    if not script.is_file():
        return [saida(f"bash: {args[0]}: No such file or directory", "erro")]
    if script.name == "iniciar.sh":
        return ctx.iniciar_sh(script.parent, args[1:])
    return rodar(["bash", str(script), *args[1:]], ctx.sessao.cwd, env)


def cmd_git(args, ctx, env):
    if not args or args[0] not in GIT_LEITURA:
        return [saida("git: a tela só roda comandos de leitura (status, log, diff, branch, show, remote)", "aviso")]
    return rodar(["git", *args], ctx.sessao.cwd, env, tempo=30)


def cmd_cp(args, ctx, env):
    sem_sobrescrever = any(a in ("-n", "--no-clobber") for a in args)
    resto = [a for a in args if not a.startswith("-")]
    if len(resto) != 2 or not resto[0].endswith(".env.example") or not resto[1].endswith(".env"):
        return [saida("cp: a tela só copia um modelo .env.example para .env — outras cópias: terminal do WSL", "aviso")]
    origem, destino = ctx.sessao.resolver(resto[0]), ctx.sessao.resolver(resto[1])
    if not origem.is_file():
        return [saida(f"cp: cannot stat '{resto[0]}': No such file or directory", "erro")]
    if destino.exists():
        return [] if sem_sobrescrever else [saida("cp: não sobrescrevo um .env que já existe (a tela protege as "
                                                  "suas senhas) — use cp -n", "aviso")]
    shutil.copyfile(origem, destino)
    return []


COMANDOS = {"pwd": cmd_pwd, "ls": cmd_ls, "ll": cmd_ll, "cd": cmd_cd, "tree": cmd_tree, "cat": cmd_cat,
            "head": cmd_head, "tail": cmd_tail, "echo": cmd_echo, "whoami": cmd_whoami, "date": cmd_date,
            "uname": cmd_uname, "hostname": cmd_hostname, "history": cmd_history, "source": cmd_source,
            ".": cmd_source, "deactivate": cmd_deactivate, "which": cmd_which, "pip": cmd_pip, "pip3": cmd_pip,
            "python": cmd_python, "python3": cmd_python, "pytest": cmd_pytest, "bash": cmd_bash, "sh": cmd_bash,
            "git": cmd_git, "cp": cmd_cp}


def executar(linha, ctx):
    """Roda uma linha de terminal. Devolve a lista de blocos, ou None se não for um comando de terminal."""
    try:
        partes = shlex.split(linha)
    except ValueError as erro:
        return [saida(f"bash: aspas sem fechar ({erro})", "erro")]
    env = {}
    while partes and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=\S*", partes[0]):   # VAR=valor comando
        chave, valor = partes.pop(0).split("=", 1)
        env[chave] = valor
    if not partes:
        return None
    nome, args = partes[0], partes[1:]
    if nome.startswith("./") and nome.endswith(".sh"):
        nome, args = "bash", [nome[2:]] + args
    if nome in RECUSADOS:
        return [saida(f"{nome}: não executado pela tela (apaga/muda arquivos, pede senha ou abre outro programa) — "
                      "use o terminal do WSL", "aviso")]
    funcao = COMANDOS.get(nome)
    if funcao is None:
        return None
    try:
        return funcao(args, ctx, env)
    except PermissionError:
        return [saida(f"{nome}: fora do projeto — a tela só acessa a pasta do projeto (~)", "erro")]
    except (FileNotFoundError, IsADirectoryError, ValueError) as erro:
        return [saida(str(erro), "erro")]

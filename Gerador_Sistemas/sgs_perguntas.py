"""
SGS · PERGUNTAS — antes de gerar, o SGS pergunta (rodadas de 10) e só gera com "sgs gerar -sp".

Fluxo (com a caixa "Perguntar antes de gerar" marcada):
  sgs gerar <pedido>   → até 10 perguntas por rodada, numa FILA única:
                         visão geral (Django, estilo, tema, tom, padrões) → CAMPOS e TIPOS (os campos do pedido cujo
                         tipo não é óbvio pelo nome; se o pedido não listou campos, pergunta quais) → finalidade,
                         comentários, notas, exercício, testes → arquitetura (Instruções Django: UUID, LNNL, apps/,
                         segurança, paleta, estados, nomes, domínio) → padrões de projeto um a um
  TIPO ÓBVIO           → não vira pergunta: o identificador de tipos (tipos_campos.py) já sabe que nome é texto,
                         idade é inteiro, peso é decimal, vacinado é sim/não, data_… é data
  CAIXA MARCADA        → não vira pergunta (vale "sim"). Só o que está desmarcado é perguntado.
  NÃO SE APLICA        → também não vira pergunta (sem Django: nada de estilo; sem estilo web: nada de tema…)
  ao fim da rodada     → "Refinar mais?"  sim = mais 10 perguntas  ·  sgs gerar -sp = gera agora
  sgs gerar -sp        → em QUALQUER pergunta: para de perguntar e gera com o que já foi decidido
  sgs gerar -sp <pedido> (logo de cara) → gera sem perguntar · sgs cancelar → desiste

Respostas: o número da opção, o nome dela, sim/não, um texto (nas perguntas abertas) ou Enter = padrão.
Tudo é determinístico: as mesmas respostas geram o mesmo sistema.
"""
import re

import gerar_sistema as gs
import temas_web
import tipos_campos

SIM = {"sim", "s", "y", "yes", "true", "1"}
NAO = {"nao", "não", "n", "no", "false", "0"}
PADRAO = {"", "-", "enter", "padrao", "padrão"}
POR_RODADA = 10
# As caixas da tela que também são perguntas: marcada = decidida ("sim"), não é perguntada.
CAIXAS = ("django", "estudo", "comentarios", "comentarios_web", "exercicio", "testar")
MAX_CAMPOS = 30          # vagas na fila para as perguntas de tipo (uma por campo duvidoso)


def _sim_nao(chave, titulo, texto, padrao):
    return {"chave": chave, "titulo": titulo, "texto": texto, "tipo": "sim_nao", "padrao": bool(padrao),
            "opcoes": [(True, "sim"), (False, "não")]}


def _opcao(chave, titulo, texto, opcoes, padrao):
    return {"chave": chave, "titulo": titulo, "texto": texto, "tipo": "opcao", "padrao": padrao, "opcoes": opcoes}


def _livre(chave, titulo, texto, padrao):
    return {"chave": chave, "titulo": titulo, "texto": texto, "tipo": "texto", "padrao": padrao, "opcoes": []}


class Questionario:
    """Estado das perguntas de UM pedido: decisões, fila de perguntas, rodada atual."""

    def __init__(self, pedido, config, marcadas=()):
        self.pedido = pedido
        self.marcadas = {c for c in marcadas if c in CAIXAS}
        analise = gs.analisar_assunto(pedido)
        dominio = analise["dominio"]
        self.detectados = analise["padroes"] or ["prova"]
        self.campos_do_pedido = bool(analise["campos"])  # o pedido já listou campos? então não pergunta quais
        self.decisoes = {
            "django": config["django"], "estilo": config["estilo"], "tema": config["tema"], "tom": config["tom"],
            "paleta": config["paleta"], "padroes": "manter", "estudo": config["estudo"],
            "comentarios": config["comentarios"], "comentarios_web": config["comentarios_web"],
            "exercicio": config["exercicio"], "testar": config["testar"], "id_publico": config["id_publico"],
            "id_interno": config["id_interno"], "lnnl_tipo": config["lnnl_tipo"], "estrutura": config["estrutura"],
            "seguranca": config["seguranca"], "estado": False, "sistema": analise["sistema"] or gs.DOMINIOS[dominio]["sistema"],
            "entidade": gs.DOMINIOS[dominio]["entidade"], "dominio": dominio,
            "campos": tipos_campos.analisar(analise["campos"]),   # tipo deduzido pelo nome (ou escrito no pedido)
        }
        for caixa in self.marcadas:                      # caixa marcada = decidida, não será perguntada
            self.decisoes[caixa] = True
        self.extras = []                                 # padrões acrescentados um a um
        self.fila = self._fila()
        self.pos = 0
        self.rodada = 0
        self.na_rodada = 0
        self.atual = None
        self.refinar = False
        self.esgotado = False
        self.respostas = 0
        self.proxima_rodada()

    # ------------------------------------------------------------------ a fila (cada item decide na hora se se aplica)
    def _fila(self):
        d = self.decisoes

        def caixa(chave, fabrica):
            return lambda: None if chave in self.marcadas else fabrica()

        def se(condicao, fabrica):
            return lambda: fabrica() if condicao() else None

        def web():
            return d["django"]

        def tema_web():
            return web() and d["estilo"] == "web"

        temas = [(t, f"{t} {temas_web.TEMAS[t]['nome']} — {temas_web.TEMAS[t]['descricao']}") for t in temas_web.TEMAS]
        fila = [
            # --- visão geral
            caixa("django", lambda: _sim_nao("django", "Django", "Gerar também o site Django (a interface web)?",
                                             d["django"])),
            se(web, lambda: _opcao("estilo", "Estilo", "Estilo de formatação das páginas web?",
                                   [(e, f"{e} — {txt}") for e, txt in gs.ESTILOS.items()], d["estilo"])),
            se(tema_web, lambda: _opcao("tema", "Tema", "Tema de cores do estilo web?", temas, d["tema"])),
            se(tema_web, lambda: _opcao("tom", "Tom", "Variação de tom do tema (do Claro ao Escuro)?",
                                        [(t, temas_web.NOMES_TONS[t]) for t in temas_web.TONS], d["tom"])),
            lambda: _opcao("padroes", "Padrões", f"Padrões de projeto? O pedido indicou: {', '.join(self.detectados)}.",
                           [("manter", "manter o que o pedido indicou"), ("prova", "os 9 da prova (P3)"),
                            ("gof", "os 23 do GoF"), ("criacao", "GoF · criação"), ("estrutural", "GoF · estruturais"),
                            ("comportamental", "GoF · comportamentais"), ("todos", "todos os 28")], d["padroes"]),
            # --- campos e tipos (identificador de tipos: só o que NÃO é óbvio vira pergunta)
            se(lambda: not self.campos_do_pedido, lambda: _livre(
                "campos", "Campos", f"Campos a mais na {d['entidade']}, além dos do domínio "
                f"({', '.join(a['nome'] for a in gs.DOMINIOS[d['dominio']]['atributos'])})? Separe por vírgula; "
                "o tipo pode ir junto (idade:int) ou fica por conta do identificador. Enter = nenhum.", "")),
            *[self._pergunta_tipo(i) for i in range(MAX_CAMPOS)],
            caixa("estudo", lambda: _opcao("estudo", "Finalidade",
                                           "Gerar para ESTUDO (antes_*.py, ADRs, README didático) ou SÓ GERAR?",
                                           [(True, "para estudo"), (False, "só gerar")], d["estudo"])),
            caixa("comentarios", lambda: _sim_nao("comentarios", "Comentários no código",
                                                  "Comentários explicativos no CÓDIGO (.py)?", d["comentarios"])),
            se(web, caixa("comentarios_web", lambda: _sim_nao(
                "comentarios_web", "Notas na web",
                "Notas de APRESENTAÇÃO nas páginas web (explicam cada parte na tela; dá para ocultar)?",
                d["comentarios_web"]))),
            caixa("exercicio", lambda: _sim_nao("exercicio", "Exercício",
                                                "Modo exercício (questionário de revisão com “Ver resposta”; o código sai completo)?",
                                                d["exercicio"])),
            caixa("testar", lambda: _sim_nao("testar", "Testes", "Rodar os testes logo depois de gerar?", d["testar"])),
            # --- arquitetura (Instruções de desenvolvimento DJANGO e motor-id-interno)
            se(web, lambda: _opcao("id_publico", "Identificador", "Identificador dos registros no Django?",
                                   [("inteiro", "inteiro (padrão do Django)"),
                                    ("uuid", "UUIDv4 (Instruções §10.4: anti-enumeração)")], d["id_publico"])),
            se(web, lambda: _sim_nao("id_interno", "ID interno LNNL",
                                     "ID interno legível LNNL (motor-id-interno, ex.: K21W-F92M-T5R-Q7L) em cada registro?",
                                     d["id_interno"])),
            se(lambda: web() and d["id_interno"], lambda: _livre(
                "lnnl_tipo", "Tipo LNNL", "Código de tipo do LNNL (2 dígitos de 1 a 9; nunca 93)?", d["lnnl_tipo"])),
            se(web, lambda: _opcao("estrutura", "Estrutura", "Estrutura da app Django?",
                                   [("plana", "plana: web/<app>/"),
                                    ("apps", "apps/<app>/ + README da app (Instruções §9.2)")], d["estrutura"])),
            se(web, lambda: _opcao("seguranca", "Segurança", "Segurança das settings?",
                                   [("basica", "básica (estudo)"),
                                    ("baseline", "baseline das Instruções §12–14 (cabeçalhos, cookies, CSP, ADMIN_URL, "
                                                 "Argon2)")], d["seguranca"])),
            se(lambda: tema_web() and d["tema"] == "T10", lambda: _opcao(
                "paleta", "Paleta (T10)", "Paleta do tema T10 Personalizado (Instruções §11.9)?",
                [(p, f"{p} {v[0]}") for p, v in temas_web.PALETAS.items()], d["paleta"])),
            lambda: _sim_nao("estado", "Máquina de estados",
                             f"Incluir uma máquina de estados (padrão State) para o ciclo de vida da {d['entidade']}?",
                             d["estado"]),
            lambda: _livre("sistema", "Nome do sistema", "Nome do sistema?", d["sistema"]),
            lambda: _livre("entidade", "Entidade", "Nome da entidade principal (a classe)?", d["entidade"]),
            lambda: _opcao("dominio", "Domínio base",
                           "Domínio base (atributos, regras e exemplos)? Aqui estão os que o pedido mais pontuou; "
                           f"dá para digitar qualquer um dos {len(gs.DOMINIOS)} (sgs dominios <termo> procura).",
                           self._opcoes_dominio(), d["dominio"]),
        ]
        # --- padrões de projeto um a um (só os que ainda não entraram)
        for p in gs.ORDEM_PADROES:
            fila.append(self._pergunta_padrao(p))
        return fila

    def _opcoes_dominio(self, limite=6):
        """Os domínios mais pontuados pelo pedido + o atual + o genérico (a lista inteira tem 100)."""
        ranking = [chave for _, chave, _ in gs.pontuar_dominios(gs.normalizar(self.pedido))][:limite]
        chaves = list(dict.fromkeys(ranking + [self.decisoes["dominio"], "generico"]))
        return [(k, f"{k} — {gs.DOMINIOS[k]['sistema']} / {gs.DOMINIOS[k]['entidade']}") for k in chaves]

    def _pergunta_tipo(self, indice):
        """Vaga nº `indice` das perguntas de tipo: pergunta o próximo campo cujo tipo ainda está em DÚVIDA."""
        def fabrica():
            ja_tem = {a["nome"] for a in gs.DOMINIOS[self.decisoes["dominio"]]["atributos"]}
            duvidosos = [c for c in tipos_campos.duvidosos(self.decisoes["campos"])   # o domínio já tem / reservado:
                         if c["nome"] not in ja_tem and c["nome"] not in gs.RESERVADOS   # o gerador ignora,
                         and c["nome"] not in gs.RESERVADOS_DJANGO]                      # então nem pergunta
            if not duvidosos:
                return None
            c = duvidosos[0]                    # o anterior já foi respondido e saiu da lista de duvidosos
            opcoes = [(tipo, tipos_campos.rotulo(tipo)) for tipo in tipos_campos.ORDEM_TIPOS]
            return _opcao(f"tipo:{c['nome']}", f"Tipo de {c['nome']}",
                          f"Qual o tipo do campo “{c['nome']}”? O tipo não é óbvio pelo nome ({c['motivo']}); "
                          f"sugestão: {tipos_campos.rotulo(c['sugestao'])}.", opcoes, c["sugestao"])
        return fabrica

    def _pergunta_padrao(self, padrao):
        def fabrica():
            if padrao in self.padroes_finais():
                return None
            info = gs.PADROES[padrao]
            return _sim_nao(f"padrao:{padrao}", info["titulo"],
                            f"Incluir o {info['titulo']}? {info['familia'].split(' (')[0]} — {_resumo(info['problema'])}",
                            False)
        return fabrica

    def _proxima_da_fila(self):
        while self.pos < len(self.fila):
            pergunta = self.fila[self.pos]()
            self.pos += 1
            if pergunta:
                return pergunta
        return None

    def proxima_rodada(self):
        pergunta = self._proxima_da_fila()
        if pergunta is None:
            self.esgotado = self.refinar = True
            return False
        self.rodada += 1
        self.na_rodada, self.atual, self.refinar = 1, pergunta, False
        return True

    # ------------------------------------------------------------------ respostas
    def pergunta_atual(self):
        return None if self.refinar else self.atual

    def responder(self, texto):
        """Aplica a resposta. Devolve None se aceitou, ou a mensagem de erro (a pergunta se repete)."""
        bruto = (texto or "").strip()
        normal = gs.normalizar(bruto)
        if self.refinar:
            if self.esgotado:
                return "não há mais perguntas — gere com: sgs gerar -sp (ou sgs cancelar)"
            if normal in SIM:
                return None if self.proxima_rodada() else "não há mais perguntas — gere com: sgs gerar -sp"
            if normal in NAO:
                return "tudo bem — para gerar: sgs gerar -sp · para desistir: sgs cancelar"
            return "responda sim (mais perguntas) ou gere com: sgs gerar -sp"
        p = self.atual
        if normal in PADRAO:
            valor = p["padrao"]
        elif p["tipo"] == "sim_nao":
            if normal not in SIM | NAO:
                return "responda sim ou não (ou Enter para o padrão)"
            valor = normal in SIM
        elif p["tipo"] == "opcao":
            valor = tipos_campos.tipo_da_resposta(bruto) if p["chave"].startswith("tipo:") else None
            valor = valor or _escolher(p["opcoes"], bruto)
            chave_digitada = gs.normalizar(bruto).replace(" ", "_").replace("-", "_")
            if valor is _NADA and p["chave"] == "dominio" and chave_digitada in gs.DOMINIOS:
                valor = chave_digitada                # qualquer um dos 100, mesmo fora da lista mostrada
            if valor is _NADA:
                return f"escolha um número de 1 a {len(p['opcoes'])} (ou Enter para o padrão)"
        else:
            valor, erro = _validar_livre(p["chave"], bruto)
            if erro:
                return erro
        self._guardar(p["chave"], valor)
        self.respostas += 1
        if self.na_rodada >= POR_RODADA:
            self.refinar = True
            return None
        proxima = self._proxima_da_fila()
        if proxima is None:
            self.refinar = self.esgotado = True
        else:
            self.atual, self.na_rodada = proxima, self.na_rodada + 1
        return None

    def _guardar(self, chave, valor):
        if chave.startswith("tipo:"):           # tipo respondido: o campo deixa de ser duvidoso
            nome = chave.split(":", 1)[1]
            self.decisoes["campos"] = [tipos_campos.identificar(nome, valor) if c["nome"] == nome else c
                                       for c in self.decisoes["campos"]]
            return
        if chave == "dominio" and valor in gs.DOMINIOS:
            # Trocou de domínio: nome do sistema e entidade acompanham, se ainda eram os do domínio anterior.
            antes = gs.DOMINIOS[self.decisoes["dominio"]]
            for campo, chave_dom in (("sistema", "sistema"), ("entidade", "entidade")):
                if self.decisoes[campo] == antes[chave_dom]:
                    self.decisoes[campo] = gs.DOMINIOS[valor][chave_dom]
            self.decisoes["dominio"] = valor
            return
        if chave == "campos":                   # Enter (padrão "") = nenhum campo a mais
            self.decisoes["campos"] = valor or []
            return
        if chave.startswith("padrao:"):
            padrao = chave.split(":", 1)[1]
            if valor and padrao not in self.extras:
                self.extras.append(padrao)
            return
        self.decisoes[chave] = valor

    # ------------------------------------------------------------------ o que vai para o gerador
    def padroes_finais(self):
        d = self.decisoes
        base = self.detectados if d["padroes"] == "manter" else [d["padroes"]]
        return gs.normalizar_padroes(base + self.extras + (["state"] if d["estado"] else []))

    def argumentos(self):
        """Argumentos de processar()/gs.gerar() com as decisões tomadas até agora."""
        d = self.decisoes
        web = {k: d[k] for k in ("estilo", "tema", "tom", "paleta", "comentarios_web", "id_publico", "id_interno",
                                 "lnnl_tipo", "estrutura", "seguranca")}
        campos = [{"nome": c["nome"], "tipo": c["tipo"]} for c in d["campos"]]
        return dict(texto=self.pedido, dominio=d["dominio"], padroes=self.padroes_finais(), sistema=d["sistema"],
                    entidade=d["entidade"], django=d["django"], exercicio=d["exercicio"], testar=d["testar"],
                    estudo=d["estudo"], comentarios=d["comentarios"], web=web, campos=campos or None)

    def resumo(self):
        """Linhas [decisão, valor] para a tela."""
        d = self.decisoes
        sim = {True: "sim", False: "não"}
        linhas = [["pedido", self.pedido],
                  ["domínio / sistema / entidade", f"{d['dominio']} · {d['sistema']} · {d['entidade']}"],
                  ["padrões", f"{len(self.padroes_finais())}: " + ", ".join(self.padroes_finais())],
                  ["campos a mais", ", ".join(f"{c['nome']} ({tipos_campos.rotulo(c['tipo'])}"
                                              + (" — sugestão, não respondido" if c["certeza"] == "duvida" else "") + ")"
                                              for c in d["campos"]) or "nenhum (só os do domínio)"],
                  ["Django", sim[d["django"]]]]
        if d["django"]:
            estilo = d["estilo"] + (f" · {d['tema']} {temas_web.TEMAS[d['tema']]['nome']} · {temas_web.NOMES_TONS[d['tom']]}"
                                    + (f" · {d['paleta']}" if d["tema"] == "T10" else "") if d["estilo"] == "web" else "")
            linhas += [["estilo", estilo], ["notas de apresentação", sim[d["comentarios_web"]]],
                       ["identificador", d["id_publico"] + (f" + LNNL tipo {d['lnnl_tipo']}" if d["id_interno"] else "")],
                       ["estrutura / segurança", f"{d['estrutura']} · {d['seguranca']}"]]
        linhas += [["finalidade", "estudo" if d["estudo"] else "só gerar"], ["comentários no código", sim[d["comentarios"]]],
                   ["exercício / testes", f"{sim[d['exercicio']]} · {sim[d['testar']]}"]]
        if self.marcadas:
            linhas.append(["marcadas na tela (não perguntadas)", ", ".join(sorted(self.marcadas))])
        return linhas

    def rotulo(self):
        if self.refinar:
            return f"rodada {self.rodada} concluída · " + ("gerar?" if self.esgotado else "refinar?")
        return f"pergunta {self.na_rodada}/{POR_RODADA} · rodada {self.rodada}"


_NADA = object()


def _escolher(opcoes, bruto):
    if bruto.isdigit() and 1 <= int(bruto) <= len(opcoes):
        return opcoes[int(bruto) - 1][0]
    alvo = gs.normalizar(bruto)
    for valor, rotulo in opcoes:                        # 1º: o valor, a 1ª palavra ou o rótulo inteiro
        if alvo in (gs.normalizar(str(valor)), gs.normalizar(rotulo.split(" ")[0]), gs.normalizar(rotulo)):
            return valor
    for valor, rotulo in opcoes:                        # 2º: uma palavra do rótulo ("estudo", "profissional")
        if alvo in re.split(r"[^a-z0-9]+", gs.normalizar(rotulo.split(" — ")[0])):
            return valor
    return _NADA


def _validar_livre(chave, bruto):
    if chave == "campos":
        campos = tipos_campos.analisar(bruto) if bruto else []
        if bruto and not campos:
            return None, "campos: nomes separados por vírgula (ex.: nome, idade:int, vacinado) — ou Enter = nenhum"
        return campos, None
    if chave == "lnnl_tipo":
        if not re.fullmatch(r"[1-9]{2}", bruto) or bruto == "93":
            return None, "tipo LNNL: dois dígitos de 1 a 9 (11–99, sem zero), e nunca 93"
        return bruto, None
    if chave == "entidade":
        nome = gs.camel(bruto)
        if not nome.isidentifier() or not nome[0].isupper():
            return None, "entidade: um nome de classe (ex.: Reserva, PedidoCompra)"
        return nome, None
    if not bruto or gs.PROIBIDO_EM_TEXTO.search(bruto) or len(bruto) > 60:
        return None, "nome do sistema: texto de até 60 caracteres, sem aspas, chaves ou barra invertida"
    return bruto, None


def _resumo(texto, limite=150):
    texto = re.sub(r"`|@@\w+@@", "", texto)
    return texto if len(texto) <= limite else texto[:limite].rsplit(" ", 1)[0] + "…"


def blocos(q, erro=None):
    """O que a tela mostra para a pergunta atual (ou para o "refinar mais?")."""
    saida = []
    if erro:
        saida.append({"t": "texto", "texto": erro, "cor": "erro"})
    if q.refinar:
        saida += [{"t": "titulo", "texto": f"Rodada {q.rodada} concluída — decisões até aqui"},
                  {"t": "tabela", "colunas": ["decisão", "valor"], "linhas": q.resumo()}]
        if q.esgotado:
            saida += [{"t": "texto", "texto": "Não há mais perguntas. Gere com sgs gerar -sp (ou sgs cancelar)."},
                      {"t": "tabela", "colunas": [""], "linhas": [[{"texto": "sgs gerar -sp — gerar agora",
                                                                    "cmd": "sgs gerar -sp"}]]}]
        else:
            saida += [{"t": "texto", "texto": "Refinar ainda mais? sim = mais perguntas · sgs gerar -sp = gera agora · "
                                              "sgs cancelar = desiste"},
                      {"t": "tabela", "colunas": ["", ""], "linhas": [[{"texto": "sim — mais perguntas", "cmd": "sim"},
                                                                       {"texto": "sgs gerar -sp — gerar agora",
                                                                        "cmd": "sgs gerar -sp"}]]}]
        return saida
    p = q.pergunta_atual()
    saida.append({"t": "titulo", "texto": f"{q.rotulo()} — {p['titulo']}"})
    saida.append({"t": "texto", "texto": p["texto"]})
    if p["opcoes"]:
        linhas = [[{"texto": str(i), "cmd": str(i)}, rotulo + ("   ← padrão" if valor == p["padrao"] else "")]
                  for i, (valor, rotulo) in enumerate(p["opcoes"], 1)]
        saida.append({"t": "tabela", "colunas": ["nº", "opção"], "linhas": linhas})
    padrao = p["padrao"] if p["tipo"] != "sim_nao" else ("sim" if p["padrao"] else "não")
    if p["tipo"] == "opcao":
        padrao = next(r for v, r in p["opcoes"] if v == p["padrao"]).split(" — ")[0]
    saida.append({"t": "texto", "cor": "suave",
                  "texto": f"Enter = padrão ({padrao}) · sgs gerar -sp = para de perguntar e gera · sgs cancelar = desiste"})
    return saida

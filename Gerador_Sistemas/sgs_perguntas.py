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

INCREMENTO (sgs app NN <pedido>, QuestionarioModulo): que funcionalidade é (o nome da classe, pelo contexto:
Destino, Voo…) → versão nova ou editar o próprio NN (sem versão) → ligação com uma classe que já existe
(Viagcert.destino → Destino) e o nome do campo → campos e tipos → padrões → estado → domínio. sgs app -sp aplica.

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

    comando = "sgs gerar"           # o comando que encerra as perguntas (com -sp)

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
        sp = f"{self.comando} -sp"
        if self.refinar:
            if self.esgotado:
                return f"não há mais perguntas — gere com: {sp} (ou sgs cancelar)"
            if normal in SIM:
                return None if self.proxima_rodada() else f"não há mais perguntas — gere com: {sp}"
            if normal in NAO:
                return f"tudo bem — para gerar: {sp} · para desistir: sgs cancelar"
            return f"responda sim (mais perguntas) ou gere com: {sp}"
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
            valor, erro = self._validar(p["chave"], bruto)
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

    def _validar(self, chave, bruto):
        return _validar_livre(chave, bruto)

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


NOVA = "*"          # nas opções de ligação, "*" é a classe NOVA (o nome dela só existe depois da 1ª pergunta)


class QuestionarioModulo(Questionario):
    """Perguntas do INCREMENTO (sgs app NN <pedido>): o que é a funcionalidade nova, conforme o contexto (Destino,
    Voo, Horario…), se vira uma VERSÃO ou edita o próprio sistema, se ganha um campo de referência para uma classe
    que já existe (ex.: Viagcert.destino → Destino), os campos e os padrões. Termina com sgs app -sp.

    As opções do sistema (estilo, tema, estudo, comentários…) vêm do próprio sistema: não são perguntadas.
    """

    comando = "sgs app"

    def __init__(self, pedido, config, projeto, numero, marcadas=(), sem_versao=False, entidade=None, padroes=None,
                 ligar=None):
        self.pedido = pedido
        self.projeto = projeto
        self.numero = numero
        self.marcadas = {c for c in marcadas if c in CAIXAS}
        self.existentes = gs.entidades_do_projeto(projeto)          # {Classe: {"app", …}} que o sistema já tem
        analise = gs.analisar_assunto(pedido)
        dominio = analise["dominio"]
        self.detectados = padroes or analise["padroes"] or ["strategy"]    # módulo: só o que o pedido pedir
        self.campos_do_pedido = bool(analise["campos"])
        nome = gs.camel(entidade) if entidade else (gs.nome_do_pedido(pedido) or gs.DOMINIOS[dominio]["entidade"])
        self.decisoes = {
            "entidade": nome, "versao": "editar" if sem_versao else "versao", "ligar": "nao", "campo_ligacao": "",
            "dominio": dominio, "sistema": gs.DOMINIOS[dominio]["sistema"], "padroes": "manter", "estado": False,
            "testar": config["testar"], "campos": tipos_campos.analisar(analise["campos"]),
        }
        if ligar:                                                   # ligar=Classe.campo[:Alvo] já veio no comando
            m = re.fullmatch(r"(\w+)\.(\w+)(?::(\w+))?", ligar)
            if m:
                origem, campo, alvo = m.group(1), m.group(2), m.group(3)
                self.decisoes["ligar"] = f"{gs.achar_classe(self.existentes, origem) or NOVA}>" + \
                    (NOVA if not alvo or gs.camel(alvo) == nome else (gs.achar_classe(self.existentes, alvo) or alvo))
                self.decisoes["campo_ligacao"] = campo
        for caixa in self.marcadas:
            self.decisoes[caixa] = True
        self.extras = []
        self.fila = self._fila()
        self.pos = self.rodada = self.na_rodada = self.respostas = 0
        self.atual, self.refinar, self.esgotado = None, False, False
        self.proxima_rodada()

    # ------------------------------------------------------------------ a fila
    def _fila(self):
        d = self.decisoes

        def caixa(chave, fabrica):
            return lambda: None if chave in self.marcadas else fabrica()

        n = self.numero
        fila = [
            lambda: _livre("entidade", "Funcionalidade nova",
                           "Que funcionalidade é esta (o nome da classe nova)? Depende do contexto: Destino, Voo, "
                           f"Horario… Pelo pedido: {d['entidade']}. Classes que o sistema {n} já tem: "
                           f"{', '.join(sorted(self.existentes)) or 'nenhuma'}.", d["entidade"]),
            lambda: _opcao("versao", "Versão ou edição", f"Criar uma VERSÃO nova (cópia {n}.k — o {n} não muda) ou "
                           f"EDITAR o próprio {n}, sem versionar?",
                           [("versao", f"versão nova (cópia {n}.k)"), ("editar", f"editar o próprio {n} (sem versão)")],
                           d["versao"]),
            lambda: _opcao("ligar", "Ligação", f"Ligar a {d['entidade']} a uma classe que já existe? (um campo de "
                           "referência: aparece no formulário e na API REST; opcional)", self._opcoes_ligar(), d["ligar"]),
            lambda: None if d["ligar"] == "nao" else _livre(
                "campo_ligacao", "Nome do campo", f"Nome do campo de referência em {self._classe_origem()}? "
                f"(aponta para {self._classe_alvo()})", d["campo_ligacao"] or self._campo_padrao()),
            lambda: None if self.campos_do_pedido else _livre(
                "campos", "Campos", f"Campos a mais na {d['entidade']}, além dos do domínio "
                f"({', '.join(a['nome'] for a in gs.DOMINIOS[d['dominio']]['atributos'])})? Separe por vírgula; o tipo "
                "pode ir junto (idade:int) ou fica por conta do identificador. Enter = nenhum.", ""),
            *[self._pergunta_tipo(i) for i in range(MAX_CAMPOS)],
            lambda: _opcao("padroes", "Padrões", f"Padrões de projeto da {d['entidade']}? O pedido indicou: "
                           f"{', '.join(self.detectados)} (o Strategy entra sempre: o Service da app usa).",
                           [("manter", "manter o que o pedido indicou"), ("strategy", "só o Strategy"),
                            ("prova", "os 9 da prova (P3)"), ("criacao", "GoF · criação"),
                            ("estrutural", "GoF · estruturais"), ("comportamental", "GoF · comportamentais")],
                           d["padroes"]),
            lambda: _sim_nao("estado", "Máquina de estados",
                             f"Incluir uma máquina de estados (padrão State) para o ciclo de vida da {d['entidade']}?",
                             d["estado"]),
            lambda: _opcao("dominio", "Domínio base",
                           f"Domínio base da {d['entidade']} (atributos, regras e exemplos)? Os que o pedido mais "
                           f"pontuou; dá para digitar qualquer um dos {len(gs.DOMINIOS)}.", self._opcoes_dominio(),
                           d["dominio"]),
            caixa("testar", lambda: _sim_nao("testar", "Testes", "Rodar os testes do sistema depois de acrescentar?",
                                             d["testar"])),
        ]
        return fila + [self._pergunta_padrao(p) for p in gs.ORDEM_PADROES]

    def _opcoes_ligar(self):
        nova = self.decisoes["entidade"]
        opcoes = [("nao", "não ligar")]
        for classe in sorted(self.existentes):
            opcoes.append((f"{classe}>{NOVA}", f"{classe}.{gs.camel_para_snake(nova)} → {nova}  (a {classe} ganha a "
                                               f"referência para a {nova})"))
            opcoes.append((f"{NOVA}>{classe}", f"{nova}.{gs.camel_para_snake(classe)} → {classe}  (a {nova} aponta "
                                               f"para a {classe})"))
        atual = self.decisoes["ligar"]
        if atual != "nao" and atual not in [v for v, _ in opcoes]:
            opcoes.append((atual, atual.replace(NOVA, nova).replace(">", " → ")))
        return opcoes

    def _classe_origem(self):
        origem = self.decisoes["ligar"].split(">")[0]
        return self.decisoes["entidade"] if origem == NOVA else origem

    def _classe_alvo(self):
        alvo = self.decisoes["ligar"].split(">")[-1]
        return self.decisoes["entidade"] if alvo == NOVA else alvo

    def _campo_padrao(self):
        return gs.camel_para_snake(self._classe_alvo())

    def _validar(self, chave, bruto):
        if chave == "entidade":
            valor, erro = _validar_livre(chave, bruto)
            if erro:
                return valor, erro
            if gs.plural(gs.camel_para_snake(valor)) in {info["app"] for info in self.existentes.values()} \
                    or valor in self.existentes:
                return None, f"o sistema {self.numero} já tem a classe {valor} — dê outro nome à funcionalidade nova"
            return valor, None
        if chave == "campo_ligacao":
            nome = gs.camel_para_snake(gs.camel(bruto))
            if not re.fullmatch(r"[a-z][a-z0-9_]*", nome) or nome in gs.RESERVADOS or nome in gs.RESERVADOS_DJANGO:
                return None, "nome do campo: letras, números e _ (ex.: destino, destino_ref)"
            return nome, None
        return super()._validar(chave, bruto)

    def _guardar(self, chave, valor):
        if chave == "ligar" and valor != self.decisoes["ligar"]:
            self.decisoes["campo_ligacao"] = ""          # a ligação mudou: o nome do campo volta ao padrão
        super()._guardar(chave, valor)
        if chave == "ligar" and valor != "nao" and not self.decisoes["campo_ligacao"]:
            self.decisoes["campo_ligacao"] = self._campo_padrao()

    # ------------------------------------------------------------------ o que vai para o gerador
    def argumentos(self):
        d = self.decisoes
        ligar = None
        if d["ligar"] != "nao":
            ligar = (self._classe_origem(), d["campo_ligacao"] or self._campo_padrao(), self._classe_alvo())
        return dict(pedido=self.pedido, entidade=d["entidade"], dominio=d["dominio"], padroes=self.padroes_finais(),
                    campos=[{"nome": c["nome"], "tipo": c["tipo"]} for c in d["campos"]] or None,
                    sem_versao=d["versao"] == "editar", ligar=ligar, testar=d["testar"])

    def resumo(self):
        d = self.decisoes
        ligar = self.argumentos()["ligar"]
        return [["pedido", self.pedido],
                ["funcionalidade nova", f"{d['entidade']} (app {gs.plural(gs.camel_para_snake(d['entidade']))})"],
                ["onde", f"editar o próprio {self.numero} (sem versão)" if d["versao"] == "editar"
                 else f"versão nova do {self.numero} (cópia)"],
                ["ligação", f"{ligar[0]}.{ligar[1]} → {ligar[2]}" if ligar else "nenhuma"],
                ["campos a mais", ", ".join(f"{c['nome']} ({tipos_campos.rotulo(c['tipo'])})" for c in d["campos"])
                 or "nenhum (só os do domínio)"],
                ["padrões", f"{len(self.padroes_finais())}: " + ", ".join(self.padroes_finais())],
                ["domínio base", d["dominio"]],
                ["testes", "sim" if d["testar"] else "não"]]


NOVO = "__novo__"   # na pergunta do campo: um campo que ainda não existe
REGRAS = [           # (chave, rótulo, o que pede depois) — o padrão do campo no sgs incrementar
    ("texto", "texto obrigatório (vazio é recusado)", None),
    ("texto-livre", "texto opcional, sem regra", None),
    ("inteiro>=", "inteiro com MÍNIMO (negativo e letras são recusados)", "minimo"),
    ("inteiro:", "inteiro numa FAIXA (mínimo..máximo)", "faixa"),
    ("decimal>=", "decimal com MÍNIMO", "minimo"),
    ("decimal:", "decimal numa FAIXA", "faixa"),
    ("lista:", "LISTA fechada de valores (só eles entram)", "lista"),
    ("simnao", "sim/não (True/False)", None),
    ("data", "data AAAA-MM-DD", None),
]


def _chave_da_regra(texto):
    """"inteiro>=0" → ("inteiro>=", "0") · "lista:a,b" → ("lista:", "a,b") · "texto" → ("texto", "")."""
    for apelido, chave in (("int>=", "inteiro>="), ("int:", "inteiro:"), ("faixa:", "inteiro:"),
                           ("float>=", "decimal>="), ("float:", "decimal:"), ("opcoes:", "lista:"), ("valores:", "lista:")):
        if texto.startswith(apelido):
            texto = chave + texto[len(apelido):]
    for chave, _, _ in REGRAS:
        if chave.endswith((">=", ":")) and texto.startswith(chave):
            return chave, texto[len(chave):]
    return (texto, "") if texto in {c for c, _, _ in REGRAS} else ("texto", "")


class QuestionarioIncremento(Questionario):
    """Perguntas do sgs incrementar NN: a CLASSE, o CAMPO (um que existe ou um novo), o PADRÃO dele (a regra que o
    @property do núcleo e o model do Django passam a exigir: mínimo, faixa, lista fechada…), o valor da regra e se
    vira versão ou edita o próprio sistema. Termina com sgs incrementar -sp."""

    comando = "sgs incrementar"

    def __init__(self, projeto, numero, classes, classe=None, campo=None, regra=None, sem_versao=False):
        self.pedido = f"sgs incrementar {numero}"
        self.projeto, self.numero, self.classes = projeto, numero, classes
        self.marcadas, self.extras = set(), []
        nome_classe = gs.achar_classe(classes, classe) or sorted(classes)[0]
        campo = gs.camel_para_snake(gs.camel(campo)) if campo else ""
        existe = any(a["nome"] == campo for a in classes[nome_classe]["atributos"])
        chave, parametro = _chave_da_regra(gs.normalizar(regra or "").replace(" ", "")) if regra else ("", "")
        if regra and chave == "lista:":
            parametro = regra.split(":", 1)[1]                # a lista com as maiúsculas e acentos digitados
        self.decisoes = {"classe": nome_classe, "campo": campo if existe else NOVO, "nome_novo": "" if existe else campo,
                         "regra": chave, "parametro": parametro, "versao": "editar" if sem_versao else "versao"}
        self.fila = self._fila()
        self.pos = self.rodada = self.na_rodada = self.respostas = 0
        self.atual, self.refinar, self.esgotado = None, False, False
        self.proxima_rodada()

    def _atributo_atual(self):
        d = self.decisoes
        return next((a for a in self.classes[d["classe"]]["atributos"] if a["nome"] == d["campo"]), None)

    def _fila(self):
        d = self.decisoes
        n = self.numero
        return [
            lambda: _opcao("classe", "Classe", f"Em qual classe do sistema {n}?",
                           [(c, f"{c}" + (" (a principal)" if i["principal"] else f" (módulo {i['app']})"))
                            for c, i in sorted(self.classes.items())], d["classe"]),
            lambda: _opcao("campo", "Campo", f"Qual campo da {d['classe']}? Um que já existe (MODIFICAR a regra) ou um "
                           "NOVO (incrementar a classe).",
                           [(a["nome"], f"{a['nome']} — hoje: {gs.regra_em_texto(a)}")
                            for a in self.classes[d["classe"]]["atributos"]] + [(NOVO, "um campo NOVO")],
                           d["campo"]),
            lambda: None if d["campo"] != NOVO else _livre(
                "nome_novo", "Nome do campo novo", f"Nome do campo novo na {d['classe']} (ex.: assento, codigo_voo)?",
                d["nome_novo"]),
            lambda: _opcao("regra", "Padrão do campo", "Que padrão o campo segue? Ele vale no @property do núcleo "
                           "(a “fechadura” do setter) e no model/form do Django.",
                           [(c, r) for c, r, _ in REGRAS], d["regra"] or self._regra_atual()[0]),
            lambda: self._pergunta_parametro(),
            lambda: _opcao("versao", "Versão ou edição", f"Criar uma VERSÃO nova (cópia {n}.k — o {n} não muda) ou "
                           f"EDITAR o próprio {n}, sem versionar?",
                           [("versao", f"versão nova (cópia {n}.k)"), ("editar", f"editar o próprio {n} (sem versão)")],
                           d["versao"]),
        ]

    def _regra_atual(self):
        a = self._atributo_atual()
        return _chave_da_regra(gs.regra_em_texto(a)) if a else ("texto", "")

    def _pergunta_parametro(self):
        d = self.decisoes
        pede = next(p for c, _, p in REGRAS if c == d["regra"])
        if pede is None:
            return None
        chave_atual, valor_atual = self._regra_atual()
        padrao = d["parametro"] or (valor_atual if chave_atual == d["regra"] else "")
        texto = {"minimo": "Valor MÍNIMO (ex.: 0 — aí negativo é recusado)?",
                 "faixa": "FAIXA mínimo..máximo (ex.: 1..30)?",
                 "lista": "Os valores da LISTA, separados por vírgula (ex.: janela, meio, corredor · ou 1, 2, 3)?"}[pede]
        return _livre("parametro", "Valor da regra", texto, padrao or {"minimo": "0", "faixa": "1..30"}.get(pede, ""))

    def _validar(self, chave, bruto):
        if chave == "nome_novo":
            nome = gs.camel_para_snake(gs.camel(bruto))
            if not re.fullmatch(r"[a-z][a-z0-9_]*", nome) or nome in gs.RESERVADOS or nome in gs.RESERVADOS_DJANGO:
                return None, "nome do campo: letras, números e _ (ex.: assento, codigo_voo)"
            if any(a["nome"] == nome for a in self.classes[self.decisoes["classe"]]["atributos"]):
                return None, f"a {self.decisoes['classe']} já tem o campo {nome} — escolha ele na pergunta anterior"
            return nome, None
        if chave == "parametro":
            try:
                gs.ler_regra(self.decisoes["regra"] + bruto)
            except gs.ErroGerador as erro:
                return None, str(erro)
            return bruto, None
        return super()._validar(chave, bruto)

    def _guardar(self, chave, valor):
        if chave == "classe" and valor != self.decisoes["classe"]:
            self.decisoes.update(campo=NOVO, nome_novo="", regra="", parametro="")
        if chave in ("campo", "regra") and valor != self.decisoes[chave]:
            self.decisoes["parametro"] = ""                 # mudou o campo ou a regra: o valor volta ao padrão
        self.decisoes[chave] = valor

    def argumentos(self):
        d = self.decisoes
        pede = next(p for c, _, p in REGRAS if c == (d["regra"] or self._regra_atual()[0]))
        regra = (d["regra"] or self._regra_atual()[0]) + (d["parametro"] or (self._regra_atual()[1] if pede else ""))
        return dict(classe=d["classe"], campo=d["nome_novo"] if d["campo"] == NOVO else d["campo"], regra=regra,
                    sem_versao=d["versao"] == "editar")

    def resumo(self):
        a = self.argumentos()
        return [["classe", a["classe"]],
                ["campo", f"{a['campo'] or '(falta o nome)'} — " + ("NOVO" if self.decisoes["campo"] == NOVO else "modificar")],
                ["padrão (regra)", a["regra"]],
                ["onde", f"editar o próprio {self.numero} (sem versão)" if a["sem_versao"]
                 else f"versão nova do {self.numero} (cópia)"]]


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
    sp = f"{q.comando} -sp"
    if erro:
        saida.append({"t": "texto", "texto": erro, "cor": "erro"})
    if q.refinar:
        saida += [{"t": "titulo", "texto": f"Rodada {q.rodada} concluída — decisões até aqui"},
                  {"t": "tabela", "colunas": ["decisão", "valor"], "linhas": q.resumo()}]
        if q.esgotado:
            saida += [{"t": "texto", "texto": f"Não há mais perguntas. Gere com {sp} (ou sgs cancelar)."},
                      {"t": "tabela", "colunas": [""], "linhas": [[{"texto": f"{sp} — gerar agora", "cmd": sp}]]}]
        else:
            saida += [{"t": "texto", "texto": f"Refinar ainda mais? sim = mais perguntas · {sp} = gera agora · "
                                              "sgs cancelar = desiste"},
                      {"t": "tabela", "colunas": ["", ""], "linhas": [[{"texto": "sim — mais perguntas", "cmd": "sim"},
                                                                       {"texto": f"{sp} — gerar agora", "cmd": sp}]]}]
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
                  "texto": f"Enter = padrão ({padrao}) · {sp} = para de perguntar e gera · sgs cancelar = desiste"})
    return saida

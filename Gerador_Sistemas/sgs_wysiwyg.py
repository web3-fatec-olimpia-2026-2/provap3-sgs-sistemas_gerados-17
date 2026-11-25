#!/usr/bin/env python3
"""
sgs_wysiwyg.py — Modo WYSIWYG (bancada em colunas de encaixe de blocos) para o SGS.

Tela inicial padrão do SGS (`/` e `/wysiwyg`), com alternância direta `WYSIWYG <-> CMD` (`/cmd`):
  - Expõe os dados estruturados do catálogo (300 domínios, 28 padrões, grupos mutuamente excludentes,
    10 temas x 6 tons de temas_web.py e projetos já gerados com classes, campos, ligações FK e API).
  - Toda ação de criação/edição (Gerar, Prova P3, Editar, Nova Classe/App, Incrementar Campo,
    Ligar Classes, Configurar API, Duplicar, Testar, Rodar, Parar, Novo Domínio) executa o MESMO
    motor `tela_prompt.executar_linha()` por baixo — garantindo 100% de consistência com o CMD e
    exibindo ao vivo o comando `sgs ...` equivalente.
"""
import json
from pathlib import Path

import dominios as dom
import gerar_sistema as gs
import temas_web


# =============================================================================
# 1. GRUPOS MUTUAMENTE EXCLUDENTES DE PADRÕES DE PROJETO (por papel arquitetural)
# =============================================================================
GRUPOS_EXCLUDENTES = [
    {
        "id": "variacao_algoritmo",
        "titulo": "Variação de Algoritmo / Regra",
        "motivo": "Strategy varia o algoritmo por composição em tempo de execução; Template Method fixa o esqueleto por herança.",
        "membros": ["strategy", "template_method"],
    },
    {
        "id": "criacao_objetos",
        "titulo": "Fábrica / Construção de Objetos",
        "motivo": "Escolha uma estratégia de criação: Factory Method (subclasse), Abstract Factory (famílias) ou Builder (passo a passo).",
        "membros": ["factory_method", "abstract_factory", "builder"],
    },
    {
        "id": "fluxo_decisao",
        "titulo": "Fluxo de Estado vs Cadeia de Aprovação",
        "motivo": "State altera o comportamento pelo estado interno; Chain of Responsibility encaminha pela cadeia de tratadores.",
        "membros": ["state", "chain"],
    },
    {
        "id": "historico_acoes",
        "titulo": "Histórico / Desfazer (Undo)",
        "motivo": "Command encapsula ações reversíveis; Memento salva retratos completos de estado.",
        "membros": ["command", "memento"],
    },
    {
        "id": "camada_apresentacao",
        "titulo": "Camada de Orquestração / Apresentação",
        "motivo": "Escolha entre a camada tradicional de Service (MVC/MVT) ou o ViewModel do padrão MVVM.",
        "membros": ["service", "mvvm"],
    },
    {
        "id": "intermediacao_objeto",
        "titulo": "Intermediação / Fachada / Proxy",
        "motivo": "Adapter traduz interface externa; Proxy controla acesso/cache na mesma interface; Facade unifica subsistemas.",
        "membros": ["adapter", "proxy", "facade"],
    },
    {
        "id": "extensao_estrutura",
        "titulo": "Extensão de Comportamento",
        "motivo": "Decorator empilha responsabilidades em torno do objeto; Visitor separa operações externas sobre a hierarquia.",
        "membros": ["decorator", "visitor"],
    },
    {
        "id": "comunicacao_objetos",
        "titulo": "Comunicação entre Objetos",
        "motivo": "Observer notifica inscritos 1->N de forma desacoplada; Mediator centraliza a coordenação N<->N.",
        "membros": ["observer", "mediator"],
    },
    {
        "id": "instancia_vs_clonagem",
        "titulo": "Instância Única vs Clonagem",
        "motivo": "Singleton garante instância única compartilhada; Prototype cria novas instâncias clonando um modelo.",
        "membros": ["singleton", "prototype"],
    },
]

CATEGORIAS_CAMPO_PALETA = [
    {
        "id": "primitivos",
        "titulo": "1 · Primitivos (Básicos)",
        "sub": "Armazenam um único dado simples diretamente na entidade.",
        "itens": [
            {"id": "obrigatorio", "rotulo": "Texto Curto", "tipo": "str", "regra": "texto",
             "exemplo": "texto", "desc": "Texto curto obrigatório até 120 chars (@property + CharField)"},
            {"id": "livre", "rotulo": "Texto Livre", "tipo": "str", "regra": "texto-livre",
             "exemplo": "texto-livre", "desc": "Texto curto opcional, sem regra (atributo simples)"},
            {"id": "texto_longo", "rotulo": "Texto Longo", "tipo": "str", "regra": "texto-longo",
             "exemplo": "texto-longo", "desc": "Descrições detalhadas / memo obrigatório (TextField + Textarea)"},
            {"id": "int_min", "rotulo": "Inteiro >= 0", "tipo": "int", "regra": "inteiro>=0",
             "exemplo": "inteiro>=0", "desc": "Número inteiro com valor mínimo (IntegerField)"},
            {"id": "int_faixa", "rotulo": "Inteiro (Faixa)", "tipo": "int", "regra": "inteiro:1..100",
             "exemplo": "inteiro:1..100", "desc": "Número inteiro limitado entre mínimo e máximo"},
            {"id": "decimal", "rotulo": "Decimal >= 0", "tipo": "float", "regra": "decimal>=0",
             "exemplo": "decimal>=0", "desc": "Número decimal / ponto flutuante com mínimo (DecimalField)"},
            {"id": "decimal_faixa", "rotulo": "Decimal (Faixa)", "tipo": "float", "regra": "decimal:0..100",
             "exemplo": "decimal:0..100", "desc": "Decimal limitado entre mínimo e máximo (ex.: percentual)"},
            {"id": "booleano", "rotulo": "Booleano", "tipo": "bool", "regra": "simnao",
             "exemplo": "simnao", "desc": "Verdadeiro/Falso, Sim/Não (BooleanField / checkbox)"},
            {"id": "data", "rotulo": "Data", "tipo": "data", "regra": "data",
             "exemplo": "data", "desc": "Dia, mês e ano no formato ISO AAAA-MM-DD (DateField)"},
            {"id": "data_hora", "rotulo": "Data e Hora", "tipo": "data_hora", "regra": "data-hora",
             "exemplo": "data-hora", "desc": "Data e hora exatas AAAA-MM-DDTHH:MM (DateTimeField + datetime-local)"},
        ],
    },
    {
        "id": "selecao",
        "titulo": "2 · Seleção e Relação",
        "sub": "Opções fechadas, múltiplas etiquetas ou chave estrangeira (FK).",
        "itens": [
            {"id": "lista", "rotulo": "Lista Única", "tipo": "str", "regra": "lista:baixo,medio,alto",
             "exemplo": "lista:baixo,medio,alto", "desc": "Seleção única entre lista fechada (Enum / choices)"},
            {"id": "multipla", "rotulo": "Múltipla Escolha", "tipo": "str", "regra": "multipla:urgente,vip,recorrente",
             "exemplo": "multipla:urgente,vip,recorrente", "desc": "Vários valores simultâneos / tags validadas por vírgula"},
            {"id": "relacionamento", "rotulo": "Relacionamento (FK)", "tipo": "fk", "regra": "__ligar__",
             "acao": "ligar", "exemplo": "sgs ligar",
             "desc": "Chave estrangeira (Lookup / ForeignKey) vinculando a outra classe do sistema"},
        ],
    },
    {
        "id": "negocio",
        "titulo": "3 · Formatados e Negócio",
        "sub": "Moeda, contato web e documentos brasileiros com validação real.",
        "itens": [
            {"id": "moeda", "rotulo": "Moeda (BRL)", "tipo": "float", "regra": "moeda",
             "exemplo": "moeda", "desc": "Valor monetário BRL >= 0 com precisão fixa (Decimal 12,2)"},
            {"id": "email", "rotulo": "E-mail", "tipo": "str", "regra": "email",
             "exemplo": "email", "desc": "Endereço de e-mail com validação de sintaxe (EmailField)"},
            {"id": "telefone", "rotulo": "Telefone", "tipo": "str", "regra": "telefone",
             "exemplo": "telefone", "desc": "Telefone brasileiro validado (10 ou 11 dígitos, aceita máscara)"},
            {"id": "url", "rotulo": "URL / Link", "tipo": "str", "regra": "url",
             "exemplo": "url", "desc": "Endereço web http:// ou https:// validado (URLField)"},
            {"id": "cpf", "rotulo": "CPF", "tipo": "str", "regra": "cpf",
             "exemplo": "cpf", "desc": "CPF com 11 dígitos e validação real dos dígitos verificadores"},
            {"id": "cnpj", "rotulo": "CNPJ", "tipo": "str", "regra": "cnpj",
             "exemplo": "cnpj", "desc": "CNPJ com 14 dígitos e validação real dos dígitos verificadores"},
            {"id": "cep", "rotulo": "CEP", "tipo": "str", "regra": "cep",
             "exemplo": "cep", "desc": "CEP brasileiro validado (00000-000 ou 8 dígitos)"},
        ],
    },
    {
        "id": "estruturados",
        "titulo": "4 · Estruturados e Mídia",
        "sub": "Referências de mídia, coordenadas, JSON dinâmico e propriedades calculadas.",
        "itens": [
            {"id": "arquivo", "rotulo": "Arquivo / Anexo", "tipo": "str", "regra": "arquivo",
             "exemplo": "arquivo", "desc": "Caminho ou URL de documento/anexo com extensão (.pdf, .xlsx, .docx...)"},
            {"id": "imagem", "rotulo": "Imagem", "tipo": "str", "regra": "imagem",
             "exemplo": "imagem", "desc": "Caminho ou URL de imagem (.png, .jpg, .webp, .gif, .svg)"},
            {"id": "geolocalizacao", "rotulo": "Geolocalização", "tipo": "str", "regra": "geolocalizacao",
             "exemplo": "geolocalizacao", "desc": "Coordenadas latitude,longitude (-90..90, -180..180)"},
            {"id": "json", "rotulo": "JSON Dinâmico", "tipo": "json", "regra": "json",
             "exemplo": "json", "desc": "Objeto ou lista JSON estruturada (dict/list no núcleo + JSONField no Django)"},
            {"id": "calculado", "rotulo": "Calculado (@property)", "tipo": "calc", "regra": "__calculado__",
             "acao": "calculado", "exemplo": "@property",
             "desc": "Campos derivados (total, valor_final) já são gerados como @property somente leitura"},
        ],
    },
]

REGRAS_CAMPO_PALETA = [
    {**item, "categoria": cat["id"], "categoria_titulo": cat["titulo"]}
    for cat in CATEGORIAS_CAMPO_PALETA
    for item in cat["itens"]
]

_SUBST_PLACEHOLDERS = {
    "@@ENT@@": "Entidade",
    "@@ENTVAR@@": "entidade",
    "@@IDENT@@": "cliente",
    "@@QTD@@": "quantidade",
    "@@PRECO@@": "preco",
    "@@CONCEITO@@": "tipo de regra",
    "@@CATBASE@@": "CategoriaBase",
    "@@GATEWAY@@": "GatewayExterno",
    "@@E1@@": "extra_1",
    "@@E2@@": "extra_2",
    "@@ZERO@@": "sem disponibilidade",
}

_RAIOS_PX = {"reto": "2px", "suave": "6px", "arredondado": "10px", "pilula": "12px"}


def _limpar_placeholders(texto):
    """Substitui marcadores @@...@@ dos textos didáticos de PADROES por termos legíveis."""
    out = str(texto or "")
    for token, subst in _SUBST_PLACEHOLDERS.items():
        if token in out:
            out = out.replace(token, subst)
    return out


def resolver_tema_wysiwyg(tema="T09", tom="escuro", paleta="P01"):
    """Resolve qualquer um dos 10 temas x 6 tons (e P01-P20 no T10) para a interface WYSIWYG.

    Escala calibrada sem opacidade lavada:
      - claro / tom2 / tom3: progressão clara e nítida no matiz do tema (ou da paleta no T10)
      - tom4: escuro médio nítido
      - tom5: escuro profundo colorido no matiz do tema (ou da paleta no T10)
      - escuro: preto estilo CMD (#0C0C0C), com colunas #111111, cartões #161616 e destaque do tema/paleta
    """
    if tema not in temas_web.TEMAS:
        tema = "T09"
    if tom not in temas_web.TONS:
        tom = "escuro"
    if paleta not in temas_web.PALETAS:
        paleta = "P01"
    t = temas_web.resolver(tema, tom, paleta)
    if tema == "T10":
        _, pal_fundo, pal_dest, pal_esc = temas_web.PALETAS[paleta]
        if temas_web.luminancia(pal_fundo) < 0.2:
            base_claro = temas_web.misturar("#FFFFFF", pal_dest, 0.10)
            base_esc = pal_fundo
            base_esc_sup = temas_web.misturar(pal_fundo, "#FFFFFF", 0.10)
            base_tom5 = temas_web.misturar(pal_fundo, pal_dest, 0.24)
        else:
            base_claro = pal_fundo
            base_esc = temas_web.misturar(pal_esc, "#0C0C0C", 0.30)
            base_esc_sup = temas_web.misturar(pal_esc, pal_dest, 0.18)
            base_tom5 = temas_web.misturar(pal_esc, pal_dest, 0.30)
    else:
        base_claro = temas_web._FUNDOS[tema][0][0]
        base_tom5 = temas_web._FUNDOS[tema][4][0]
        base_esc = temas_web._FUNDOS[tema][5][0]
        base_esc_sup = temas_web._FUNDOS[tema][5][1]

    if tom == "claro":
        escuro = False
        fundo = base_claro
        bg_col = temas_web.misturar(base_claro, "#000000", 0.03)
        card = "#FFFFFF"
        card_hover = temas_web.misturar(base_claro, "#000000", 0.05)
        input_bg = "#FFFFFF"
        border = temas_web.misturar(base_claro, "#000000", 0.16)
        border_strong = temas_web.misturar(base_claro, "#000000", 0.30)
        text = "#1E1E1E"
        title = "#0D0D0D"
        muted = "#555555"
    elif tom == "tom2":
        escuro = False
        fundo = temas_web.misturar(base_claro, base_esc, 0.09)
        bg_col = temas_web.misturar(base_claro, base_esc, 0.05)
        card = "#FFFFFF"
        card_hover = temas_web.misturar(base_claro, base_esc, 0.07)
        input_bg = "#FAFAFA"
        border = temas_web.misturar(fundo, "#000000", 0.18)
        border_strong = temas_web.misturar(fundo, "#000000", 0.34)
        text = "#1B1B1B"
        title = "#0A0A0A"
        muted = "#4F4F4F"
    elif tom == "tom3":
        escuro = False
        fundo = temas_web.misturar(base_claro, base_esc, 0.22)
        bg_col = temas_web.misturar(base_claro, base_esc, 0.14)
        card = temas_web.misturar(base_claro, base_esc, 0.06)
        card_hover = temas_web.misturar(base_claro, base_esc, 0.11)
        input_bg = "#F7F7F7"
        border = temas_web.misturar(fundo, "#000000", 0.24)
        border_strong = temas_web.misturar(fundo, "#000000", 0.40)
        text = "#161616"
        title = "#080808"
        muted = "#424242"
    elif tom == "tom4":
        escuro = True
        # Escuro médio sólido (sem aparência cinza lavada)
        fundo = temas_web.misturar(base_tom5, "#181818", 0.48)
        bg_col = temas_web.misturar(fundo, "#FFFFFF", 0.05)
        card = temas_web.misturar(fundo, "#FFFFFF", 0.10)
        card_hover = temas_web.misturar(fundo, "#FFFFFF", 0.15)
        input_bg = temas_web.misturar(fundo, "#000000", 0.18)
        border = temas_web.misturar(card, "#FFFFFF", 0.16)
        border_strong = temas_web.misturar(card, "#FFFFFF", 0.28)
        text = "#E0E0E0"
        title = "#F5F5F5"
        muted = "#B0B0B0"
    elif tom == "tom5":
        escuro = True
        # Escuro profundo no matiz do tema (onde ficava o antigo Escuro)
        fundo = temas_web.misturar(base_esc, "#0C0C0C", 0.20)
        bg_col = temas_web.misturar(base_esc, base_esc_sup, 0.35)
        card = temas_web.misturar(base_esc_sup, "#0C0C0C", 0.18)
        card_hover = temas_web.misturar(card, "#FFFFFF", 0.08)
        input_bg = temas_web.misturar(fundo, "#000000", 0.22)
        border = temas_web.misturar(card, "#FFFFFF", 0.14)
        border_strong = temas_web.misturar(card, "#FFFFFF", 0.26)
        text = "#D8D8D8"
        title = "#F2F2F2"
        muted = "#A0A0A0"
    else:
        # Escuro = PRETO estilo CMD (#0C0C0C), sólido e nítido
        escuro = True
        fundo = "#0C0C0C"
        bg_col = temas_web.misturar("#111111", base_esc_sup, 0.06)
        card = temas_web.misturar("#161616", base_esc_sup, 0.06)
        card_hover = "#202020"
        input_bg = "#090909"
        border = "#282828"
        border_strong = "#3E3E3E"
        text = "#D4D4D4"
        title = "#F2F2F2"
        muted = "#9B9B9B"

    if t["acessivel"]:
        title = "#FFFFFF" if escuro else "#000000"
        text = "#F0F0F0" if escuro else "#0A0A0A"

    dest = temas_web.PALETAS[paleta][2] if tema == "T10" else (
        temas_web.TEMAS[tema].get("destaque_escuro") if escuro and t["acessivel"] else temas_web.TEMAS[tema]["destaque"]
    )
    dest = temas_web.ajustar_contraste(dest, card, 4.5 if t["acessivel"] else (4.0 if tema == "T10" else 3.4))
    sobre = "#FFFFFF" if temas_web.contraste("#FFFFFF", dest) >= temas_web.contraste("#000000", dest) else "#000000"
    r, g, b = temas_web._rgb(dest)

    c_cls = temas_web.ajustar_contraste("#6CA672" if escuro else "#2E6936", card, 3.6)
    c_lnk = temas_web.ajustar_contraste("#9B86BA" if escuro else "#5E487D", card, 3.6)
    c_pat = temas_web.ajustar_contraste("#C7A05A" if escuro else "#825F22", card, 3.6)
    c_err = temas_web.ajustar_contraste("#C96464" if escuro else "#993232", card, 3.8)
    cr, cg, cb = temas_web._rgb(c_cls)
    lr, lg, lb = temas_web._rgb(c_lnk)
    pr, pg, pb = temas_web._rgb(c_pat)
    er, eg, eb = temas_web._rgb(c_err)
    return {
        "ok": True,
        "tema": tema,
        "nome": t["nome"],
        "tom": tom,
        "tom_nome": temas_web.NOMES_TONS[tom],
        "paleta": paleta if tema == "T10" else None,
        "escuro": escuro,
        "vars": {
            "--bg": fundo,
            "--bg-col": bg_col,
            "--card": card,
            "--card-hover": card_hover,
            "--input-bg": input_bg,
            "--border": border,
            "--border-strong": border_strong,
            "--text": text,
            "--muted": muted,
            "--title": title,
            "--c-dom": dest,
            "--c-dom-bg": f"rgba({r}, {g}, {b}, 0.16)",
            "--c-dom-sobre": sobre,
            "--c-cls": c_cls,
            "--c-cls-bg": f"rgba({cr}, {cg}, {cb}, 0.15)",
            "--c-lnk": c_lnk,
            "--c-lnk-bg": f"rgba({lr}, {lg}, {lb}, 0.15)",
            "--c-pat": c_pat,
            "--c-pat-bg": f"rgba({pr}, {pg}, {pb}, 0.16)",
            "--c-err": c_err,
            "--c-err-bg": f"rgba({er}, {eg}, {eb}, 0.15)",
            "--radius": _RAIOS_PX.get(t["raio"], "6px"),
        },
    }


def grupo_do_padrao(chave):
    """Devolve o dict do grupo mutuamente excludente de um padrão (ou None se livre)."""
    for g in GRUPOS_EXCLUDENTES:
        if chave in g["membros"]:
            return g
    return None


def conflitos_padroes(ativos):
    """Dado um conjunto/lista de padrões ativos, devolve {padrao_bloqueado: info_bloqueio}."""
    ativos_set = set(ativos or ())
    bloqueios = {}
    for g in GRUPOS_EXCLUDENTES:
        presentes = [p for p in g["membros"] if p in ativos_set]
        if not presentes:
            continue
        for membro in g["membros"]:
            if membro in ativos_set:
                continue
            bloqueios[membro] = {
                "grupo": g["id"],
                "titulo": g["titulo"],
                "motivo": g["motivo"],
                "bloqueado_por": presentes,
            }
    return bloqueios


def _extrair_ligacoes(pasta, classes):
    """Extrai ligações ForeignKey registradas no especificacao.json ou nos atributos das classes."""
    ligacoes = []
    vistas = set()
    spec_path = Path(pasta) / "especificacao.json"
    if spec_path.is_file():
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            spec = {}
        for lig in spec.get("ligacoes", []) or []:
            if isinstance(lig, dict) and lig.get("origem") and lig.get("alvo"):
                chave = (lig["origem"], lig.get("campo", ""), lig["alvo"])
                if chave not in vistas:
                    vistas.add(chave)
                    ligacoes.append({"origem": lig["origem"], "campo": lig.get("campo", ""), "alvo": lig["alvo"]})
    for nome_cls, dados in (classes or {}).items():
        for atr in dados.get("atributos", []):
            alvo = atr.get("alvo") or atr.get("fk")
            if atr.get("tipo") == "fk" or alvo:
                chave = (nome_cls, atr["nome"], alvo or "")
                if chave not in vistas:
                    vistas.add(chave)
                    ligacoes.append({"origem": nome_cls, "campo": atr["nome"], "alvo": alvo or ""})
    return ligacoes


def _resumo_projeto(ctx, num, pasta, servidores_por_pasta):
    """Monta o JSON completo de um projeto gerado para a bancada WYSIWYG."""
    import tela_prompt as tp

    info = tp.info_sistema(pasta)
    spec = tp.ler_spec(pasta) or {}
    numero_str = tp.nn(num)
    porta = tp.porta_de(num, ctx.config.valores["porta_base"])
    srv = servidores_por_pasta.get(pasta.resolve())
    classes_raw = gs.classes_do_projeto(pasta) if pasta.is_dir() else {}
    classes = [
        {
            "nome": nome,
            "app": dados.get("app", ""),
            "principal": bool(dados.get("principal")),
            "atributos": [
                {
                    **a,
                    "regra_texto": gs.regra_em_texto(a)
                    if a.get("tipo") in gs.TIPOS_ATRIBUTO and a.get("regra") in gs.REGRAS_VALIDAS
                    else str(a.get("regra") or ""),
                }
                for a in dados.get("atributos", [])
            ],
        }
        for nome, dados in sorted(classes_raw.items(), key=lambda kv: (not kv[1].get("principal"), kv[0]))
    ]
    ligacoes = _extrair_ligacoes(pasta, classes_raw)
    endpoints = []
    if info.get("django"):
        try:
            for ep in gs.endpoints_do_projeto(pasta):
                endpoints.append({
                    "rota": ep["rota"],
                    "entidade": ep["entidade"],
                    "app": ep.get("app", ""),
                    "campos": list(ep.get("campos", [])),
                    "ativos": list(ep.get("ativos", [])),
                })
        except Exception:
            endpoints = []
    arquivos = tp.listar_arquivos(pasta)
    return {
        "numero": numero_str,
        "pasta": pasta.name,
        "sistema": info.get("sistema", pasta.name),
        "entidade": info.get("entidade", ""),
        "padroes": list(info.get("padroes", [])),
        "django": bool(info.get("django")),
        "exercicio": bool(info.get("exercicio")),
        "estudo": bool(info.get("estudo")),
        "comentarios": bool(info.get("comentarios")),
        "porta": srv["porta"] if srv else porta,
        "no_ar": srv is not None,
        "url": srv["url"] if srv else f"http://127.0.0.1:{porta}/",
        "admin_url": tp.admin_url(pasta),
        "web": spec.get("web") or {},
        "classes": classes,
        "ligacoes": ligacoes,
        "endpoints": endpoints,
        "total_arquivos": len(arquivos),
        "arquivos": arquivos,
    }


def _servidores_ativos(ctx):
    mapa = {}
    try:
        for item in ctx.servidores.listar():
            pasta = item.get("pasta")
            if pasta:
                mapa[Path(pasta).resolve()] = item
    except Exception:
        pass
    return mapa


def estado_completo(ctx):
    """GET /wysiwyg/estado — estado completo para renderizar a bancada WYSIWYG."""
    import tela_prompt as tp

    servs = _servidores_ativos(ctx)
    projetos = [_resumo_projeto(ctx, num, pasta, servs) for num, pasta in tp.sistemas(ctx.saida)]

    setores = [{"ini": f"{ini:03d}", "fim": f"{fim:03d}", "nome": nome} for ini, fim, nome in dom.SETORES]
    setores_vistos = {s["nome"] for s in setores}
    dominios_lista = []
    for chave, d in gs.DOMINIOS.items():
        info_d = gs.INFO_DOMINIOS[chave]
        setor_nome = info_d["setor"]
        if setor_nome not in setores_vistos:
            setores_vistos.add(setor_nome)
            setores.append({"ini": info_d["id"], "fim": info_d["id"], "nome": setor_nome})
        dominios_lista.append({
            "id": info_d["id"],
            "chave": chave,
            "setor": setor_nome,
            "sistema": d["sistema"],
            "entidade": d["entidade"],
            "palavras_total": len(d["palavras"]),
            "palavras": d["palavras"][:14],
            "atributos": [
                {"nome": a["nome"], "tipo": a["tipo"], "regra": a["regra"],
                 "min": a.get("min"), "max": a.get("max")}
                for a in d.get("atributos", [])
            ],
        })

    padroes_lista = []
    for cat_chave, membros in gs.CATEGORIAS.items():
        cat_nome = gs.NOMES_CATEGORIAS[cat_chave]
        for p in membros:
            pd = gs.PADROES[p]
            grp = grupo_do_padrao(p)
            padroes_lista.append({
                "chave": p,
                "titulo": pd["titulo"],
                "categoria": cat_chave,
                "categoria_nome": cat_nome,
                "familia": pd["familia"],
                "modulo": pd["modulo"],
                "problema": _limpar_placeholders(pd["problema"]),
                "conceito": _limpar_placeholders(pd["conceito"]),
                "quando_nao": _limpar_placeholders(pd["quando_nao"]),
                "alternativa": _limpar_placeholders(pd["alternativa"]),
                "grupo_excludente": grp["id"] if grp else None,
            })

    temas_lista = [{"chave": k, "nome": v["nome"], "descricao": v["descricao"]}
                   for k, v in temas_web.TEMAS.items()]
    tons_lista = [{"chave": t, "nome": temas_web.NOMES_TONS[t]} for t in temas_web.TONS]
    paletas_lista = [{"chave": k, "nome": v[0]} for k, v in temas_web.PALETAS.items()]
    temas_resolvidos = {
        f"{t}:{tom}": resolver_tema_wysiwyg(t, tom, "P01")["vars"]
        for t in temas_web.TEMAS
        for tom in temas_web.TONS
    }
    for tom in temas_web.TONS:
        for pal in temas_web.PALETAS:
            temas_resolvidos[f"T10:{tom}:{pal}"] = resolver_tema_wysiwyg("T10", tom, pal)["vars"]

    return {
        "ok": True,
        "config": ctx.config.publica(),
        "sistemas": projetos,
        "dominios": dominios_lista,
        "setores": setores,
        "padroes": padroes_lista,
        "grupos_excludentes": GRUPOS_EXCLUDENTES,
        "presets": {k: list(v) for k, v in gs.GRUPOS.items()},
        "estilos": [{"chave": k, "desc": v} for k, v in gs.ESTILOS.items()],
        "temas": temas_lista,
        "tons": tons_lista,
        "paletas": paletas_lista,
        "temas_resolvidos": temas_resolvidos,
        "regras_campo": REGRAS_CAMPO_PALETA,
        "categorias_campo": CATEGORIAS_CAMPO_PALETA,
    }


def detalhe_projeto(ctx, numero):
    """GET /wysiwyg/projeto?numero=NN — retorna o estado atualizado de um único projeto."""
    import tela_prompt as tp

    try:
        destino, _ = tp.escolher(ctx, numero)
    except ValueError as erro:
        return {"ok": False, "erro": str(erro)}
    servs = _servidores_ativos(ctx)
    num_tupla = next((n for n, p in tp.sistemas(ctx.saida) if p.resolve() == destino.resolve()), None)
    if num_tupla is None:
        return {"ok": False, "erro": f"sistema {numero} não encontrado"}
    return {"ok": True, "projeto": _resumo_projeto(ctx, num_tupla, destino, servs)}


# =============================================================================
# 2. PÁGINA HTML + CSS + JS DO MODO WYSIWYG (10 temas x 6 tons · tela inicial)
# =============================================================================
def pagina():
    return _HTML_WYSIWYG


_HTML_WYSIWYG = r"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0a0a0a">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icone-192.png">
<title>SGS</title>
<style>
  /* Padrão inicial: Escuro preto estilo CMD (#0C0C0C) */
  :root {
    --bg: #0C0C0C;
    --bg-col: #111111;
    --card: #161616;
    --card-hover: #202020;
    --input-bg: #090909;
    --border: #282828;
    --border-strong: #3E3E3E;
    --text: #D4D4D4;
    --muted: #9B9B9B;
    --title: #F2F2F2;

    --c-dom: #5b8cb5;
    --c-dom-bg: rgba(91, 140, 181, .14);
    --c-dom-sobre: #ffffff;
    --c-cls: #6a9a6e;
    --c-cls-bg: rgba(106, 154, 110, .13);
    --c-lnk: #8f7ea8;
    --c-lnk-bg: rgba(143, 126, 168, .13);
    --c-pat: #b59254;
    --c-pat-bg: rgba(181, 146, 84, .14);
    --c-err: #b85d5d;
    --c-err-bg: rgba(184, 93, 93, .13);

    --radius: 6px;
    --mono: "Cascadia Mono", "Cascadia Code", Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace;
    --sans: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; height: 100%;
    background: var(--bg); color: var(--text);
    font: 13px/1.45 var(--sans);
  }
  body { display: flex; flex-direction: column; overflow: hidden; }
  button, input, select, textarea { font: inherit; color: inherit; }

  /* ---- TOPBAR EM 2 LINHAS FIXAS (sem elementos dançando na tela) ---- */
  .topbar {
    display: flex; flex-direction: column;
    background: var(--bg-col); border-bottom: 1px solid var(--border);
    flex-shrink: 0; z-index: 20;
  }
  .topbar-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 10px; padding: 5px 14px; min-height: 34px;
  }
  .topbar-row-1 { border-bottom: 1px solid var(--border); }
  .topbar-row-2 { padding: 4px 14px; min-height: 31px; background: var(--bg); }
  .tb-left { display: flex; align-items: center; gap: 8px; min-width: 0; }
  .mode-switch {
    display: inline-flex; background: var(--bg); border: 1px solid var(--border);
    border-radius: 5px; padding: 2px; gap: 2px; font-family: var(--mono); flex-shrink: 0;
  }
  .mode-switch a, .mode-switch span {
    text-decoration: none; font-size: 11px; font-weight: 700;
    padding: 2px 9px; border-radius: 3px; color: var(--muted);
  }
  .mode-switch a:hover { color: var(--title); background: var(--card); }
  .mode-switch .ativo {
    background: var(--card); color: var(--title); border: 1px solid var(--border-strong);
  }

  .proj-picker {
    display: flex; align-items: center; gap: 6px; width: 270px; flex-shrink: 0;
    background: var(--input-bg); border: 1px solid var(--border);
    border-radius: 5px; padding: 2px 8px;
  }
  .proj-picker select {
    background: transparent; border: 0; outline: none; font-weight: 600; font-size: 12px;
    color: var(--title); width: 100%; cursor: pointer; text-overflow: ellipsis;
  }
  .proj-picker select option { background: var(--bg-col); color: var(--text); }
  .status-dot {
    width: 8px; height: 8px; border-radius: 50%; background: var(--border-strong);
    display: inline-block; flex-shrink: 0;
  }
  .status-dot.on { background: var(--c-cls); }

  /* Seletor dos 10 temas x 6 tons (larguras fixas — zero deslocamento horizontal) */
  .theme-bar {
    display: inline-flex; align-items: center; gap: 4px; flex-shrink: 0;
    background: var(--input-bg); border: 1px solid var(--border);
    border-radius: 5px; padding: 2px 6px;
  }
  .theme-bar select {
    background: transparent; border: 0; outline: none; font-size: 11.5px;
    color: var(--title); cursor: pointer; padding: 1px 2px;
  }
  .theme-bar select#ui-tema { width: 158px; }
  .theme-bar select#ui-tom { width: 78px; }
  .theme-bar select#ui-paleta { width: 148px; }
  .theme-bar select:disabled { opacity: .35; cursor: not-allowed; }
  .theme-bar select option { background: var(--bg-col); color: var(--text); }
  .theme-bar .sep { color: var(--border-strong); font-size: 11px; user-select: none; }

  .tb-actions { display: flex; align-items: center; gap: 6px; flex-wrap: nowrap; overflow-x: auto; }
  .tb-status {
    font-family: var(--mono); font-size: 11px; color: var(--muted);
    white-space: nowrap; flex-shrink: 0;
  }
  .btn {
    border: 1px solid var(--border); background: var(--card); color: var(--text);
    padding: 3px 9px; border-radius: 4px; cursor: pointer; font-weight: 600;
    font-size: 11.5px; line-height: 1.3; display: inline-flex; align-items: center; gap: 5px;
    text-decoration: none; white-space: nowrap;
  }
  .btn:hover:not(:disabled) { background: var(--card-hover); border-color: var(--border-strong); color: var(--title); }
  .btn:disabled { opacity: .45; cursor: not-allowed; }
  .btn-primary { border-color: var(--c-dom); background: var(--c-dom-bg); color: var(--title); }
  .btn-primary:hover:not(:disabled) { border-color: var(--c-dom); background: var(--c-dom); color: var(--c-dom-sobre); }
  .btn-green { border-color: var(--c-cls); background: var(--c-cls-bg); color: var(--title); }
  .btn-green:hover:not(:disabled) { border-color: var(--c-cls); background: var(--c-cls); color: #ffffff; }
  .btn-red { border-color: var(--c-err); background: var(--c-err-bg); color: var(--c-err); }
  .btn-amber { border-color: var(--c-pat); background: var(--c-pat-bg); color: var(--c-pat); }
  .btn-purple { border-color: var(--c-lnk); background: var(--c-lnk-bg); color: var(--title); }
  .btn-sm { padding: 2px 7px; font-size: 11px; border-radius: 4px; }

  /* ---- FAIXA DE PROJETOS EXISTENTES ---- */
  .proj-strip {
    display: flex; align-items: center; gap: 6px; padding: 6px 14px;
    background: var(--bg); border-bottom: 1px solid var(--border);
    overflow-x: auto; scrollbar-width: thin; flex-shrink: 0;
  }
  .proj-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 9px; border-radius: 4px; font-size: 11.5px; font-weight: 600;
    background: var(--bg-col); border: 1px solid var(--border); color: var(--muted);
    cursor: pointer; white-space: nowrap;
  }
  .proj-pill:hover { border-color: var(--border-strong); color: var(--title); }
  .proj-pill.ativo { background: var(--c-dom-bg); border-color: var(--c-dom); color: var(--title); }
  .proj-pill .num { font-family: var(--mono); font-size: 11px; color: var(--c-dom); }

  /* ---- QUADRO DE 4 COLUNAS ENCAIXÁVEIS ---- */
  .board {
    flex: 1; min-height: 0; display: grid;
    grid-template-columns: repeat(4, minmax(290px, 1fr));
    gap: 10px; padding: 10px 14px; overflow-x: auto; overflow-y: hidden;
  }
  .col {
    background: var(--bg-col); border: 1px solid var(--border);
    border-radius: var(--radius); display: flex; flex-direction: column;
    min-height: 0; overflow: hidden;
  }
  .col-head {
    padding: 8px 11px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    border-top: 2px solid var(--border-strong); flex-shrink: 0;
  }
  .col-1 .col-head { border-top-color: var(--c-dom); }
  .col-2 .col-head { border-top-color: var(--c-cls); }
  .col-3 .col-head { border-top-color: var(--c-lnk); }
  .col-4 .col-head { border-top-color: var(--c-pat); }
  .col-title { font-weight: 700; color: var(--title); font-size: 12.5px; letter-spacing: .2px; }
  .col-count {
    font-size: 11px; font-family: var(--mono); padding: 1px 7px; border-radius: 4px;
    background: var(--card); border: 1px solid var(--border); color: var(--muted);
  }
  .col-body {
    flex: 1; min-height: 0; overflow-y: auto; padding: 9px;
    display: flex; flex-direction: column; gap: 9px;
    scrollbar-width: thin;
  }
  .col-body > * { flex-shrink: 0; }

  /* ---- CARTÕES E CAMPOS ---- */
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 9px 10px;
  }
  .card-title {
    font-weight: 700; color: var(--title); font-size: 12.5px;
    display: flex; align-items: center; justify-content: space-between; gap: 6px;
    margin-bottom: 5px;
  }
  .card-sub { font-size: 11.5px; color: var(--muted); line-height: 1.4; }
  .inp, .sel {
    width: 100%; background: var(--input-bg); border: 1px solid var(--border);
    border-radius: 4px; padding: 5px 8px; color: var(--title); outline: none;
  }
  .inp:focus, .sel:focus { border-color: var(--c-dom); }
  .row { display: flex; gap: 6px; align-items: center; }
  .row > * { min-width: 0; }
  .lbl {
    display: block; font-size: 10.5px; font-weight: 700; color: var(--muted);
    margin: 7px 0 3px; text-transform: uppercase; letter-spacing: .4px;
  }

  .pill-group { display: flex; flex-wrap: wrap; gap: 5px; }
  .pill {
    padding: 3px 8px; border-radius: 4px; font-size: 11.5px; font-weight: 600;
    background: var(--input-bg); border: 1px solid var(--border); color: var(--muted);
    cursor: pointer;
  }
  .pill:hover:not(:disabled) { border-color: var(--border-strong); color: var(--title); }
  .pill.on { background: var(--c-dom-bg); border-color: var(--c-dom); color: var(--title); }
  .pill:disabled { opacity: .35; cursor: not-allowed; text-decoration: line-through; }

  /* Lista dos 300 Domínios */
  .dom-list {
    max-height: 210px; overflow-y: auto; display: flex; flex-direction: column;
    gap: 4px; margin-top: 6px; padding-right: 2px;
  }
  .dom-item {
    display: flex; align-items: center; justify-content: space-between; gap: 6px;
    padding: 5px 8px; border-radius: 4px; border: 1px solid var(--border);
    background: var(--input-bg); cursor: pointer; text-align: left;
  }
  .dom-item:hover { border-color: var(--c-dom); background: var(--card-hover); }
  .dom-item.ativo { border-color: var(--c-dom); background: var(--c-dom-bg); }
  .dom-id { font-family: var(--mono); font-size: 11px; color: var(--c-dom); font-weight: 700; }
  .dom-name { font-weight: 600; color: var(--title); font-size: 12px; }
  .dom-meta { font-size: 11px; color: var(--muted); }

  /* Paleta de Campos Categorizada */
  .palette-tabs { display: flex; flex-wrap: wrap; gap: 4px; margin: 6px 0 8px; }
  .palette-group { margin-top: 7px; padding-top: 6px; border-top: 1px solid var(--border); }
  .palette-group:first-of-type { margin-top: 2px; padding-top: 4px; }
  .palette-group-title {
    font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em;
    color: var(--muted); margin-bottom: 5px; display: flex; align-items: center; justify-content: space-between;
  }
  .palette { display: flex; flex-wrap: wrap; gap: 5px; }
  .brick {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 7px; border-radius: 4px; font-size: 11px; font-weight: 600;
    font-family: var(--mono); background: var(--input-bg);
    border: 1px dashed var(--c-cls); color: var(--c-cls);
    cursor: grab; user-select: none;
  }
  .brick:hover { background: var(--c-cls-bg); color: var(--title); }
  .brick:active { cursor: grabbing; }
  .brick.cat-selecao { border-color: var(--c-lnk); color: var(--c-lnk); }
  .brick.cat-selecao:hover { background: var(--c-lnk-bg); color: var(--title); }
  .brick.cat-negocio { border-color: var(--c-pat); color: var(--c-pat); }
  .brick.cat-negocio:hover { background: var(--c-pat-bg); color: var(--title); }
  .brick.cat-estruturados { border-color: var(--c-dom); color: var(--c-dom); }
  .brick.cat-estruturados:hover { background: var(--c-dom-bg); color: var(--title); }
  .modal-presets {
    max-height: 220px; overflow-y: auto; padding-right: 4px;
    display: flex; flex-direction: column; gap: 6px;
  }

  /* Cartões de Classe e Campos */
  .cls-card {
    background: var(--card); border: 1px solid var(--border);
    border-left: 3px solid var(--c-cls); border-radius: var(--radius); padding: 9px 10px;
  }
  .cls-card.drop-over { border-color: var(--c-cls); background: var(--c-cls-bg); }
  .field-list { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 7px; }
  .field-chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 7px; border-radius: 4px; font-size: 11.5px;
    background: var(--input-bg); border: 1px solid var(--border);
    cursor: pointer;
  }
  .field-chip:hover { border-color: var(--c-cls); color: var(--title); }
  .field-chip .fname { font-weight: 700; color: var(--title); font-family: var(--mono); }
  .field-chip .ftype { font-size: 10.5px; color: var(--c-cls); font-family: var(--mono); }
  .field-chip .frule { font-size: 10.5px; color: var(--muted); }
  .field-chip.is-fk { border-color: var(--c-lnk); background: var(--c-lnk-bg); }
  .field-chip.is-fk .ftype { color: var(--c-lnk); }

  /* Ligações FK & API */
  .link-card {
    display: flex; align-items: center; justify-content: space-between; gap: 6px;
    padding: 6px 9px; border-radius: 5px; background: var(--c-lnk-bg);
    border: 1px solid var(--c-lnk); font-family: var(--mono); font-size: 11.5px;
    color: var(--title);
  }
  .drag-cls {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 8px; border-radius: 4px; background: var(--input-bg);
    border: 1px solid var(--c-lnk); color: var(--title); font-weight: 600;
    font-family: var(--mono); font-size: 11.5px; cursor: grab;
  }
  .api-field {
    padding: 3px 7px; border-radius: 4px; font-family: var(--mono); font-size: 11px;
    border: 1px solid var(--border); background: var(--input-bg); color: var(--muted);
    cursor: pointer;
  }
  .api-field.on { background: var(--c-cls-bg); border-color: var(--c-cls); color: var(--title); font-weight: 700; }

  /* Padrões de Projeto — Encaixe + Exclusão Mútua */
  .dropzone {
    display: flex; flex-wrap: wrap; gap: 5px; align-items: flex-start;
    min-height: 44px; max-height: 150px; overflow-y: auto;
    padding: 7px; border-radius: var(--radius);
    border: 1px dashed var(--c-pat); background: var(--c-pat-bg);
    flex-shrink: 0;
  }
  .dropzone.over { border-style: solid; }
  .dropzone-empty { font-size: 11.5px; color: var(--muted); padding: 4px 2px; }
  .snap-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 8px; border-radius: 4px; font-size: 11.5px; font-weight: 600;
    background: var(--card); border: 1px solid var(--c-pat); color: var(--title);
    line-height: 1.3;
  }
  .snap-chip button {
    all: unset; cursor: pointer; font-family: var(--mono); font-weight: 700;
    color: var(--muted); padding: 0 2px;
  }
  .snap-chip button:hover { color: var(--c-err); }

  .pat-groups-slot { display: flex; flex-direction: column; gap: 7px; flex-shrink: 0; }
  .pat-group-title {
    font-size: 10.5px; font-weight: 700; color: var(--muted); text-transform: uppercase;
    letter-spacing: .5px; margin: 4px 0 0; padding-top: 5px;
    border-top: 1px solid var(--border);
  }
  .pat-grid { display: flex; flex-direction: column; gap: 5px; }
  .pat-block {
    padding: 7px 9px; border-radius: 5px; border: 1px solid var(--border);
    background: var(--card); display: flex; flex-direction: column; gap: 3px;
    cursor: pointer;
  }
  .pat-block:hover:not(.bloqueado) { border-color: var(--c-pat); background: var(--card-hover); }
  .pat-block.ativo {
    border-color: var(--c-pat); background: var(--c-pat-bg);
    border-left: 3px solid var(--c-pat);
  }
  .pat-block.bloqueado {
    background: var(--input-bg); border-style: dashed; border-color: var(--c-err);
    cursor: not-allowed;
  }
  .pat-block.bloqueado .pat-name { color: var(--muted); }
  .pat-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
  .pat-name { font-weight: 700; color: var(--title); font-size: 12px; display: flex; align-items: center; gap: 6px; }
  .pat-badge {
    font-family: var(--mono); font-size: 10px; font-weight: 700;
    padding: 1px 5px; border-radius: 3px; border: 1px solid var(--border);
    color: var(--muted);
  }
  .pat-badge.on { border-color: var(--c-pat); color: var(--c-pat); }
  .pat-badge.bloq { border-color: var(--c-err); color: var(--c-err); }
  .pat-mod { font-family: var(--mono); font-size: 10.5px; color: var(--muted); }
  .pat-desc { font-size: 11.5px; color: var(--muted); line-height: 1.38; }
  .pat-lock {
    display: flex; align-items: center; justify-content: space-between; gap: 6px;
    margin-top: 3px; padding: 4px 6px; border-radius: 4px;
    background: var(--c-err-bg); border: 1px solid var(--c-err);
    color: var(--c-err); font-size: 11px; font-weight: 600;
  }
  .btn-swap {
    border: 1px solid var(--c-pat); background: var(--card); color: var(--c-pat);
    font-size: 10.5px; font-weight: 700; padding: 2px 7px; border-radius: 4px; cursor: pointer;
    flex-shrink: 0;
  }
  .btn-swap:hover { background: var(--c-pat); color: #0c0c0c; }

  /* ---- BARRA INFERIOR VIVA ---- */
  .bottom-bar {
    background: var(--bg-col); border-top: 1px solid var(--border);
    display: flex; flex-direction: column; flex-shrink: 0; z-index: 25;
  }
  .cmd-strip {
    display: flex; align-items: center; gap: 8px; padding: 6px 14px; flex-wrap: wrap;
  }
  .cmd-label {
    font-family: var(--mono); font-size: 11px; font-weight: 700;
    color: var(--muted); text-transform: uppercase; letter-spacing: .4px;
  }
  .cmd-preview {
    flex: 1; min-width: 200px; font-family: var(--mono); font-size: 12.5px;
    background: var(--bg); border: 1px solid var(--border); border-radius: 4px;
    padding: 4px 9px; color: var(--title); overflow-x: auto; white-space: nowrap;
  }
  .drawer {
    border-top: 1px solid var(--border); background: var(--bg);
    height: 240px; display: flex; flex-direction: column;
  }
  .drawer[hidden] { display: none; }
  .drawer-tabs {
    display: flex; align-items: center; gap: 6px; padding: 5px 14px;
    background: var(--bg-col); border-bottom: 1px solid var(--border);
  }
  .drawer-body { flex: 1; min-height: 0; display: flex; overflow: hidden; }
  .log-pane {
    flex: 1; overflow-y: auto; padding: 10px 14px; font-family: var(--mono); font-size: 12px;
    white-space: pre-wrap; color: var(--text);
  }
  .code-split { flex: 1; display: grid; grid-template-columns: 260px 1fr; min-height: 0; }
  .file-tree {
    border-right: 1px solid var(--border); overflow-y: auto; padding: 6px;
    display: flex; flex-direction: column; gap: 2px;
  }
  .file-btn {
    text-align: left; background: transparent; border: 0; padding: 4px 8px;
    border-radius: 4px; font-family: var(--mono); font-size: 11.5px; color: var(--muted);
    cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .file-btn:hover, .file-btn.ativo { background: var(--c-dom-bg); color: var(--title); }
  .code-view {
    margin: 0; padding: 10px 14px; overflow: auto; font-family: var(--mono);
    font-size: 12px; line-height: 1.5; color: var(--text);
  }

  /* ---- MODAL LEVE ---- */
  .backdrop {
    position: fixed; inset: 0; background: rgba(0, 0, 0, .72);
    display: flex; align-items: center; justify-content: center; z-index: 60; padding: 16px;
  }
  .backdrop[hidden] { display: none; }
  .modal {
    width: 100%; max-width: 480px; background: var(--bg-col);
    border: 1px solid var(--border-strong); border-radius: var(--radius); overflow: hidden;
  }
  .modal-head {
    padding: 10px 14px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    font-weight: 700; color: var(--title);
  }
  .modal-body { padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; }
  .modal-foot {
    padding: 9px 14px; border-top: 1px solid var(--border);
    display: flex; justify-content: flex-end; gap: 8px;
  }
  .toast {
    position: fixed; top: 56px; right: 16px; z-index: 70;
    padding: 8px 12px; border-radius: 5px; font-weight: 600; font-size: 12px;
    border: 1px solid var(--border-strong); background: var(--card); color: var(--title);
    max-width: 420px;
  }
  .toast.ok { border-color: var(--c-cls); color: var(--c-cls); }
  .toast.erro { border-color: var(--c-err); color: var(--c-err); }

  @media (max-width: 1200px) {
    .board { grid-template-columns: repeat(2, minmax(300px, 1fr)); overflow-y: auto; }
  }
  @media (max-width: 720px) {
    .board { grid-template-columns: 1fr; overflow-y: auto; }
  }
</style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-row topbar-row-1">
      <div class="tb-left">
        <nav class="mode-switch" aria-label="Alternar modo WYSIWYG e CMD">
          <span class="ativo">WYSIWYG</span>
          <a href="/cmd" id="link-cmd" title="Abrir o modo terminal CMD">CMD</a>
        </nav>
        <div class="proj-picker">
          <span class="status-dot" id="proj-dot"></span>
          <select id="proj-select" aria-label="Selecionar projeto"></select>
        </div>
      </div>
      <div class="theme-bar" title="Aparência do WYSIWYG: 10 temas x 6 tons (Paleta P01–P20 ativa no T10)">
        <select id="ui-tema" aria-label="Tema do WYSIWYG"></select>
        <span class="sep">|</span>
        <select id="ui-tom" aria-label="Tom do WYSIWYG"></select>
        <span class="sep">|</span>
        <select id="ui-paleta" aria-label="Paleta do tema T10"></select>
      </div>
    </div>
    <div class="topbar-row topbar-row-2">
      <div class="tb-actions" id="tb-actions"></div>
      <span class="tb-status" id="tb-status">Novo projeto · Montagem de blocos</span>
    </div>
  </header>

  <div class="proj-strip" id="proj-strip"></div>

  <main class="board">
    <section class="col col-1">
      <div class="col-head">
        <div class="col-title">1 · Projeto &amp; Domínio</div>
        <span class="col-count" id="c-dominios">300</span>
      </div>
      <div class="col-body" id="col-dominio"></div>
    </section>

    <section class="col col-2">
      <div class="col-head">
        <div class="col-title">2 · Classes &amp; Campos</div>
        <span class="col-count" id="c-classes">0</span>
      </div>
      <div class="col-body" id="col-classes"></div>
    </section>

    <section class="col col-3">
      <div class="col-head">
        <div class="col-title">3 · Ligações &amp; API</div>
        <span class="col-count" id="c-ligacoes">0</span>
      </div>
      <div class="col-body" id="col-ligacoes"></div>
    </section>

    <section class="col col-4">
      <div class="col-head">
        <div class="col-title">4 · Padrões de Projeto</div>
        <span class="col-count" id="c-padroes">0 / 28</span>
      </div>
      <div class="col-body" id="col-padroes"></div>
    </section>
  </main>

  <footer class="bottom-bar">
    <div class="cmd-strip">
      <span class="cmd-label">Comando SGS</span>
      <div class="cmd-preview" id="cmd-preview">sgs gerar -sp hotel encapsulamento strategy</div>
      <button class="btn btn-sm" id="btn-copiar">Copiar</button>
      <button class="btn btn-sm btn-primary" id="btn-exec-cmd">Executar</button>
      <button class="btn btn-sm" id="btn-drawer">Console &amp; Código</button>
    </div>
    <div class="drawer" id="drawer" hidden>
      <div class="drawer-tabs">
        <button class="btn btn-sm" id="tab-log">Saída SGS</button>
        <button class="btn btn-sm" id="tab-code">Código do Projeto</button>
        <span class="card-sub" id="drawer-info" style="margin-left:auto"></span>
        <button class="btn btn-sm" id="btn-fechar-drawer">Fechar</button>
      </div>
      <div class="drawer-body" id="drawer-body"></div>
    </div>
  </footer>

  <div class="backdrop" id="modal-backdrop" hidden>
    <div class="modal">
      <div class="modal-head">
        <span id="modal-title">Ação</span>
        <button class="btn btn-sm" id="modal-close">x</button>
      </div>
      <div class="modal-body" id="modal-body"></div>
      <div class="modal-foot" id="modal-foot"></div>
    </div>
  </div>
  <div id="toast-box"></div>

<script>
const $ = (id) => document.getElementById(id);
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
/* Substitui filhos filtrando null/undefined/false (evita renderizar texto "null"). */
function setChildren(node, ...items) {
  const validos = items.flat().filter((x) => x !== null && x !== undefined && x !== false);
  node.replaceChildren(...validos);
}

const state = {
  data: null,
  projetoAtual: "__novo__",
  dominio: "hotel",
  assuntoLivre: "",
  filtroSetor: "",
  filtroCatCampo: "",
  buscaDominio: "",
  buscaPadrao: "",
  padroesAtivos: ["encapsulamento", "strategy"],
  modoExcludente: true,
  uiTema: localStorage.getItem("sgs.wysiwyg.uiTema") || "T09",
  uiTom: localStorage.getItem("sgs.wysiwyg.uiTom") || "escuro",
  uiPaleta: localStorage.getItem("sgs.wysiwyg.uiPaleta") || "P01",
  opcoes: {
    django: true,
    exercicio: false,
    estudo: true,
    comentarios: true,
    testar: true,
    estilo: "web",
    tema: "T10",
    paleta: "P01",
    id_publico: "inteiro",
    id_interno: false,
    estrutura: "plana",
  },
  ocupado: false,
  drawerAberto: false,
  drawerAba: "log",
  logTexto: "Pronto. Monte os blocos nas colunas e clique em Gerar projeto ou selecione um projeto existente para editar.",
  arquivoAberto: null,
  conteudoArquivo: "",
  _colDomModo: null,
  _colPatModo: null,
};

function toast(msg, tipo = "ok") {
  const box = $("toast-box");
  const t = el("div", { class: "toast " + tipo }, msg);
  setChildren(box, t);
  clearTimeout(toast._tm);
  toast._tm = setTimeout(() => { t.remove(); }, 4200);
}

function projetoSelecionado() {
  if (!state.data || state.projetoAtual === "__novo__") return null;
  return state.data.sistemas.find((s) => s.numero === state.projetoAtual) || null;
}

/* ---- 10 TEMAS x 6 TONS NO WYSIWYG ---- */
function aplicarVarsTema(vars) {
  if (!vars) return;
  const root = document.documentElement;
  for (const [k, v] of Object.entries(vars)) root.style.setProperty(k, v);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta && vars["--bg"]) meta.setAttribute("content", vars["--bg"]);
}

async function aplicarTemaUI(tema, tom, paleta) {
  state.uiTema = tema;
  state.uiTom = tom;
  state.uiPaleta = paleta || "P01";
  localStorage.setItem("sgs.wysiwyg.uiTema", state.uiTema);
  localStorage.setItem("sgs.wysiwyg.uiTom", state.uiTom);
  localStorage.setItem("sgs.wysiwyg.uiPaleta", state.uiPaleta);
  const sPal = $("ui-paleta");
  if (sPal) {
    sPal.disabled = state.uiTema !== "T10";
    sPal.title = state.uiTema === "T10"
      ? "Paleta ativa do tema T10 · Personalizado"
      : "Disponível quando o tema T10 · Personalizado estiver selecionado";
  }
  const chave = state.uiTema === "T10"
    ? `T10:${state.uiTom}:${state.uiPaleta}`
    : `${state.uiTema}:${state.uiTom}`;
  if (state.data?.temas_resolvidos?.[chave]) {
    aplicarVarsTema(state.data.temas_resolvidos[chave]);
    return;
  }
  try {
    const url = `/wysiwyg/tema?tema=${encodeURIComponent(state.uiTema)}&tom=${encodeURIComponent(state.uiTom)}&paleta=${encodeURIComponent(state.uiPaleta)}`;
    const r = await fetch(url);
    const d = await r.json();
    if (d.ok && d.vars) aplicarVarsTema(d.vars);
  } catch {}
}

function montarSeletoresTemaUI() {
  if (!state.data) return;
  const sTema = $("ui-tema"), sTom = $("ui-tom"), sPal = $("ui-paleta");
  setChildren(sTema, ...state.data.temas.map((t) =>
    el("option", { value: t.chave, selected: t.chave === state.uiTema }, `${t.chave} · ${t.nome}`)
  ));
  setChildren(sTom, ...state.data.tons.map((t) =>
    el("option", { value: t.chave, selected: t.chave === state.uiTom }, t.nome)
  ));
  setChildren(sPal, ...state.data.paletas.map((p) =>
    el("option", { value: p.chave, selected: p.chave === state.uiPaleta }, `${p.chave} · ${p.nome}`)
  ));
  sTema.onchange = () => aplicarTemaUI(sTema.value, sTom.value, sPal.value);
  sTom.onchange = () => aplicarTemaUI(sTema.value, sTom.value, sPal.value);
  sPal.onchange = () => aplicarTemaUI(sTema.value, sTom.value, sPal.value);
  aplicarTemaUI(state.uiTema, state.uiTom, state.uiPaleta);
}

function conflitosAtuais(listaPadroes) {
  if (!state.modoExcludente || !state.data) return {};
  const ativos = new Set(listaPadroes);
  const bl = {};
  for (const g of state.data.grupos_excludentes) {
    const presentes = g.membros.filter((m) => ativos.has(m));
    if (!presentes.length) continue;
    for (const m of g.membros) {
      if (ativos.has(m)) continue;
      bl[m] = { grupo: g.id, titulo: g.titulo, motivo: g.motivo, bloqueado_por: presentes };
    }
  }
  return bl;
}

function nomePadrao(chave) {
  const p = state.data?.padroes.find((x) => x.chave === chave);
  return p ? p.titulo.split(" (")[0] : chave;
}

function comandoEquivalente() {
  const proj = projetoSelecionado();
  if (proj) return `sgs editar ${proj.numero}`;
  const partes = ["sgs gerar -sp"];
  if (state.assuntoLivre.trim()) {
    partes.push(state.assuntoLivre.trim());
  } else {
    partes.push(state.dominio);
  }
  const pats = state.padroesAtivos.filter(Boolean);
  if (pats.length) partes.push(pats.join(" "));
  return partes.join(" ");
}

async function salvarOpcoesServidor() {
  const cfg = {
    django: state.opcoes.django,
    exercicio: state.opcoes.exercicio,
    estudo: state.opcoes.estudo,
    comentarios: state.opcoes.comentarios,
    testar: state.opcoes.testar,
    estilo: state.opcoes.estilo,
    tema: state.opcoes.tema,
    paleta: state.opcoes.paleta,
  };
  await fetch("/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cfg),
  }).catch(() => {});
}

function formatarBlocos(resp) {
  const linhas = [];
  if (resp.erro) linhas.push("[ERRO] " + resp.erro);
  for (const b of resp.blocos || []) {
    if (b.t === "titulo") linhas.push("\n== " + b.texto + " ==");
    else if (b.t === "texto") linhas.push(b.texto);
    else if (b.t === "codigo" || b.t === "saida") linhas.push(b.texto);
    else if (b.t === "link") linhas.push(`${b.texto}: ${b.href}`);
    else if (b.t === "tabela") {
      linhas.push((b.colunas || []).join(" | "));
      for (const l of b.linhas || []) {
        linhas.push(l.map((c) => (typeof c === "object" && c ? (c.texto || c.rotulo || "") : String(c))).join(" | "));
      }
    }
  }
  return linhas.join("\n").trim() || (resp.ok ? "Concluído." : "Falhou.");
}

async function executarComando(linha, opcoesExtra = {}) {
  if (state.ocupado) return null;
  state.ocupado = true;
  renderTopbar();
  state.logTexto = `> ${linha}\nExecutando...`;
  renderDrawer();
  try {
    await salvarOpcoesServidor();
    const r = await fetch("/comando", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ linha, opcoes: { ...state.opcoes, ...opcoesExtra } }),
    });
    const d = await r.json();
    state.logTexto = `> ${linha}\n\n${formatarBlocos(d)}`;
    if (d.ok) {
      toast(d.cartao ? `OK: ${d.cartao.sistema} (${d.cartao.numero})` : "Comando concluído.", "ok");
    } else {
      toast(d.erro || "Erro ao executar comando", "erro");
      state.drawerAberto = true;
      state.drawerAba = "log";
    }
    await carregarEstado(d.cartao ? d.cartao.numero : null);
    return d;
  } catch (err) {
    state.logTexto = `> ${linha}\n[ERRO] Falha de rede: ${err}`;
    toast("Erro de comunicação com o servidor SGS", "erro");
    state.drawerAberto = true;
    return null;
  } finally {
    state.ocupado = false;
    renderAll();
  }
}

async function carregarEstado(selecionarNumero = null) {
  const primeiro = !state.data;
  const r = await fetch("/wysiwyg/estado");
  const d = await r.json();
  if (!d.ok) return;
  state.data = d;
  if (d.config) {
    state.opcoes.django = !!d.config.django;
    state.opcoes.exercicio = !!d.config.exercicio;
    state.opcoes.estudo = !!d.config.estudo;
    state.opcoes.comentarios = !!d.config.comentarios;
    state.opcoes.testar = !!d.config.testar;
    if (d.config.estilo) state.opcoes.estilo = d.config.estilo;
    if (d.config.tema) state.opcoes.tema = d.config.tema;
    if (d.config.paleta) state.opcoes.paleta = d.config.paleta;
  }
  if (selecionarNumero && d.sistemas.some((s) => s.numero === selecionarNumero)) {
    state.projetoAtual = selecionarNumero;
  } else if (state.projetoAtual !== "__novo__" && !d.sistemas.some((s) => s.numero === state.projetoAtual)) {
    state.projetoAtual = "__novo__";
  }
  if (primeiro) montarSeletoresTemaUI();
  state._colDomModo = null;
  state._colPatModo = null;
  renderAll();
}

/* ---- MODAL AUXILIAR ---- */
function abrirModal(titulo, bodyNodes, footNodes) {
  $("modal-title").textContent = titulo;
  setChildren($("modal-body"), bodyNodes);
  setChildren($("modal-foot"), footNodes);
  $("modal-backdrop").hidden = false;
}
function fecharModal() { $("modal-backdrop").hidden = true; }
$("modal-close").onclick = fecharModal;
$("modal-backdrop").onclick = (e) => { if (e.target === $("modal-backdrop")) fecharModal(); };

function modalCampoCalculado(proj, classeNome) {
  abrirModal(
    `Campos Calculados (@property) em ${classeNome}`,
    [
      el("div", { class: "card-sub" },
        "No SGS, campos calculados (fórmulas) não são gravados como colunas editáveis no banco — são gerados como @property somente leitura no núcleo Python e no Model Django para nunca ficarem desatualizados."),
      el("div", { class: "card", style: "margin-top:4px" },
        el("div", { class: "pat-name" }, "Propriedades calculadas nativas"),
        el("div", { class: "card-sub", style: "font-family:var(--mono); margin-top:4px" },
          "• total -> quantidade * preco (somente leitura)\n• valor_final -> calculado pelo Service + Strategy\n• codigo / titulo / valor -> formatados no ViewModel / API")),
      el("div", { class: "card-sub" },
        "Você pode ligar ou desligar a exposição de total e valor_final na API REST na Coluna 3 (Ligações & API)."),
    ],
    [el("button", { class: "btn btn-primary", onclick: fecharModal }, "Entendi")]
  );
}

function aplicarBlocoCampo(proj, classeNome, rc) {
  if (!proj) {
    if (rc.acao === "calculado") return modalCampoCalculado(null, "Entidade");
    return toast("Gere ou selecione um projeto para encaixar novos campos.", "erro");
  }
  if (rc.acao === "ligar") {
    if (!proj.django) return toast("Relacionamento ForeignKey (sgs ligar) requer projeto com Django.", "erro");
    if (proj.classes.length < 2) {
      toast("Crie primeiro uma 2ª classe para ligar via ForeignKey.", "ok");
      return modalNovaClasse(proj);
    }
    return modalLigarClasses(proj, classeNome);
  }
  if (rc.acao === "calculado") {
    return modalCampoCalculado(proj, classeNome);
  }
  return modalIncrementarCampo(proj, classeNome, "", rc.regra);
}

function modalIncrementarCampo(proj, classeNome, campoInicial = "", regraInicial = "texto") {
  const inpCampo = el("input", { class: "inp", value: campoInicial, placeholder: "ex.: cidade, cpf, data_agendamento, tags" });
  const inpRegra = el("input", { class: "inp", value: regraInicial, placeholder: "ex.: texto, data-hora, moeda, email, cpf, json, lista:a,b,c" });
  const categorias = state.data.categorias_campo || [];
  const presets = el("div", { class: "modal-presets" },
    ...categorias.map((cat) => {
      const editaveis = cat.itens.filter((rc) => !rc.acao);
      if (!editaveis.length) return null;
      return el("div", {},
        el("div", { class: "palette-group-title" }, cat.titulo),
        el("div", { class: "pill-group" },
          ...editaveis.map((rc) =>
            el("button", {
              class: "pill", type: "button", title: `${rc.regra} — ${rc.desc}`,
              onclick: () => { inpRegra.value = rc.regra; },
            }, rc.rotulo)
          )
        )
      );
    })
  );
  abrirModal(
    `Incrementar campo em ${classeNome} (sistema ${proj.numero})`,
    [
      el("div", { class: "card-sub" }, "Cria um campo novo ou altera a regra de validação (@property + Django) diretamente no sistema."),
      el("label", { class: "lbl" }, "Nome do campo"),
      inpCampo,
      el("label", { class: "lbl" }, "Regra / Tipo do campo"),
      inpRegra,
      el("label", { class: "lbl" }, "Tipos categorizados (clique para preencher)"),
      presets,
    ],
    [
      el("button", { class: "btn", onclick: fecharModal }, "Cancelar"),
      el("button", {
        class: "btn btn-green",
        onclick: async () => {
          const c = inpCampo.value.trim();
          const rg = inpRegra.value.trim();
          if (!c || !rg) return toast("Informe o nome do campo e a regra.", "erro");
          fecharModal();
          await executarComando(`sgs incrementar ${proj.numero} ${classeNome}.${c} ${rg}`);
        },
      }, "Aplicar campo"),
    ]
  );
  setTimeout(() => (campoInicial ? inpRegra : inpCampo).focus(), 30);
}

function modalNovaClasse(proj) {
  const inpPedido = el("input", { class: "inp", placeholder: "ex.: clientes com nome, email e telefone" });
  const inpEnt = el("input", { class: "inp", placeholder: "Opcional (ex.: Cliente)" });
  const selLigar = el("select", { class: "sel" },
    el("option", { value: "" }, "Não ligar automaticamente"),
    ...proj.classes.map((c) => el("option", { value: c.nome }, `Ligar a partir de ${c.nome}`))
  );
  abrirModal(
    `Nova Classe / App no sistema ${proj.numero}`,
    [
      el("div", { class: "card-sub" }, "Cria model, form, CRUD, API REST e testes diretamente no sistema selecionado."),
      el("label", { class: "lbl" }, "Descrição da nova funcionalidade / campos"),
      inpPedido,
      el("label", { class: "lbl" }, "Nome da Classe (opcional)"),
      inpEnt,
      el("label", { class: "lbl" }, "Ligação automática (opcional)"),
      selLigar,
    ],
    [
      el("button", { class: "btn", onclick: fecharModal }, "Cancelar"),
      el("button", {
        class: "btn btn-green",
        onclick: async () => {
          const ped = inpPedido.value.trim();
          if (!ped) return toast("Descreva a nova classe/funcionalidade.", "erro");
          const partes = [`sgs app ${proj.numero} -sp`, ped];
          if (inpEnt.value.trim()) partes.push(`entidade=${inpEnt.value.trim()}`);
          if (selLigar.value) {
            const campoFk = (inpEnt.value.trim() || ped.split(/\s+/)[0]).toLowerCase().replace(/[^a-z0-9_]/g, "");
            partes.push(`ligar=${selLigar.value}.${campoFk || "item"}`);
          }
          fecharModal();
          await executarComando(partes.join(" "));
        },
      }, "Criar classe / app"),
    ]
  );
  setTimeout(() => inpPedido.focus(), 30);
}

function modalLigarClasses(proj, origemInit = "", alvoInit = "") {
  const selOrigem = el("select", { class: "sel" },
    ...proj.classes.map((c) => el("option", { value: c.nome, selected: c.nome === origemInit }, c.nome))
  );
  const selAlvo = el("select", { class: "sel" },
    ...proj.classes.map((c) => el("option", { value: c.nome, selected: c.nome === alvoInit }, c.nome))
  );
  const inpCampo = el("input", { class: "inp", value: (alvoInit || "").toLowerCase(), placeholder: "ex.: cliente, destino, categoria" });
  selAlvo.onchange = () => { if (!inpCampo.value.trim()) inpCampo.value = selAlvo.value.toLowerCase(); };
  abrirModal(
    `Ligar Classes (FK) no sistema ${proj.numero}`,
    [
      el("div", { class: "card-sub" }, "Cria campo ForeignKey na Classe Origem apontando para a Classe Alvo."),
      el("label", { class: "lbl" }, "Classe Origem (recebe o campo)"),
      selOrigem,
      el("label", { class: "lbl" }, "Classe Alvo (referenciada)"),
      selAlvo,
      el("label", { class: "lbl" }, "Nome do campo de ligação"),
      inpCampo,
    ],
    [
      el("button", { class: "btn", onclick: fecharModal }, "Cancelar"),
      el("button", {
        class: "btn btn-purple",
        onclick: async () => {
          const o = selOrigem.value, a = selAlvo.value, c = inpCampo.value.trim() || a.toLowerCase();
          if (o === a) return toast("Escolha duas classes diferentes.", "erro");
          fecharModal();
          await executarComando(`sgs ligar ${proj.numero} ${o}.${c} ${a}`);
        },
      }, "Conectar classes"),
    ]
  );
}

function modalNovoDominio() {
  const inpChave = el("input", { class: "inp", placeholder: "ex.: maremotriz" });
  const inpSist = el("input", { class: "inp", placeholder: "ex.: Maré Oceânica" });
  const inpEnt = el("input", { class: "inp", placeholder: "ex.: TurbinaMare" });
  const inpPal = el("textarea", { class: "inp", rows: 3, placeholder: "maremotriz, turbina submarina, oceano, barragem mare" });
  abrirModal(
    "Cadastrar Novo Domínio Personalizado (ID >= 301)",
    [
      el("label", { class: "lbl" }, "Chave do domínio (snake_case)"), inpChave,
      el("label", { class: "lbl" }, "Nome do sistema"), inpSist,
      el("label", { class: "lbl" }, "Entidade principal (CamelCase)"), inpEnt,
      el("label", { class: "lbl" }, "Palavras-chave (mínimo 3, separadas por vírgula)"), inpPal,
    ],
    [
      el("button", { class: "btn", onclick: fecharModal }, "Cancelar"),
      el("button", {
        class: "btn btn-primary",
        onclick: async () => {
          const ch = inpChave.value.trim(), si = inpSist.value.trim(), en = inpEnt.value.trim(), pa = inpPal.value.trim();
          if (!ch || !si || !en || !pa) return toast("Preencha todos os campos do domínio.", "erro");
          fecharModal();
          await executarComando(`sgs dominios novo ${ch} sistema="${si}" entidade=${en} palavras="${pa}"`);
        },
      }, "Cadastrar domínio"),
    ]
  );
  setTimeout(() => inpChave.focus(), 30);
}

/* ---- RENDER: TOPBAR & FAIXA DE PROJETOS ---- */
function renderTopbar() {
  if (!state.data) return;
  const proj = projetoSelecionado();
  const sel = $("proj-select");
  setChildren(sel,
    el("option", { value: "__novo__", selected: !proj }, "+ Novo Projeto (Montar Blocos)"),
    ...state.data.sistemas.map((s) =>
      el("option", { value: s.numero, selected: s.numero === state.projetoAtual },
        `${s.no_ar ? "[NO AR] " : ""}${s.numero} · ${s.sistema} (${s.entidade})`)
    )
  );
  sel.onchange = () => {
    state.projetoAtual = sel.value;
    state.arquivoAberto = null;
    state.conteudoArquivo = "";
    renderAll();
  };
  $("proj-dot").className = "status-dot" + (proj?.no_ar ? " on" : "");
  const stEl = $("tb-status");
  if (stEl) {
    stEl.textContent = proj
      ? `Sistema ${proj.numero} · ${proj.entidade} · ${proj.no_ar ? "NO AR :" + proj.porta : "parado"}`
      : "Novo projeto · Montagem de blocos";
  }

  const acts = $("tb-actions");
  if (!proj) {
    setChildren(acts,
      el("button", {
        class: "btn btn-primary", disabled: state.ocupado,
        onclick: () => executarComando(comandoEquivalente()),
      }, "Gerar projeto"),
      el("button", {
        class: "btn btn-amber", disabled: state.ocupado,
        onclick: () => executarComando("sgs provap3"),
      }, "Prova P3 (101)")
    );
  } else {
    setChildren(acts,
      proj.django
        ? (proj.no_ar
            ? el("button", { class: "btn btn-red", disabled: state.ocupado, onclick: () => executarComando(`sgs parar ${proj.numero}`) }, "Parar")
            : el("button", { class: "btn btn-green", disabled: state.ocupado, onclick: () => executarComando(`sgs rodar ${proj.numero}`) }, "Rodar"))
        : null,
      proj.no_ar
        ? el("a", { class: "btn btn-primary", href: proj.url, target: "_blank", rel: "noopener" }, `Abrir :${proj.porta}`)
        : null,
      el("button", { class: "btn", disabled: state.ocupado, onclick: () => executarComando(`sgs testar ${proj.numero}`) }, "Testar"),
      el("button", { class: "btn", disabled: state.ocupado, onclick: () => executarComando(`sgs duplicar ${proj.numero}`) }, "Duplicar"),
      el("button", {
        class: "btn",
        onclick: () => {
          state.drawerAberto = true;
          state.drawerAba = "code";
          if (!state.arquivoAberto && proj.arquivos.length) abrirArquivoProjeto(proj, proj.arquivos[0]);
          renderDrawer();
        },
      }, "Código"),
      el("button", { class: "btn btn-primary", onclick: () => { state.projetoAtual = "__novo__"; renderAll(); } }, "+ Novo")
    );
  }

  const strip = $("proj-strip");
  setChildren(strip,
    el("button", {
      class: "proj-pill" + (!proj ? " ativo" : ""),
      onclick: () => { state.projetoAtual = "__novo__"; renderAll(); },
    }, "+ Novo Projeto"),
    ...state.data.sistemas.map((s) =>
      el("button", {
        class: "proj-pill" + (s.numero === state.projetoAtual ? " ativo" : ""),
        onclick: () => { state.projetoAtual = s.numero; state.arquivoAberto = null; renderAll(); },
      },
        el("span", { class: "status-dot" + (s.no_ar ? " on" : "") }),
        el("span", { class: "num" }, s.numero),
        s.sistema
      )
    )
  );
}

/* ---- COLUNA 1: DOMÍNIO & OPÇÕES (input persistente — nunca perde foco!) ---- */
function atualizarListaDominios() {
  const listaSlot = $("dom-list-slot");
  if (!listaSlot || !state.data) return;
  const doms = state.data.dominios.filter((d) => {
    if (state.filtroSetor && d.setor !== state.filtroSetor) return false;
    if (!state.buscaDominio.trim()) return true;
    const q = state.buscaDominio.toLowerCase();
    return d.chave.toLowerCase().includes(q) || d.sistema.toLowerCase().includes(q) ||
           d.id.includes(q) || d.setor.toLowerCase().includes(q) ||
           d.palavras.some((p) => p.toLowerCase().includes(q));
  });
  $("c-dominios").textContent = `${doms.length} / ${state.data.dominios.length}`;
  setChildren(listaSlot,
    ...doms.slice(0, 60).map((d) =>
      el("button", {
        class: "dom-item" + (d.chave === state.dominio && !state.assuntoLivre.trim() ? " ativo" : ""),
        onclick: () => {
          state.dominio = d.chave;
          state.assuntoLivre = "";
          const inpA = $("inp-assunto-livre");
          if (inpA) inpA.value = "";
          atualizarListaDominios();
          renderColClasses();
          renderCmdPreview();
        },
      },
        el("div", {},
          el("div", { class: "dom-name" }, el("span", { class: "dom-id" }, d.id + " "), d.sistema),
          el("div", { class: "dom-meta" }, `${d.chave} · ${d.entidade} · ${d.setor}`)
        )
      )
    ),
    doms.length > 60 ? el("div", { class: "card-sub", style: "padding:4px" }, `Mostrando 60 de ${doms.length} — filtre acima para refinar.`) : null
  );
}

function atualizarOpcoesGerador() {
  const slot = $("opt-card-slot");
  if (!slot || !state.data) return;
  const webAtivo = state.opcoes.django;
  const temaAtivo = webAtivo && state.opcoes.estilo === "web";
  setChildren(slot,
    el("div", { class: "card-title" }, "Opções Excludentes do Gerador"),
    el("label", { class: "lbl" }, "Camada Web"),
    el("div", { class: "pill-group" },
      el("button", { class: "pill" + (webAtivo ? " on" : ""), onclick: () => { state.opcoes.django = true; atualizarOpcoesGerador(); } }, "Com Django"),
      el("button", { class: "pill" + (!webAtivo ? " on" : ""), onclick: () => { state.opcoes.django = false; atualizarOpcoesGerador(); } }, "Só Python (núcleo)")
    ),
    el("label", { class: "lbl" }, "Estilo Web (requer Django)"),
    el("div", { class: "pill-group" },
      ...state.data.estilos.map((es) =>
        el("button", {
          class: "pill" + (state.opcoes.estilo === es.chave ? " on" : ""),
          disabled: !webAtivo,
          title: es.desc,
          onclick: () => { state.opcoes.estilo = es.chave; atualizarOpcoesGerador(); },
        }, es.chave)
      )
    ),
    el("label", { class: "lbl" }, "Tema do Sistema Gerado (requer estilo web)"),
    el("div", { class: "row" },
      el("select", {
        class: "sel", disabled: !temaAtivo,
        onchange: (e) => { state.opcoes.tema = e.target.value; atualizarOpcoesGerador(); },
      }, ...state.data.temas.map((t) => el("option", { value: t.chave, selected: t.chave === state.opcoes.tema }, `${t.chave} · ${t.nome}`))),
      el("select", {
        class: "sel", disabled: !temaAtivo || state.opcoes.tema !== "T10",
        onchange: (e) => { state.opcoes.paleta = e.target.value; },
      }, ...state.data.paletas.map((p) => el("option", { value: p.chave, selected: p.chave === state.opcoes.paleta }, `${p.chave} · ${p.nome}`)))
    ),
    el("label", { class: "lbl" }, "Modo & Qualidade"),
    el("div", { class: "pill-group" },
      el("button", { class: "pill" + (!state.opcoes.exercicio ? " on" : ""), onclick: () => { state.opcoes.exercicio = false; atualizarOpcoesGerador(); } }, "Completo"),
      el("button", { class: "pill" + (state.opcoes.exercicio ? " on" : ""), onclick: () => { state.opcoes.exercicio = true; atualizarOpcoesGerador(); } }, "Exercício (TODOs)"),
      el("button", { class: "pill" + (state.opcoes.estudo ? " on" : ""), onclick: () => { state.opcoes.estudo = !state.opcoes.estudo; atualizarOpcoesGerador(); } }, "Para Estudo"),
      el("button", { class: "pill" + (state.opcoes.comentarios ? " on" : ""), onclick: () => { state.opcoes.comentarios = !state.opcoes.comentarios; atualizarOpcoesGerador(); } }, "Comentários"),
      el("button", { class: "pill" + (state.opcoes.testar ? " on" : ""), onclick: () => { state.opcoes.testar = !state.opcoes.testar; atualizarOpcoesGerador(); } }, "Rodar Testes")
    )
  );
}

function renderColDominio() {
  const box = $("col-dominio");
  const proj = projetoSelecionado();
  if (proj) {
    state._colDomModo = proj.numero;
    $("c-dominios").textContent = `Sistema ${proj.numero}`;
    const web = proj.web || {};
    setChildren(box,
      el("div", { class: "card" },
        el("div", { class: "card-title" }, proj.sistema, el("span", { class: "dom-id" }, `#${proj.numero}`)),
        el("div", { class: "card-sub" }, `Pasta: ${proj.pasta}`),
        el("div", { class: "card-sub" }, `Entidade: ${proj.entidade} · Arquivos: ${proj.total_arquivos}`),
        el("div", { class: "card-sub" }, `Porta: ${proj.porta} · Status: ${proj.no_ar ? "NO AR" : "parado"}`),
        proj.admin_url ? el("div", { class: "card-sub" }, `Admin: ${proj.admin_url}`) : null,
        el("div", { class: "pill-group", style: "margin-top:8px" },
          el("span", { class: "pill on" }, proj.django ? "Django Web" : "Só Python"),
          web.estilo ? el("span", { class: "pill on" }, `Estilo: ${web.estilo}`) : null,
          web.tema ? el("span", { class: "pill on" }, `Tema: ${web.tema}`) : null,
          proj.exercicio ? el("span", { class: "pill on" }, "Modo Exercício") : null
        )
      ),
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "Ações do projeto"),
        el("div", { class: "pill-group" },
          el("button", { class: "btn btn-sm", onclick: () => executarComando(`sgs info ${proj.numero}`) }, "Info"),
          el("button", { class: "btn btn-sm", onclick: () => executarComando(`sgs comandos ${proj.numero}`) }, "Comandos CLI"),
          el("button", { class: "btn btn-sm btn-amber", onclick: () => executarComando(`sgs duplicar ${proj.numero}`) }, "Duplicar versão"),
          el("button", {
            class: "btn btn-sm",
            onclick: () => {
              state.projetoAtual = "__novo__";
              state.padroesAtivos = [...proj.padroes];
              state.opcoes.django = proj.django;
              state.opcoes.exercicio = proj.exercicio;
              renderAll();
              toast("Padrões copiados para um Novo Projeto.", "ok");
            },
          }, "Usar como base")
        )
      ),
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "Edição direta ativa"),
        el("div", { class: "card-sub" },
          `Alterações nas colunas 2 (Classes/Campos) e 3 (Ligações/API) modificam diretamente o sistema ${proj.numero}, sem criar cópias acidentais. Use Duplicar para versionar.`)
      )
    );
    return;
  }

  if (state._colDomModo !== "__novo__") {
    state._colDomModo = "__novo__";
    const selSetor = el("select", {
      class: "sel", id: "sel-setor-dom",
      onchange: (e) => { state.filtroSetor = e.target.value; atualizarListaDominios(); },
    },
      el("option", { value: "" }, `Todos os setores (${state.data.setores.length})`),
      ...state.data.setores.map((s) =>
        el("option", { value: s.nome, selected: s.nome === state.filtroSetor }, `${s.ini}-${s.fim} · ${s.nome}`)
      )
    );
    const inpBusca = el("input", {
      class: "inp", id: "inp-busca-dom",
      placeholder: "Buscar nos 300 domínios (ex.: cardiologia, 199, agro...)",
      value: state.buscaDominio,
      oninput: (e) => { state.buscaDominio = e.target.value; atualizarListaDominios(); },
    });
    const inpAssunto = el("input", {
      class: "inp", id: "inp-assunto-livre",
      placeholder: "Ou descreva em texto livre (opcional)",
      value: state.assuntoLivre,
      oninput: (e) => { state.assuntoLivre = e.target.value; renderCmdPreview(); },
    });
    setChildren(box,
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "Escolher Domínio",
          el("button", { class: "btn btn-sm", onclick: modalNovoDominio }, "+ Novo Domínio")
        ),
        selSetor,
        el("div", { style: "margin-top:6px" }, inpBusca),
        el("div", { class: "dom-list", id: "dom-list-slot" }),
        el("label", { class: "lbl" }, "Pedido em texto livre (substitui domínio)"),
        inpAssunto
      ),
      el("div", { class: "card", id: "opt-card-slot" })
    );
  }
  atualizarListaDominios();
  atualizarOpcoesGerador();
}

/* ---- COLUNA 2: CLASSES & CAMPOS ---- */
function renderColClasses() {
  const box = $("col-classes");
  const proj = projetoSelecionado();
  const categorias = state.data.categorias_campo || [];
  const visiveis = state.filtroCatCampo
    ? categorias.filter((c) => c.id === state.filtroCatCampo)
    : categorias;
  const totalTipos = categorias.reduce((acc, c) => acc + c.itens.length, 0);
  const rotulosCurto = {
    primitivos: "Primitivos",
    selecao: "Seleção",
    negocio: "Negócio",
    estruturados: "Estruturados",
  };

  const paletaCard = el("div", { class: "card" },
    el("div", { class: "card-title" },
      "Paleta de Campos (arraste -> Classe)",
      proj && proj.django
        ? el("button", { class: "btn btn-sm btn-green", onclick: () => modalNovaClasse(proj) }, "+ Nova Classe")
        : null
    ),
    el("div", { class: "palette-tabs" },
      el("button", {
        class: "pill" + (!state.filtroCatCampo ? " on" : ""),
        onclick: () => { state.filtroCatCampo = ""; renderColClasses(); },
      }, `Todos (${totalTipos})`),
      ...categorias.map((cat) =>
        el("button", {
          class: "pill" + (state.filtroCatCampo === cat.id ? " on" : ""),
          title: cat.sub,
          onclick: () => { state.filtroCatCampo = cat.id; renderColClasses(); },
        }, `${rotulosCurto[cat.id] || cat.titulo} (${cat.itens.length})`)
      )
    ),
    ...visiveis.map((cat) =>
      el("div", { class: "palette-group" },
        el("div", { class: "palette-group-title", title: cat.sub },
          el("span", {}, cat.titulo),
          el("span", {}, String(cat.itens.length))
        ),
        el("div", { class: "palette" },
          ...cat.itens.map((rc) =>
            el("div", {
              class: `brick cat-${cat.id}`, draggable: true,
              title: `${rc.rotulo} (${rc.exemplo}) — ${rc.desc}`,
              ondragstart: (e) => { e.dataTransfer.setData("text/sgs-field", JSON.stringify(rc)); },
              onclick: () => {
                const alvoCls = proj && proj.classes.length ? proj.classes[0].nome : "Entidade";
                aplicarBlocoCampo(proj, alvoCls, rc);
              },
            }, ":: ", rc.rotulo)
          )
        )
      )
    )
  );

  if (!proj) {
    const domSel = state.data.dominios.find((d) => d.chave === state.dominio) || state.data.dominios[0];
    $("c-classes").textContent = "1 (prévia)";
    setChildren(box,
      paletaCard,
      el("div", { class: "cls-card" },
        el("div", { class: "card-title" },
          `class ${domSel.entidade}`,
          el("span", { class: "col-count" }, "principal · prévia")
        ),
        el("div", { class: "card-sub" }, `Domínio: ${domSel.id} · ${domSel.sistema}`),
        el("div", { class: "field-list" },
          ...domSel.atributos.map((a) =>
            el("div", { class: "field-chip" },
              el("span", { class: "fname" }, a.nome),
              el("span", { class: "ftype" }, a.tipo),
              el("span", { class: "frule" }, a.regra)
            )
          )
        ),
        el("div", { class: "card-sub", style: "margin-top:8px" },
          "Clique em Gerar projeto no topo para criar este sistema e liberar edição direta de campos, novas classes e ligações.")
      )
    );
    return;
  }

  $("c-classes").textContent = String(proj.classes.length);
  const cards = proj.classes.map((cls) => {
    const card = el("div", {
      class: "cls-card",
      ondragover: (e) => {
        if (e.dataTransfer.types.includes("text/sgs-field")) {
          e.preventDefault(); card.classList.add("drop-over");
        }
      },
      ondragleave: () => card.classList.remove("drop-over"),
      ondrop: (e) => {
        card.classList.remove("drop-over");
        const raw = e.dataTransfer.getData("text/sgs-field");
        if (!raw) return;
        e.preventDefault();
        try {
          const rc = JSON.parse(raw);
          aplicarBlocoCampo(proj, cls.nome, rc);
        } catch {}
      },
    },
      el("div", { class: "card-title" },
        `class ${cls.nome}`,
        el("div", { class: "row" },
          el("span", { class: "col-count" }, cls.principal ? "principal" : cls.app),
          el("button", { class: "btn btn-sm", onclick: () => modalIncrementarCampo(proj, cls.nome) }, "+ Campo")
        )
      ),
      el("div", { class: "field-list" },
        ...cls.atributos.map((a) => {
          const isFk = a.tipo === "fk" || !!a.alvo;
          return el("button", {
            class: "field-chip" + (isFk ? " is-fk" : ""),
            title: "Clique para incrementar/alterar a regra deste campo",
            onclick: () => isFk
              ? modalLigarClasses(proj, cls.nome, a.alvo || "")
              : modalIncrementarCampo(proj, cls.nome, a.nome, a.regra_texto || a.regra || "texto"),
          },
            el("span", { class: "fname" }, a.nome),
            el("span", { class: "ftype" }, isFk ? `-> ${a.alvo || "FK"}` : a.tipo),
            el("span", { class: "frule" }, a.regra_texto || a.regra)
          );
        })
      )
    );
    return card;
  });

  setChildren(box, paletaCard, ...cards);
}

/* ---- COLUNA 3: LIGAÇÕES (FK) & API REST ---- */
function renderColLigacoes() {
  const box = $("col-ligacoes");
  const proj = projetoSelecionado();
  if (!proj) {
    $("c-ligacoes").textContent = "0";
    setChildren(box,
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "Ligações entre Classes (ForeignKey)"),
        el("div", { class: "card-sub" }, "Após gerar o projeto, crie uma 2ª classe e arraste uma classe sobre a outra para conectar com ForeignKey (sgs ligar).")),
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "API REST"),
        el("div", { class: "card-sub" }, "Projetos com Django expõem automaticamente endpoints JSON (/api/v1/...) com seleção de campos por clique."))
    );
    return;
  }

  $("c-ligacoes").textContent = `${proj.ligacoes.length} FK · ${proj.endpoints.length} API`;
  const ligNodes = [];

  if (proj.classes.length < 2) {
    ligNodes.push(
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "Conectar Classes"),
        el("div", { class: "card-sub" }, "Este projeto tem apenas 1 classe. Crie uma 2ª classe para ligar relacionamentos ForeignKey."),
        proj.django
          ? el("button", { class: "btn btn-sm btn-purple", style: "margin-top:8px", onclick: () => modalNovaClasse(proj) }, "+ Criar 2ª Classe / App")
          : null
      )
    );
  } else {
    const zonas = el("div", { class: "pill-group", style: "margin-top:6px" },
      ...proj.classes.map((cls) => {
        const chip = el("div", {
          class: "drag-cls", draggable: true,
          title: "Arraste sobre outra classe para ligar (Origem -> Alvo)",
          ondragstart: (e) => e.dataTransfer.setData("text/sgs-cls", cls.nome),
          ondragover: (e) => {
            if (e.dataTransfer.types.includes("text/sgs-cls")) { e.preventDefault(); chip.style.background = "var(--c-lnk-bg)"; }
          },
          ondragleave: () => { chip.style.background = ""; },
          ondrop: (e) => {
            chip.style.background = "";
            const origem = e.dataTransfer.getData("text/sgs-cls");
            if (!origem || origem === cls.nome) return;
            e.preventDefault();
            modalLigarClasses(proj, origem, cls.nome);
          },
        }, ":: ", cls.nome);
        return chip;
      })
    );
    ligNodes.push(
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "Arraste Origem -> Alvo",
          el("button", { class: "btn btn-sm btn-purple", onclick: () => modalLigarClasses(proj) }, "+ Ligar")
        ),
        el("div", { class: "card-sub" }, "Arraste uma classe sobre a outra ou clique em + Ligar."),
        zonas
      )
    );
  }

  for (const lig of proj.ligacoes) {
    ligNodes.push(
      el("div", { class: "link-card" },
        el("span", {}, `${lig.origem}.${lig.campo}`),
        el("span", {}, "->"),
        el("span", {}, lig.alvo)
      )
    );
  }

  if (proj.endpoints.length) {
    ligNodes.push(
      el("div", { class: "card" },
        el("div", { class: "card-title" }, "API REST · Campos Expostos"),
        el("div", { class: "card-sub", style: "margin-bottom:6px" }, "Clique em um campo para ligar/desligar na resposta JSON."),
        ...proj.endpoints.map((ep) =>
          el("div", { style: "margin-bottom:8px; padding-top:6px; border-top:1px solid var(--border)" },
            el("div", { class: "pat-name", style: "font-family:var(--mono); font-size:11.5px" }, ep.rota,
              el("span", { class: "pat-mod" }, ep.entidade)),
            el("div", { class: "pill-group", style: "margin-top:5px" },
              ...ep.campos.map((cp) => {
                const ativo = ep.ativos.includes(cp);
                return el("button", {
                  class: "api-field" + (ativo ? " on" : ""),
                  onclick: () => executarComando(`sgs api config ${proj.numero} ${ep.rota} ${cp}=${ativo ? "nao" : "sim"}`),
                }, (ativo ? "[x] " : "[ ] ") + cp);
              })
            )
          )
        )
      )
    );
  }

  setChildren(box, ...ligNodes);
}

/* ---- COLUNA 4: PADRÕES DE PROJETO (input de filtro persistente — nunca perde foco!) ---- */
function togglePadrao(chave) {
  const proj = projetoSelecionado();
  if (proj) {
    toast("Padrões de um projeto já gerado são somente leitura aqui. Clique em 'Usar como base' para gerar uma nova montagem.", "erro");
    return;
  }
  const idx = state.padroesAtivos.indexOf(chave);
  if (idx >= 0) {
    state.padroesAtivos.splice(idx, 1);
  } else {
    const conf = conflitosAtuais(state.padroesAtivos)[chave];
    if (conf) {
      toast(`Excludente com ${conf.bloqueado_por.map(nomePadrao).join(", ")} (${conf.titulo}). Use "Trocar" ou ative o Modo Livre.`, "erro");
      return;
    }
    state.padroesAtivos.push(chave);
  }
  atualizarConteudoPadroes();
  renderCmdPreview();
}

function trocarPadrao(novoChave, bloqueadores) {
  state.padroesAtivos = state.padroesAtivos.filter((p) => !bloqueadores.includes(p));
  if (!state.padroesAtivos.includes(novoChave)) state.padroesAtivos.push(novoChave);
  toast(`Substituído: ${bloqueadores.map(nomePadrao).join(", ")} -> ${nomePadrao(novoChave)}`, "ok");
  atualizarConteudoPadroes();
  renderCmdPreview();
}

function aplicarPreset(nome) {
  if (projetoSelecionado()) return;
  const lista = state.data.presets[nome] || [];
  if (nome === "todos" || nome === "prova" || nome === "gof") {
    state.modoExcludente = false;
    state.padroesAtivos = [...lista];
    toast(`Preset '${nome}' ativou o Modo Livre para combinar ${lista.length} padrões.`, "ok");
  } else {
    const escolhidos = [];
    for (const p of lista) {
      if (!state.modoExcludente || !conflitosAtuais(escolhidos)[p]) escolhidos.push(p);
    }
    state.padroesAtivos = escolhidos;
  }
  atualizarConteudoPadroes();
  renderCmdPreview();
}

function atualizarConteudoPadroes() {
  const proj = projetoSelecionado();
  const ativos = proj ? proj.padroes : state.padroesAtivos;
  const conflitos = conflitosAtuais(ativos);
  $("c-padroes").textContent = `${ativos.length} / ${state.data.padroes.length}`;

  const hdr = $("pat-mode-header");
  if (hdr) {
    setChildren(hdr,
      el("div", { class: "card-title" },
        state.modoExcludente ? "Exclusão Mútua: ATIVA" : "Modo Livre: ATIVO",
        el("button", {
          class: "btn btn-sm " + (state.modoExcludente ? "btn-amber" : ""),
          onclick: () => {
            state.modoExcludente = !state.modoExcludente;
            if (state.modoExcludente && !proj) {
              const limpos = [];
              for (const p of state.padroesAtivos) {
                if (!conflitosAtuais(limpos)[p]) limpos.push(p);
              }
              state.padroesAtivos = limpos;
            }
            atualizarConteudoPadroes();
            renderCmdPreview();
          },
        }, state.modoExcludente ? "Modo Livre" : "Ativar Exclusão")
      ),
      el("div", { class: "card-sub" },
        state.modoExcludente
          ? "Padrões concorrentes pelo mesmo papel arquitetural ficam desativados automaticamente."
          : "Todos os 28 padrões podem ser combinados livremente.")
    );
  }

  const dropzone = $("pat-drop-slot");
  if (dropzone) {
    setChildren(dropzone,
      ativos.length
        ? ativos.map((ch) =>
            el("span", { class: "snap-chip" },
              nomePadrao(ch),
              !proj ? el("button", { title: "Desencaixar", onclick: () => togglePadrao(ch) }, "x") : null
            )
          )
        : el("span", { class: "dropzone-empty" }, "Arraste ou clique nos padrões abaixo para encaixar no projeto")
    );
  }

  const groupsSlot = $("pat-groups-slot");
  if (!groupsSlot) return;
  const porCat = new Map();
  const q = state.buscaPadrao.trim().toLowerCase();
  for (const p of state.data.padroes) {
    if (q && !p.chave.includes(q) && !p.titulo.toLowerCase().includes(q) && !p.problema.toLowerCase().includes(q)) continue;
    if (!porCat.has(p.categoria_nome)) porCat.set(p.categoria_nome, []);
    porCat.get(p.categoria_nome).push(p);
  }

  const blocosCat = [];
  for (const [catNome, lista] of porCat.entries()) {
    blocosCat.push(el("div", { class: "pat-group-title" }, catNome));
    blocosCat.push(el("div", { class: "pat-grid" },
      ...lista.map((p) => {
        const isAtivo = ativos.includes(p.chave);
        const bl = conflitos[p.chave];
        const cls = "pat-block" + (isAtivo ? " ativo" : "") + (bl ? " bloqueado" : "");
        return el("div", {
          class: cls,
          draggable: !proj && !bl && !isAtivo,
          title: `${p.conceito}\n\nQuando não usar: ${p.quando_nao}`,
          ondragstart: (e) => e.dataTransfer.setData("text/sgs-pat", p.chave),
          onclick: () => { if (!bl) togglePadrao(p.chave); },
        },
          el("div", { class: "pat-top" },
            el("span", { class: "pat-name" },
              p.titulo.split(" (")[0],
              isAtivo ? el("span", { class: "pat-badge on" }, "ATIVO")
                      : (bl ? el("span", { class: "pat-badge bloq" }, "EXCLUDENTE") : null)
            ),
            el("span", { class: "pat-mod" }, `nucleo/${p.modulo}.py`)
          ),
          el("div", { class: "pat-desc" }, p.problema),
          bl
            ? el("div", { class: "pat-lock" },
                el("span", {}, `Excludente com ${bl.bloqueado_por.map(nomePadrao).join(", ")} (${bl.titulo})`),
                !proj
                  ? el("button", {
                      class: "btn-swap",
                      onclick: (e) => { e.stopPropagation(); trocarPadrao(p.chave, bl.bloqueado_por); },
                    }, "Trocar")
                  : null
              )
            : null
        );
      })
    ));
  }
  setChildren(groupsSlot, ...blocosCat);
}

function renderColPadroes() {
  const box = $("col-padroes");
  const proj = projetoSelecionado();
  const modo = proj ? proj.numero : "__novo__";

  if (state._colPatModo !== modo) {
    state._colPatModo = modo;
    const ctrlCard = el("div", { class: "card" },
      el("div", { id: "pat-mode-header" }),
      !proj
        ? el("div", { class: "pill-group", style: "margin-top:7px" },
            el("button", { class: "btn btn-sm", onclick: () => aplicarPreset("prova") }, "Prova (9)"),
            el("button", { class: "btn btn-sm", onclick: () => aplicarPreset("criacao") }, "Criação"),
            el("button", { class: "btn btn-sm", onclick: () => aplicarPreset("estrutural") }, "Estrutural"),
            el("button", { class: "btn btn-sm", onclick: () => aplicarPreset("comportamental") }, "Comportamental"),
            el("button", { class: "btn btn-sm", onclick: () => aplicarPreset("todos") }, "Todos (28)"),
            el("button", { class: "btn btn-sm", onclick: () => { state.padroesAtivos = []; atualizarConteudoPadroes(); renderCmdPreview(); } }, "Limpar")
          )
        : null,
      el("div", { style: "margin-top:7px" },
        el("input", {
          class: "inp", id: "inp-busca-padrao",
          placeholder: "Filtrar padrões (ex.: strategy, factory, state...)",
          value: state.buscaPadrao,
          oninput: (e) => { state.buscaPadrao = e.target.value; atualizarConteudoPadroes(); },
        })
      )
    );

    const dropzone = el("div", {
      class: "dropzone", id: "pat-drop-slot",
      ondragover: (e) => {
        if (!projetoSelecionado() && e.dataTransfer.types.includes("text/sgs-pat")) { e.preventDefault(); dropzone.classList.add("over"); }
      },
      ondragleave: () => dropzone.classList.remove("over"),
      ondrop: (e) => {
        dropzone.classList.remove("over");
        const p = e.dataTransfer.getData("text/sgs-pat");
        if (p && !state.padroesAtivos.includes(p)) { e.preventDefault(); togglePadrao(p); }
      },
    });

    setChildren(box, ctrlCard, dropzone, el("div", { class: "pat-groups-slot", id: "pat-groups-slot" }));
  }
  atualizarConteudoPadroes();
}

/* ---- RODAPÉ: COMANDO EQUIVALENTE + GAVETA DE LOG / CÓDIGO ---- */
function renderCmdPreview() {
  $("cmd-preview").textContent = comandoEquivalente();
}

async function abrirArquivoProjeto(proj, caminho) {
  state.arquivoAberto = caminho;
  state.conteudoArquivo = "Carregando...";
  renderDrawer();
  const r = await fetch(`/arquivo?pasta=${encodeURIComponent(proj.pasta)}&caminho=${encodeURIComponent(caminho)}`);
  const d = await r.json();
  state.conteudoArquivo = d.ok ? d.conteudo : (d.erro || "Erro ao ler arquivo.");
  renderDrawer();
}

function renderDrawer() {
  const dr = $("drawer");
  dr.hidden = !state.drawerAberto;
  $("btn-drawer").textContent = state.drawerAberto ? "Ocultar Console & Código" : "Console & Código";
  if (!state.drawerAberto) return;

  $("tab-log").className = "btn btn-sm" + (state.drawerAba === "log" ? " btn-primary" : "");
  $("tab-code").className = "btn btn-sm" + (state.drawerAba === "code" ? " btn-primary" : "");
  const body = $("drawer-body");
  const proj = projetoSelecionado();

  if (state.drawerAba === "log") {
    $("drawer-info").textContent = "Saída do motor SGS";
    setChildren(body, el("pre", { class: "log-pane" }, state.logTexto));
  } else if (!proj) {
    $("drawer-info").textContent = "Selecione um projeto gerado";
    setChildren(body, el("pre", { class: "log-pane" }, "Selecione um projeto existente na barra superior para inspecionar o código-fonte."));
  } else {
    $("drawer-info").textContent = `${proj.pasta} · ${state.arquivoAberto || `${proj.arquivos.length} arquivo(s)`}`;
    setChildren(body,
      el("div", { class: "code-split" },
        el("div", { class: "file-tree" },
          ...proj.arquivos.map((arq) =>
            el("button", {
              class: "file-btn" + (arq === state.arquivoAberto ? " ativo" : ""),
              onclick: () => abrirArquivoProjeto(proj, arq),
            }, arq)
          )
        ),
        el("pre", { class: "code-view" }, state.conteudoArquivo || "Clique em um arquivo à esquerda para visualizar.")
      )
    );
  }
}

function renderAll() {
  if (!state.data) return;
  renderTopbar();
  renderColDominio();
  renderColClasses();
  renderColLigacoes();
  renderColPadroes();
  renderCmdPreview();
  renderDrawer();
}

/* ---- EVENTOS GLOBAIS ---- */
$("btn-copiar").onclick = () => {
  navigator.clipboard?.writeText(comandoEquivalente()).then(() => toast("Comando copiado.", "ok")).catch(() => {});
};
$("btn-exec-cmd").onclick = () => executarComando(comandoEquivalente());
$("btn-drawer").onclick = () => { state.drawerAberto = !state.drawerAberto; renderDrawer(); };
$("btn-fechar-drawer").onclick = () => { state.drawerAberto = false; renderDrawer(); };
$("tab-log").onclick = () => { state.drawerAba = "log"; renderDrawer(); };
$("tab-code").onclick = () => {
  state.drawerAba = "code";
  const proj = projetoSelecionado();
  if (proj && !state.arquivoAberto && proj.arquivos.length) abrirArquivoProjeto(proj, proj.arquivos[0]);
  renderDrawer();
};

(function init() {
  const params = new URLSearchParams(location.search);
  const pInit = params.get("projeto");
  carregarEstado(pInit || null);
})();
</script>
</body>
</html>
"""

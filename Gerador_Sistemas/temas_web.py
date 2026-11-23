"""
TEMAS da formatação "web" dos sistemas gerados (Bootstrap + cores).

Fonte das cores:
  * pasta temas/ (imagens tons-6-T01-T05.png, tons-6-T06-T10.png e config-6-tons-tom3.png):
    10 temas × 6 tons (Claro, Tom 2, Tom 3, Tom 4, Tom 5, Escuro). Os FUNDOS e SUPERFÍCIES de cada
    combinação estão escritos nas imagens e foram copiados exatamente. A cor de DESTAQUE de T01
    (#1B4D3E) e a do T09 escuro (#4DA3FF) estão escritas nos documentos; as dos outros temas foram
    lidas das imagens (aproximadas) — e todas passam pela checagem de contraste abaixo.
  * Instruções de desenvolvimento DJANGO, §11.7 (três cores: Fundos, Destaques, Escritas; contraste
    WCAG 2.1: Escritas × Fundos ≥ 4,5:1 — 7:1 no Acessível; Destaques × Fundos ≥ 3:1 — 4,5:1 no
    Acessível; texto sobre Destaque branco ou preto, o de maior contraste), §11.9 (20 paletas
    sugeridas, usadas pelo T10 Personalizado) e §11.10 (eixos de estilo em atributos data-*).

Tudo aqui é determinístico: o mesmo tema/tom/paleta gera sempre o mesmo CSS.
"""

TONS = ["claro", "tom2", "tom3", "tom4", "tom5", "escuro"]
NOMES_TONS = {"claro": "Claro", "tom2": "Tom 2", "tom3": "Tom 3", "tom4": "Tom 4", "tom5": "Tom 5", "escuro": "Escuro"}

# (fundo, superfície) por tom, copiados das imagens da pasta temas/.
_FUNDOS = {
    "T01": [("#F8FAF8", "#FFFFFF"), ("#D3D6D4", "#E7E8E7"), ("#B0B6B3", "#C0C5C2"), ("#989E9B", "#A8AEAB"),
            ("#48514E", "#58615E"), ("#121816", "#232826")],
    "T02": [("#FAF8FB", "#FFFFFF"), ("#D6D3D7", "#E8E7E9"), ("#B6B0BC", "#C5C0C9"), ("#A098A7", "#AFA8B5"),
            ("#52495C", "#62596B"), ("#17131D", "#27242D")],
    "T03": [("#F8FAFC", "#FFFFFF"), ("#D3D6DA", "#E7E8EB"), ("#B0B4BC", "#C0C3C9"), ("#979DA6", "#A8ADB4"),
            ("#474F5E", "#585F6C"), ("#0F172A", "#202739")],
    "T04": [("#FFF5F8", "#FFFFFF"), ("#DBD1D4", "#EBE6E7"), ("#C0ADB4", "#CDBDC3"), ("#AB969D", "#B8A7AD"),
            ("#5E4750", "#6C5860"), ("#1E1216", "#2E2326")],
    "T05": [("#FCF9F5", "#FFFFFF"), ("#D8D5D1", "#EAE8E6"), ("#BEB6AD", "#CBC5BD"), ("#AA9F96", "#B8AEA7"),
            ("#5E5248", "#6C6258"), ("#1A1715", "#2A2725")],
    "T06": [("#FAF8F5", "#FFFFFF"), ("#D6D4D1", "#E8E7E6"), ("#B9B5AE", "#C7C4BE"), ("#A39F96", "#B2AEA7"),
            ("#565148", "#656158"), ("#1A1713", "#2A2724")],
    "T07": [("#F0F7FF", "#FFFFFF"), ("#CCD3DC", "#E3E7EC"), ("#A7B6C2", "#B9C5CE"), ("#8EA0AE", "#A0AFBB"),
            ("#405464", "#516372"), ("#0C1824", "#1D2833")],
    "T08": [("#F5F6FC", "#FFFFFF"), ("#D0D2DA", "#E5E6EB"), ("#AFB1C1", "#BFC1CD"), ("#9899AD", "#A8A9BA"),
            ("#494B65", "#595B73"), ("#101426", "#212435")],
    "T09": [("#FFFFFF", "#FFFFFF"), ("#D8D8D8", "#EAEAEA"), ("#B5B7BA", "#C4C5C8"), ("#9C9FA2", "#ACAEB1"),
            ("#43474D", "#54585D"), ("#0A0A0A", "#1B1B1B")],
    "T10": [("#F8FAF8", "#FFFFFF"), ("#D5D7D6", "#E8E9E8"), ("#B3B7B7", "#C2C5C5"), ("#9BA2A1", "#ABB1B0"),
            ("#505658", "#606567"), ("#1E2125", "#2E3134")],
}

# Nome, descrição (das imagens), destaque e eixos de estilo (Instruções §11.6 e §11.10, pelo NOME do modelo).
TEMAS = {
    "T01": {"nome": "Profissional", "descricao": "Corporativo equilibrado (padrão do sistema).", "destaque": "#1B4D3E",
            "raio": "suave", "sombra": "suave", "movimento": "discreto", "tipografia": "sans"},
    "T02": {"nome": "Sofisticado", "descricao": "Elegante e contido; títulos serifados e filetes finos.",
            "destaque": "#6B2A9E", "raio": "suave", "sombra": "nenhuma", "movimento": "discreto",
            "tipografia": "serifa-titulos"},
    "T03": {"nome": "Sóbrio", "descricao": "Neutro e formal; cantos retos e sem sombras.", "destaque": "#334155",
            "raio": "reto", "sombra": "nenhuma", "movimento": "nenhum", "tipografia": "sans"},
    "T04": {"nome": "Animado", "descricao": "Dinâmico e energético; sombras marcadas e movimento expressivo.",
            "destaque": "#BE185D", "raio": "arredondado", "sombra": "marcada", "movimento": "expressivo",
            "tipografia": "arredondada"},
    "T05": {"nome": "Alegre", "descricao": "Vivo e acolhedor; tons quentes e cantos arredondados.",
            "destaque": "#B45309", "raio": "pilula", "sombra": "suave", "movimento": "discreto",
            "tipografia": "arredondada"},
    "T06": {"nome": "Luxuoso", "descricao": "Exclusivo; tons dourados clássicos e bronze.", "destaque": "#8A6A1F",
            "raio": "reto", "sombra": "nenhuma", "movimento": "discreto", "tipografia": "serifa-titulos"},
    "T07": {"nome": "SoftClean", "descricao": "Leve e limpo; azul céu corporativo moderno.", "destaque": "#0B6FA4",
            "raio": "arredondado", "sombra": "difusa", "movimento": "discreto", "tipografia": "sans"},
    "T08": {"nome": "Noturno", "descricao": "Índigo profundo / Midnight equilibrado.", "destaque": "#4338CA",
            "raio": "suave", "sombra": "nenhuma", "movimento": "discreto", "tipografia": "sans"},
    "T09": {"nome": "Acessível", "descricao": "Alto contraste WCAG AAA (≥ 7:1) e foco reforçado.",
            "destaque": "#0B3D91", "destaque_escuro": "#4DA3FF", "raio": "suave", "sombra": "nenhuma",
            "movimento": "nenhum", "tipografia": "sans", "acessivel": True},
    "T10": {"nome": "Personalizado", "descricao": "Modelo livre: as cores vêm de uma paleta (P01–P20).",
            "destaque": None, "raio": "suave", "sombra": "suave", "movimento": "discreto", "tipografia": "sans"},
}

# Instruções §11.9 — paletas sugeridas (Fundos, Destaques, Escritas). O T10 usa o Destaque da paleta escolhida.
PALETAS = {
    "P01": ("Oceano", "#F0F7FF", "#0B5FA5", "#0B1F33"), "P02": ("Floresta", "#F2F8F2", "#1F6B3A", "#10261A"),
    "P03": ("Terracota", "#FBF4EE", "#B4502B", "#2B1A12"), "P04": ("Lavanda", "#F7F3FF", "#6D3FC4", "#231942"),
    "P05": ("Grafite", "#F4F4F5", "#3F3F46", "#18181B"), "P06": ("Areia", "#FAF6EE", "#9A6B1F", "#2E2412"),
    "P07": ("Cereja", "#FFF5F6", "#B3123A", "#2A0E15"), "P08": ("Menta", "#F0FBF8", "#0F766E", "#0B2B28"),
    "P09": ("Céu", "#F2F9FF", "#0369A1", "#0C2A3D"), "P10": ("Pôr do sol", "#FFF7ED", "#C2410C", "#3B1B0A"),
    "P11": ("Ameixa", "#F8F2F8", "#7A2E7E", "#2B112C"), "P12": ("Esmeralda noturna", "#0B1F1A", "#34D399", "#E6FFF5"),
    "P13": ("Índigo noturno", "#0F1B3D", "#8AB4FF", "#E8EEFF"), "P14": ("Bordô e creme", "#FFF8F0", "#7B1E3A", "#2A1015"),
    "P15": ("Rosa chá", "#FFF5F7", "#BE185D", "#3A0A1F"), "P16": ("Turquesa", "#F0FDFC", "#0E7490", "#082F3A"),
    "P17": ("Oliva", "#F6F7EE", "#5B6B1F", "#1F2410"), "P18": ("Cobalto", "#F3F6FF", "#1D4ED8", "#0B1B4D"),
    "P19": ("Névoa", "#F5F7FA", "#4B6584", "#1B2733"), "P20": ("Alto contraste", "#FFFFFF", "#0033A0", "#000000"),
}

ESCRITA_CLARA, ESCRITA_ESCURA = "#E8ECEA", "#191F2B"


# ----------------------------------------------------------------- cor e contraste (WCAG 2.1)
def _rgb(hexa):
    return tuple(int(hexa[i:i + 2], 16) for i in (1, 3, 5))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def luminancia(hexa):
    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in _rgb(hexa))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    """Razão de contraste WCAG entre duas cores (1 a 21)."""
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def misturar(a, b, peso):
    """peso 0 → a; peso 1 → b."""
    return _hex(tuple(x + (y - x) * peso for x, y in zip(_rgb(a), _rgb(b))))


def ajustar_contraste(cor, fundo, minimo):
    """Clareia ou escurece a cor (preservando o matiz) até atingir o contraste mínimo contra o fundo."""
    alvo = "#FFFFFF" if luminancia(fundo) < 0.18 else "#000000"
    passo = 0
    while contraste(cor, fundo) < minimo and passo < 40:
        cor = misturar(cor, alvo, 0.06)
        passo += 1
    return cor


# ----------------------------------------------------------------- o tema resolvido
def resolver(tema="T01", tom="tom3", paleta="P02"):
    """As cores finais (já com contraste validado) de um tema × tom (× paleta, no T10)."""
    if tema not in TEMAS:
        raise ValueError(f"tema desconhecido: {tema} (use T01 a T10)")
    if tom not in TONS:
        raise ValueError(f"tom desconhecido: {tom} (use {', '.join(TONS)})")
    if paleta not in PALETAS:
        raise ValueError(f"paleta desconhecida: {paleta} (use P01 a P20)")
    info = TEMAS[tema]
    fundo, superficie = _FUNDOS[tema][TONS.index(tom)]
    escuro = luminancia(fundo) < 0.18
    acessivel = info.get("acessivel", False)
    escrita = ESCRITA_CLARA if contraste(ESCRITA_CLARA, fundo) > contraste(ESCRITA_ESCURA, fundo) else ESCRITA_ESCURA
    if acessivel:
        escrita = "#FFFFFF" if escuro else "#000000"
    destaque = PALETAS[paleta][2] if tema == "T10" else (info.get("destaque_escuro") if escuro and acessivel
                                                         else info["destaque"])
    destaque = ajustar_contraste(destaque, fundo, 4.5 if acessivel else 3.0)
    escrita = ajustar_contraste(escrita, fundo, 7.0 if acessivel else 4.5)
    sobre = "#FFFFFF" if contraste("#FFFFFF", destaque) >= contraste("#000000", destaque) else "#000000"
    return {
        "tema": tema, "nome": info["nome"], "tom": tom, "paleta": paleta if tema == "T10" else None,
        "fundo": fundo, "superficie": superficie, "escrita": escrita, "destaque": destaque,
        "sobre_destaque": sobre, "borda": misturar(fundo, escrita, 0.22), "atenuado": misturar(escrita, fundo, 0.35),
        "destaque_hover": misturar(destaque, "#000000" if not escuro else "#FFFFFF", 0.15),
        "escuro": escuro, "raio": info["raio"], "sombra": info["sombra"], "movimento": info["movimento"],
        "tipografia": info["tipografia"], "acessivel": acessivel,
        "contraste_escrita": round(contraste(escrita, fundo), 2), "contraste_destaque": round(contraste(destaque, fundo), 2),
    }


def css(tema="T01", tom="tom3", paleta="P02"):
    """O tema.css de um sistema gerado: variáveis próprias (--sgs-*) que reconfiguram o Bootstrap."""
    t = resolver(tema, tom, paleta)
    r, g, b = _rgb(t["destaque"])
    rotulo = f"{t['tema']} {t['nome']} · {NOMES_TONS[tom]}" + (f" · paleta {paleta} {PALETAS[paleta][0]}" if t["paleta"] else "")
    return f"""/* Tema {rotulo} — gerado pelo SGS (temas_web.py), sem edição manual.
   Contraste WCAG: escrita × fundo {t['contraste_escrita']}:1 · destaque × fundo {t['contraste_destaque']}:1 */
:root, [data-bs-theme] {{
  --sgs-fundo: {t['fundo']};
  --sgs-superficie: {t['superficie']};
  --sgs-escrita: {t['escrita']};
  --sgs-destaque: {t['destaque']};
  --sgs-destaque-hover: {t['destaque_hover']};
  --sgs-sobre-destaque: {t['sobre_destaque']};
  --sgs-borda: {t['borda']};
  --sgs-atenuado: {t['atenuado']};
  --bs-body-bg: var(--sgs-fundo);
  --bs-body-color: var(--sgs-escrita);
  --bs-emphasis-color: var(--sgs-escrita);
  --bs-secondary-color: var(--sgs-atenuado);
  --bs-secondary-bg: var(--sgs-superficie);
  --bs-tertiary-bg: var(--sgs-superficie);
  --bs-border-color: var(--sgs-borda);
  --bs-primary: var(--sgs-destaque);
  --bs-primary-rgb: {r}, {g}, {b};
  --bs-link-color: var(--sgs-destaque);
  --bs-link-color-rgb: {r}, {g}, {b};
  --bs-link-hover-color: var(--sgs-destaque-hover);
  --bs-focus-ring-color: rgba({r}, {g}, {b}, .35);
}}
.navbar-sgs {{ background-color: var(--sgs-destaque); color: var(--sgs-sobre-destaque); }}
.navbar-sgs .navbar-brand, .navbar-sgs .nav-link {{ color: var(--sgs-sobre-destaque); }}
.btn-primary {{
  --bs-btn-bg: var(--sgs-destaque); --bs-btn-border-color: var(--sgs-destaque);
  --bs-btn-color: var(--sgs-sobre-destaque); --bs-btn-hover-color: var(--sgs-sobre-destaque);
  --bs-btn-hover-bg: var(--sgs-destaque-hover); --bs-btn-hover-border-color: var(--sgs-destaque-hover);
  --bs-btn-active-bg: var(--sgs-destaque-hover); --bs-btn-active-color: var(--sgs-sobre-destaque);
}}
.btn-outline-primary {{
  --bs-btn-color: var(--sgs-destaque); --bs-btn-border-color: var(--sgs-destaque);
  --bs-btn-hover-bg: var(--sgs-destaque); --bs-btn-hover-color: var(--sgs-sobre-destaque);
}}
.card {{ --bs-card-bg: var(--sgs-superficie); --bs-card-color: var(--sgs-escrita); --bs-card-border-color: var(--sgs-borda); }}
.table {{ --bs-table-bg: var(--sgs-superficie); --bs-table-color: var(--sgs-escrita); --bs-table-border-color: var(--sgs-borda);
          --bs-table-hover-bg: rgba({r}, {g}, {b}, .08); --bs-table-hover-color: var(--sgs-escrita); }}
.form-control, .form-select {{ background-color: var(--sgs-superficie); color: var(--sgs-escrita); border-color: var(--sgs-borda); }}
.badge-destaque {{ background-color: var(--sgs-destaque); color: var(--sgs-sobre-destaque); }}
"""

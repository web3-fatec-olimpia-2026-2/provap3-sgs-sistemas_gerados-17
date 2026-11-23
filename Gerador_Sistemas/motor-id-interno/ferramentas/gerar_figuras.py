"""
Gera as figuras SVG da especificação (imagens/*.svg) a partir da implementação de referência
e de analise/resultados.json (rode antes ferramentas/analise_deteccao.py).

Uso:  python ferramentas/gerar_figuras.py
SVG autocontido (fundo branco, cores explícitas): renderiza igual em GitHub, GitLab,
VS Code e navegadores, nos temas claro e escuro.
"""
from __future__ import annotations

import json
import math
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'referencia' / 'python'))
import lnnl  # noqa: E402

SAIDA = RAIZ / 'imagens'
RES = json.loads((RAIZ / 'analise' / 'resultados.json').read_text(encoding='utf-8'))

TINTA = '#111827'
SUAVE = '#4B5563'
BORDA = '#D1D5DB'
FUNDO = '#FFFFFF'
FAIXA = '#F3F4F6'
TIPO = ('#DBEAFE', '#1E40AF')        # preenchimento, texto/contorno
VERIF = ('#FEF3C7', '#92400E')
LETRA = ('#F3F4F6', '#1F2937')
DIGITO = ('#E0E7FF', '#3730A3')
VERDE = '#047857'
CINZA_A = '#9CA3AF'
CINZA_B = '#6B7280'
VERMELHO = '#B91C1C'
FONTE = "font-family='Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif'"
MONO = "font-family='JetBrains Mono, Consolas, Menlo, monospace'"


def svg(largura, altura, corpo, titulo):
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {largura} {altura}' width='{largura}' "
        f"height='{altura}' role='img' aria-labelledby='t'>\n<title id='t'>{escape(titulo)}</title>\n"
        f"<rect width='100%' height='100%' fill='{FUNDO}'/>\n{corpo}\n</svg>\n"
    )


def texto(x, y, s, tam=14, cor=TINTA, peso=400, ancora='start', mono=False, extra=''):
    return (f"<text x='{x}' y='{y}' font-size='{tam}' fill='{cor}' font-weight='{peso}' "
            f"text-anchor='{ancora}' {MONO if mono else FONTE} {extra}>{escape(str(s))}</text>")


def caixa(x, y, w, h, fill, stroke=BORDA, r=6, sw=1, extra=''):
    return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{r}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' {extra}/>"


def pct(v, casas=2):
    return f'{v * 100:.{casas}f}%'.replace('.', ',')


def milhar(n):
    return f'{n:,}'.replace(',', '.')


def gravar(nome, conteudo):
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / nome).write_text(conteudo, encoding='utf-8')
    print('gerado', nome)


# ------------------------------------------------------------------ 01 anatomia
def fig_anatomia():
    exemplo = 'K12WF22MT5RQ7L'
    papeis = ['L', 'T', 'T', 'L', 'L', 'V', 'V', 'L', 'L', 'N', 'L', 'L', 'N', 'L']
    estilo = {'L': LETRA, 'T': TIPO, 'V': VERIF, 'N': DIGITO}
    grupos = [(0, 4), (4, 8), (8, 11), (11, 14)]
    W, cel, gap, sep = 960, 52, 6, 26
    xs, x = [], 40
    for g, (a, b) in enumerate(grupos):
        for i in range(a, b):
            xs.append(x)
            x += cel + gap
        x += sep
    corpo = [texto(40, 40, 'Anatomia do identificador LNNL (14 caracteres, exibido em 4 grupos)', 20, peso=700)]
    corpo.append(texto(40, 66, 'Máscara LNNL-LNNL-LNL-LNL · L = letra A–Z (26) · N = dígito 1–9 (9; o 0 não existe para não ser confundido com O)', 13, SUAVE))
    y = 110
    for i, (ch, p) in enumerate(zip(exemplo, papeis)):
        f, t = estilo[p]
        corpo.append(caixa(xs[i], y, cel, cel, f, t if p in 'TV' else BORDA, sw=2 if p in 'TV' else 1))
        corpo.append(texto(xs[i] + cel / 2, y + 35, ch, 26, t, 700, 'middle', mono=True))
        corpo.append(texto(xs[i] + cel / 2, y - 10, i + 1, 11, SUAVE, ancora='middle'))
        corpo.append(texto(xs[i] + cel / 2, y + cel + 18, lnnl.CLASSES[i], 13, SUAVE, 600, 'middle', mono=True))
    for g, (a, b) in enumerate(grupos[:-1]):
        xh = xs[b - 1] + cel + (gap + sep) / 2
        corpo.append(texto(xh, y + 34, '–', 24, SUAVE, ancora='middle'))
    # chaves dos papéis
    def chave(i0, i1, rot, cor, yb):
        x0, x1 = xs[i0], xs[i1] + cel
        return (f"<path d='M{x0} {yb} v8 H{x1} v-8' fill='none' stroke='{cor}' stroke-width='2'/>"
                + texto((x0 + x1) / 2, yb + 28, rot, 13, cor, 700, 'middle'))
    yb = y + cel + 32
    corpo.append(chave(1, 2, 'Tipo (2 dígitos)', TIPO[1], yb))
    corpo.append(chave(5, 6, 'Verificadores (mód. 79)', VERIF[1], yb))
    corpo.append(chave(9, 9, 'livre', DIGITO[1], yb))
    corpo.append(chave(12, 12, 'livre', DIGITO[1], yb))
    # legenda
    ly = 300
    itens = [
        (LETRA, 'Letra livre (8 posições, sorteadas)'),
        (DIGITO, 'Dígito livre (2 posições, sorteadas)'),
        (TIPO, 'Código do tipo (11–99 sem zero; 93 reservado)'),
        (VERIF, 'Verificadores: derivados dos outros 12'),
    ]
    for k, ((f, t), rot) in enumerate(itens):
        lx = 40 + (k % 2) * 450
        yy = ly + (k // 2) * 30
        corpo.append(caixa(lx, yy - 14, 18, 18, f, t, r=4))
        corpo.append(texto(lx + 28, yy, rot, 13))
    corpo.append(texto(40, 380, 'Canônico (armazenado): K12WF22MT5RQ7L  ·  Exibição: K12W-F22M-T5R-Q7L  ·  Entrada aceita: k12w f22m t5r q7l', 13, SUAVE, mono=True))
    corpo.append(texto(40, 404, 'Como cada posição tem classe fixa, 0/O, 1/I, 5/S e 8/B nunca são ambíguos: a posição diz se é letra ou dígito.', 13, SUAVE))
    gravar('01-anatomia.svg', svg(W, 430, '\n'.join(corpo), 'Anatomia do identificador LNNL'))


# ------------------------------------------------------------------ 02 cálculo
def fig_calculo():
    dados = 'K12WFMT5RQ7L'
    posicoes = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14]
    valores = [lnnl.valor_caractere(c) for c in dados]
    produtos = [p * v for p, v in zip(lnnl.PESOS, valores)]
    soma = sum(produtos)
    r = soma % lnnl.MODULO
    d1, d2 = r // 9 + 1, r % 9 + 1
    W = 960
    x0, cw = 150, 62
    corpo = [texto(40, 40, 'Cálculo dos 2 dígitos verificadores (módulo 79)', 20, peso=700),
             texto(40, 66, 'Exemplo: dados K12W·F··M·T5R·Q7L → os 12 caracteres sem as posições 6 e 7', 13, SUAVE)]
    linhas = [('Posição', posicoes, SUAVE), ('Caractere', list(dados), TINTA), ('Valor', valores, DIGITO[1]),
              ('Peso', list(lnnl.PESOS), VERIF[1]), ('Peso × valor', produtos, TINTA)]
    y = 100
    for k, (rot, vals, cor) in enumerate(linhas):
        corpo.append(caixa(30, y - 22, W - 60, 34, FAIXA if k % 2 == 0 else FUNDO, 'none', r=0))
        corpo.append(texto(40, y, rot, 13, SUAVE, 600))
        for i, v in enumerate(vals):
            corpo.append(texto(x0 + i * cw + cw / 2, y, v, 15, cor, 700 if k in (1, 4) else 500, 'middle', mono=True))
        y += 34
    corpo.append(texto(40, y + 10, 'Valores: A=1 … Z=26 e dígitos 1–9 valem o próprio número.', 12, SUAVE))
    # fluxo
    fy = y + 50
    passos = [
        (f'Σ = {milhar(soma)}', 'soma ponderada'),
        (f'{milhar(soma)} mod 79 = {r}', 'resto r (0 … 78)'),
        (f'd1 = {r} div 9 + 1 = {d1}', '1º verificador'),
        (f'd2 = {r} mod 9 + 1 = {d2}', '2º verificador'),
    ]
    bw, bx = 205, 40
    for k, (a, b) in enumerate(passos):
        corpo.append(caixa(bx, fy, bw, 62, VERIF[0] if k >= 2 else FAIXA, VERIF[1] if k >= 2 else BORDA))
        corpo.append(texto(bx + bw / 2, fy + 28, a, 15, TINTA, 700, 'middle', mono=True))
        corpo.append(texto(bx + bw / 2, fy + 48, b, 12, SUAVE, ancora='middle'))
        if k < 3:
            corpo.append(f"<path d='M{bx + bw + 4} {fy + 31} h18' stroke='{SUAVE}' stroke-width='2' marker-end='url(#seta)'/>")
        bx += bw + 28
    corpo.insert(0, f"<defs><marker id='seta' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto'><path d='M0 0 L10 5 L0 10z' fill='{SUAVE}'/></marker></defs>")
    ry = fy + 110
    corpo.append(texto(40, ry, 'Resultado: os verificadores entram nas posições 6 e 7', 14, peso=700))
    final = f'K12W-F{d1}{d2}M-T5R-Q7L'
    corpo.append(texto(40, ry + 38, final, 30, TINTA, 700, mono=True))
    corpo.append(texto(420, ry + 30, 'Por que 79?  É primo e maior que a maior diferença entre dois', 13, SUAVE))
    corpo.append(texto(420, ry + 48, 'caracteres (25). Com pesos distintos e não nulos mód. 79, toda troca', 13, SUAVE))
    corpo.append(texto(420, ry + 66, 'de 1 caractere e toda transposição mudam o resto: detecção garantida.', 13, SUAVE))
    gravar('02-calculo-verificadores.svg', svg(W, ry + 92, '\n'.join(corpo), 'Cálculo dos verificadores LNNL'))


# ------------------------------------------------------------------ 03 grade dos restos
def fig_grade_restos():
    W, cel = 960, 46
    x0, y0 = 120, 110
    corpo = [texto(40, 40, 'Codificação do resto (0 … 78) nos dois verificadores', 20, peso=700),
             texto(40, 66, 'd1 = r div 9 + 1 (linha) · d2 = r mod 9 + 1 (coluna). 79 dos 81 pares são usados; 98 e 99 nunca são emitidos.', 13, SUAVE)]
    for j in range(9):
        corpo.append(texto(x0 + j * cel + cel / 2, y0 - 10, f'd2={j + 1}', 11, SUAVE, ancora='middle'))
    for i in range(9):
        corpo.append(texto(x0 - 12, y0 + i * cel + 28, f'd1={i + 1}', 11, SUAVE, ancora='end'))
        for j in range(9):
            r = i * 9 + j
            usado = r < 79
            corpo.append(caixa(x0 + j * cel, y0 + i * cel, cel - 4, cel - 4, VERIF[0] if usado else '#FEE2E2', VERIF[1] if usado else VERMELHO, r=4))
            corpo.append(texto(x0 + j * cel + (cel - 4) / 2, y0 + i * cel + 20, f'{i + 1}{j + 1}', 13, TINTA, 700, 'middle', mono=True))
            corpo.append(texto(x0 + j * cel + (cel - 4) / 2, y0 + i * cel + 35, f'r={r}' if usado else 'nunca', 10, SUAVE if usado else VERMELHO, ancora='middle'))
    tx = x0 + 9 * cel + 40
    linhas = ['Leitura rápida do exemplo', 'K12W-F22M-T5R-Q7L → par 22 → r = 10.', '',
              'Um par 98 ou 99 é rejeitado antes', 'de qualquer conta: é um sinal extra', 'de digitação errada.', '',
              'Os 2 dígitos guardam log₂ 79 ≈ 6,3 bits', 'de verificação — não consomem', 'espaço amostral: são derivados.']
    for k, l in enumerate(linhas):
        corpo.append(texto(tx, y0 + 14 + k * 22, l, 13 if k else 14, TINTA if k == 0 else SUAVE, 700 if k == 0 else 400))
    gravar('03-grade-restos.svg', svg(W, y0 + 9 * cel + 30, '\n'.join(corpo), 'Grade dos restos do módulo 79'))


# ------------------------------------------------------------------ 04 detecção comparativa
def fig_deteccao():
    ex = RES['exato']
    classes = [
        (('Troca de', '1 letra'), lambda r: r['substituicao']['letra']),
        (('Troca de', '1 dígito'), lambda r: r['substituicao']['digito']),
        (('Transposição', 'de vizinhos'), lambda r: r['transposicao_adjacente']),
        (('Transposição de', '2 posições quaisquer'), lambda r: r['transposicao_qualquer']),
        (('2 caracteres', 'errados'), lambda r: r['substituicao_dupla']),
        (('Código', 'aleatório'), lambda r: r['cadeia_aleatoria']),
    ]
    esquemas = [('A', CINZA_A), ('B', CINZA_B), ('C', VERDE)]
    W, H = 960, 500
    x0, y0, ah = 90, 100, 280
    vmax = 0.26
    corpo = [texto(40, 40, 'Erros que passam despercebidos, por esquema de verificador (menor é melhor)', 20, peso=700),
             texto(40, 66, 'Cálculo exato sobre os 12 caracteres de dados (contagem de todos os casos, sem amostragem).', 13, SUAVE)]
    for k in range(0, 6):
        v = k * 0.05
        yy = y0 + ah - v / vmax * ah
        corpo.append(f"<line x1='{x0}' x2='{W - 30}' y1='{yy}' y2='{yy}' stroke='{BORDA}' stroke-width='1'/>")
        corpo.append(texto(x0 - 8, yy + 4, f'{int(v * 100)}%', 11, SUAVE, ancora='end'))
    gw = (W - 30 - x0) / len(classes)
    bw = 34
    for c, (rot, f) in enumerate(classes):
        gx = x0 + c * gw + (gw - 3 * bw - 8) / 2
        for e, (chave, cor) in enumerate(esquemas):
            v = f(ex[chave])
            h = max(v / vmax * ah, 0)
            bx = gx + e * (bw + 4)
            if h > 0:
                corpo.append(f"<rect x='{bx}' y='{y0 + ah - h}' width='{bw}' height='{h}' rx='3' fill='{cor}'/>")
            else:
                corpo.append(f"<rect x='{bx}' y='{y0 + ah - 2}' width='{bw}' height='2' fill='{cor}'/>")
            corpo.append(texto(bx + bw / 2, y0 + ah - h - 6, pct(v, 1 if v else 0), 10, cor if cor != CINZA_A else SUAVE, 700, 'middle'))
        cx = x0 + c * gw + gw / 2
        corpo.append(texto(cx, y0 + ah + 22, rot[0], 12, TINTA, 600, 'middle'))
        corpo.append(texto(cx, y0 + ah + 38, rot[1], 12, TINTA, 600, 'middle'))
    ly = H - 28
    corpo.append(f"<line x1='40' x2='{W - 30}' y1='{ly - 26}' y2='{ly - 26}' stroke='{BORDA}'/>")
    lx = 90
    for chave, cor in esquemas:
        corpo.append(caixa(lx, ly - 12, 14, 14, cor, cor, r=3))
        corpo.append(texto(lx + 22, ly, ex[chave]['nome'], 13, TINTA, 700 if chave == 'C' else 400))
        lx += 290
    gravar('04-deteccao-comparativa.svg', svg(W, H, '\n'.join(corpo), 'Comparação de detecção de erros: mód. 9 × mód. 79'))


# ------------------------------------------------------------------ 05 mitigação
def fig_mitigacao():
    ex, mc = RES['exato'], RES['monte_carlo']
    casos = [
        ('1 caractere digitado errado', 1.0, ex['A']['substituicao']['qualquer'], mc['substituicao_14']),
        ('2 vizinhos trocados de lugar', 1.0, ex['A']['transposicao_adjacente'], mc['transposicao_adjacente_14']),
        ('2 caracteres errados (mesma classe)', 1.0, ex['A']['substituicao_dupla'], mc['substituicao_dupla_mesma_classe_14']),
        ('Código inventado, no formato certo', 1.0, ex['A']['cadeia_aleatoria'], mc['cadeia_aleatoria_14']),
    ]
    W = 960
    x0, bwmax = 330, 470
    corpo = [texto(40, 40, 'Mitigação de códigos digitados incorretamente', 20, peso=700),
             texto(40, 66, 'Fração de erros que seriam aceitos como válidos. "Sem verificador" = só o formato (o erro mantém a classe L/N).', 13, SUAVE)]
    y = 110
    rotulos = [('Sem verificador', VERMELHO), ('1 verificador mód. 9', CINZA_B), ('LNNL (2 verif. mód. 79)', VERDE)]
    for rot, sem, mod9, lnnl_v in casos:
        corpo.append(texto(40, y + 4, rot, 14, TINTA, 700))
        reducao = 1 - lnnl_v / sem
        corpo.append(texto(W - 40, y + 4, f'redução {pct(reducao, 2)}', 14, VERDE, 700, 'end'))
        for k, (v, (nome, cor)) in enumerate(zip((sem, mod9, lnnl_v), rotulos)):
            yy = y + 16 + k * 22
            corpo.append(texto(x0 - 10, yy + 12, nome, 12, SUAVE, ancora='end'))
            corpo.append(caixa(x0, yy, bwmax, 16, FAIXA, 'none', r=3))
            if v > 0:
                corpo.append(caixa(x0, yy, max(bwmax * v, 2), 16, cor, 'none', r=3))
            corpo.append(texto(x0 + max(bwmax * v, 2) + 8, yy + 12, pct(v, 2), 12, cor, 700))
        y += 112
    corpo.append(texto(40, y + 2, 'LNNL medido na implementação de referência sobre os 14 caracteres (Monte Carlo, '
                       f"{milhar(mc['amostras'])} amostras por caso); mód. 9 pelo cálculo exato.", 12, SUAVE))
    corpo.append(texto(40, y + 22, 'O verificador é filtro de digitação, não segurança: todo ID aceito ainda deve ser conferido no armazenamento.', 12, SUAVE))
    gravar('05-mitigacao.svg', svg(W, y + 44, '\n'.join(corpo), 'Mitigação de códigos digitados incorretamente'))


# ------------------------------------------------------------------ 06 espaço amostral
def fig_espacos():
    e = RES['espacos']
    itens = [
        ('LNNL, por tipo', e['lnnl_por_tipo_bits'], '14 (17 com hífens)', VERDE),
        ('LNNL, 80 tipos', e['lnnl_total_bits'], '14 (17 com hífens)', VERDE),
        ('Snowflake ID (63 bits úteis)', 63, '≤ 19 dígitos decimais', CINZA_B),
        ('TSID (64 bits totais)', 64, '13 (Crockford Base32)', CINZA_B),
        ('UUID v7 (parte aleatória)', 74, '36 (32 hex + 4 hífens)', '#2563EB'),
        ('ULID (parte aleatória)', 80, '26 (Crockford Base32)', CINZA_B),
        ('UUID v4', 122, '36 (32 hex + 4 hífens)', '#2563EB'),
        ('NanoID (21 car.)', 126, '21 (A–Z a–z 0–9 _-)', CINZA_B),
        ('KSUID (parte aleatória)', 128, '27 (Base62)', CINZA_B),
    ]
    W = 960
    x0, bmax, escala = 250, 470, 130
    corpo = [texto(40, 40, 'Espaço amostral em bits (escala logarítmica: cada bit dobra o espaço)', 20, peso=700),
             texto(40, 66, 'Entre parênteses à direita: tamanho do texto que um humano lê, dita ou digita.', 13, SUAVE)]
    y = 96
    for k in range(0, 129, 16):
        xx = x0 + k / escala * bmax
        corpo.append(f"<line x1='{xx}' x2='{xx}' y1='{y - 8}' y2='{y + len(itens) * 34}' stroke='{BORDA}'/>")
        corpo.append(texto(xx, y + len(itens) * 34 + 16, k, 11, SUAVE, ancora='middle'))
    for rot, bits, chars, cor in itens:
        corpo.append(texto(x0 - 10, y + 15, rot, 13, TINTA, 600, 'end'))
        corpo.append(caixa(x0, y + 2, bits / escala * bmax, 18, cor, 'none', r=3))
        corpo.append(texto(x0 + bits / escala * bmax + 8, y + 15, f'{bits:.1f} bits'.replace('.', ','), 12, cor, 700))
        corpo.append(texto(W - 30, y + 15, chars, 12, SUAVE, ancora='end'))
        y += 34
    y += 40
    corpo.append(texto(40, y, f"LNNL por tipo: 26⁸ × 9² = {milhar(e['lnnl_por_tipo'])} ≈ 1,69 × 10¹³", 13, TINTA, 600, mono=True))
    corpo.append(texto(40, y + 22, f"LNNL total:   80 × 26⁸ × 9² = {milhar(e['lnnl_total'])} ≈ 1,35 × 10¹⁵", 13, TINTA, 600, mono=True))
    razao = e['uuid_v4_espaco'] / e['lnnl_total']
    expoente = int(math.floor(math.log10(razao)))
    sobrescrito = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
    mantissa = f'{razao / 10 ** expoente:.1f}'.replace('.', ',')
    corpo.append(texto(40, y + 44, f'UUID v4:      2¹²² ≈ 5,32 × 10³⁶  (≈ {mantissa} × 10{str(expoente).translate(sobrescrito)} vezes o LNNL total)', 13, TINTA, 600, mono=True))
    gravar('06-espaco-amostral.svg', svg(W, y + 70, '\n'.join(corpo), 'Espaço amostral comparado'))


# ------------------------------------------------------------------ 07 posicionamento
def fig_posicionamento():
    W, H = 960, 560
    x0, y0, pw, ph = 100, 90, 500, 380
    bmin, bmax = 40, 168

    def px(chars):
        return x0 + (chars - 10) / (38 - 10) * pw

    def py(bits):
        return y0 + ph - (bits - bmin) / (bmax - bmin) * ph

    # (nome, caracteres exibidos, bits não fixos, cor, descrição, destaque, deslocamento do rótulo)
    pontos = [
        ('LNNL', 14, 50.3, VERDE, 'verificador e tipo embutidos; sem ordem', 1, (14, 5)),
        ('TSID', 13, 64, CINZA_B, 'ordenável no tempo; Crockford Base32', 0, (-34, -12)),
        ('Snowflake', 19, 63, CINZA_B, 'ordenável; exige ID de nó; sem verificador', 0, (10, -10)),
        ('NanoID', 21, 126, CINZA_B, 'aleatório; alfabeto configurável', 0, (-30, 24)),
        ('ULID', 26, 128, CINZA_B, 'ordenável; Crockford Base32', 0, (-18, -14)),
        ('KSUID', 27, 160, CINZA_B, 'ordenável (segundos); Base62', 0, (10, 5)),
        ('UUID v4 / v7', 36, 122, '#2563EB', 'padrão IETF (RFC 9562); v7 ordenável', 0, (-92, 24)),
    ]
    corpo = [texto(40, 40, 'Onde o LNNL se encaixa: esforço humano × espaço amostral', 20, peso=700),
             texto(40, 66, 'Eixo X: caracteres que uma pessoa lê ou dita. Eixo Y: bits não fixos do identificador (capacidade).', 13, SUAVE)]
    corpo.append(caixa(x0, y0, pw, ph, '#FAFAFA', BORDA, r=0))
    corpo.append(f"<rect x='{px(10)}' y='{y0}' width='{px(18) - px(10)}' height='{ph}' fill='#ECFDF5'/>")
    corpo.append(texto(px(14), y0 + 18, 'confortável para ditar', 11, VERDE, 600, 'middle'))
    for bb in range(40, 161, 20):
        corpo.append(f"<line x1='{x0}' x2='{x0 + pw}' y1='{py(bb)}' y2='{py(bb)}' stroke='{BORDA}' stroke-dasharray='3 3'/>")
        corpo.append(texto(x0 - 8, py(bb) + 4, bb, 11, SUAVE, ancora='end'))
    for c in range(10, 39, 4):
        corpo.append(texto(px(c), y0 + ph + 18, c, 11, SUAVE, ancora='middle'))
    corpo.append(texto(x0 + pw / 2, y0 + ph + 40, 'caracteres exibidos', 12, SUAVE, ancora='middle'))
    corpo.append(texto(x0 - 50, y0 + ph / 2, 'bits', 12, SUAVE, ancora='middle', extra=f"transform='rotate(-90 {x0 - 50} {y0 + ph / 2})'"))
    for nome, c, b, cor, _, destaque, (dx, dy) in pontos:
        r = 9 if destaque else 6
        corpo.append(f"<circle cx='{px(c)}' cy='{py(b)}' r='{r}' fill='{cor}' stroke='#FFFFFF' stroke-width='2'/>")
        corpo.append(texto(px(c) + dx, py(b) + dy, nome, 13 if destaque else 12, cor, 700))
    lx = x0 + pw + 30
    corpo.append(texto(lx, y0 + 6, 'Características', 14, TINTA, 700))
    for k, (nome, _, _, cor, desc, _, _) in enumerate(pontos):
        corpo.append(texto(lx, y0 + 34 + k * 44, nome, 12, cor, 700))
        corpo.append(texto(lx, y0 + 50 + k * 44, desc, 11, SUAVE))
    corpo.append(texto(lx, y0 + 34 + len(pontos) * 44, 'LNNL: menor texto com verificação,', 11, TINTA, 600))
    corpo.append(texto(lx, y0 + 50 + len(pontos) * 44, 'ao custo de espaço e de ordenação.', 11, TINTA, 600))
    gravar('07-posicionamento.svg', svg(W, H, '\n'.join(corpo), 'Posicionamento do LNNL entre UUID e Snowflake'))


# ------------------------------------------------------------------ 08 tipos
def fig_tipos():
    W, cel = 960, 46
    x0, y0 = 120, 110
    corpo = [texto(40, 40, 'Códigos de tipo: 81 combinações de 2 dígitos (1–9), 80 atribuíveis', 20, peso=700),
             texto(40, 66, 'O tipo ocupa as posições 2–3. 93 é reservado como escape para uma futura extensão do espaço de tipos.', 13, SUAVE)]
    for i in range(9):
        for j in range(9):
            cod = f'{i + 1}{j + 1}'
            reservado = cod == lnnl.TIPO_RESERVADO
            f, t = ('#FEE2E2', VERMELHO) if reservado else TIPO
            corpo.append(caixa(x0 + j * cel, y0 + i * cel, cel - 4, cel - 4, f, t, r=4,
                               extra="stroke-dasharray='4 3'" if reservado else ''))
            corpo.append(texto(x0 + j * cel + (cel - 4) / 2, y0 + i * cel + 27, cod, 15, t, 700, 'middle', mono=True))
    tx = x0 + 9 * cel + 40
    linhas = ['Regras do registro de tipos', '• Cada entidade recebe 1 código, para sempre.',
              '• Registro só cresce (append-only); nunca', '  reatribuir nem reaproveitar um código.',
              '• O tipo descreve a entidade, não o estado', '  (ex.: "pedido", não "pedido pago").',
              '• Sorteio offline e reprodutível (semente',
              '  registrada) evita códigos "óbvios".',
              '• 93 nunca é atribuído: se os 80 códigos', '  esgotarem, 93 sinaliza o tipo estendido.',
              '• O 0 não existe: 10, 20 … 90 e 01 … 09', '  não são códigos.']
    for k, l in enumerate(linhas):
        corpo.append(texto(tx, y0 + 14 + k * 22, l, 13 if k else 14, TINTA if k == 0 else SUAVE, 700 if k == 0 else 400))
    gravar('08-codigos-de-tipo.svg', svg(W, y0 + 9 * cel + 30, '\n'.join(corpo), 'Códigos de tipo LNNL'))


if __name__ == '__main__':
    fig_anatomia()
    fig_calculo()
    fig_grade_restos()
    fig_deteccao()
    fig_mitigacao()
    fig_espacos()
    fig_posicionamento()
    fig_tipos()

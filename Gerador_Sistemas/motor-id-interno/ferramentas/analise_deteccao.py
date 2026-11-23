"""
Análise de detecção de erros e de espaço amostral do padrão LNNL.

Duas partes:
1. Cálculo EXATO (contagem combinatória, sem amostragem) das taxas de erro não detectado,
   comparando três esquemas de verificador sobre os mesmos 12 caracteres de dados:
     A) 1 verificador módulo 9;
     B) 2 verificadores módulo 9 com pesos distintos;
     C) 2 verificadores módulo 79 (o LNNL).
2. Contraprova por simulação (Monte Carlo) sobre os 14 caracteres, usando a implementação
   de referência (referencia/python/lnnl.py), incluindo erros que mudam a classe L/N.

Uso:  python ferramentas/analise_deteccao.py            (grava analise/resultados.json)
      python ferramentas/analise_deteccao.py --amostras 200000 --semente 7
Somente biblioteca padrão.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'referencia' / 'python'))
import lnnl  # noqa: E402

LETRAS = range(1, 27)
DIGITOS = range(1, 10)
# Classes dos 12 caracteres de dados, na ordem dos pesos (posições 1–5 e 8–14).
CLASSES_DADOS = 'LNNLL' + 'LLNLLNL'

# Esquemas comparados: lista de (pesos, módulo); o erro passa despercebido se TODAS as
# congruências continuarem satisfeitas.
PESOS_COPRIMOS_9 = (1, 2, 4, 5, 7, 8, 1, 2, 4, 5, 7, 8)
PESOS_COPRIMOS_9_B = (2, 4, 8, 7, 5, 1, 5, 7, 1, 8, 4, 2)
ESQUEMAS = {
    'A': {'nome': '1 verificador, mód. 9', 'congruencias': [(PESOS_COPRIMOS_9, 9)]},
    'B': {'nome': '2 verificadores mód. 9 (pesos distintos)', 'congruencias': [(PESOS_COPRIMOS_9, 9), (PESOS_COPRIMOS_9_B, 9)]},
    'C': {'nome': '2 verificadores, mód. 79 (LNNL)', 'congruencias': [(lnnl.PESOS, lnnl.MODULO)]},
}


def alfabeto(classe):
    return LETRAS if classe == 'L' else DIGITOS


def assinatura(congruencias, i, delta):
    """Vetor de restos que um desvio 'delta' na posição i provoca em cada congruência."""
    return tuple((pesos[i] * delta) % m for pesos, m in congruencias)


def substituicao_simples(congruencias):
    por_classe = {'L': [0, 0], 'N': [0, 0]}
    for i, classe in enumerate(CLASSES_DADOS):
        for v in alfabeto(classe):
            for v2 in alfabeto(classe):
                if v == v2:
                    continue
                por_classe[classe][1] += 1
                if all(r == 0 for r in assinatura(congruencias, i, v2 - v)):
                    por_classe[classe][0] += 1
    total = [por_classe['L'][0] + por_classe['N'][0], por_classe['L'][1] + por_classe['N'][1]]
    return {
        'letra': por_classe['L'][0] / por_classe['L'][1],
        'digito': por_classe['N'][0] / por_classe['N'][1],
        'qualquer': total[0] / total[1],
    }


def transposicoes(congruencias, apenas_adjacentes):
    """Troca de dois caracteres de mesma classe (com valores diferentes)."""
    if apenas_adjacentes:
        # Pares adjacentes no identificador de 14 posições que são ambos dados e mesma classe:
        # (2,3) tipo, (4,5), (8,9), (11,12) letras → índices nos 12 dados.
        pares = [(1, 2), (3, 4), (5, 6), (8, 9)]
    else:
        pares = [(i, j) for i, j in combinations(range(12), 2) if CLASSES_DADOS[i] == CLASSES_DADOS[j]]
    nao_detectados = total = 0
    for i, j in pares:
        for a in alfabeto(CLASSES_DADOS[i]):
            for b in alfabeto(CLASSES_DADOS[j]):
                if a == b:
                    continue
                total += 1
                # Troca: posição i recebe b, j recebe a → desvio (b-a) em i e (a-b) em j.
                if all((pesos[i] * (b - a) + pesos[j] * (a - b)) % m == 0 for pesos, m in congruencias):
                    nao_detectados += 1
    return nao_detectados / total


def substituicao_dupla(congruencias):
    """Dois caracteres trocados (cada um por outro da mesma classe), em posições distintas. Exato."""
    hist = []
    for i, classe in enumerate(CLASSES_DADOS):
        h = Counter()
        for v in alfabeto(classe):
            for v2 in alfabeto(classe):
                if v != v2:
                    h[assinatura(congruencias, i, v2 - v)] += 1
        hist.append(h)
    nao_detectados = total = 0
    for i, j in combinations(range(12), 2):
        hi, hj = hist[i], hist[j]
        total += sum(hi.values()) * sum(hj.values())
        for sig, n in hi.items():
            oposto = tuple((-r) % m for r, (_, m) in zip(sig, congruencias))
            nao_detectados += n * hj.get(oposto, 0)
    return nao_detectados / total


def cadeia_aleatoria(congruencias):
    """Probabilidade de uma cadeia aleatória no formato correto passar na verificação."""
    if len(congruencias) == 1 and congruencias[0][1] == lnnl.MODULO:
        return 1 / 81  # 81 pares possíveis nas posições 6–7; exatamente 1 é o correto
    combinacoes = 1
    for _, m in congruencias:
        combinacoes *= 9  # cada verificador é um dígito de 1 a 9
    return 1 / combinacoes


def exato():
    saida = {}
    for chave, esquema in ESQUEMAS.items():
        c = esquema['congruencias']
        saida[chave] = {
            'nome': esquema['nome'],
            'substituicao': substituicao_simples(c),
            'transposicao_adjacente': transposicoes(c, True),
            'transposicao_qualquer': transposicoes(c, False),
            'substituicao_dupla': substituicao_dupla(c),
            'cadeia_aleatoria': cadeia_aleatoria(c),
        }
    return saida


SIMBOLOS_DIGITADOS = lnnl.LETRAS + lnnl.DIGITOS + '0'


def monte_carlo(amostras, semente):
    rng = random.Random(semente)
    ids = [lnnl.gerar(rng.choice(lnnl.codigos_tipo_disponiveis()), aleatorio=rng) for _ in range(2000)]

    def detectado(original, alterado):
        return alterado == original or not lnnl.validar(alterado)

    def subst(s, pos):
        ch = rng.choice([c for c in SIMBOLOS_DIGITADOS if c != s[pos]])
        return s[:pos] + ch + s[pos + 1:]

    res = {}
    # 1 caractere errado (qualquer símbolo, inclusive 0 e troca de classe)
    ok = 0
    for _ in range(amostras):
        s = rng.choice(ids)
        ok += detectado(s, subst(s, rng.randrange(14)))
    res['substituicao_14'] = 1 - ok / amostras
    # 2 caracteres errados
    ok = 0
    for _ in range(amostras):
        s = rng.choice(ids)
        i, j = rng.sample(range(14), 2)
        ok += detectado(s, subst(subst(s, i), j))
    res['substituicao_dupla_14'] = 1 - ok / amostras
    # 2 caracteres errados, mantendo a classe (o caso difícil: o formato não ajuda)
    ok = n = 0
    for _ in range(amostras):
        s = rng.choice(ids)
        i, j = rng.sample(range(14), 2)
        t = list(s)
        for p in (i, j):
            alfa = lnnl.LETRAS if lnnl.CLASSES[p] == 'L' else lnnl.DIGITOS
            t[p] = rng.choice([c for c in alfa if c != s[p]])
        alterado = ''.join(t)
        n += 1
        ok += detectado(s, alterado)
    res['substituicao_dupla_mesma_classe_14'] = 1 - ok / n
    # transposição de vizinhos (efetiva: caracteres diferentes)
    ok = n = 0
    for _ in range(amostras):
        s = rng.choice(ids)
        i = rng.randrange(13)
        if s[i] == s[i + 1]:
            continue
        n += 1
        ok += detectado(s, s[:i] + s[i + 1] + s[i] + s[i + 2:])
    res['transposicao_adjacente_14'] = 1 - ok / n
    # cadeia aleatória no formato
    ok = 0
    for _ in range(amostras):
        cad = ''.join(rng.choice(lnnl.LETRAS if c == 'L' else lnnl.DIGITOS) for c in lnnl.CLASSES)
        if cad[1:3] == lnnl.TIPO_RESERVADO:
            cad = cad[0] + '11' + cad[3:]
        ok += not lnnl.validar(cad)
    res['cadeia_aleatoria_14'] = 1 - ok / amostras
    res['amostras'] = amostras
    return res


def espacos_amostrais():
    por_tipo = 26 ** 8 * 9 ** 2
    tipos_atribuiveis = 80
    total = por_tipo * tipos_atribuiveis

    def bits(n):
        return math.log2(n)

    def n50(n):  # registros para 50% de chance de existir alguma colisão (aniversário)
        return math.sqrt(2 * n * math.log(2))

    return {
        'lnnl_por_tipo': por_tipo,
        'lnnl_por_tipo_bits': bits(por_tipo),
        'lnnl_tipos_teoricos': 81,
        'lnnl_tipos_atribuiveis': tipos_atribuiveis,
        'lnnl_total': total,
        'lnnl_total_bits': bits(total),
        'lnnl_grade_14': 26 ** 8 * 9 ** 6,
        'lnnl_aniversario_50pct_por_tipo': n50(por_tipo),
        'lnnl_colisao_por_insercao_com_1M': 1_000_000 / por_tipo,
        'uuid_v4_bits_aleatorios': 122,
        'uuid_v4_espaco': 2 ** 122,
        'uuid_v4_aniversario_50pct': n50(2 ** 122),
        'uuid_v7_bits_aleatorios': 74,
        'snowflake_bits': 64,
        'snowflake_por_ms_por_no': 4096,
        'ulid_bits': 128,
        'ulid_bits_aleatorios': 80,
        'ksuid_bits': 160,
        'nanoid_21_bits': 21 * 6,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--amostras', type=int, default=200_000)
    ap.add_argument('--semente', type=int, default=79)
    ap.add_argument('--saida', default=str(RAIZ / 'analise' / 'resultados.json'))
    args = ap.parse_args()

    resultado = {
        'exato': exato(),
        'monte_carlo': monte_carlo(args.amostras, args.semente),
        'espacos': espacos_amostrais(),
    }
    Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.saida).write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print('Taxa de erros NÃO detectados (cálculo exato sobre os 12 caracteres de dados):')
    cab = ('Esquema', 'Troca letra', 'Troca dígito', 'Transp. vizinhos', 'Transp. qualquer', '2 erros', 'Aleatório')
    print(' | '.join(cab))
    for r in resultado['exato'].values():
        print(' | '.join([
            r['nome'],
            f"{r['substituicao']['letra']:.2%}", f"{r['substituicao']['digito']:.2%}",
            f"{r['transposicao_adjacente']:.2%}", f"{r['transposicao_qualquer']:.2%}",
            f"{r['substituicao_dupla']:.2%}", f"{r['cadeia_aleatoria']:.2%}",
        ]))
    print('\nContraprova Monte Carlo (14 caracteres, implementação de referência):')
    for k, v in resultado['monte_carlo'].items():
        print(f'  {k}: {v:.4%}' if k != 'amostras' else f'  amostras: {v}')
    print(f"\nGravado em {args.saida}")


if __name__ == '__main__':
    main()

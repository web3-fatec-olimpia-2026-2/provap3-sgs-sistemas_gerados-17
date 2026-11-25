#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_sistema.py — GERADOR DETERMINÍSTICO de sistemas de estudo (ILP-037 · P3).

SEM IA. Tudo sai de três peças fixas:
  1. um CATÁLOGO de domínios (hotel, biblioteca, academia, loja...) com entidade, atributos,
     regras de validação, variações de regra, extras, categorias etc.;
  2. um CATÁLOGO de 28 padrões com palavras-chave e textos explicativos: os 23 do GoF por categoria
     (5 de criação, 7 estruturais, 11 comportamentais — lista da Wikipédia, cópia em referencias/)
     + 5 fundamentos das aulas (encapsulamento, polimorfismo, SRP/OCP, Service, MVVM);
  3. MODELOS de código (templates) que combinam os dois.
A mesma entrada gera SEMPRE os mesmos arquivos, byte a byte (não há data, sorteio nem rede).

O que sai (um "sistema" completo, pronto para rodar):
  nucleo/          Python puro: a entidade com @property (validações) + um módulo por padrão
                   + a versão "antes" (o smell) de cada padrão, para comparar
  tests/           pytest: validações e limites, equivalência antes × depois, extensão sem
                   modificar (OCP) e os testes próprios de cada padrão
  docs/            um ADR por padrão (Contexto · Decisão · Alternativa · Consequências)
  README.md        mapa dos arquivos e ligações + explicação de cada padrão + o tripé da P3
                   ("o que faz / por que assim / o que muda se") de cada função principal
  web/             (--django) projeto Django MVT: model com validators, ModelForm, Service
                   que reaproveita o Strategy do núcleo, ViewModel, views finas, templates, testes
  exercicios.html  (--exercicio) questionário de revisão sobre os padrões DESTE sistema, com a resposta
                   oculta (botão "Ver resposta"); o código sai sempre completo e correto

Uso (no WSL, na raiz do projeto — use o Python do .venv):
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py                    # menu interativo
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py --listar
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py --dominio biblioteca --padrao strategy decorator --testar
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py --assunto "academia em que o preço muda conforme o plano" --testar
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py --dominio hotel --padrao todos --django --testar
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py --dominio loja --padrao facade --exercicio --testar
  .venv/bin/python Gerador_Sistemas/gerar_sistema.py --modelo-spec > meu.json   # edite e use --spec meu.json
"""
from __future__ import annotations

import argparse
import ast
import copy
import functools
import hashlib
import html
import importlib.util
import io
import struct
import tokenize
import zlib
import itertools
import json
import keyword
import os
import re
import shutil
import subprocess
import sys
import textwrap
import unicodedata
from pathlib import Path

VERSAO = "2.0"
MARCADOR = ".gerado_por_gerar_sistema"
PASTA_PADRAO = Path(__file__).resolve().parent / "sistemas_gerados"
REFERENCIA_GOF = "referencias/wikipedia_padrao_de_projeto_de_software.html"
# Dependências de um sistema gerado com Django (testado com Django 6.1, pytest 9 e pytest-django 4.14).
# requirements.txt dos sistemas gerados: o PYTHON exigido, o DJANGO e o que ele usa, os TESTES e as dependências
# PONTUAIS de cada sistema (as que dependem das opções escolhidas).
PYTHON_MINIMO = (3, 12)     # o Django 6 exige 3.12+ (e o núcleo conta com o sum() exato do 3.12+)
DEPENDENCIAS_DJANGO = [("Django>=6.0,<7.0", "o framework web: MVT, ORM, admin, formulários"),
                       ("asgiref>=3.9.1", "o Django usa (views síncronas e assíncronas)"),
                       ("sqlparse>=0.5.0", "o Django usa (formata o SQL das migrations)"),
                       ('tzdata; sys_platform == "win32"', "o Django usa só no Windows (fusos horários)")]
DEPENDENCIAS_TESTES = [("pytest>=8.0", "os testes do núcleo"),
                       ("pytest-django>=4.9", "os testes da camada web (Django)")]
AQUI = Path(__file__).resolve().parent
BOOTSTRAP = AQUI / "recursos" / "bootstrap-5.3.3"
MOTOR_LNNL = AQUI / "motor-id-interno" / "referencia" / "python" / "lnnl.py"

# Opções da camada WEB (valem com --django). Estilos: simples (sem formatação), cmd (tela preta),
# bootstrap (Bootstrap padrão) e web (Bootstrap + temas da pasta temas/). As demais vêm das
# Instruções de desenvolvimento DJANGO (§9.2 apps/, §10.4 UUID, §12–14 segurança) e do motor-id-interno.
ESTILOS = {"simples": "sem formatação (HTML puro)", "cmd": "tela preta, estilo terminal",
           "bootstrap": "Bootstrap padrão", "web": "Bootstrap + temas (cores da pasta temas/)"}
WEB_PADRAO = {"estilo": "simples", "tema": "T01", "tom": "tom3", "paleta": "P02", "comentarios_web": False,
              "id_publico": "inteiro", "id_interno": False, "lnnl_tipo": "21", "estrutura": "plana",
              "seguranca": "basica"}


def normalizar_web(opcoes=None):
    """Valida as opções web (listas fechadas: nada de texto livre vira CSS ou código)."""
    import temas_web
    w = dict(WEB_PADRAO)
    for chave, valor in (opcoes or {}).items():
        if chave not in WEB_PADRAO:
            raise ErroGerador(f"opção web desconhecida: {chave!r}")
        w[chave] = valor
    for chave in ("comentarios_web", "id_interno"):
        w[chave] = bool(w[chave])
    w["tema"], w["paleta"] = str(w["tema"]).upper(), str(w["paleta"]).upper()
    fechadas = {"estilo": list(ESTILOS), "tema": list(temas_web.TEMAS), "tom": temas_web.TONS,
                "paleta": list(temas_web.PALETAS), "id_publico": ["inteiro", "uuid"], "estrutura": ["plana", "apps"],
                "seguranca": ["basica", "baseline"]}
    for chave, opcoes_validas in fechadas.items():
        if w[chave] not in opcoes_validas:
            raise ErroGerador(f"{chave} inválido: {w[chave]!r} (use: {', '.join(opcoes_validas)})")
    w["lnnl_tipo"] = str(w["lnnl_tipo"])
    if not re.fullmatch(r"[1-9]{2}", w["lnnl_tipo"]) or w["lnnl_tipo"] == "93":
        raise ErroGerador("lnnl_tipo: dois dígitos de 1 a 9 (11–99, sem zero), e nunca 93 (reservado)")
    return w

# Padrões por CATEGORIA. Os 23 do GoF seguem a lista da Wikipédia (cópia em REFERENCIA_GOF):
# 5 de criação · 7 estruturais · 11 comportamentais. "fundamentos" = OO, SOLID e arquitetura das aulas.
CATEGORIAS = {
    "fundamentos": ["encapsulamento", "polimorfismo", "srp", "service", "mvvm"],
    "criacao": ["singleton", "factory_method", "abstract_factory", "builder", "prototype"],
    "estrutural": ["adapter", "bridge", "composite", "decorator", "facade", "flyweight", "proxy"],
    "comportamental": ["chain", "command", "interpreter", "iterator", "mediator", "memento", "observer",
                       "state", "strategy", "template_method", "visitor"],
}
NOMES_CATEGORIAS = {"fundamentos": "Fundamentos (OO, SOLID e arquitetura — aulas)",
                    "criacao": "GoF · Padrões de criação", "estrutural": "GoF · Padrões estruturais",
                    "comportamental": "GoF · Padrões comportamentais"}
ORDEM_PADROES = [p for lista in CATEGORIAS.values() for p in lista]
GOF = CATEGORIAS["criacao"] + CATEGORIAS["estrutural"] + CATEGORIAS["comportamental"]
# Os 9 cobrados na P3 de ILP-037 (Aulas 02–10): o padrão quando o assunto não cita nenhum padrão.
PROVA = ["encapsulamento", "polimorfismo", "strategy", "srp", "service", "mvvm", "adapter", "facade", "decorator"]
GRUPOS = {"todos": ORDEM_PADROES, "gof": GOF, "prova": PROVA, "fundamentos": CATEGORIAS["fundamentos"],
          "criacao": CATEGORIAS["criacao"], "estrutural": CATEGORIAS["estrutural"],
          "comportamental": CATEGORIAS["comportamental"]}


# =============================================================================
# 0. UTILIDADES
# =============================================================================
class ErroGerador(Exception):
    """Erro de uso: mostrado ao usuário como mensagem, sem traceback."""


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def normalizar(texto):
    """minúsculas, sem acento, espaços simples — base de toda comparação de palavras."""
    return re.sub(r"\s+", " ", sem_acento(texto).lower()).strip()


def snake(texto):
    return re.sub(r"[^a-z0-9]+", "_", normalizar(texto)).strip("_") or "sistema"


def camel(texto):
    partes = re.split(r"[^A-Za-z0-9]+", sem_acento(texto))
    return "".join(p[:1].upper() + p[1:] for p in partes if p) or "Item"


def camel_para_snake(nome):
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", nome).lower()


def plural(nome_snake):
    """Plural simples em português para nomes de app Django (reserva→reservas, inscricao→inscricoes)."""
    partes = nome_snake.split("_")
    p = partes[-1]
    if p.endswith("ao"):
        p = p[:-2] + "oes"
    elif p.endswith(("r", "z", "s")):
        p += "es"
    elif p.endswith("m"):
        p = p[:-1] + "ns"
    elif p.endswith("l"):
        p = p[:-1] + "is"
    else:
        p += "s"
    partes[-1] = p
    return "_".join(partes)


def render(modelo, **valores):
    """Preenche um modelo de código.

    * `@@CHAVE@@` no meio da linha é trocado pelo valor (texto de uma linha).
    * Uma linha que contém SÓ `@@CHAVE@@` (com recuo) recebe um BLOCO de várias linhas,
      e cada linha do bloco ganha o mesmo recuo.
    Se sobrar algum marcador sem valor, é erro (o gerador nunca escreve código pela metade).
    """
    texto = textwrap.dedent(modelo).lstrip("\n")
    saida = []
    for linha in texto.split("\n"):
        bloco = re.fullmatch(r"([ ]*)@@([A-Z0-9_]+)@@", linha)
        if bloco and bloco.group(2) in valores:
            recuo = bloco.group(1)
            conteudo = str(valores[bloco.group(2)]).rstrip("\n")
            saida.extend((recuo + l) if l.strip() else "" for l in conteudo.split("\n"))
            continue
        for chave, valor in valores.items():
            linha = linha.replace(f"@@{chave}@@", str(valor))
        saida.append(linha)
    texto = "\n".join(saida)
    resto = re.findall(r"@@[A-Z0-9_]+@@", texto)
    if resto:
        raise RuntimeError(f"modelo com marcador sem valor: {sorted(set(resto))}")
    return texto.rstrip("\n") + "\n"


@functools.lru_cache(maxsize=None)
def icone_png(tamanho=192):
    """Ícone do app (PWA): um prompt ">_" verde sobre fundo escuro, desenhado pixel a pixel e
    codificado em PNG só com a biblioteca padrão (zlib + struct). Mesmo tamanho → mesmos bytes."""
    fundo, frente = (12, 12, 12), (22, 198, 12)
    espessura = 0.075

    def no_traco(u, v, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        k = max(0.0, min(1.0, ((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy)))
        return (u - ax - k * dx) ** 2 + (v - ay - k * dy) ** 2 <= (espessura / 2) ** 2

    linhas = []
    for y in range(tamanho):
        v = (y + 0.5) / tamanho
        linha = bytearray(b"\x00")                       # filtro 0 (nenhum) no início de cada linha
        for x in range(tamanho):
            u = (x + 0.5) / tamanho
            verde = (no_traco(u, v, 0.22, 0.28, 0.48, 0.50) or no_traco(u, v, 0.48, 0.50, 0.22, 0.72)
                     or (0.56 <= u <= 0.80 and 0.665 <= v <= 0.735))
            linha += bytes(frente if verde else fundo)
        linhas.append(bytes(linha))

    def pedaco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + pedaco(b"IHDR", struct.pack(">IIBBBBB", tamanho, tamanho, 8, 2, 0, 0, 0))
            + pedaco(b"IDAT", zlib.compress(b"".join(linhas), 9)) + pedaco(b"IEND", b""))


def lit(valor):
    """Literal Python determinístico."""
    return repr(valor)


def dict_lit(d):
    return "{" + ", ".join(f"{k!r}: {v!r}" for k, v in d.items()) + "}"


# =============================================================================
# 1. CATÁLOGO DE DOMÍNIOS
# =============================================================================
def A(nome, tipo, regra, minimo=None, maximo=None):
    """Atributo da entidade. tipo: str|int|float · regra: obrigatorio|minimo|faixa|livre."""
    return {"nome": nome, "tipo": tipo, "regra": regra, "min": minimo, "max": maximo}


DOMINIOS = {
    "hotel": {
        "sistema": "Hotel Resort",
        "palavras": ["hotel", "resort", "pousada", "hospedagem", "hospede", "hospedes", "quarto",
                     "quartos", "diaria", "diarias", "suite", "check-in", "checkin"],
        "entidade": "Reserva",
        "atributos": [A("hospede", "str", "obrigatorio"), A("quarto", "int", "minimo", 1),
                      A("diarias", "int", "faixa", 1, 30), A("valor_diaria", "float", "minimo", 0),
                      A("observacao", "str", "livre")],
        "ident": "hospede", "quantidade": "diarias", "preco": "valor_diaria", "unidade": "diária(s)",
        "precos_exemplo": [200.0, 150.0, 99.9, 0.0],
        "variantes": {"conceito": "tipo de hóspede",
                      "itens": [["Comum", 1.0], ["Fidelidade", 0.9], ["Parceiro", 0.8]],
                      "nova": ["VIP", 0.5]},
        "categorias": {"unidade": "noite", "base": ["Quarto", "Quarto comum", 200.0],
                       "subtipos": [["Suite", "Suíte", 500.0], ["Presidencial", "Quarto presidencial", 1200.0]],
                       "nova": ["Chale", "Chalé", 350.0]},
        "extras": {"fixos": [["CafeDaManha", 40.0, "café da manhã"], ["Transfer", 80.0, "transfer"],
                             ["LateCheckout", 60.0, "late checkout"]],
                   "percentual": ["DescontoFidelidade", 0.9, "-10% fidelidade"]},
        "gateway": "PagaFacil",
        "recurso": "quarto", "recursos": [101, 201, 301],
        "painel": {"titulo": "Quarto", "livre": "livre", "ocupado": "INDISPONIVEL",
                   "acao_livre": "Reservar", "acao_ocupado": "(ocupado)",
                   "zero": "LOTADO - nenhum quarto livre", "contagem": "quarto(s) livre(s)"},
        "nomes": ["Ana", "Bruno", "Carla", "Diego"],
    },
    "biblioteca": {
        "sistema": "Biblioteca Municipal",
        "palavras": ["biblioteca", "livro", "livros", "emprestimo", "emprestimos", "acervo", "leitor",
                     "leitores", "exemplar", "exemplares", "devolucao", "multa"],
        "entidade": "Emprestimo",
        "atributos": [A("leitor", "str", "obrigatorio"), A("exemplar", "int", "minimo", 1),
                      A("dias", "int", "faixa", 1, 30), A("taxa_dia", "float", "minimo", 0),
                      A("observacao", "str", "livre")],
        "ident": "leitor", "quantidade": "dias", "preco": "taxa_dia", "unidade": "dia(s)",
        "precos_exemplo": [2.5, 1.0, 10.0, 0.0],
        "variantes": {"conceito": "tipo de leitor",
                      "itens": [["Comum", 1.0], ["Estudante", 0.5], ["Professor", 0.7]],
                      "nova": ["Visitante", 1.5]},
        "categorias": {"unidade": "dia", "base": ["Livro", "Livro comum", 2.0],
                       "subtipos": [["Revista", "Revista", 1.0], ["LivroRaro", "Livro raro", 10.0]],
                       "nova": ["Ebook", "E-book", 0.5]},
        "extras": {"fixos": [["ReservaAntecipada", 5.0, "reserva antecipada"],
                             ["EntregaEmCasa", 12.0, "entrega em casa"], ["Plastificacao", 3.0, "plastificação"]],
                   "percentual": ["Urgencia", 1.2, "+20% urgência"]},
        "gateway": "PixRapido",
        "recurso": "exemplar", "recursos": [1001, 1002, 1003],
        "painel": {"titulo": "Exemplar", "livre": "disponível", "ocupado": "EMPRESTADO",
                   "acao_livre": "Emprestar", "acao_ocupado": "(aguardar)",
                   "zero": "ESGOTADO - nenhum exemplar disponível", "contagem": "exemplar(es) disponível(is)"},
        "nomes": ["Beatriz", "Caio", "Denise", "Eduardo"],
    },
    "academia": {
        "sistema": "Academia Fit",
        "palavras": ["academia", "treino", "treinos", "aluno", "alunos", "matricula", "mensalidade",
                     "musculacao", "personal", "ginastica", "crossfit"],
        "entidade": "Matricula",
        "atributos": [A("aluno", "str", "obrigatorio"), A("turma", "int", "minimo", 1),
                      A("meses", "int", "faixa", 1, 24), A("mensalidade", "float", "minimo", 0),
                      A("objetivo", "str", "livre")],
        "ident": "aluno", "quantidade": "meses", "preco": "mensalidade", "unidade": "mês(es)",
        "precos_exemplo": [100.0, 150.0, 89.9, 0.0],
        "variantes": {"conceito": "tipo de plano",
                      "itens": [["Mensal", 1.0], ["Universitario", 0.7], ["Corporativo", 0.8]],
                      "nova": ["Familia", 0.6]},
        "categorias": {"unidade": "mês", "base": ["Musculacao", "Musculação", 100.0],
                       "subtipos": [["Natacao", "Natação", 150.0], ["Crossfit", "Crossfit", 180.0]],
                       "nova": ["Pilates", "Pilates", 160.0]},
        "extras": {"fixos": [["Personal", 80.0, "personal trainer"], ["Armario", 15.0, "armário"],
                             ["Avaliacao", 40.0, "avaliação física"]],
                   "percentual": ["Promocao", 0.85, "-15% promoção"]},
        "gateway": "CobraJa",
        "recurso": "turma", "recursos": [10, 20, 30],
        "painel": {"titulo": "Turma", "livre": "vagas abertas", "ocupado": "LOTADA",
                   "acao_livre": "Matricular", "acao_ocupado": "(lista de espera)",
                   "zero": "SEM VAGAS - todas as turmas lotadas", "contagem": "turma(s) com vaga"},
        "nomes": ["Fernanda", "Gustavo", "Helena", "Igor"],
    },
    "loja": {
        "sistema": "Loja Virtual",
        "palavras": ["loja", "pedido", "pedidos", "produto", "produtos", "carrinho", "compra", "compras",
                     "venda", "vendas", "ecommerce", "e-commerce", "estoque", "frete"],
        "entidade": "Pedido",
        "atributos": [A("cliente", "str", "obrigatorio"), A("produto", "int", "minimo", 1),
                      A("quantidade", "int", "faixa", 1, 50), A("preco_unitario", "float", "minimo", 0),
                      A("observacao", "str", "livre")],
        "ident": "cliente", "quantidade": "quantidade", "preco": "preco_unitario", "unidade": "unidade(s)",
        "precos_exemplo": [50.0, 19.9, 300.0, 0.0],
        "variantes": {"conceito": "tipo de cliente",
                      "itens": [["Comum", 1.0], ["Fidelidade", 0.9], ["Atacado", 0.85]],
                      "nova": ["Funcionario", 0.7]},
        "categorias": {"unidade": "unidade", "base": ["Produto", "Produto comum", 50.0],
                       "subtipos": [["Eletronico", "Eletrônico", 300.0], ["Livro", "Livro", 40.0]],
                       "nova": ["Alimento", "Alimento", 20.0]},
        "extras": {"fixos": [["Embrulho", 15.0, "embrulho para presente"], ["Cartao", 5.0, "cartão"],
                             ["EntregaExpressa", 25.0, "entrega expressa"]],
                   "percentual": ["Cupom10", 0.9, "-10% cupom"]},
        "gateway": "PagueMais",
        "recurso": "produto", "recursos": [501, 502, 503],
        "painel": {"titulo": "Produto", "livre": "em estoque", "ocupado": "ESGOTADO",
                   "acao_livre": "Comprar", "acao_ocupado": "(avise-me)",
                   "zero": "SEM ESTOQUE - nenhum produto disponível", "contagem": "produto(s) em estoque"},
        "nomes": ["Juliana", "Kleber", "Larissa", "Marcos"],
    },
    "estacionamento": {
        "sistema": "Estacionamento Centro",
        "palavras": ["estacionamento", "vaga", "vagas", "carro", "carros", "veiculo", "veiculos", "placa",
                     "ticket", "garagem", "moto", "motos"],
        "entidade": "Ticket",
        "atributos": [A("placa", "str", "obrigatorio"), A("vaga", "int", "minimo", 1),
                      A("horas", "int", "faixa", 1, 24), A("valor_hora", "float", "minimo", 0),
                      A("observacao", "str", "livre")],
        "ident": "placa", "quantidade": "horas", "preco": "valor_hora", "unidade": "hora(s)",
        "precos_exemplo": [10.0, 5.0, 12.5, 0.0],
        "variantes": {"conceito": "tipo de cliente",
                      "itens": [["Avulso", 1.0], ["Mensalista", 0.5], ["Conveniado", 0.8]],
                      "nova": ["Evento", 2.0]},
        "categorias": {"unidade": "hora", "base": ["Carro", "Carro", 10.0],
                       "subtipos": [["Moto", "Moto", 5.0], ["Caminhonete", "Caminhonete", 15.0]],
                       "nova": ["Van", "Van", 20.0]},
        "extras": {"fixos": [["Lavagem", 30.0, "lavagem"], ["Manobrista", 20.0, "manobrista"],
                             ["VagaCoberta", 8.0, "vaga coberta"]],
                   "percentual": ["Noturno", 1.25, "+25% noturno"]},
        "gateway": "PagVaga",
        "recurso": "vaga", "recursos": [1, 2, 3],
        "painel": {"titulo": "Vaga", "livre": "livre", "ocupado": "OCUPADA",
                   "acao_livre": "Estacionar", "acao_ocupado": "(ocupada)",
                   "zero": "LOTADO - nenhuma vaga livre", "contagem": "vaga(s) livre(s)"},
        "nomes": ["ABC1D23", "EFG4H56", "IJK7L89", "MNO0P12"],
    },
    "cinema": {
        "sistema": "Cine Olímpia",
        "palavras": ["cinema", "filme", "filmes", "sessao", "sessoes", "ingresso", "ingressos", "sala",
                     "pipoca", "espectador"],
        "entidade": "Ingresso",
        "atributos": [A("espectador", "str", "obrigatorio"), A("sessao", "int", "minimo", 1),
                      A("quantidade", "int", "faixa", 1, 10), A("preco", "float", "minimo", 0),
                      A("poltrona", "str", "livre")],
        "ident": "espectador", "quantidade": "quantidade", "preco": "preco", "unidade": "ingresso(s)",
        "precos_exemplo": [30.0, 40.0, 25.5, 0.0],
        "variantes": {"conceito": "tipo de ingresso",
                      "itens": [["Inteira", 1.0], ["Meia", 0.5], ["Clube", 0.8]],
                      "nova": ["Promocional", 0.6]},
        "categorias": {"unidade": "ingresso", "base": ["Sala", "Sala 2D", 30.0],
                       "subtipos": [["SalaImersiva", "Sala 3D", 40.0], ["Imax", "Sala IMAX", 60.0]],
                       "nova": ["SalaVip", "Sala VIP", 80.0]},
        "extras": {"fixos": [["Pipoca", 25.0, "pipoca"], ["Refrigerante", 12.0, "refrigerante"],
                             ["Oculos", 5.0, "óculos 3D"]],
                   "percentual": ["TercaPromo", 0.5, "-50% terça"]},
        "gateway": "TicketPag",
        "recurso": "sessão", "recursos": [1, 2, 3],
        "painel": {"titulo": "Sessão", "livre": "disponível", "ocupado": "ESGOTADA",
                   "acao_livre": "Comprar", "acao_ocupado": "(esgotada)",
                   "zero": "ESGOTADO - nenhuma sessão disponível", "contagem": "sessão(ões) disponível(is)"},
        "nomes": ["Natália", "Otávio", "Paula", "Rafael"],
    },
    "clinica": {
        "sistema": "Clínica Vida",
        "palavras": ["clinica", "consulta", "consultas", "paciente", "pacientes", "medico", "medica",
                     "agendamento", "exame", "exames", "saude"],
        "entidade": "Consulta",
        "atributos": [A("paciente", "str", "obrigatorio"), A("sala", "int", "minimo", 1),
                      A("sessoes", "int", "faixa", 1, 12), A("valor_sessao", "float", "minimo", 0),
                      A("anotacao", "str", "livre")],
        "ident": "paciente", "quantidade": "sessoes", "preco": "valor_sessao", "unidade": "sessão(ões)",
        "precos_exemplo": [150.0, 300.0, 99.9, 0.0],
        "variantes": {"conceito": "tipo de convênio",
                      "itens": [["Particular", 1.0], ["ConvenioOuro", 0.6], ["ConvenioPrata", 0.75]],
                      "nova": ["Empresa", 0.5]},
        "categorias": {"unidade": "sessão", "base": ["ClinicoGeral", "Clínico geral", 150.0],
                       "subtipos": [["Cardiologia", "Cardiologia", 300.0], ["Pediatria", "Pediatria", 200.0]],
                       "nova": ["Dermatologia", "Dermatologia", 250.0]},
        "extras": {"fixos": [["Laudo", 40.0, "laudo"], ["Exame", 90.0, "exame"],
                             ["Prioridade", 30.0, "atendimento prioritário"]],
                   "percentual": ["Urgencia", 1.5, "+50% urgência"]},
        "gateway": "SaudePag",
        "recurso": "horário", "recursos": [8, 9, 10],
        "painel": {"titulo": "Horário", "livre": "livre", "ocupado": "OCUPADO",
                   "acao_livre": "Agendar", "acao_ocupado": "(ocupado)",
                   "zero": "AGENDA CHEIA - nenhum horário livre", "contagem": "horário(s) livre(s)"},
        "nomes": ["Sérgio", "Tatiana", "Ulisses", "Vanessa"],
    },
    "generico": {
        "sistema": "Sistema Exemplo",
        "palavras": [],
        "entidade": "Atendimento",
        "atributos": [A("cliente", "str", "obrigatorio"), A("codigo", "int", "minimo", 1),
                      A("quantidade", "int", "faixa", 1, 100), A("valor_unitario", "float", "minimo", 0),
                      A("observacao", "str", "livre")],
        "ident": "cliente", "quantidade": "quantidade", "preco": "valor_unitario", "unidade": "unidade(s)",
        "precos_exemplo": [100.0, 49.9, 250.0, 0.0],
        "variantes": {"conceito": "tipo de cliente",
                      "itens": [["Comum", 1.0], ["Especial", 0.9], ["Parceiro", 0.8]],
                      "nova": ["Vip", 0.5]},
        "categorias": {"unidade": "unidade", "base": ["Basico", "Básico", 100.0],
                       "subtipos": [["Intermediario", "Intermediário", 200.0], ["Premium", "Premium", 400.0]],
                       "nova": ["Personalizado", "Personalizado", 300.0]},
        "extras": {"fixos": [["Urgente", 30.0, "urgente"], ["Embalagem", 10.0, "embalagem"],
                             ["Seguro", 15.0, "seguro"]],
                   "percentual": ["Desconto10", 0.9, "-10% desconto"]},
        "gateway": "PagaJa",
        "recurso": "recurso", "recursos": [1, 2, 3],
        "painel": {"titulo": "Recurso", "livre": "disponível", "ocupado": "INDISPONÍVEL",
                   "acao_livre": "Solicitar", "acao_ocupado": "(indisponível)",
                   "zero": "SEM DISPONIBILIDADE", "contagem": "recurso(s) disponível(is)"},
        "nomes": ["Ana", "Bruno", "Carla", "Diego"],
    },
}

# Os 100 domínios: os 8 acima + 92 de dominios.py, na ordem do catalogo_100_dominios.txt (lista do usuário:
# ID, sistema, entidade e as 30 palavras que ativam cada um). INFO_DOMINIOS[chave] = {"id": "001", "setor": …}.
import dominios as _dominios  # noqa: E402

DOMINIOS, INFO_DOMINIOS = _dominios.montar(DOMINIOS)


# =============================================================================
# 2. CATÁLOGO DE PADRÕES (palavras-chave + textos para README/ADR)
# =============================================================================
PADROES = {
    "encapsulamento": {
        "titulo": "Encapsulamento com @property", "familia": "Fundamento de OO — Aulas 02 e 03",
        "modulo": "entidades", "antes": None,
        "aliases": ["encapsulamento", "property", "validacao", "validar"],
        "palavras": ["encapsulamento", "property", "setter", "validacao", "validar", "valida", "validado",
                     "negativo", "negativa", "nao pode ser", "minimo", "maximo", "proteger", "protegido",
                     "invalido", "invalida", "obrigatorio"],
        "problema": "Um atributo público aceita qualquer valor: `obj.@@QTD@@ = 0` ou `obj.@@PRECO@@ = -50` "
                    "passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.",
        "conceito": "O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + "
                    "setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa "
                    "`self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.",
        "pecas": [["Atributo interno", "`self._@@QTD@@`, `self._@@PRECO@@`…"], ["Getter", "`@property`"],
                  ["Setter (a fechadura)", "`@@@QTD@@.setter` → `ValueError` se inválido"],
                  ["Dado calculado", "`total` (só leitura)"]],
        "quando_nao": "Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique "
                      "é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra "
                      "ModelForm, admin e ORM.",
        "alternativa": "Validar só no formulário da tela — não protege quem cria o objeto pelo shell, admin, "
                       "importação ou outro código.",
        "consequencia": "O objeto nunca fica inválido e o erro aparece perto da causa; em troca, quem cria "
                        "a @@ENT@@ precisa tratar `ValueError`.",
        "tripe": [["`@@ENT@@.@@QTD@@` (setter)",
                   "Intercepta toda escrita em `@@QTD@@` e só grava se a regra for respeitada; senão levanta `ValueError`.",
                   "Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.@@QTD@@ = ...`, vale também na criação. Descartado: validar só na tela.",
                   "Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_@@QTD@@`, o objeto pode nascer inválido."],
                  ["`@@ENT@@.total`",
                   "Calcula `@@QTD@@ × @@PRECO@@` na hora.",
                   "Dado derivado não se guarda: se fosse atributo, mudar `@@QTD@@` deixaria o total desatualizado.",
                   "Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta."]],
    },
    "polimorfismo": {
        "titulo": "Polimorfismo (herança + sobrescrita)", "familia": "Fundamento de OO — Aula 04",
        "modulo": "categorias", "antes": "antes_categorias",
        "aliases": ["polimorfismo", "heranca", "sobrescrita"],
        "palavras": ["polimorfismo", "heranca", "herdar", "herda", "subtipo", "subtipos", "subclasse",
                     "subclasses", "sobrescrever", "sobrescrita", "override", "especializacao",
                     "cada categoria", "categorias diferentes"],
        "problema": "`imprimir_preco(tipo)` decide o texto com `if/elif` por categoria; cada categoria nova "
                    "obriga a editar a função (e arriscar as que já funcionavam).",
        "conceito": "Cada categoria é uma subclasse de `@@CATBASE@@` que SOBRESCREVE `descricao()` e "
                    "`preco_unidade()`. `imprimir_preco(categoria)` só chama os métodos — o Python escolhe a "
                    "versão pelo tipo real do objeto, em tempo de execução.",
        "pecas": [["Classe base", "`@@CATBASE@@`"], ["Subtipos que sobrescrevem", "@@CATSUBS@@"],
                  ["Subtipo que não sobrescreve (usa o da mãe)", "`@@CATBASE@@Padrao`"],
                  ["Função polimórfica", "`imprimir_preco(categoria)`"], ["Categoria nova", "`@@CATNOVA@@`"]],
        "quando_nao": "Se as categorias só diferem num número (sem comportamento próprio), um atributo ou tabela "
                      "basta. Herança só para relação É-UM; TEM-UM é composição.",
        "alternativa": "Manter o `if/elif` por tipo — cada categoria nova reabriria a função.",
        "consequencia": "Categoria nova = classe nova; a função não muda. Custo: uma classe por categoria.",
        "tripe": [["`imprimir_preco(categoria)`",
                   "Monta \"descrição: R$ preço por @@CATUNID@@\" de qualquer categoria.",
                   "Polimorfismo: não pergunta o tipo (zero `if`); cada subclasse responde a seu modo.",
                   "Com `if/elif`, o `@@CATNOVA@@` exigiria editar a função; hoje entra sem mudar uma linha. Se um subtipo não sobrescrever, usa o método da mãe."]],
    },
    "strategy": {
        "titulo": "Strategy", "familia": "Padrão comportamental (GoF) — Aula 05",
        "modulo": "politicas", "antes": "antes_politicas",
        "aliases": ["strategy", "estrategia", "estrategias"],
        "palavras": ["strategy", "estrategia", "tipo de", "tipos de", "varia", "variam", "variar", "depende do",
                     "depende da", "conforme o", "conforme a", "politica", "politicas", "plano", "planos",
                     "desconto", "descontos", "tarifa", "tarifas", "convenio", "convenios", "modalidade",
                     "modalidades", "regras diferentes", "elif", "muda o preco", "muda conforme"],
        "problema": "`CobrancaAntiga.valor()` tem um `if/elif` por @@CONCEITO@@ que cresce a cada regra nova — "
                    "cada uma obriga a reabrir a classe.",
        "conceito": "Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) "
                    "RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`.",
        "pecas": [["Contexto", "`Cobranca`"], ["Interface da estratégia", "`aplicar(base)`"],
                  ["Estratégias", "@@POLITICAS@@"], ["Estratégia nova (OCP)", "`Politica@@VNOVA@@`"],
                  ["Versão pythônica", "`CobrancaComFuncao` (estratégia = função)"]],
        "quando_nao": "Uma regra só, que nunca varia → uma função ou constante basta (Strategy seria cerimônia). "
                      "Em Python a estratégia pode ser uma função.",
        "alternativa": "Dicionário `{tipo: percentual}` — resolve percentuais, mas não comporta uma regra com "
                       "comportamento próprio (prazo, limite, cálculo diferente).",
        "consequencia": "Regra nova = classe nova; `Cobranca` intacta (OCP). Custo: uma classe por regra.",
        "tripe": [["`Cobranca.valor()`",
                   "Pega o `total` da @@ENT@@ e devolve o valor depois da política aplicada.",
                   "Strategy: a família de regras de @@CONCEITO@@ varia; cada uma é uma classe e o contexto delega, sem `if`.",
                   "Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança."]],
    },
    "srp": {
        "titulo": "SRP + OCP (separar responsabilidades)", "familia": "Princípios SOLID — Aula 06",
        "modulo": "recibo", "antes": "antes_recibo",
        "aliases": ["srp", "ocp", "solid", "responsabilidade"],
        "palavras": ["srp", "ocp", "solid", "responsabilidade", "responsabilidades", "recibo", "comprovante",
                     "imprimir", "salvar em arquivo", "salva em arquivo", "exportar", "csv", "pdf", "faz tudo",
                     "faz coisas demais", "formato novo"],
        "problema": "`@@ENT@@FazTudo` calcula, formata o recibo e grava em arquivo: três motivos para mudar "
                    "na mesma classe.",
        "conceito": "`@@ENT@@` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); "
                    "`ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova "
                    "(`ReciboCsvFormatter`) → OCP.",
        "pecas": [["Negócio", "`@@ENT@@` (nucleo/entidades.py)"], ["Apresentação", "`ReciboFormatter`"],
                  ["Extensão (OCP)", "`ReciboCsvFormatter`"], ["Infraestrutura", "`ArquivoRepository`"],
                  ["Junta as peças", "`emitir_recibo(...)`"]],
        "quando_nao": "SRP não é uma classe por método: separar \"calcula\", \"soma\", \"arredonda\" em classes é "
                      "tão ruim quanto juntar tudo. A unidade é a responsabilidade (motivo para mudar).",
        "alternativa": "Manter tudo na entidade — layout, destino e regra mudariam a mesma classe.",
        "consequencia": "Cada mudança mexe num lugar só; formato novo não reabre nada. Custo: mais classes pequenas.",
        "tripe": [["`ReciboFormatter.formatar(item)`",
                   "Recebe a @@ENT@@ e devolve o texto do recibo.",
                   "SRP: layout tem motivo de mudança próprio; recebe a entidade por parâmetro e só lê.",
                   "Layout novo mexe só aqui; formato novo é outra classe; devolver isto para a @@ENT@@ recriaria os 3 motivos para mudar."]],
    },
    "service": {
        "titulo": "Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web)",
        "familia": "Arquitetura — Aula 07", "modulo": "relatorio", "antes": "antes_relatorio",
        "aliases": ["service", "servico", "mvt", "mvc", "mvp", "arquitetura"],
        "palavras": ["service", "servico", "camada de servico", "mvc", "mvt", "mvp", "view gorda",
                     "regra na view", "relatorio", "relatorios", "sem http", "testar sem", "reaproveitar",
                     "api e tela"],
        "problema": "`relatorio_view` mistura a regra (desconto por @@CONCEITO@@) com a apresentação (texto); "
                    "para testar a conta é preciso chamar a view e ler texto.",
        "conceito": "`RelatorioService.calcular()` faz só a regra e devolve DADOS; a view fica fina (chama e "
                    "formata); a mesma regra serve a API (`relatorio_api`). No Django: models = dado, "
                    "views = regra/orquestração, template = apresentação, services.py = a regra complexa.",
        "pecas": [["Regra (sem web)", "`RelatorioService`"], ["View fina", "`relatorio_view`"],
                  ["Outra apresentação", "`relatorio_api`"]],
        "quando_nao": "View que só lista e renderiza não precisa de Service — só há Service quando há cálculo, "
                      "decisão ou orquestração de vários passos.",
        "alternativa": "Deixar a regra na view e testar com o client HTTP — teste lento e acoplado; a API "
                       "teria que duplicar a conta.",
        "consequencia": "Regra testável sem HTTP e reaproveitável. Custo: uma camada a mais.",
        "tripe": [["`RelatorioService.calcular()`",
                   "Aplica o fator de cada @@CONCEITO@@ e devolve `(linhas, total_geral)`.",
                   "A regra fica fora da web: testável sem request/servidor e reaproveitável pela API.",
                   "Se passar a receber `request` ou devolver texto, volta a exigir a web para testar e a API teria que duplicar a conta."]],
    },
    "mvvm": {
        "titulo": "MVVM (ViewModel)", "familia": "Arquitetura — Aulas 08 e 09",
        "modulo": "painel", "antes": "antes_painel",
        "aliases": ["mvvm", "viewmodel"],
        "palavras": ["mvvm", "viewmodel", "view model", "tela", "telas", "painel", "dashboard", "exibicao",
                     "exibir", "mostrar", "rotulo", "rotulos", "botao", "status", "selo", "lotado", "esgotado"],
        "problema": "`tela_painel` decide no meio do desenho o status, o rótulo do botão, o \"R$\" e o rodapé "
                    "\"@@ZERO@@\" — só dá para testar lendo a tela.",
        "conceito": "`ItemViewModel` / `PainelVM` traduzem o dado cru em dado pronto (`status_label`, "
                    "`acao_label`, `preco_formatado`, `rodape`); a View só costura. No Django não há binding: "
                    "o ViewModel é preparação chamada antes do `render`.",
        "pecas": [["Model (dado cru)", "dicts em `ITENS`"], ["ViewModel de um item", "`ItemViewModel`"],
                  ["ViewModel do painel", "`PainelVM`"], ["View burra", "`tela_painel_mvvm`"]],
        "quando_nao": "Tela que mostra o dado como está não precisa de ViewModel. Service × ViewModel: regra "
                      "de negócio (o que é verdade) × lógica de exibição (como aparece).",
        "alternativa": "Manter os `if` de exibição no template — só se testaria lendo HTML.",
        "consequencia": "Rótulo/estado novo muda só o ViewModel; testes sem renderizar. Custo: uma camada a mais.",
        "tripe": [["`ItemViewModel.__init__`",
                   "Transforma o dict cru em textos prontos para a tela (status, ação, preço formatado).",
                   "MVVM: a decisão de como mostrar fica num lugar só e testável sem renderizar.",
                   "Status novo muda só o ViewModel; voltar os `if` para a tela obriga a ler HTML para testar."]],
    },
    "adapter": {
        "titulo": "Adapter", "familia": "Padrão estrutural (GoF) — Aula 08",
        "modulo": "integracao", "antes": "antes_integracao",
        "aliases": ["adapter", "adaptador"],
        "palavras": ["adapter", "adaptador", "adaptar", "terceiro", "terceiros", "externa", "externo",
                     "api de", "integracao", "integrar", "integra", "gateway", "driver", "legado", "sdk",
                     "incompativel", "outra interface", "formato diferente", "biblioteca de pagamento"],
        "problema": "O gateway `@@GATEWAY@@` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema "
                    "espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.",
        "conceito": "`@@GATEWAY@@Adapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro "
                    "traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → "
                    "`PagamentoRecusado`).",
        "pecas": [["Alvo (interface esperada)", "`ProcessadorPagamento.processar(valor, token)`"],
                  ["Adaptado (terceiro)", "`Gateway@@GATEWAY@@.charge(payload)`"],
                  ["Adapter", "`@@GATEWAY@@Adapter`"], ["Cliente limpo", "`CheckoutService`"]],
        "quando_nao": "Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter "
                      "só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).",
        "alternativa": "`if usa_gateway` dentro do serviço — o detalhe do terceiro vaza para a regra e se "
                       "repete em cada método.",
        "consequencia": "Trocar de gateway = injetar outro processador. Custo: uma classe de tradução.",
        "tripe": [["`@@GATEWAY@@Adapter.processar(valor, token)`",
                   "Converte o pedido de pagamento do sistema numa chamada `charge` e devolve o id ou levanta `PagamentoRecusado`.",
                   "Adapter: o gateway é de terceiro (não controlamos a assinatura); o adapter faz a peça caber e o `CheckoutService` perde o `if`.",
                   "Devolvendo o dict cru, o formato do terceiro vaza e a recusa passaria como sucesso; sem `round`, 19.99 viraria 1998 centavos."]],
    },
    "facade": {
        "titulo": "Facade", "familia": "Padrão estrutural (GoF) — Aula 09",
        "modulo": "atendimento", "antes": "antes_atendimento",
        "aliases": ["facade", "fachada"],
        "palavras": ["facade", "fachada", "varios passos", "varias etapas", "etapas", "orquestra", "orquestrar",
                     "orquestracao", "fluxo", "sequencia", "na ordem", "checkout", "finalizar", "concluir",
                     "processo completo", "subsistemas", "varios sistemas"],
        "problema": "`atender_na_mao` conhece 5 subsistemas, a ordem e as regras de aborto; cada tela que "
                    "conclui um atendimento repetiria tudo isso.",
        "conceito": "`AtendimentoFacade.concluir(recurso, item)` é o balcão único: disponibilidade → cálculo → "
                    "cobrança → registro → notificação, DELEGANDO a cada subsistema.",
        "pecas": [["Subsistemas", "`Disponibilidade`, `Calculadora`, `Pagamentos`, `Registro`, `Notificador`"],
                  ["Fachada", "`AtendimentoFacade.concluir(...)`"], ["Antes", "`atender_na_mao(...)`"]],
        "quando_nao": "1–2 passos num lugar só → uma função basta. Se a fachada passar a executar regra (em "
                      "vez de delegar) vira God object. Ela não proíbe usar os subsistemas direto.",
        "alternativa": "Cada tela orquestrar os subsistemas — duplicação e acoplamento a cinco objetos.",
        "consequencia": "Passo novo entra só na fachada; clientes conhecem um objeto. Custo: mais uma classe.",
        "tripe": [["`AtendimentoFacade.concluir(recurso, item)`",
                   "Orquestra os 5 subsistemas na ordem e aborta se indisponível ou se o pagamento for recusado.",
                   "Facade: esconde a orquestração; o cliente conhece um objeto em vez de cinco; a fachada delega, não reimplementa.",
                   "Um passo novo entra só aqui; mover o cálculo para dentro dela a transforma em God object."]],
    },
    "decorator": {
        "titulo": "Decorator", "familia": "Padrão estrutural (GoF) — Aula 10",
        "modulo": "extras", "antes": "antes_extras",
        "aliases": ["decorator", "decorador"],
        "palavras": ["decorator", "decorador", "extra", "extras", "opcional", "opcionais", "adicional",
                     "adicionais", "combinacao", "combinacoes", "combinar", "empilhar", "acrescentar",
                     "embrulho", "camada", "camadas", "complemento", "complementos", "acessorio", "acessorios"],
        "problema": "`preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá "
                    "para repetir extra nem combinar dinamicamente.",
        "conceito": "Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua "
                    "parte; por isso empilha: `Com@@E2@@(Com@@E1@@(@@ENT@@Base(item)))`.",
        "pecas": [["Componente", "`@@ENT@@Base(item)`"], ["Decorador base (delega)", "`Adicional`"],
                  ["Decoradores que somam", "@@EXTRAS@@"], ["Decorador que multiplica", "`Com@@PERC@@`"]],
        "quando_nao": "Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python "
                      "decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.",
        "alternativa": "Flags booleanas — cada extra novo vira parâmetro + `if` + mudança em quem chama; "
                       "subclasse por combinação explodiria.",
        "consequencia": "Extra novo = classe nova, combinável em tempo de execução. Custo: cadeias longas são "
                        "difíceis de depurar.",
        "tripe": [["`Com@@E1@@.preco()`",
                   "Pergunta o preço ao componente de dentro e soma @@VE1@@.",
                   "Decorator: o extra é opcional e combinável; mantendo a interface, empilha.",
                   "Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda."]],
    },
}

_EXTRA = " (GoF) — além das aulas; referência: lista GoF da Wikipédia"
PADROES.update({
    # ------------------------------------------------------------------ GoF · CRIAÇÃO
    "singleton": {
        "titulo": "Singleton", "familia": "Padrão de criação" + _EXTRA,
        "modulo": "configuracao", "antes": "antes_configuracao",
        "aliases": ["singleton", "instancia_unica"],
        "palavras": ["singleton", "instancia unica", "unica instancia", "uma so instancia", "configuracao global",
                     "configuracao unica", "ponto global"],
        "problema": "Cada parte do sistema cria a sua `ConfiguracaoAntiga()`; mudar a taxa no caixa não muda no "
                    "relatório — dois lugares cobrando valores diferentes.",
        "conceito": "`Configuracao.__new__` devolve SEMPRE o mesmo objeto (guardado em `_instancia`); quem precisa "
                    "chama `Configuracao()` e recebe a única que existe. `reiniciar()` existe só para os testes.",
        "pecas": [["Singleton", "`Configuracao` (`__new__` + `_instancia`)"],
                  ["Clientes", "`total_com_taxa(item)`, `formatar(valor)`"],
                  ["Antes", "`CONFIG_DO_CAIXA` × `CONFIG_DO_RELATORIO`"]],
        "quando_nao": "Em Python um módulo já é único: uma variável no módulo resolve sem cerimônia. Singleton é "
                      "estado global escondido — dificulta testes; prefira injetar a dependência quando der.",
        "alternativa": "Passar a configuração por parâmetro (injeção) — mais explícito, mas todo construtor a recebe.",
        "consequencia": "Um ponto só de verdade para a configuração. Custo: estado global (testes precisam reiniciar).",
        "tripe": [["`Configuracao.__new__`",
                   "Cria o objeto na primeira chamada e devolve o mesmo nas seguintes.",
                   "Singleton: `__new__` decide qual objeto sai (antes do `__init__`); guardar na classe garante um só.",
                   "Sem o `if _instancia is None`, cada chamada criaria outro objeto e as partes divergiriam; com um `__init__` atribuindo valores, cada `Configuracao()` apagaria as mudanças."]],
    },
    "factory_method": {
        "titulo": "Factory Method", "familia": "Padrão de criação" + _EXTRA,
        "modulo": "avisos", "antes": "antes_avisos",
        "aliases": ["factory_method", "factorymethod", "metodo_fabrica", "metodo_de_fabrica"],
        "palavras": ["factory method", "metodo fabrica", "metodo de fabrica", "subclasse decide", "quem cria",
                     "criar o objeto certo", "canal de aviso", "canais de aviso"],
        "problema": "`avisar_antigo(item, canal)` tem um `if/elif` para CRIAR o canal certo no meio do algoritmo — "
                    "canal novo reabre a função.",
        "conceito": "`Avisador.avisar(item)` é o algoritmo comum; o passo que varia — QUAL canal criar — é o método "
                    "fábrica `criar_canal()`, sobrescrito por `AvisadorEmail`, `AvisadorSms`… O criador não conhece "
                    "as classes concretas dos produtos.",
        "pecas": [["Produto", "`Canal` → `CanalEmail`, `CanalSms`"], ["Criador", "`Avisador` (com `avisar`)"],
                  ["Método fábrica", "`criar_canal()`"], ["Criadores concretos", "`AvisadorEmail`, `AvisadorSms`"],
                  ["Extensão (OCP)", "`CanalWhatsapp` + `AvisadorWhatsapp`"]],
        "quando_nao": "Um tipo só de produto, ou escolha resolvida por um dicionário `{nome: Classe}` — em Python "
                      "dá para passar a própria classe como parâmetro.",
        "alternativa": "`if/elif` (ou dicionário) na criação — simples, mas a escolha fica longe de quem sabe o que precisa.",
        "consequencia": "Canal novo = produto + criador novos; `Avisador` intacto. Custo: uma subclasse de criador por produto.",
        "tripe": [["`Avisador.avisar(item)`",
                   "Monta a mensagem da @@ENT@@ e envia pelo canal que `criar_canal()` devolver.",
                   "Factory Method: o algoritmo é comum e só a criação do produto varia — fica num método que a subclasse sobrescreve.",
                   "Com `CanalEmail()` fixo aqui, todo avisador viraria e-mail; com `if` por canal, cada canal novo reabriria o método."]],
    },
    "abstract_factory": {
        "titulo": "Abstract Factory", "familia": "Padrão de criação" + _EXTRA,
        "modulo": "kits", "antes": "antes_kits",
        "aliases": ["abstract_factory", "abstractfactory", "fabrica_abstrata"],
        "palavras": ["abstract factory", "fabrica abstrata", "familia de objetos", "familias de objetos",
                     "familias de componentes", "pecas que combinam", "tema visual", "temas visuais"],
        "problema": "`montar_relatorio_antigo(itens, formato)` decide o formato em CADA peça (cabeçalho, linha, "
                    "rodapé); esquecer um `if` mistura texto com HTML no mesmo relatório.",
        "conceito": "`KitRelatorio` (fábrica abstrata) declara `criar_cabecalho`, `criar_linha` e `criar_rodape`; "
                    "cada kit concreto (`KitTexto`, `KitHtml`) cria TODAS as peças da mesma família. "
                    "`montar_relatorio(kit, itens)` só conhece a interface.",
        "pecas": [["Fábrica abstrata", "`KitRelatorio`"], ["Fábricas concretas", "`KitTexto`, `KitHtml`"],
                  ["Família nova", "`KitMarkdown`"], ["Cliente", "`montar_relatorio(kit, itens)`"]],
        "quando_nao": "Uma família só, ou uma peça só — Factory Method (ou a classe direta) resolve. Um TIPO de peça "
                      "novo obriga a mexer em todos os kits.",
        "alternativa": "Um `if formato` por peça — funciona, mas nada garante que as peças combinem.",
        "consequencia": "Família nova = kit novo, e as peças sempre combinam. Custo: peça nova = método novo em todos os kits.",
        "tripe": [["`montar_relatorio(kit, itens)`",
                   "Monta cabeçalho, uma linha por @@ENT@@ e o rodapé com o total, pedindo cada peça ao kit.",
                   "Abstract Factory: o cliente recebe a família inteira e não sabe qual é — impossível misturar.",
                   "Criando uma peça direto (ex.: `<li>` fixo), um relatório em texto ganharia HTML; trocar o kit troca todas as peças de uma vez."]],
    },
    "builder": {
        "titulo": "Builder", "familia": "Padrão de criação" + _EXTRA,
        "modulo": "construtor", "antes": "antes_construtor",
        "aliases": ["builder", "construtor"],
        "palavras": ["builder", "passo a passo", "montar o objeto", "muitos parametros", "parametros opcionais",
                     "interface fluente", "fluente", "montagem em etapas"],
        "problema": "`nova_@@ENTVAR@@_antiga(...)` recebe os campos na ORDEM certa; trocar dois números de lugar cria "
                    "uma @@ENT@@ válida porém errada, e não há valores padrão.",
        "conceito": "`@@ENT@@Builder` tem um `com_<campo>()` por atributo, cada um devolvendo o próprio builder "
                    "(interface fluente); `construir()` confere o que falta e só então cria a @@ENT@@. "
                    "`DiretorDe@@ENT@@` guarda receitas prontas.",
        "pecas": [["Builder", "`@@ENT@@Builder` (`com_…`, `faltando`, `construir`)"], ["Produto", "`@@ENT@@`"],
                  ["Diretor", "`DiretorDe@@ENT@@.basico(...)`"]],
        "quando_nao": "Objeto com poucos campos: em Python, argumentos NOMEADOS já resolvem a ordem.",
        "alternativa": "Argumentos nomeados com padrão — resolve a ordem, mas não monta em etapas nem guarda receitas.",
        "consequencia": "Montagem legível e em etapas, com erro claro do que falta. Custo: uma classe espelhando os campos.",
        "tripe": [["`@@ENT@@Builder.construir()`",
                   "Confere os campos obrigatórios e cria a @@ENT@@ com os valores juntados.",
                   "Builder: separa o passo a passo da montagem da criação final; cada valor continua validado pelos setters.",
                   "Sem `faltando()`, o erro seria um TypeError confuso do construtor; se `com_…` não devolvesse `self`, não daria para encadear."]],
    },
    "prototype": {
        "titulo": "Prototype", "familia": "Padrão de criação" + _EXTRA,
        "modulo": "prototipos", "antes": "antes_prototipos",
        "aliases": ["prototype", "prototipo", "clone"],
        "palavras": ["prototype", "prototipo", "clonar", "clone", "duplicar", "copiar um modelo",
                     "a partir de um modelo", "modelo pronto"],
        "problema": "`copiar_na_mao(original)` repete campo por campo; quando a @@ENT@@ ganha um dado novo, a cópia "
                    "esquece dele sem avisar.",
        "conceito": "`clonar(original, **mudancas)` copia o objeto inteiro com `copy.deepcopy` (inclusive listas "
                    "internas) e aplica as mudanças pelos setters. `RegistroDePrototipos` guarda modelos e entrega clones.",
        "pecas": [["Protótipo", "a @@ENT@@ modelo"], ["Clonagem", "`clonar(original, **mudancas)`"],
                  ["Registro", "`RegistroDePrototipos` (`registrar`, `criar`)"]],
        "quando_nao": "Objeto simples, criado em uma linha — copiar não economiza nada. Cuidado: cópia RASA "
                      "(`copy.copy`) compartilha as listas internas com o original.",
        "alternativa": "Construir do zero repetindo os valores — espalha a receita e esquece dados novos.",
        "consequencia": "Criar a partir de modelos prontos sem conhecer cada campo. Custo: deepcopy de objeto grande é caro.",
        "tripe": [["`clonar(original, **mudancas)`",
                   "Faz uma cópia profunda e aplica as mudanças pedidas (validadas pelos setters).",
                   "Prototype: o próprio objeto é o molde; a cópia não precisa conhecer cada campo.",
                   "Com `copy.copy` (rasa) listas internas seriam compartilhadas; gravando em `__dict__`, as mudanças pulariam a validação."]],
    },
    # ------------------------------------------------------------------ GoF · ESTRUTURAIS
    "bridge": {
        "titulo": "Bridge", "familia": "Padrão estrutural" + _EXTRA,
        "modulo": "comprovantes", "antes": "antes_comprovantes",
        "aliases": ["bridge", "ponte"],
        "palavras": ["bridge", "duas dimensoes", "variam separadamente", "independentemente", "explosao de classes",
                     "cada combinacao", "combinacoes de tipo e formato"],
        "problema": "Uma classe por COMBINAÇÃO: `SimplesTexto`, `SimplesHtml`, `DetalhadoTexto`, `DetalhadoHtml` — "
                    "2 tipos × 2 formatos = 4 classes repetidas; formato novo exigiria uma classe por tipo.",
        "conceito": "Duas hierarquias separadas: a ABSTRAÇÃO `Comprovante` (Simples, Detalhado) decide O QUE mostrar; "
                    "a IMPLEMENTAÇÃO `Formato` (Texto, Html) decide COMO escrever. A ponte é `self.formato` (composição).",
        "pecas": [["Abstração", "`Comprovante` → `ComprovanteSimples`, `ComprovanteDetalhado`"],
                  ["Implementação", "`Formato` → `FormatoTexto`, `FormatoHtml`"], ["A ponte", "`self.formato` (TEM-UM)"],
                  ["Extensão", "`FormatoMarkdown` serve a todos os tipos"]],
        "quando_nao": "Só uma dimensão varia — herança simples ou Strategy basta. Bridge se planeja no início; "
                      "encaixar duas classes prontas é Adapter.",
        "alternativa": "Herança por combinação — N × M classes com código duplicado.",
        "consequencia": "N + M classes em vez de N × M; formato trocado em tempo de execução. Custo: mais indireção.",
        "tripe": [["`ComprovanteDetalhado.gerar(item)`",
                   "Escolhe as linhas do comprovante e pede ao formato para escrever cada uma.",
                   "Bridge: tipo de comprovante e formato variam separados; a ligação é um atributo, não uma subclasse.",
                   "Escrevendo `<p>` direto aqui, o tipo voltaria a depender do formato; trocar `self.formato` muda a saída sem criar classe."]],
    },
    "composite": {
        "titulo": "Composite", "familia": "Padrão estrutural" + _EXTRA,
        "modulo": "pacotes", "antes": "antes_pacotes",
        "aliases": ["composite", "composto", "arvore"],
        "palavras": ["composite", "arvore", "hierarquia", "pacote com", "pacotes", "combo", "combos",
                     "grupo de itens", "subitens", "itens dentro de"],
        "problema": "`total_antigo(coisa)` pergunta com `isinstance` se é lista ou @@ENT@@ e se chama de novo — "
                    "cada operação nova (descrição, contagem) repete essa checagem.",
        "conceito": "`Componente` define a interface comum (`preco`, `descricao`); `Unitario` (folha) embrulha uma "
                    "@@ENT@@; `Pacote` (composto) guarda filhos — folhas ou pacotes — e repassa a pergunta a eles.",
        "pecas": [["Componente", "`Componente`"], ["Folha", "`Unitario(item)`"],
                  ["Composto", "`Pacote(nome, desconto)` com `adicionar`"], ["Recursão", "`Pacote.preco()` soma `filho.preco()`"]],
        "quando_nao": "Lista plana, sem pacotes dentro de pacotes — `sum()` resolve.",
        "alternativa": "Listas aninhadas + `isinstance` — cada operação repete a recursão.",
        "consequencia": "Árvores de qualquer profundidade com uma interface só. Custo: a interface comum pode ficar genérica.",
        "tripe": [["`Pacote.preco()`",
                   "Soma o preço de cada filho (que pode ser outro pacote) e aplica o desconto do pacote.",
                   "Composite: folha e composto respondem `preco()`, então a soma não pergunta o tipo e a recursão acontece sozinha.",
                   "Com `isinstance` aqui o pacote voltaria a conhecer os tipos; sem `round`, centavos se acumulariam."]],
    },
    "flyweight": {
        "titulo": "Flyweight", "familia": "Padrão estrutural" + _EXTRA,
        "modulo": "tipos_compartilhados", "antes": "antes_tipos_compartilhados",
        "aliases": ["flyweight", "peso_mosca"],
        "palavras": ["flyweight", "peso mosca", "compartilhar", "compartilhado", "compartilhados", "milhares de",
                     "economizar memoria", "pouca memoria"],
        "problema": "Cada registro cria o SEU objeto de @@CONCEITO@@ (nome + fator); 10 000 registros = 10 000 "
                    "objetos iguais na memória.",
        "conceito": "`TipoCompartilhado` guarda só o estado INTRÍNSECO (nome, fator), igual para todos e imutável; "
                    "`FabricaDeTipos.obter(chave)` devolve sempre o mesmo objeto; o estado EXTRÍNSECO (a @@ENT@@) "
                    "chega por parâmetro: `tipo.valor(item)`.",
        "pecas": [["Flyweight", "`TipoCompartilhado` (`__slots__`, imutável)"],
                  ["Fábrica (cache)", "`FabricaDeTipos.obter(chave)`"], ["Estado extrínseco", "`Registro(item, tipo)`"]],
        "quando_nao": "Poucos objetos, ou objetos que mudam — o ganho de memória não paga a complexidade.",
        "alternativa": "Um objeto por registro — simples, porém multiplica a memória.",
        "consequencia": "Milhares de registros apontam para poucos objetos. Custo: imutabilidade e contexto por parâmetro.",
        "tripe": [["`FabricaDeTipos.obter(chave)`",
                   "Devolve o objeto do tipo pedido, criando só na primeira vez.",
                   "Flyweight: o que se repete é compartilhado; o cache garante um objeto por chave.",
                   "Sem o cache, cada chamada criaria outro objeto; se o tipo fosse mutável, mudar um mudaria todos os registros."]],
    },
    "proxy": {
        "titulo": "Proxy", "familia": "Padrão estrutural" + _EXTRA,
        "modulo": "acesso", "antes": "antes_acesso",
        "aliases": ["proxy", "procurador"],
        "palavras": ["proxy", "procurador", "cache", "acesso controlado", "controle de acesso", "permissao",
                     "permissoes", "carregamento tardio", "lazy"],
        "problema": "Quem consulta faz o cache e confere a permissão na mão, misturado com a chamada — cada ponto de "
                    "uso repete (ou esquece) essas regras.",
        "conceito": "`ConsultaComCache` e `ConsultaProtegida` têm o MESMO `calcular(item)` do objeto real "
                    "(`ConsultaDePreco`); por dentro guardam respostas ou barram perfis e só então repassam. "
                    "Quem usa nem percebe — e os proxies empilham.",
        "pecas": [["Sujeito real", "`ConsultaDePreco`"], ["Proxy de cache", "`ConsultaComCache`"],
                  ["Proxy de proteção", "`ConsultaProtegida`"]],
        "quando_nao": "Acesso simples, sem custo nem regra. Proxy × Decorator: o Decorator ACRESCENTA comportamento; "
                      "o Proxy CONTROLA o acesso ao objeto real.",
        "alternativa": "Cache e permissão no código de quem chama — repetido em cada ponto de uso.",
        "consequencia": "Regras de acesso num lugar só, transparentes. Custo: uma indireção e, no cache, dado velho.",
        "tripe": [["`ConsultaComCache.calcular(item)`",
                   "Devolve o valor guardado; se ainda não tem, pergunta ao objeto real e guarda.",
                   "Proxy: mesma interface do real, então substitui o original sem o cliente mudar.",
                   "Com a chave só pelo @@IDENT@@, mudar a @@QTD@@ devolveria valor velho; sem guardar, todo pedido iria ao real."]],
    },
    # ------------------------------------------------------------------ GoF · COMPORTAMENTAIS
    "chain": {
        "titulo": "Chain of Responsibility", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "aprovacao", "antes": "antes_aprovacao",
        "aliases": ["chain", "chain_of_responsibility", "cadeia", "cadeia_de_responsabilidade"],
        "palavras": ["chain of responsibility", "cadeia de responsabilidade", "cadeia", "aprovacao", "aprovar",
                     "alcada", "alcadas", "niveis de aprovacao", "escalonar"],
        "problema": "`quem_aprova_antigo(item)` tem todas as alçadas num `if/elif`; incluir um nível (ex.: "
                    "supervisor) obriga a reescrever a função.",
        "conceito": "Cada `Aprovador` conhece só a SUA alçada e o PRÓXIMO elo: se pode, aprova; senão, repassa. A "
                    "cadeia é montada de fora (`encadear`) — incluir ou tirar um nível não mexe nos outros.",
        "pecas": [["Elo base", "`Aprovador` (`encadear`, `aprovar`)"], ["Elos", "`Atendente`, `Gerente`, `Diretoria`"],
                  ["Nível novo", "`Supervisor`"], ["Montagem", "`cadeia_padrao()`"]],
        "quando_nao": "Poucas regras fixas — um `if/elif` curto é mais legível. O pedido pode chegar ao fim da cadeia "
                      "sem ninguém tratar.",
        "alternativa": "`if/elif` central — simples, mas concentra todas as alçadas.",
        "consequencia": "Níveis entram e saem sem mexer nos demais. Custo: seguir o pedido exige percorrer a cadeia.",
        "tripe": [["`Aprovador.aprovar(item)`",
                   "Aprova se o total cabe na alçada; senão repassa ao próximo; no fim devolve \"sem aprovador\".",
                   "Chain of Responsibility: cada elo decide sozinho e não conhece a cadeia inteira.",
                   "Sem testar `proximo is None`, o último elo quebraria com AttributeError; trocando a ordem dos elos, muda quem aprova."]],
    },
    "command": {
        "titulo": "Command", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "comandos", "antes": "antes_comandos",
        "aliases": ["command", "comando"],
        "palavras": ["command", "desfazer", "refazer", "undo", "redo", "fila de acoes", "historico de acoes",
                     "acao como objeto", "acoes como objetos"],
        "problema": "`alterar_antigo(item, campo, valor)` muda a @@ENT@@ direto e a ação some — sem registro do "
                    "valor anterior, não dá para desfazer.",
        "conceito": "Cada ação vira um OBJETO (`AlterarCampo`) que sabe `executar()` e `desfazer()` (guarda o valor "
                    "anterior). `Historico` (o invocador) empilha os comandos e faz desfazer/refazer em ordem.",
        "pecas": [["Comando", "`Comando` → `AlterarCampo`"], ["Invocador", "`Historico` (`executar`, `desfazer`, `refazer`)"],
                  ["Receptor", "a `@@ENT@@` (setters validam)"]],
        "quando_nao": "Ação simples que nunca será desfeita, enfileirada ou registrada — chame o método direto.",
        "alternativa": "Guardar cópias do objeto inteiro antes de cada ação — é o Memento (mais memória).",
        "consequencia": "Desfazer/refazer, fila e histórico de ações. Custo: uma classe por tipo de ação.",
        "tripe": [["`Historico.executar(comando)`",
                   "Executa o comando e só então o empilha; limpa a pilha de refazer.",
                   "Command: a ação é um objeto, então pode ser guardada, desfeita e refeita.",
                   "Empilhando antes de executar, um comando inválido entraria no histórico; sem limpar `_desfeitos`, refazer misturaria linhas do tempo."]],
    },
    "interpreter": {
        "titulo": "Interpreter", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "regras", "antes": "antes_regras",
        "aliases": ["interpreter", "interpretador"],
        "palavras": ["interpreter", "interpretador", "interpretar", "expressao", "expressoes", "gramatica",
                     "mini linguagem", "regra escrita", "regras escritas", "regra em texto", "formula", "formulas"],
        "problema": "`regra_antiga(item)` traz a condição fixa no código — mudar \"a partir de 3\" para \"a partir "
                    "de 4\" exige programar e publicar de novo.",
        "conceito": "Cada pedaço da gramática é uma classe com `interpretar(item)`: `Comparacao` (terminal), `E` e "
                    "`Ou` (não terminais). `ler_regra(texto)` monta a árvore a partir do texto — a regra vira DADO.",
        "pecas": [["Expressão terminal", "`Comparacao(campo, operador, numero)`"], ["Não terminais", "`E`, `Ou`"],
                  ["Leitor (parser)", "`ler_regra(texto)`"]],
        "quando_nao": "Linguagem grande (vira compilador — use uma biblioteca de parsing) ou regra que nunca muda.",
        "alternativa": "`eval()` do texto — perigoso (executa qualquer código) e sem mensagens de erro úteis.",
        "consequencia": "Regras guardáveis como texto e combináveis. Custo: cada operador novo é uma classe.",
        "tripe": [["`ler_regra(texto)`",
                   "Quebra o texto em \"ou\" e depois em \"e\" e monta a árvore de `Comparacao`.",
                   "Interpreter: cada regra da gramática vira uma classe; o texto vira objetos que se avaliam sozinhos.",
                   "Separando primeiro por \" e \", o \"e\" valeria depois do \"ou\" (outra regra); com `eval`, qualquer código rodaria."]],
    },
    "iterator": {
        "titulo": "Iterator", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "colecao", "antes": "antes_colecao",
        "aliases": ["iterator", "iterador"],
        "palavras": ["iterator", "iterador", "iterar", "percorrer", "percorre", "navegar pela colecao", "colecao",
                     "proximo item"],
        "problema": "`totais_antigo(colecao)` lê `colecao._itens[i]` por índice — depende da lista interna; trocar a "
                    "estrutura quebra todos os laços.",
        "conceito": "`Colecao@@ENT@@` esconde como guarda (dicionário por @@IDENT@@) e entrega um ITERADOR "
                    "(`IteradorDeItens`, com `__next__`) em `__iter__`. Percursos especiais (`acima_de`, "
                    "`ordenados_por_total`) não expõem o interior.",
        "pecas": [["Agregado", "`Colecao@@ENT@@`"], ["Iterador", "`IteradorDeItens` (`__iter__`, `__next__`)"],
                  ["Percursos", "`acima_de` (gerador), `ordenados_por_total`"]],
        "quando_nao": "Lista e dicionário já são iteráveis em Python; classe de iterador só para percurso especial — "
                      "um gerador (`yield`) é o atalho.",
        "alternativa": "Expor a lista interna — rápido, mas acopla todo mundo à estrutura.",
        "consequencia": "Estrutura interna livre para mudar; percursos independentes. Custo: mais uma classe.",
        "tripe": [["`IteradorDeItens.__next__()`",
                   "Devolve o próximo item e avança a posição; no fim levanta `StopIteration`.",
                   "Iterator: a posição fica no iterador, então dois `for` não se atrapalham.",
                   "Sem `StopIteration` o `for` não termina (ou dá IndexError); com a posição na coleção, dois percursos se misturariam."]],
    },
    "mediator": {
        "titulo": "Mediator", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "mediador", "antes": "antes_mediador",
        "aliases": ["mediator", "mediador"],
        "palavras": ["mediator", "mediador", "intermediario", "coordenar componentes", "componentes conversam",
                     "torre de controle", "central de mensagens"],
        "problema": "O campo de @@QTD@@ conhece o seletor, o resumo e o botão e mexe neles direto — todos acoplados "
                    "a todos; componente novo obriga a mexer nos outros.",
        "conceito": "Cada componente só conhece o MEDIADOR e avisa `notificar(self, evento)`; `FormularioMediador` "
                    "decide quem reage (recalcula o resumo, liga/desliga o botão).",
        "pecas": [["Mediador", "`FormularioMediador`"],
                  ["Componentes", "`Campo@@QTDCAMEL@@`, `SeletorTipo`, `Resumo`, `BotaoConfirmar`"],
                  ["Aviso", "`mediador.notificar(origem, evento)`"]],
        "quando_nao": "2–3 objetos que conversam pouco. Cuidado para o mediador não virar um \"objeto deus\".",
        "alternativa": "Componentes chamando uns aos outros — N × N ligações.",
        "consequencia": "Componentes independentes e reaproveitáveis. Custo: a complexidade se concentra no mediador.",
        "tripe": [["`FormularioMediador.notificar(origem, evento)`",
                   "Recalcula o resumo (@@QTD@@ × preço × fator do tipo) e só habilita o botão se a @@QTD@@ for válida.",
                   "Mediator: a coordenação fica num lugar; os componentes não se conhecem.",
                   "Se o campo voltasse a atualizar o resumo direto, perderia a reutilização; esquecendo o botão aqui, ele ficaria ligado com valor inválido."]],
    },
    "memento": {
        "titulo": "Memento", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "versoes", "antes": "antes_versoes",
        "aliases": ["memento"],
        "palavras": ["memento", "restaurar", "voltar ao estado", "versao anterior", "versoes anteriores",
                     "snapshot", "salvar o estado", "rascunho"],
        "problema": "Para \"voltar atrás\", quem usa copia os campos internos (`_campo`) da @@ENT@@ num dicionário — "
                    "depende do interior dela e esquece campos novos.",
        "conceito": "`Editor@@ENT@@` (originador) cria um `Memento` com a cópia do próprio estado e sabe restaurá-lo; "
                    "`HistoricoDeVersoes` (zelador) só empilha mementos, sem olhar dentro.",
        "pecas": [["Originador", "`Editor@@ENT@@` (`salvar`, `restaurar`)"], ["Memento", "`Memento` (estado + rótulo)"],
                  ["Zelador", "`HistoricoDeVersoes`"]],
        "quando_nao": "Estado grande e muitas versões (memória). Memento × Command: o Command desfaz UMA ação; o "
                      "Memento volta o estado inteiro.",
        "alternativa": "Copiar os campos na mão — quebra o encapsulamento e esquece o que for novo.",
        "consequencia": "Desfazer sem expor o interior. Custo: cada versão ocupa memória.",
        "tripe": [["`Editor@@ENT@@.salvar(rotulo)`",
                   "Cria um Memento com uma CÓPIA profunda do estado atual.",
                   "Memento: só o originador conhece o próprio estado; o zelador guarda sem abrir.",
                   "Sem `deepcopy`, o memento apontaria para o mesmo estado e mudaria junto; guardando os campos fora, o encapsulamento se perde."]],
    },
    "observer": {
        "titulo": "Observer", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "eventos", "antes": "antes_eventos",
        "aliases": ["observer", "observador"],
        "palavras": ["observer", "observador", "observadores", "notificar", "notificacao", "notificacoes",
                     "assinantes", "inscritos", "inscrever", "evento", "eventos", "quando mudar", "publicar"],
        "problema": "`alterar_antigo(...)` chama painel e log um por um — conhece todos os interessados; um "
                    "interessado novo obriga a editar a função.",
        "conceito": "`@@ENT@@Observavel` (sujeito) guarda a lista de observadores e, a cada mudança, chama "
                    "`atualizar(evento)` em todos. Interessado novo = `inscrever(obj)`; o sujeito não muda.",
        "pecas": [["Sujeito", "`@@ENT@@Observavel` (`inscrever`, `cancelar`, `notificar`)"],
                  ["Observadores", "`PainelObservador`, `LogObservador`, `AlertaObservador`"],
                  ["Evento", "dict com campo, valor, total anterior e total"]],
        "quando_nao": "Um interessado único e fixo — chame-o direto. Cadeias de observadores escondem o fluxo.",
        "alternativa": "Chamar cada interessado na mão — acoplamento a todos.",
        "consequencia": "Sujeito e observadores independentes. Custo: ordem e efeitos ficam menos visíveis.",
        "tripe": [["`@@ENT@@Observavel.alterar(campo, valor)`",
                   "Altera a @@ENT@@ (validando) e avisa todos os inscritos com um evento.",
                   "Observer: o sujeito não sabe quem escuta; cada observador reage do seu jeito.",
                   "Notificando ANTES do setter, um valor inválido seria anunciado; sem copiar a lista, quem se cancelasse no meio faria pular um observador."]],
    },
    "state": {
        "titulo": "State", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "situacao", "antes": "antes_situacao",
        "aliases": ["state", "estado", "estados"],
        "palavras": ["state", "maquina de estados", "ciclo de vida", "transicao", "transicoes", "muda de estado",
                     "mudanca de estado", "confirmado", "cancelado", "concluido"],
        "problema": "`SituacaoAntiga` repete a mesma escada de `if/elif` sobre `self.status` em `confirmar`, "
                    "`concluir` e `cancelar`.",
        "conceito": "Cada estado é uma classe (`Aberto`, `Confirmado`, `Concluido`, `Cancelado`) que sabe as SUAS "
                    "transições; `Situacao@@ENT@@` (contexto) guarda o estado atual e delega. Transição proibida "
                    "levanta `TransicaoInvalida`.",
        "pecas": [["Contexto", "`Situacao@@ENT@@`"], ["Estado base", "`Estado` (tudo proibido por padrão)"],
                  ["Estados", "`Aberto`, `Confirmado`, `Concluido`, `Cancelado`"]],
        "quando_nao": "Dois estados e uma regra (um booleano basta). State × Strategy: no State o próprio estado "
                      "troca o objeto do contexto; no Strategy quem escolhe é o cliente.",
        "alternativa": "`if/elif` por status em cada método — repetido e fácil de esquecer uma transição.",
        "consequencia": "Cada estado num lugar; estado novo = classe nova. Custo: uma classe por estado.",
        "tripe": [["`Aberto.confirmar(contexto)`",
                   "Troca o estado do contexto para `Confirmado`.",
                   "State: a transição pertence ao estado de origem; o contexto só delega.",
                   "Sem sobrescrever, valeria o padrão da base (TransicaoInvalida); trocando para `Concluido`, pularia a confirmação."]],
    },
    "template_method": {
        "titulo": "Template Method", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "fechamento", "antes": "antes_fechamento",
        "aliases": ["template_method", "templatemethod", "metodo_template", "template"],
        "palavras": ["template method", "metodo template", "esqueleto", "roteiro fixo", "mesmo roteiro",
                     "passos fixos", "mesmos passos", "algoritmo fixo", "gancho", "hook"],
        "problema": "`fechar_padrao_antigo` e `fechar_com_taxa_antigo` são cópias do mesmo roteiro (validar → "
                    "calcular → ajustar → formatar); corrigir um passo exige lembrar de todas as cópias.",
        "conceito": "`Fechamento.fechar(item)` é o método TEMPLATE: fixa a ordem dos passos; as subclasses "
                    "sobrescrevem só o passo que muda (`ajustar`), e o gancho tem padrão vazio.",
        "pecas": [["Classe abstrata", "`Fechamento`"], ["Método template", "`fechar(item)`"],
                  ["Passos / gancho", "`validar`, `calcular`, `ajustar` (gancho), `formatar`"],
                  ["Subclasses", "`FechamentoPadrao`, `FechamentoComTaxa`, `Fechamento@@VTM@@`"]],
        "quando_nao": "Só um passo varia — passe uma função (Strategy). Template Method usa HERANÇA; Strategy, COMPOSIÇÃO.",
        "alternativa": "Copiar o roteiro em cada variação — duplicação.",
        "consequencia": "Roteiro num lugar só; subclasses mínimas. Custo: a herança amarra as subclasses à base.",
        "tripe": [["`Fechamento.fechar(item)`",
                   "Chama validar, calcular, ajustar e formatar, nessa ordem.",
                   "Template Method: o esqueleto é fixo e as subclasses preenchem só os passos variáveis.",
                   "Se uma subclasse sobrescrever `fechar`, perde-se a garantia da ordem; esquecendo `validar`, total inválido passaria."]],
    },
    "visitor": {
        "titulo": "Visitor", "familia": "Padrão comportamental" + _EXTRA,
        "modulo": "orcamento", "antes": "antes_orcamento",
        "aliases": ["visitor", "visitante"],
        "palavras": ["visitor", "visitante", "visitar", "despacho duplo", "double dispatch",
                     "operacao nova sem mudar", "operacoes sobre a estrutura", "varios tipos de linha"],
        "problema": "`total_antigo` e `texto_antigo` percorrem as linhas perguntando o tipo — cada operação nova "
                    "repete a escada; cada tipo novo mexe em todas.",
        "conceito": "Cada linha tem `aceitar(visitante)` e chama o método certo do visitante (despacho duplo); cada "
                    "OPERAÇÃO é um visitante (`CalculoDoTotal`, `TextoDoOrcamento`) com um `visitar_*` por tipo.",
        "pecas": [["Elementos", "`Linha@@ENT@@`, `LinhaExtra`, `LinhaDesconto` (`aceitar`)"], ["Estrutura", "`Orcamento`"],
                  ["Visitantes", "`CalculoDoTotal`, `TextoDoOrcamento`"], ["Operação nova", "`ContagemPorTipo`"]],
        "quando_nao": "Tipos de elemento que mudam muito (cada tipo novo mexe em TODOS os visitantes) — prefira "
                      "polimorfismo comum.",
        "alternativa": "`isinstance`/`if` por tipo em cada operação — repetido.",
        "consequencia": "Operação nova sem tocar nos elementos. Custo: tipo novo de elemento = método novo em todos os visitantes.",
        "tripe": [["`LinhaExtra.aceitar(visitante)`",
                   "Chama `visitante.visitar_extra(self)`.",
                   "Visitor: o despacho duplo escolhe o método pelo tipo da linha E pelo visitante, sem `if`.",
                   "Chamando outro `visitar_*`, a linha seria tratada como outro tipo; sem `aceitar`, voltaria o `isinstance` em cada operação."]],
    },
})

# Grupos aceitos em --padrao e no texto do assunto (expandem para vários padrões).
APELIDOS = {"todos": "todos", "tudo": "todos", "all": "todos", "gof": "gof", "gang_of_four": "gof",
            "prova": "prova", "p3": "prova", "aulas": "prova", "ilp037": "prova", "fundamentos": "fundamentos",
            "criacao": "criacao", "criacional": "criacao", "criacionais": "criacao", "creational": "criacao",
            "estrutural": "estrutural", "estruturais": "estrutural", "structural": "estrutural",
            "comportamental": "comportamental", "comportamentais": "comportamental", "behavioral": "comportamental"}
for _chave, _info in PADROES.items():
    for _apelido in _info["aliases"] + [_chave]:
        APELIDOS[normalizar(_apelido)] = _chave
# Frases do assunto que pedem um GRUPO inteiro de padrões.
GRUPOS_PALAVRAS = {
    "todos": ["todos os padroes"],
    "gof": ["gof", "gang of four", "padroes gof", "todos os padroes gof"],
    "criacao": ["padroes de criacao", "padrao de criacao", "criacionais", "criacional"],
    "estrutural": ["padroes estruturais", "padrao estrutural", "estruturais"],
    "comportamental": ["padroes comportamentais", "padrao comportamental", "comportamentais"],
}

# palavras do texto que NÃO devem contar como domínio (ex.: "biblioteca de pagamento" é Adapter)
FRASES_NAO_DOMINIO = ["biblioteca de pagamento", "biblioteca de terceiro", "biblioteca externa", "biblioteca de terceiros"]


def contem(texto_normalizado, palavra):
    alvo = normalizar(palavra)
    return re.search(r"(?<![a-z0-9])" + re.escape(alvo) + r"(?![a-z0-9])", texto_normalizado) is not None


BONUS_NOME = 3   # o NOME do domínio no texto ("hotel", "lava rapido") vale 3 palavras


def pontuar_dominios(texto_normalizado):
    """[(pontos, chave, palavras que bateram)] dos domínios que bateram, do mais pontuado ao menos.

    Pontos = palavras do domínio que aparecem no texto + 3 se o nome do domínio aparece. Empate, nesta ordem:
    mais letras nas palavras que bateram (a palavra mais específica vence) → ordem do catálogo (ID menor).
    O `generico` não pontua: as palavras dele (sistema, cadastro, cliente…) estão em quase todo pedido.
    """
    candidatos = []
    for ordem, (chave, dom) in enumerate(DOMINIOS.items()):
        if chave == "generico":
            continue
        hits = [p for p in dom["palavras"] if contem(texto_normalizado, p)]
        nome = contem(texto_normalizado, chave.replace("_", " "))
        pontos = len(hits) + (BONUS_NOME if nome else 0)
        if pontos:
            letras = sum(len(normalizar(h)) for h in hits)
            candidatos.append((-pontos, -letras, ordem, chave, hits + ([f"nome: {chave}"] if nome else [])))
    return [(-c[0], c[3], c[4]) for c in sorted(candidatos)]


def escolher_dominio(texto_normalizado):
    """(chave, palavras) do domínio de maior pontuação; nenhum bateu → ("generico", [])."""
    ranking = pontuar_dominios(texto_normalizado)
    return (ranking[0][1], ranking[0][2]) if ranking else ("generico", [])


def analisar_assunto(assunto):
    """Decide, por regras fixas de palavras-chave, o domínio e os padrões de um texto livre."""
    t = normalizar(assunto)
    t_dom = t
    for frase in FRASES_NAO_DOMINIO:
        t_dom = t_dom.replace(frase, " ")
    melhor, melhor_hits = escolher_dominio(t_dom)
    motivos = {}
    for chave in ORDEM_PADROES:
        hits = [p for p in PADROES[chave]["palavras"] if contem(t, p)]
        if hits:
            motivos[chave] = hits
    # Frases que pedem um GRUPO inteiro ("padrões de criação", "gof"...): cada membro registra o motivo.
    acertos = {g: [f for f in frases if contem(t, f)] for g, frases in GRUPOS_PALAVRAS.items()}
    if any(acertos[g] for g in acertos if g != "todos"):
        acertos["todos"] = []            # "todos os padrões DE CRIAÇÃO" é o grupo específico, não os 28
    for grupo, hits in acertos.items():
        for chave in (GRUPOS[grupo] if hits else []):
            motivos.setdefault(chave, []).append(f"grupo {grupo}: {hits[0]}")
    padroes = [p for p in ORDEM_PADROES if p in motivos]
    sistema = None
    if melhor == "generico":
        m = re.search(r"(?:sistema|app|aplicativo|aplicacao|aplicação|software|projeto|site|plataforma)\s+"
                      r"(?:de|para|da|do|das|dos)\s+(.+?)(?:\s+(?:com|que|onde|em que|no qual|na qual|e|para|cujo|cuja)\s|[,.;:!?]|$)",
                      assunto.strip().lower())
        if m:
            sistema = " ".join(p[:1].upper() + p[1:] for p in m.group(1).split())
    import tipos_campos   # identificador de tipos: a lista de campos que o pedido declarou (se declarou)
    return {"dominio": melhor, "dominio_palavras": melhor_hits, "padroes": padroes,
            "padroes_palavras": motivos, "sistema": sistema,
            "campos": [{"nome": c["nome"], "tipo": c["tipo"]} for c in tipos_campos.extrair_campos(assunto)]}


def normalizar_padroes(lista, inserir_base=True):
    """Apelidos e grupos → lista na ORDEM canônica (ORDEM_PADROES). Grupos: todos, gof, prova, criacao..."""
    escolhidos = []
    for item in lista:
        for parte in re.split(r"[,\s]+", item.strip()):
            if not parte:
                continue
            chave = APELIDOS.get(normalizar(parte).replace("-", "_"))
            if chave is None:
                raise ErroGerador(f"padrão desconhecido: {parte!r}. Use --listar para ver as opções.")
            for membro in GRUPOS.get(chave, [chave]):          # um grupo expande para os seus padrões
                if membro not in escolhidos:
                    escolhidos.append(membro)
    if inserir_base and "encapsulamento" not in escolhidos:  # a entidade com @property é sempre a base
        escolhidos.insert(0, "encapsulamento")
    return [p for p in ORDEM_PADROES if p in escolhidos]


# =============================================================================
# 3. ESPECIFICAÇÃO NORMALIZADA (tudo que os modelos precisam saber)
# =============================================================================
RESERVADOS = {"total", "self", "item", "tipo", "id", "pk", "indice", "mudancas", "objects", "valor", "id_interno"}
# Nomes que um campo do model Django não pode ter (sombreariam métodos do Model).
RESERVADOS_DJANGO = {"save", "delete", "clean", "full_clean", "clean_fields", "check", "refresh_from_db",
                     "validate_unique", "validate_constraints", "get_deferred_fields", "serializable_value",
                     "from_db", "asave", "adelete", "arefresh_from_db", "prepare_database_save", "DoesNotExist",
                     "MultipleObjectsReturned", "TIPOS", "id_interno_formatado"}
# str/int/float desde o início; bool (sim/não) e data (AAAA-MM-DD) chegaram com o identificador de tipos.
TIPOS_ATRIBUTO = ("str", "int", "float", "bool", "data")
DATAS_EXEMPLO = ["2026-01-10", "2026-02-15", "2026-03-20", "2026-04-25"]
PROIBIDO_EM_TEXTO = re.compile(r'["{}\\]')


class Spec:
    def __init__(self, dados, padroes, django=False, exercicio=False, origem=None,
                 estudo=True, comentarios=True, web=None):
        # estudo=False → "só gerar": sem antes_*.py, sem ADRs, README curto.
        # comentarios=False → "apenas o código": comentários e docstrings removidos dos .py.
        # web → estilo das páginas, tema, comentários de apresentação, UUID, LNNL, apps/, segurança.
        self.estudo = bool(estudo)
        self.comentarios = bool(comentarios)
        self.web = normalizar_web(web)
        try:
            self._montar(dados, padroes, django, exercicio, origem)
        except KeyError as erro:
            raise ErroGerador(f"especificação incompleta: falta a chave {erro}") from erro
        except (TypeError, ValueError, IndexError) as erro:
            raise ErroGerador(f"especificação com formato inválido: {erro}") from erro
        self._validar()

    def _montar(self, dados, padroes, django, exercicio, origem):
        d = copy.deepcopy(dados)
        self.dados = d
        self.sistema = d["sistema"]
        self.slug = snake(self.sistema)
        self.ent = d["entidade"]
        self.ent_var = camel_para_snake(self.ent)
        # PERFIL do domínio (dominios.PERFIS): pasta, projeto e app Django, rota do app, DRF e pytest.ini próprios
        # (ex.: a Prova P3 — provaP3 / cooperativa / citricultura). Sem perfil: o de sempre.
        self.perfil = dict(d.get("perfil") or {})
        self.projeto = self.perfil.get("projeto") or "config"
        self.app = self.perfil.get("app") or plural(self.ent_var)
        if self.app in ("nucleo", "config", "tests", "web", "gabarito", "docs", self.projeto):
            self.app += "_app"
        self.rota = self.perfil.get("rota") or ""                  # "" = o app na raiz do site
        self.drf = bool(self.perfil.get("drf"))
        self.pasta = self.perfil.get("pasta")                      # nome fixo da pasta (senão, nome_saida)
        self.pytest_arquivos = self.perfil.get("pytest_arquivos") or "test_*.py"
        self.atributos = d["atributos"]
        self.ident, self.qtd, self.preco = d["ident"], d["quantidade"], d["preco"]
        self.unidade = d["unidade"]
        self.precos = list(d.get("precos_exemplo") or [100.0, 49.9, 250.0, 0.0])
        v = d["variantes"]
        self.conceito = v["conceito"]
        self.variantes = [(n, float(f), camel(n), camel_para_snake(camel(n))) for n, f in v["itens"]]
        n, f = v["nova"]
        self.vnova = (n, float(f), camel(n), camel_para_snake(camel(n)))
        c = d["categorias"]
        self.cat_unid = c["unidade"]
        self.cat_base = (camel(c["base"][0]), c["base"][1], float(c["base"][2]))
        self.cat_sub = [(camel(x[0]), x[1], float(x[2])) for x in c["subtipos"]]
        self.cat_nova = (camel(c["nova"][0]), c["nova"][1], float(c["nova"][2]))
        e = d["extras"]
        self.extras = [(camel(n), float(val), txt, camel_para_snake(camel(n))) for n, val, txt in e["fixos"]]
        n, f, txt = e["percentual"]
        self.perc = (camel(n), float(f), txt)
        self.gw = camel(d["gateway"])
        self.gw_pref = ("".join(ch for ch in self.gw if ch.isupper())[:3] or "GW")
        self.recurso = d["recurso"]
        self.recursos = list(d["recursos"])
        self.painel = d["painel"]
        self.nomes = list(d["nomes"])
        self.padroes = list(padroes)
        self.django = django
        self.exercicio = exercicio
        self.origem = origem or {}

    # ---------------------------------------------------------------- validação
    def _validar(self):
        erros = []

        def identificador(nome):
            return isinstance(nome, str) and nome.isidentifier() and not keyword.iskeyword(nome)

        if not identificador(self.ent) or not self.ent[0].isupper():
            erros.append(f"entidade {self.ent!r} deve ser um nome de classe (ex.: Reserva, PedidoCompra)")
        textos = [self.sistema, self.unidade, self.conceito, self.cat_unid, self.recurso,
                  self.cat_base[1], self.cat_nova[1], *[s[1] for s in self.cat_sub],
                  *[x[2] for x in self.extras], self.perc[2], *self.painel.values(), *self.nomes]
        for t in textos:
            if not isinstance(t, str) or not t.strip() or PROIBIDO_EM_TEXTO.search(t):
                erros.append(f"texto inválido {t!r}: não pode ser vazio nem conter aspas duplas, chaves ou barra invertida")
        nomes = [a["nome"] for a in self.atributos]
        if len(set(nomes)) != len(nomes):
            erros.append("há atributos com nome repetido")
        por_nome = {}
        for a in self.atributos:
            n = a["nome"]
            por_nome[n] = a
            if not identificador(n) or n != n.lower() or n.startswith("_"):
                erros.append(f"atributo {n!r}: use snake_case (ex.: valor_diaria)")
            if n in RESERVADOS or n in RESERVADOS_DJANGO:
                erros.append(f"atributo {n!r} é reservado pelo gerador")
            if a["tipo"] not in TIPOS_ATRIBUTO:
                erros.append(f"atributo {n!r}: tipo deve ser {', '.join(TIPOS_ATRIBUTO)}")
            if a["regra"] not in ("obrigatorio", "minimo", "faixa", "livre", "lista"):
                erros.append(f"atributo {n!r}: regra deve ser obrigatorio, minimo, faixa, lista ou livre")
            if a["regra"] == "lista":
                opcoes = a.get("opcoes") or []
                if a["tipo"] not in ("str", "int") or len(opcoes) < 2 or len(set(opcoes)) != len(opcoes) or not all(
                        (isinstance(o, str) and o.strip() and not PROIBIDO_EM_TEXTO.search(o)) if a["tipo"] == "str"
                        else (isinstance(o, int) and not isinstance(o, bool)) for o in opcoes):
                    erros.append(f"atributo {n!r}: lista precisa de 2+ valores diferentes, todos texto (str) ou todos "
                                 "inteiros (int)")
            if a["regra"] == "livre" and a["tipo"] != "str":
                erros.append(f"atributo {n!r}: a regra livre é para texto (str)")
            if a["regra"] == "obrigatorio" and a["tipo"] not in ("str", "bool", "data"):
                erros.append(f"atributo {n!r}: a regra obrigatorio é para str, bool ou data")
            if a["regra"] in ("minimo", "faixa") and a["tipo"] not in ("int", "float"):
                erros.append(f"atributo {n!r}: minimo/faixa são para números")
            if a["regra"] == "minimo" and a.get("min") is None:
                erros.append(f"atributo {n!r}: informe 'min'")
            if a["regra"] == "faixa" and (a.get("min") is None or a.get("max") is None or a["min"] >= a["max"]):
                erros.append(f"atributo {n!r}: faixa precisa de 'min' < 'max'")
        i, q, p = por_nome.get(self.ident), por_nome.get(self.qtd), por_nome.get(self.preco)
        if not i or i["tipo"] != "str" or i["regra"] != "obrigatorio":
            erros.append("'ident' deve apontar um atributo str com regra obrigatorio")
        if not q or q["tipo"] != "int" or q.get("min") != 1 or (q["regra"] == "faixa" and q["max"] < 4):
            erros.append("'quantidade' deve ser int com min 1 (e max >= 4, se faixa)")
        if not p or p["tipo"] != "float" or p["regra"] != "minimo" or p.get("min") != 0:
            erros.append("'preco' deve ser float com regra minimo e min 0")
        chaves = [x[3] for x in self.variantes] + [self.vnova[3]]
        if len(self.variantes) < 2 or len(set(chaves)) != len(chaves):
            erros.append("variantes: pelo menos 2, com nomes diferentes entre si e da 'nova'")
        if any(f < 0 for _, f, _, _ in self.variantes + [self.vnova]):
            erros.append("variantes: fatores não podem ser negativos")
        if len(self.extras) < 2 or any(v <= 0 for _, v, _, _ in self.extras):
            erros.append("extras: pelo menos 2 fixos, com valor > 0")
        if self.perc[1] <= 0 or abs(self.perc[1] - 1) < 0.05:
            erros.append("extras.percentual: fator > 0 e diferente de 1 (ex.: 0.9 ou 1.2)")
        nomes_cls = [self.cat_base[0]] + [x[0] for x in self.cat_sub] + [self.cat_nova[0]]
        if not self.cat_sub or len(set(nomes_cls)) != len(nomes_cls):
            erros.append("categorias: pelo menos 1 subtipo e nomes de classe diferentes")
        if len(self.recursos) != 3 or len(set(self.recursos)) != 3 or not all(isinstance(r, int) for r in self.recursos):
            erros.append("recursos: exatamente 3 números inteiros diferentes")
        if len(self.nomes) < 4:
            erros.append("nomes: informe pelo menos 4 nomes de exemplo")
        if len(self.precos) < 4 or any(x < 0 for x in self.precos):
            erros.append("precos_exemplo: 4 valores >= 0")
        for chave in ("titulo", "livre", "ocupado", "acao_livre", "acao_ocupado", "zero", "contagem"):
            if chave not in self.painel:
                erros.append(f"painel: falta a chave {chave!r}")
        for campo, valor in (("projeto", self.projeto), ("app", self.app)):      # o perfil vira nome de pacote
            if not identificador(valor) or valor != valor.lower():
                erros.append(f"perfil.{campo} {valor!r}: use um nome de pacote Python em minúsculas (ex.: cooperativa)")
        if self.rota and not re.fullmatch(r"[a-z0-9_-]+/", self.rota):
            erros.append(f"perfil.rota {self.rota!r}: use letras minúsculas e terminar com / (ex.: citricultura/)")
        if self.pasta is not None and not re.fullmatch(r"[A-Za-z0-9_]+", str(self.pasta)):
            erros.append(f"perfil.pasta {self.pasta!r}: só letras, números e _ (ex.: provaP3)")
        if erros:
            raise ErroGerador("especificação inválida:\n  - " + "\n  - ".join(erros))

    # ---------------------------------------------------------------- dados de exemplo
    def valor_exemplo(self, a, i):
        n = a["nome"]
        if n == self.ident:
            return self.nomes[i % len(self.nomes)]
        if n == self.qtd:
            return [2, 3, 1, 4][i % 4]
        if n == self.preco:
            return float(self.precos[i % 4])
        if a["regra"] == "lista":
            return a["opcoes"][i % len(a["opcoes"])]
        if a["tipo"] == "str" and a["regra"] == "obrigatorio":
            return f"{n.replace('_', ' ').capitalize()} {i + 1}"
        if a["tipo"] == "bool":
            return [True, False, True, False][i % 4]
        if a["tipo"] == "data":
            return DATAS_EXEMPLO[i % 4]
        if a["tipo"] == "int":
            if a["regra"] == "faixa":
                return a["min"] + (i % (a["max"] - a["min"] + 1))
            return a["min"] + 100 * (i + 1)
        if a["tipo"] == "float":
            if a["regra"] == "faixa":
                return round(a["min"] + (a["max"] - a["min"]) * [0.5, 0.25, 0.75, 0.0][i % 4], 2)
            return round(a["min"] + 10.0 * (i + 1), 2)
        return None                                            # str livre: usa o padrão ""

    def dados_exemplo(self, i):
        out = {}
        for a in self.atributos:
            if a["regra"] != "livre":
                out[a["nome"]] = self.valor_exemplo(a, i)
        return out

    def total_exemplo(self, i):
        d = self.dados_exemplo(i)
        return round(d[self.qtd] * d[self.preco], 2)

    @staticmethod
    def invalidos(a):
        if a["regra"] == "lista":                            # fora da lista (e do tipo errado) é recusado
            if a["tipo"] == "str":
                return ["", "   ", "valor fora da lista", 123, None]
            return [max(a["opcoes"]) + 1, str(a["opcoes"][0]), True, 2.5, None]
        if a["tipo"] == "str":
            return ["", "   ", 123, None]
        if a["tipo"] == "bool":
            return [1, 0, "sim", None]                       # só True/False (1 e 0 NÃO valem)
        if a["tipo"] == "data":
            return ["10/01/2026", "2026-02-30", "", 20260110, None]
        if a["tipo"] == "int":
            extra = [2.5, "3", True, None]
            if a["regra"] == "minimo":
                return [a["min"] - 1, a["min"] - 10] + extra
            return [a["min"] - 1, a["max"] + 1] + extra
        extra = ["10", True, None]
        if a["regra"] == "minimo":
            return [round(a["min"] - 0.01, 2), a["min"] - 10] + extra
        return [round(a["min"] - 0.01, 2), round(a["max"] + 0.01, 2)] + extra

    @staticmethod
    def limites(a):
        if a["regra"] == "lista":
            return [a["opcoes"][0], a["opcoes"][-1]]
        if a["tipo"] == "str":
            return ["X"]
        if a["tipo"] == "bool":
            return [True, False]
        if a["tipo"] == "data":
            return ["2000-01-01", "2099-12-31", "2028-02-29"]   # 2028 é bissexto
        if a["tipo"] == "int":
            return [a["min"]] if a["regra"] == "minimo" else [a["min"], a["max"]]
        return [float(a["min"])] if a["regra"] == "minimo" else [float(a["min"]), float(a["max"])]

    def textos(self):
        """Valores para os marcadores dos textos explicativos (README/ADR)."""
        return {
            "ENT": self.ent, "SISTEMA": self.sistema, "QTD": self.qtd, "PRECO": self.preco,
            "IDENT": self.ident, "CONCEITO": self.conceito, "CATBASE": self.cat_base[0],
            "CATSUBS": ", ".join(f"`{x[0]}`" for x in self.cat_sub), "CATNOVA": self.cat_nova[0],
            "CATUNID": self.cat_unid, "VNOVA": self.vnova[2],
            "POLITICAS": ", ".join(f"`Politica{x[2]}`" for x in self.variantes),
            "GATEWAY": self.gw, "ZERO": self.painel["zero"], "E1": self.extras[0][0], "E2": self.extras[1][0],
            "VE1": f"R$ {self.extras[0][1]:.2f}", "PERC": self.perc[0],
            "EXTRAS": ", ".join(f"`Com{x[0]}`" for x in self.extras),
            "ENTVAR": self.ent_var, "UNIDADE": self.unidade, "QTDCAMEL": camel(self.qtd),
            "VTM": self.variante_template()[2],
        }

    def variante_template(self):
        """Variante usada no Template Method (evita colidir com FechamentoPadrao/FechamentoComTaxa)."""
        for v in self.variantes[1:] + [self.vnova]:
            if v[2] not in ("Padrao", "ComTaxa"):
                return v
        return self.vnova


def descrever_regra(a):
    n, tipo = a["nome"], {"int": "inteiro", "float": "número", "str": "texto", "bool": "sim/não",
                          "data": "data"}[a["tipo"]]
    if a["regra"] == "lista":
        return f"{n}: {tipo}, um destes valores — {', '.join(str(o) for o in a['opcoes'])}"
    if a["tipo"] == "bool":
        return f"{n}: sim/não (só True ou False — 1 e 0 não valem)"
    if a["tipo"] == "data":
        return f"{n}: data válida no formato AAAA-MM-DD (ex.: 2026-01-10)"
    if a["regra"] == "obrigatorio":
        return f"{n}: texto obrigatório (não pode ser vazio)"
    if a["regra"] == "minimo":
        return f"{n}: {tipo} maior ou igual a {a['min']}"
    if a["regra"] == "faixa":
        return f"{n}: {tipo} entre {a['min']} e {a['max']}"
    return f"{n}: texto livre, sem regra (atributo simples — proteger seria cerimônia)"


def subst(texto, valores):
    for k, v in valores.items():
        texto = texto.replace(f"@@{k}@@", str(v))
    return texto


# =============================================================================
# 4. MODELOS — NÚCLEO (Python puro) E TESTES
# =============================================================================
def gerar_property(a):
    n = a["nome"]
    chk = []
    if a["tipo"] == "str":
        chk += ["if not isinstance(valor, str) or not valor.strip():",
                f'    raise ValueError("{n} é obrigatório (texto não vazio)")',
                "valor = valor.strip()  # guarda sem espaços nas pontas"]
    elif a["tipo"] == "bool":
        chk += ["# Só True ou False: 1, 0 e \"sim\" são recusados (bool é subclasse de int, mas o contrário não).",
                "if not isinstance(valor, bool):",
                f'    raise ValueError("{n} deve ser True ou False")']
    elif a["tipo"] == "data":
        chk += ["# Data como texto ISO (AAAA-MM-DD): o mesmo formato do <input type=\"date\"> e do DateField.",
                "try:",
                "    valida = isinstance(valor, str) and date.fromisoformat(valor).isoformat() == valor",
                "except ValueError:  # ex.: 2026-02-30 não existe",
                "    valida = False",
                "if not valida:",
                f'    raise ValueError("{n} deve ser uma data válida no formato AAAA-MM-DD")']
    elif a["tipo"] == "int":
        chk += ["# bool é subclasse de int em Python (True == 1): por isso é recusado explicitamente.",
                "if isinstance(valor, bool) or not isinstance(valor, int):",
                f'    raise ValueError("{n} deve ser um número inteiro")']
    else:
        chk += ["if isinstance(valor, bool) or not isinstance(valor, (int, float)):",
                f'    raise ValueError("{n} deve ser um número")']
    if a["regra"] == "minimo":
        chk += [f"if valor < {a['min']!r}:", f'    raise ValueError("{n} deve ser no mínimo {a["min"]}")']
    elif a["regra"] == "faixa":
        chk += [f"if not {a['min']!r} <= valor <= {a['max']!r}:",
                f'    raise ValueError("{n} deve estar entre {a["min"]} e {a["max"]}")']
    elif a["regra"] == "lista":
        valores = ", ".join(repr(o) for o in a["opcoes"])
        chk += ["# Lista fechada: só um dos valores definidos entra (qualquer outro é recusado).",
                f"if valor not in ({valores},):",
                f'    raise ValueError("{n} deve ser um destes: {", ".join(str(o) for o in a["opcoes"])}")']
    return render(r'''
        @property
        def @@N@@(self):
            """Getter: lê `@@N@@` (o valor de verdade fica no atributo interno `_@@N@@`)."""
            return self._@@N@@

        @@@N@@.setter
        def @@N@@(self, valor):
            """Setter (a "fechadura"): só grava se a regra for respeitada — @@REGRA@@."""
            @@CORPO@@
            self._@@N@@ = valor
        ''', N=n, REGRA=descrever_regra(a), CORPO="\n".join(chk))


def gerar_entidades(s):
    req = [a for a in s.atributos if a["regra"] != "livre"]
    livres = [a for a in s.atributos if a["regra"] == "livre"]
    params = ", ".join([a["nome"] for a in req] + [f'{a["nome"]}=""' for a in livres])
    init = [f"self.{a['nome']} = {a['nome']}  # passa pelo setter → validado já na criação" for a in req]
    init += [f"self.{a['nome']} = {a['nome']}  # sem regra → atributo simples (antifachada)" for a in livres]
    codigo = _gerar_entidades(s, params, init, req)
    if any(a["tipo"] == "data" for a in s.atributos):   # campo de data: o setter usa date.fromisoformat
        codigo = codigo.replace(f'"""\n\n\nclass {s.ent}:', f'"""\nfrom datetime import date\n\n\nclass {s.ent}:', 1)
        if "from datetime import date" not in codigo:  # pragma: no cover - bug do gerador
            raise RuntimeError("entidades.py: não achei onde importar date")
    return codigo


def _gerar_entidades(s, params, init, req):
    return render(r'''
        """
        @@SISTEMA@@ — entidade principal `@@ENT@@` (ENCAPSULAMENTO com @property).

        Gerado por gerar_sistema.py (determinístico, sem IA). Regras dos atributos:
        @@REGRAS@@

        Ideias das Aulas 02 e 03:
          * o objeto controla o acesso ao próprio estado (encapsulamento);
          * @property + setter = a "fechadura": valida ANTES de gravar no atributo interno (_nome);
          * no __init__, `self.x = x` passa pelo setter → o objeto já nasce válido;
          * `total` é property CALCULADA (sem setter): nunca fica desatualizada;
          * atributo sem regra fica simples — @property sem problema que a justifique é cerimônia;
          * no model Django a mesma regra vai em validators (setter em campo quebra form/admin/ORM).
        """


        class @@ENT@@:
            """@@ENT@@ do sistema @@SISTEMA@@: total = @@QTD@@ × @@PRECO@@."""

            def __init__(self, @@PARAMS@@):
                @@INIT@@

            @@PROPS@@

            @property
            def total(self):
                """Valor total = @@QTD@@ × @@PRECO@@ (2 casas).

                Property CALCULADA e SÓ LEITURA: sem setter, `obj.total = 1` levanta AttributeError.
                Calculada na hora, acompanha qualquer mudança em @@QTD@@ ou @@PRECO@@.
                """
                return round(self.@@QTD@@ * self.@@PRECO@@, 2)

            def __repr__(self):
                return f"@@ENT@@(@@IDENT@@={self.@@IDENT@@!r}, total={self.total})"
        ''', SISTEMA=s.sistema, ENT=s.ent, QTD=s.qtd, PRECO=s.preco, IDENT=s.ident, PARAMS=params,
        INIT="\n".join(init), PROPS="\n".join(gerar_property(a) for a in req),
        REGRAS="\n".join(f"  - {descrever_regra(a)}" for a in s.atributos))


def gerar_fabrica(s):
    linhas = ",\n".join("    " + dict_lit(s.dados_exemplo(i)) for i in range(4))
    return render(r'''
        """Fábrica de objetos VÁLIDOS para todos os testes (gerada).

        Centraliza os dados de exemplo: se a @@ENT@@ ganhar um atributo, só este arquivo muda.
        """
        from nucleo.entidades import @@ENT@@

        DADOS_EXEMPLO = [
        @@LINHAS@@
        ]


        def dados(indice=0, **mudancas):
            """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
            copia = dict(DADOS_EXEMPLO[indice])
            copia.update(mudancas)
            return copia


        def criar(indice=0, **mudancas):
            """Cria uma @@ENT@@ (válida, a menos que as mudanças a tornem inválida)."""
            return @@ENT@@(**dados(indice, **mudancas))


        def itens_exemplo():
            """Quatro @@ENT@@s diferentes e válidas — objetos novos a cada chamada."""
            return [@@ENT@@(**d) for d in DADOS_EXEMPLO]
        ''', ENT=s.ent, LINHAS=linhas)


def gerar_test_entidades(s):
    req = [a for a in s.atributos if a["regra"] != "livre"]
    blocos = []
    for a in req:
        inv = s.invalidos(a)
        blocos.append(render(r'''
            @pytest.mark.parametrize("invalido", @@INV@@)
            def test_@@N@@_invalido_e_barrado_na_criacao(invalido):
                with pytest.raises(ValueError):
                    criar(@@N@@=invalido)


            def test_@@N@@_invalido_e_barrado_na_alteracao():
                obj = criar()
                with pytest.raises(ValueError):
                    obj.@@N@@ = @@PRIMEIRO@@
                assert obj.@@N@@ == DADOS_EXEMPLO[0]["@@N@@"]  # o valor válido foi preservado


            @pytest.mark.parametrize("limite", @@LIM@@)
            def test_@@N@@_valor_no_limite_e_aceito(limite):
                assert criar(@@N@@=limite).@@N@@ == limite
            ''', N=a["nome"], INV=lit(inv), PRIMEIRO=lit(inv[0]), LIM=lit(s.limites(a))))
    livres = []
    for a in s.atributos:
        if a["regra"] == "livre":
            livres.append(render(r'''
                def test_@@N@@_sem_regra_aceita_qualquer_texto():
                    assert criar().@@N@@ == ""
                    assert criar(@@N@@="qualquer coisa").@@N@@ == "qualquer coisa"
                ''', N=a["nome"]))
    return render(r'''
        """Testes da @@ENT@@ (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
        import pytest

        from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


        def test_cria_com_dados_validos():
            obj = criar()
            for campo, valor in DADOS_EXEMPLO[0].items():
                assert getattr(obj, campo) == valor


        def test_total_e_quantidade_vezes_preco():
            for obj in itens_exemplo():
                assert obj.total == round(obj.@@QTD@@ * obj.@@PRECO@@, 2)


        def test_total_acompanha_mudanca():
            obj = criar()
            obj.@@QTD@@ = obj.@@QTD@@ + 1
            assert obj.total == round(obj.@@QTD@@ * obj.@@PRECO@@, 2)


        def test_total_e_somente_leitura():
            with pytest.raises(AttributeError):
                criar().total = 1


        def test_texto_obrigatorio_e_guardado_sem_espacos():
            assert criar(@@IDENT@@="  @@NOME@@  ").@@IDENT@@ == "@@NOME@@"


        @@LIVRES@@


        @@BLOCOS@@
        ''', ENT=s.ent, QTD=s.qtd, PRECO=s.preco, IDENT=s.ident, NOME=s.nomes[0],
        LIVRES="\n\n".join(livres) or "# (a entidade não tem atributo livre)",
        BLOCOS="\n\n".join(blocos))


# ----------------------------------------------------------------- polimorfismo
def gerar_categorias(s):
    base, desc, preco = s.cat_base
    partes = [render(r'''
        class @@C@@:
            """Classe BASE: o comportamento PADRÃO de toda categoria."""

            def __init__(self, codigo):
                self.codigo = codigo

            def descricao(self):
                return @@DESC@@

            def preco_unidade(self):
                return @@PRECO@@
        ''', C=base, DESC=lit(desc), PRECO=lit(preco))]
    for cls, d, p in s.cat_sub + [s.cat_nova]:
        doc = (f"NOVA categoria: entrou SEM mudar imprimir_preco (aberto ao novo)." if cls == s.cat_nova[0]
               else f"{cls} É-UM {base}: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade().")
        partes.append(render(r'''
            class @@C@@(@@BASE@@):
                """@@DOC@@"""

                def descricao(self):
                    return @@DESC@@

                def preco_unidade(self):
                    return @@PRECO@@
            ''', C=cls, BASE=base, DOC=doc, DESC=lit(d), PRECO=lit(p)))
    partes.append(render(r'''
        class @@BASE@@Padrao(@@BASE@@):
            """Não sobrescreve nada: o Python procura o método aqui, não acha e SOBE para @@BASE@@."""
        ''', BASE=base))
    return render(r'''
        """
        @@SISTEMA@@ — POLIMORFISMO (Aula 04): muitas categorias, uma função.

        ANTES (nucleo/antes_categorias.py): imprimir_preco(tipo) com if/elif por categoria.
        DEPOIS: cada categoria SOBRESCREVE descricao() e preco_unidade(); imprimir_preco(categoria)
        só chama os métodos — o Python escolhe a versão pelo tipo REAL do objeto.
        Herdar = ganhar o que é igual · sobrescrever = mudar o que é diferente.
        """


        @@CLASSES@@


        def imprimir_preco(categoria):
            """Função POLIMÓRFICA: não pergunta o tipo (zero if); cada categoria responde a seu modo."""
            return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por @@UNID@@"
        ''', SISTEMA=s.sistema, CLASSES="\n\n".join(partes), UNID=s.cat_unid)


def gerar_antes_categorias(s):
    base, desc, preco = s.cat_base
    ramos = []
    for i, (cls, d, p) in enumerate(s.cat_sub):
        kw = "if" if i == 0 else "elif"
        ramos.append(f'{kw} tipo == "{camel_para_snake(cls)}":\n    return "{d}: R$ {p:.2f} por {s.cat_unid}"')
    ramos.append(f'else:\n    return "{desc}: R$ {preco:.2f} por {s.cat_unid}"')
    return render(r'''
        """ANTES — o smell do polimorfismo ausente: um if que cresce a cada categoria nova."""


        def imprimir_preco(tipo):
            """Para a categoria "@@NOVA@@" seria preciso EDITAR esta função (e ela cai no else, errada)."""
            @@RAMOS@@
        ''', RAMOS="\n".join(ramos), NOVA=s.cat_nova[0])


def gerar_test_categorias(s):
    base = s.cat_base[0]
    subs = [x[0] for x in s.cat_sub]
    nova_cls, nova_desc, nova_preco = s.cat_nova
    pares = ", ".join(f'({c}, "{camel_para_snake(c)}")' for c in subs)
    todas = ", ".join(subs + [nova_cls, base + "Padrao"])
    imports = ", ".join(sorted([base, base + "Padrao", nova_cls] + subs) + ["imprimir_preco"])
    return render(r'''
        """Testes do POLIMORFISMO: mesma saída que o if/elif, e categoria nova sem mudar a função."""
        import pytest

        from nucleo import antes_categorias
        from nucleo.categorias import @@IMPORTS@@


        @pytest.mark.parametrize("classe, tipo", [@@PARES@@])
        def test_mesmo_texto_que_a_versao_com_if(classe, tipo):
            assert imprimir_preco(classe(1)) == antes_categorias.imprimir_preco(tipo)


        def test_base_igual_ao_else_da_versao_antiga():
            assert imprimir_preco(@@BASE@@(1)) == antes_categorias.imprimir_preco("qualquer")


        @pytest.mark.parametrize("classe", [@@TODAS@@])
        def test_todo_subtipo_e_um_@@BASEMIN@@(classe):
            assert isinstance(classe(1), @@BASE@@)


        def test_subtipo_herda_o_construtor():
            assert @@SUB1@@(7).codigo == 7


        def test_categoria_nova_sem_mudar_a_funcao():
            assert imprimir_preco(@@NOVA@@(1)) == "@@NOVATXT@@"


        def test_quem_nao_sobrescreve_usa_o_metodo_da_mae():
            assert imprimir_preco(@@BASE@@Padrao(1)) == imprimir_preco(@@BASE@@(1))


        def test_versao_com_if_erra_a_categoria_nova():
            assert antes_categorias.imprimir_preco("@@NOVAKEY@@") != imprimir_preco(@@NOVA@@(1))
        ''', IMPORTS=imports, PARES=pares, BASE=base, BASEMIN=camel_para_snake(base), TODAS=todas,
        SUB1=subs[0], NOVA=nova_cls, NOVAKEY=camel_para_snake(nova_cls),
        NOVATXT=f"{nova_desc}: R$ {nova_preco:.2f} por {s.cat_unid}")


# ----------------------------------------------------------------- strategy
def gerar_politicas(s):
    blocos = []
    for nome, fator, cls, chave in s.variantes + [s.vnova]:
        if chave == s.vnova[3]:
            doc = f"Política NOVA ({nome}): criada SEM tocar em Cobranca — aberto p/ estender, fechado p/ modificar."
        else:
            doc = f"Política {nome} ({s.conceito}): aplica o fator {fator} sobre o total."
        blocos.append(render(r'''
            class Politica@@C@@:
                """@@DOC@@"""

                FATOR = @@F@@

                def aplicar(self, base):
                    # Cada política conhece só a SUA regra; quem usa não precisa de if.
                    return round(base * self.FATOR, 2)
            ''', C=cls, DOC=doc, F=lit(fator)))
    return render(r'''
        """
        @@SISTEMA@@ — STRATEGY (Aula 05): as regras de @@CONCEITO@@.

        ANTES (nucleo/antes_politicas.py): CobrancaAntiga.valor() com if/elif por @@CONCEITO@@.
        DEPOIS (aqui):
          * cada regra é uma classe com o MESMO método aplicar(base) → estratégias intercambiáveis;
          * Cobranca (o CONTEXTO) recebe a estratégia e DELEGA — nenhum if;
          * política nova = classe nova; Cobranca não muda (OCP).
        Quando NÃO usar: uma regra só, que nunca varia — uma função ou constante basta.
        """


        @@POLITICAS@@


        class Cobranca:
            """CONTEXTO do Strategy: TEM-UM item (@@ENT@@) e TEM-UMA política."""

            def __init__(self, item, politica):
                self.item = item
                # Sem "_": trocar a política de fora é permitido (ex.: cliente mudou de categoria).
                self.politica = politica

            def valor(self):
                """Delega: pede à política que se aplique ao total. Não sabe QUAL política é."""
                return self.politica.aplicar(self.item.total)


        class CobrancaComFuncao:
            """Variante pythônica (GIRIDHAR): a estratégia pode ser qualquer FUNÇÃO f(base) -> valor."""

            def __init__(self, item, politica):
                self.item = item
                self.politica = politica

            def valor(self):
                return self.politica(self.item.total)
        ''', SISTEMA=s.sistema, CONCEITO=s.conceito, ENT=s.ent, POLITICAS="\n\n".join(blocos))


def gerar_antes_politicas(s):
    ramos = []
    for i, (nome, fator, cls, chave) in enumerate(s.variantes):
        kw = "if" if i == 0 else "elif"
        ramos.append(f'{kw} self.tipo == "{chave}":\n    return round(base * {fator!r}, 2)')
    ramos.append(f'else:\n    raise ValueError(f"{s.conceito} desconhecido: {{self.tipo}}")')
    return render(r'''
        """ANTES — o smell do Strategy: um if/elif por @@CONCEITO@@ que cresce a cada regra nova."""


        class CobrancaAntiga:
            def __init__(self, item, tipo):
                self.item = item
                self.tipo = tipo  # um TEXTO decide o comportamento

            def valor(self):
                base = self.item.total
                @@RAMOS@@
        ''', CONCEITO=s.conceito, RAMOS="\n".join(ramos))


def gerar_test_politicas(s):
    pares = ", ".join(f'("{x[3]}", Politica{x[2]})' for x in s.variantes)
    imports = ", ".join(["Cobranca", "CobrancaComFuncao"] + sorted(f"Politica{x[2]}" for x in s.variantes + [s.vnova]))
    return render(r'''
        """Testes do STRATEGY: o resultado não muda (antes × depois) e a extensão não toca no contexto."""
        import pytest

        from nucleo.antes_politicas import CobrancaAntiga
        from nucleo.politicas import @@IMPORTS@@
        from tests.fabrica import criar, itens_exemplo

        PARES = [@@PARES@@]


        @pytest.mark.parametrize("tipo, classe", PARES)
        @pytest.mark.parametrize("indice", range(4))
        def test_refatoracao_preserva_o_resultado(tipo, classe, indice):
            item = itens_exemplo()[indice]
            assert Cobranca(item, classe()).valor() == CobrancaAntiga(item, tipo).valor()


        def test_politica_nova_entra_sem_mudar_a_cobranca():
            item = criar()
            assert Cobranca(item, Politica@@NOVA@@()).valor() == round(item.total * @@FNOVA@@, 2)


        def test_versao_com_if_nao_conhece_a_politica_nova():
            with pytest.raises(ValueError):
                CobrancaAntiga(criar(), "@@KNOVA@@").valor()


        def test_qualquer_objeto_com_aplicar_serve():
            class PoliticaDeTeste:
                def aplicar(self, base):
                    return 0

            assert Cobranca(criar(), PoliticaDeTeste()).valor() == 0


        def test_politica_trocada_em_tempo_de_execucao():
            cobranca = Cobranca(criar(), Politica@@PRIMEIRA@@())
            cobranca.politica = Politica@@ULTIMA@@()
            assert cobranca.valor() == round(cobranca.item.total * @@FULTIMA@@, 2)


        def test_estrategia_como_funcao():
            item = criar()
            assert CobrancaComFuncao(item, lambda base: base).valor() == item.total
        ''', IMPORTS=imports, PARES=pares, NOVA=s.vnova[2], FNOVA=lit(s.vnova[1]), KNOVA=s.vnova[3],
        PRIMEIRA=s.variantes[0][2], ULTIMA=s.variantes[-1][2], FULTIMA=lit(s.variantes[-1][1]))


# ----------------------------------------------------------------- srp
def gerar_antes_recibo(s):
    return render(r'''
        """ANTES — o smell do SRP: a classe que faz tudo (três motivos para mudar)."""
        from nucleo.entidades import @@ENT@@


        class @@ENT@@FazTudo(@@ENT@@):
            """Herda dados e total (negócio) e ainda FORMATA (apresentação) e SALVA (infraestrutura)."""

            def formatar_recibo(self):
                return (f"RECIBO - @@SISTEMA@@\n{self.@@IDENT@@}\n"
                        f"{self.@@QTD@@} @@UNIDADE@@\nTotal: R$ {self.total:.2f}")

            def salvar_em_arquivo(self, caminho):
                with open(caminho, "w", encoding="utf-8") as arquivo:
                    arquivo.write(self.formatar_recibo())
        ''', ENT=s.ent, SISTEMA=s.sistema, IDENT=s.ident, QTD=s.qtd, UNIDADE=s.unidade)


def gerar_recibo(s):
    return render(r'''
        """
        @@SISTEMA@@ — SRP + OCP (Aula 06): uma classe, um motivo para mudar.

        @@ENT@@ (nucleo/entidades.py) → dados + total      (muda se a REGRA mudar)
        ReciboFormatter               → texto do recibo    (muda se o LAYOUT mudar)
        ReciboCsvFormatter            → formato novo       (EXTENSÃO: nada foi reaberto → OCP)
        ArquivoRepository             → grava o texto      (muda se o DESTINO mudar)
        Cuidado: SRP não é "uma classe por método" — a unidade é a responsabilidade.
        """


        class ReciboFormatter:
            """APRESENTAÇÃO: recebe a @@ENT@@ por parâmetro e só LÊ os dados dela."""

            def formatar(self, item):
                # Texto idêntico ao da versão "faz-tudo" → prova de refatoração segura.
                return (f"RECIBO - @@SISTEMA@@\n{item.@@IDENT@@}\n"
                        f"{item.@@QTD@@} @@UNIDADE@@\nTotal: R$ {item.total:.2f}")


        class ReciboCsvFormatter:
            """Formato NOVO por extensão (OCP): mesma interface formatar(item)."""

            def formatar(self, item):
                return "@@IDENT@@;@@QTD@@;total\n" + f"{item.@@IDENT@@};{item.@@QTD@@};{item.total:.2f}"


        class ArquivoRepository:
            """INFRAESTRUTURA: só grava um texto (arquivo hoje; banco/nuvem amanhã)."""

            def salvar(self, texto, caminho):
                with open(caminho, "w", encoding="utf-8") as arquivo:
                    arquivo.write(texto)


        def emitir_recibo(item, formatter, repositorio, caminho):
            """Junta as peças: cada uma faz a sua parte sem conhecer os detalhes das outras."""
            texto = formatter.formatar(item)
            repositorio.salvar(texto, caminho)
            return texto
        ''', ENT=s.ent, SISTEMA=s.sistema, IDENT=s.ident, QTD=s.qtd, UNIDADE=s.unidade)


def gerar_test_recibo(s):
    return render(r'''
        """Testes do SRP: o recibo sai idêntico e cada classe tem uma só responsabilidade."""
        import pytest

        from nucleo.antes_recibo import @@ENT@@FazTudo
        from nucleo.entidades import @@ENT@@
        from nucleo.recibo import ArquivoRepository, ReciboCsvFormatter, ReciboFormatter, emitir_recibo
        from tests.fabrica import dados


        @pytest.mark.parametrize("indice", range(4))
        def test_recibo_identico_ao_da_versao_faz_tudo(indice):
            antes = @@ENT@@FazTudo(**dados(indice)).formatar_recibo()
            depois = ReciboFormatter().formatar(@@ENT@@(**dados(indice)))
            assert depois == antes


        def test_formato_novo_por_extensao():
            item = @@ENT@@(**dados())
            linhas = ReciboCsvFormatter().formatar(item).split("\n")
            assert linhas[0] == "@@IDENT@@;@@QTD@@;total"
            assert linhas[1] == f"{item.@@IDENT@@};{item.@@QTD@@};{item.total:.2f}"


        def test_repository_so_grava(tmp_path):
            caminho = tmp_path / "recibo.txt"
            ArquivoRepository().salvar("conteúdo", caminho)
            assert caminho.read_text(encoding="utf-8") == "conteúdo"


        def test_emitir_junta_as_pecas(tmp_path):
            caminho = tmp_path / "recibo.txt"
            texto = emitir_recibo(@@ENT@@(**dados()), ReciboFormatter(), ArquivoRepository(), caminho)
            assert caminho.read_text(encoding="utf-8") == texto


        def test_entidade_nao_formata_nem_salva():
            item = @@ENT@@(**dados())
            assert not hasattr(item, "formatar_recibo") and not hasattr(item, "salvar_em_arquivo")
        ''', ENT=s.ent, IDENT=s.ident, QTD=s.qtd)


# ----------------------------------------------------------------- service
def registros_exemplo(s):
    out = []
    for i in range(4):
        chave = s.variantes[i % len(s.variantes)][3]
        out.append({"nome": s.nomes[i], "quantidade": [2, 3, 1, 4][i], "preco": float(s.precos[i]), "tipo": chave})
    return out


def gerar_antes_relatorio(s):
    ramos = []
    descontos = [x for x in s.variantes if x[1] != 1.0]
    for i, (nome, fator, cls, chave) in enumerate(descontos):
        kw = "if" if i == 0 else "elif"
        ramos.append(f'{kw} r["tipo"] == "{chave}":\n    total = base * {fator!r}')
    ramos.append("else:\n    total = base" if ramos else "total = base")
    return render(r'''
        """ANTES — a "view" que faz tudo: regra de negócio + apresentação no mesmo laço."""


        def relatorio_view(registros, request=None):
            linhas = []
            total_geral = 0
            for r in registros:
                base = r["quantidade"] * r["preco"]
                # ↓ regra de negócio presa na view
                @@RAMOS@@
                total_geral += total
                linhas.append(f"{r['nome']}: R$ {total:.2f}")  # ← apresentação
            corpo = "\n".join(linhas)
            return f"RELATORIO - @@SISTEMA@@\n{corpo}\nTOTAL: R$ {total_geral:.2f}"
        ''', RAMOS="\n".join(ramos), SISTEMA=s.sistema)


def gerar_relatorio(s):
    fatores = "{" + ", ".join(f'"{x[3]}": {x[1]!r}' for x in s.variantes if x[1] != 1.0) + "}"
    regs = ",\n".join("    " + dict_lit(r) for r in registros_exemplo(s))
    return render(r'''
        """
        @@SISTEMA@@ — Camada de SERVICE (Aula 07): a regra de negócio não sabe o que é web.

        MVC (Model·Controller·View) · MVT do Django (Model·View·Template) · MVP (Model·Presenter·View):
        todas separam DADO, REGRA e APRESENTAÇÃO. Aqui:
          RelatorioService → só a regra; recebe e devolve DADOS (testável sem HTTP)
          relatorio_view   → fina: chama o service e formata texto
          relatorio_api    → outra apresentação reaproveitando a MESMA regra
        Quando NÃO usar: view que só lista e renderiza não precisa de Service.
        """

        REGISTROS = [
        @@REGS@@
        ]


        class RelatorioService:
            """SÓ a regra de negócio (desconto por @@CONCEITO@@). Nada de request, HTML ou template."""

            FATORES = @@FATORES@@  # tipo sem desconto → fator 1.0

            def __init__(self, registros):
                self.registros = registros

            def _total(self, registro):
                base = registro["quantidade"] * registro["preco"]
                return base * self.FATORES.get(registro["tipo"], 1.0)

            def calcular(self):
                """Devolve DADOS: ([(nome, total), ...], total_geral)."""
                linhas = [(r["nome"], self._total(r)) for r in self.registros]
                total_geral = 0
                for _, total in linhas:  # soma na MESMA ordem e do MESMO jeito que a view antiga: centavo igual
                    total_geral += total  # (o sum() do Python 3.12+ compensa o erro e pode mudar o último centavo)
                return linhas, total_geral


        def relatorio_view(registros, request=None):
            """View FINA: 1) pede os dados ao service  2) formata a resposta."""
            linhas, total_geral = RelatorioService(registros).calcular()
            corpo = "\n".join(f"{nome}: R$ {total:.2f}" for nome, total in linhas)
            return f"RELATORIO - @@SISTEMA@@\n{corpo}\nTOTAL: R$ {total_geral:.2f}"


        def relatorio_api(registros, request=None):
            """Outra apresentação (JSON) com a mesma regra — sem duplicar a conta."""
            linhas, total_geral = RelatorioService(registros).calcular()
            return {"itens": [{"nome": nome, "total": round(total, 2)} for nome, total in linhas],
                    "total_geral": round(total_geral, 2)}
        ''', SISTEMA=s.sistema, CONCEITO=s.conceito, FATORES=fatores, REGS=regs)


def gerar_test_relatorio(s):
    params = ", ".join(f'("{x[3]}", {x[1]!r})' for x in s.variantes)
    return render(r'''
        """Testes do SERVICE: saída idêntica à view faz-tudo e regra testada sem HTTP."""
        import ast
        import inspect
        import textwrap

        import pytest

        from nucleo import antes_relatorio
        from nucleo.relatorio import REGISTROS, RelatorioService, relatorio_api, relatorio_view


        def test_saida_identica_a_view_faz_tudo():
            assert relatorio_view(REGISTROS) == antes_relatorio.relatorio_view(REGISTROS)


        @pytest.mark.parametrize("tipo, fator", [@@PARAMS@@])
        def test_regra_testada_direto_sem_http(tipo, fator):
            _, total = RelatorioService([{"nome": "T", "quantidade": 2, "preco": 100.0, "tipo": tipo}]).calcular()
            assert total == pytest.approx(200.0 * fator)


        def test_tipo_desconhecido_fica_sem_desconto():
            _, total = RelatorioService([{"nome": "T", "quantidade": 2, "preco": 100.0, "tipo": "???"}]).calcular()
            assert total == 200.0


        def test_lista_vazia():
            assert RelatorioService([]).calcular() == ([], 0)


        def test_service_nao_conhece_web():
            arvore = ast.parse(textwrap.dedent(inspect.getsource(RelatorioService)))
            nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
            nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
            nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
            for palavra in ("request", "http", "template", "render"):
                assert not any(palavra in nome for nome in nomes), palavra


        def test_mesma_regra_outra_apresentacao():
            _, total = RelatorioService(REGISTROS).calcular()
            assert relatorio_api(REGISTROS)["total_geral"] == round(total, 2)
        ''', PARAMS=params)


# ----------------------------------------------------------------- mvvm
def itens_painel(s):
    cats = [s.cat_base] + s.cat_sub
    out = []
    for i in range(3):
        cls, _, preco = cats[i % len(cats)]
        out.append({"codigo": s.recursos[i], "categoria": camel_para_snake(cls), "preco": preco, "disponivel": i != 1})
    return out


def gerar_antes_painel(s):
    p = s.painel
    return render(r'''
        """ANTES — a tela que decide como mostrar (status, rótulo, R$, rodapé) no meio do desenho."""


        def tela_painel(itens):
            linhas = []
            livres = 0
            for item in itens:
                if item["disponivel"]:
                    status = "@@LIVRE@@"
                    acao = "@@ACAO_LIVRE@@"
                    livres += 1
                else:
                    status = "@@OCUPADO@@"
                    acao = "@@ACAO_OCUPADO@@"
                preco = f"R$ {item['preco']:.2f}"
                linhas.append(f"@@TITULO@@ {item['codigo']} [{item['categoria']}] - {preco} - {status} - {acao}")
            if livres:
                rodape = f"{livres} @@CONTAGEM@@"
            else:
                rodape = "@@ZERO@@"
            return "\n".join(linhas) + "\n" + rodape
        ''', LIVRE=p["livre"], ACAO_LIVRE=p["acao_livre"], OCUPADO=p["ocupado"], ACAO_OCUPADO=p["acao_ocupado"],
        TITULO=p["titulo"], CONTAGEM=p["contagem"], ZERO=p["zero"])


def gerar_painel(s):
    p = s.painel
    itens = ",\n".join("    " + dict_lit(x) for x in itens_painel(s))
    return render(r'''
        """
        @@SISTEMA@@ — MVVM (Aulas 08/09): o ViewModel prepara a vitrine; a View só serve.

        MODEL     = os dicts crus em ITENS (codigo, categoria, preco, disponivel)
        VIEWMODEL = ItemViewModel / PainelVM → dado PRONTO para a tela, sem saber desenhar
        VIEW      = tela_painel_mvvm → só costura o que o ViewModel preparou (zero if)
        No Django não há data binding: o ViewModel é só a preparação chamada antes do render.
        Service × ViewModel: regra de negócio (o que é verdade) × lógica de exibição (como aparece).
        """

        ITENS = [
        @@ITENS@@
        ]


        class ItemViewModel:
            """Prepara UM item para exibição. Não sabe o que é tela: entrega texto pronto."""

            def __init__(self, item):
                self.codigo = item["codigo"]
                self.categoria = item["categoria"]
                self.disponivel = bool(item["disponivel"])  # estado derivado, num lugar só
                self.status_label = "@@LIVRE@@" if self.disponivel else "@@OCUPADO@@"
                self.acao_label = "@@ACAO_LIVRE@@" if self.disponivel else "@@ACAO_OCUPADO@@"
                self.preco_formatado = f"R$ {item['preco']:.2f}"


        class PainelVM:
            """Prepara o PAINEL: um ViewModel por item, a contagem e o rodapé."""

            def __init__(self, itens):
                self.itens = [ItemViewModel(i) for i in itens]
                self.livres = sum(1 for i in self.itens if i.disponivel)
                self.rodape = f"{self.livres} @@CONTAGEM@@" if self.livres else "@@ZERO@@"


        def tela_painel_mvvm(itens):
            """View 'burra': só lê o ViewModel."""
            painel = PainelVM(itens)
            linhas = [f"@@TITULO@@ {i.codigo} [{i.categoria}] - {i.preco_formatado} - {i.status_label} - {i.acao_label}"
                      for i in painel.itens]
            return "\n".join(linhas) + "\n" + painel.rodape
        ''', SISTEMA=s.sistema, ITENS=itens, LIVRE=p["livre"], OCUPADO=p["ocupado"],
        ACAO_LIVRE=p["acao_livre"], ACAO_OCUPADO=p["acao_ocupado"], CONTAGEM=p["contagem"],
        ZERO=p["zero"], TITULO=p["titulo"])


def gerar_test_painel(s):
    p = s.painel
    return render(r'''
        """Testes do MVVM: nenhum teste lê a tela — todos perguntam ao ViewModel."""
        import pytest

        from nucleo import antes_painel
        from nucleo.painel import ITENS, ItemViewModel, PainelVM, tela_painel_mvvm

        LIVRE = {"codigo": @@R0@@, "categoria": "c", "preco": 200.0, "disponivel": True}
        OCUPADO = {"codigo": @@R1@@, "categoria": "c", "preco": 200.0, "disponivel": False}


        def test_item_livre():
            vm = ItemViewModel(LIVRE)
            assert vm.disponivel is True
            assert (vm.status_label, vm.acao_label) == (@@LIVRE@@, @@ACAO_LIVRE@@)


        def test_item_ocupado():
            vm = ItemViewModel(OCUPADO)
            assert vm.disponivel is False
            assert (vm.status_label, vm.acao_label) == (@@OCUPADO@@, @@ACAO_OCUPADO@@)


        def test_preco_formatado():
            assert ItemViewModel(dict(LIVRE, preco=99.9)).preco_formatado == "R$ 99.90"


        def test_dados_preservados():
            vm = ItemViewModel(LIVRE)
            assert (vm.codigo, vm.categoria) == (@@R0@@, "c")


        def test_painel_conta_os_livres():
            assert PainelVM([LIVRE, OCUPADO, LIVRE]).livres == 2


        def test_rodape_com_disponibilidade():
            assert PainelVM([LIVRE, OCUPADO]).rodape == "1 " + @@CONTAGEM@@


        def test_rodape_sem_disponibilidade():
            assert PainelVM([OCUPADO, OCUPADO]).rodape == @@ZERO@@
            assert PainelVM([]).rodape == @@ZERO@@


        def test_um_viewmodel_por_item():
            painel = PainelVM([LIVRE, OCUPADO])
            assert len(painel.itens) == 2 and all(isinstance(i, ItemViewModel) for i in painel.itens)


        @pytest.mark.parametrize("cenario", [ITENS, [OCUPADO], [LIVRE, LIVRE], []])
        def test_tela_mvvm_igual_a_original(cenario):
            assert tela_painel_mvvm(cenario) == antes_painel.tela_painel(cenario)
        ''', R0=s.recursos[0], R1=s.recursos[1], LIVRE=lit(p["livre"]), ACAO_LIVRE=lit(p["acao_livre"]),
        OCUPADO=lit(p["ocupado"]), ACAO_OCUPADO=lit(p["acao_ocupado"]), CONTAGEM=lit(p["contagem"]),
        ZERO=lit(p["zero"]))


# ----------------------------------------------------------------- adapter
def gerar_integracao_base(s):
    return render(r'''
        """
        Peças PRONTAS do Adapter (não mexer): a interface do NOSSO sistema e o gateway de TERCEIRO.
        """


        class PagamentoRecusado(Exception):
            """Erro de domínio: o sistema inteiro trata recusa com esta exceção."""


        class ProcessadorPagamento:
            """ALVO: a interface que o nosso sistema espera."""

            def processar(self, valor, token):
                raise NotImplementedError


        class ProcessadorInterno(ProcessadorPagamento):
            """Implementação NOSSA (já fala a língua certa — não precisa de adapter)."""

            def __init__(self):
                self._seq = 0

            def processar(self, valor, token):
                if token == "tok_recusado":
                    raise PagamentoRecusado("cartão recusado")
                self._seq += 1
                return f"INT-{self._seq:04d}"


        class Gateway@@GW@@:
            """ADAPTADO: biblioteca de TERCEIRO — não controlamos esta assinatura."""

            def __init__(self):
                self.recebidos = []
                self._seq = 0

            def charge(self, payload):
                self.recebidos.append(dict(payload))
                if payload["card"] == "tok_recusado":
                    return {"result": "denied", "reason": "cartão recusado"}
                if payload["amount_cents"] <= 0:
                    return {"result": "denied", "reason": "valor inválido"}
                self._seq += 1
                return {"result": "approved", "tx": f"@@PREF@@-{self._seq:04d}"}
        ''', GW=s.gw, PREF=s.gw_pref)


def gerar_antes_integracao(s):
    return render(r'''
        """ANTES — o smell do Adapter: o serviço conhece os dois mundos e decide no if."""
        from nucleo.integracao_base import PagamentoRecusado


        class CheckoutAntigo:
            def __init__(self, interno, gateway, usa_gateway):
                self.interno, self.gateway, self.usa_gateway = interno, gateway, usa_gateway

            def pagar(self, item, token):
                valor = item.total
                if self.usa_gateway:  # ← detalhe do terceiro vazando para a regra
                    resp = self.gateway.charge({"amount_cents": round(valor * 100), "card": token, "currency": "BRL"})
                    if resp["result"] == "approved":
                        return {"ok": True, "tx": resp["tx"], "valor": valor}
                    return {"ok": False, "motivo": resp["reason"]}
                try:
                    return {"ok": True, "tx": self.interno.processar(valor, token), "valor": valor}
                except PagamentoRecusado as erro:
                    return {"ok": False, "motivo": str(erro)}
        ''')


def gerar_integracao(s):
    return render(r'''
        """
        @@SISTEMA@@ — ADAPTER (Aula 08): fazer a peça de terceiro CABER na interface do sistema.

        ALVO     ProcessadorPagamento.processar(valor, token)   (nucleo/integracao_base.py)
        ADAPTADO Gateway@@GW@@.charge({"amount_cents", "card", "currency"})   (terceiro)
        ADAPTER  @@GW@@Adapter — fala `processar` por fora e traduz para `charge` por dentro
        Quando NÃO usar: se as duas pontas são nossas e parecidas, duck typing basta.
        Adapter ≠ Facade: aqui é UMA peça e uma interface que JÁ existe.
        """
        from nucleo.integracao_base import PagamentoRecusado, ProcessadorPagamento


        class @@GW@@Adapter(ProcessadorPagamento):
            """Veste o Gateway@@GW@@ com a interface ProcessadorPagamento (É-UM processador, TEM-UM gateway)."""

            MOEDA = "BRL"

            def __init__(self, gateway):
                self._gateway = gateway  # "_": detalhe interno; quem usa só chama processar()

            def processar(self, valor, token):
                # 1) dados de entrada: reais (float) → centavos (int); round evita 19.99*100 = 1998.999…
                payload = {"amount_cents": round(valor * 100), "card": token, "currency": self.MOEDA}
                # 2) a CHAMADA: processar → charge
                resposta = self._gateway.charge(payload)
                # 3) a SAÍDA: dict do terceiro → id (aprovado) ou exceção do NOSSO domínio (negado)
                if resposta["result"] == "approved":
                    return resposta["tx"]
                raise PagamentoRecusado(resposta.get("reason", "recusado"))


        class CheckoutService:
            """Serviço LIMPO: conhece só a interface ProcessadorPagamento. Zero 'if de gateway'."""

            def __init__(self, processador):
                self._processador = processador  # injeção: quem monta escolhe o gateway

            def pagar(self, item, token):
                valor = item.total
                try:
                    return {"ok": True, "tx": self._processador.processar(valor, token), "valor": valor}
                except PagamentoRecusado as erro:
                    return {"ok": False, "motivo": str(erro)}
        ''', SISTEMA=s.sistema, GW=s.gw)


def gerar_test_integracao(s):
    return render(r'''
        """Testes do ADAPTER: tradução de chamada, dados e resposta + substituibilidade."""
        import pytest

        from nucleo.antes_integracao import CheckoutAntigo
        from nucleo.integracao import @@GW@@Adapter, CheckoutService
        from nucleo.integracao_base import Gateway@@GW@@, PagamentoRecusado, ProcessadorInterno, ProcessadorPagamento
        from tests.fabrica import criar


        def test_adapter_e_um_processador():
            assert isinstance(@@GW@@Adapter(Gateway@@GW@@()), ProcessadorPagamento)


        def test_traduz_reais_para_centavos_inteiros():
            gateway = Gateway@@GW@@()
            @@GW@@Adapter(gateway).processar(19.99, "tok_ok")
            assert gateway.recebidos[0] == {"amount_cents": 1999, "card": "tok_ok", "currency": "BRL"}
            assert isinstance(gateway.recebidos[0]["amount_cents"], int)


        def test_aprovado_devolve_o_id():
            assert @@GW@@Adapter(Gateway@@GW@@()).processar(10, "tok_ok") == "@@PREF@@-0001"


        def test_recusado_vira_excecao_do_sistema():
            with pytest.raises(PagamentoRecusado, match="recusado"):
                @@GW@@Adapter(Gateway@@GW@@()).processar(10, "tok_recusado")


        @pytest.fixture(params=["interno", "gateway"])
        def processador(request):
            return ProcessadorInterno() if request.param == "interno" else @@GW@@Adapter(Gateway@@GW@@())


        def test_checkout_funciona_com_qualquer_processador(processador):
            item = criar()
            resultado = CheckoutService(processador).pagar(item, "tok_ok")
            assert resultado["ok"] is True and resultado["valor"] == item.total
            assert CheckoutService(processador).pagar(item, "tok_recusado") == {"ok": False, "motivo": "cartão recusado"}


        @pytest.mark.parametrize("token", ["tok_ok", "tok_recusado"])
        def test_mesmo_resultado_que_o_checkout_com_if(token):
            item = criar()
            novo = CheckoutService(@@GW@@Adapter(Gateway@@GW@@())).pagar(item, token)
            antigo = CheckoutAntigo(ProcessadorInterno(), Gateway@@GW@@(), usa_gateway=True).pagar(item, token)
            assert novo == antigo
        ''', GW=s.gw, PREF=s.gw_pref)


# ----------------------------------------------------------------- facade
def gerar_atendimento_base(s):
    return render(r'''
        """
        Subsistemas PRONTOS do Facade (não mexer). Cada um anota no `log` o que fez, para os
        testes conferirem a ORDEM da orquestração.
        """


        class PagamentoRecusado(Exception):
            pass


        class Disponibilidade:
            def __init__(self, indisponiveis, log):
                self._indisponiveis = set(indisponiveis)
                self._log = log

            def esta_disponivel(self, recurso):
                self._log.append("disponibilidade.esta_disponivel")
                return recurso not in self._indisponiveis


        class Calculadora:
            def __init__(self, log):
                self._log = log

            def calcular(self, item):
                self._log.append("calculadora.calcular")
                return item.total


        class Pagamentos:
            def __init__(self, log, recusar=False):
                self._log = log
                self._recusar = recusar

            def cobrar(self, cliente, valor):
                self._log.append("pagamentos.cobrar")
                if self._recusar:
                    raise PagamentoRecusado("cartão recusado")
                return f"TX-{cliente}-{valor:.2f}"


        class Registro:
            def __init__(self, log):
                self._log = log
                self._dados = {}
                self._seq = 1

            def registrar(self, recurso, item, valor):
                self._log.append("registro.registrar")
                protocolo = self._seq
                self._dados[protocolo] = {"recurso": recurso, "cliente": item.@@IDENT@@, "valor": valor}
                self._seq += 1
                return protocolo

            def buscar(self, protocolo):
                return self._dados.get(protocolo)


        class Notificador:
            def __init__(self, log):
                self._log = log
                self.enviadas = []

            def enviar(self, cliente, mensagem):
                self._log.append("notificador.enviar")
                self.enviadas.append((cliente, mensagem))
        ''', IDENT=s.ident)


def gerar_antes_atendimento(s):
    return render(r'''
        """ANTES — o smell do Facade: o CLIENTE orquestra os 5 subsistemas na mão (e cada tela repete)."""
        from nucleo.atendimento_base import PagamentoRecusado


        def atender_na_mao(recurso, item, disponibilidade, calculadora, pagamentos, registro, notificador):
            if not disponibilidade.esta_disponivel(recurso):
                return {"ok": False, "motivo": "indisponivel"}
            valor = calculadora.calcular(item)
            try:
                tx = pagamentos.cobrar(item.@@IDENT@@, valor)
            except PagamentoRecusado:
                return {"ok": False, "motivo": "pagamento recusado"}
            protocolo = registro.registrar(recurso, item, valor)
            notificador.enviar(item.@@IDENT@@, f"Protocolo {protocolo} confirmado - @@RECURSO@@ {recurso} - total R$ {valor:.2f}")
            return {"ok": True, "protocolo": protocolo, "tx": tx, "total": valor}
        ''', IDENT=s.ident, RECURSO=s.recurso)


def gerar_atendimento(s):
    return render(r'''
        """
        @@SISTEMA@@ — FACADE (Aula 09): um balcão único na frente de vários subsistemas.

        ORDEM: disponibilidade → cálculo → cobrança → registro → notificação.
        A fachada ORQUESTRA e DELEGA; a regra de cada passo continua no seu subsistema.
        Quando NÃO usar: 1–2 passos num lugar só (uma função basta). Cuidado com o God object.
        Facade ≠ Adapter: aqui são VÁRIOS subsistemas e uma interface NOVA e simples.
        """
        from nucleo.atendimento_base import PagamentoRecusado


        class AtendimentoFacade:
            def __init__(self, disponibilidade, calculadora, pagamentos, registro, notificador):
                # Segura os subsistemas (injetados → dá para testar com fakes).
                self._disponibilidade = disponibilidade
                self._calculadora = calculadora
                self._pagamentos = pagamentos
                self._registro = registro
                self._notificador = notificador

            def concluir(self, recurso, item):
                """Ponto de entrada único: o cliente não conhece os subsistemas nem a ordem."""
                # 1) Verifica ANTES de cobrar: não se cobra o que não se pode entregar.
                if not self._disponibilidade.esta_disponivel(recurso):
                    return {"ok": False, "motivo": "indisponivel"}
                # 2) Quanto custa — quem sabe é a Calculadora.
                valor = self._calculadora.calcular(item)
                # 3) Cobra; se recusar, para aqui (nada registrado, ninguém notificado).
                try:
                    tx = self._pagamentos.cobrar(item.@@IDENT@@, valor)
                except PagamentoRecusado:
                    return {"ok": False, "motivo": "pagamento recusado"}
                # 4) e 5) Só com o pagamento garantido: registra e avisa.
                protocolo = self._registro.registrar(recurso, item, valor)
                self._notificador.enviar(item.@@IDENT@@, f"Protocolo {protocolo} confirmado - @@RECURSO@@ {recurso} - total R$ {valor:.2f}")
                return {"ok": True, "protocolo": protocolo, "tx": tx, "total": valor}
        ''', SISTEMA=s.sistema, IDENT=s.ident, RECURSO=s.recurso)


def gerar_test_atendimento(s):
    r0, r1, _ = s.recursos
    return render(r'''
        """Testes do FACADE: ordem dos passos, regras de aborto e equivalência com a versão 'na mão'."""
        import pytest

        from nucleo.antes_atendimento import atender_na_mao
        from nucleo.atendimento import AtendimentoFacade
        from nucleo.atendimento_base import Calculadora, Disponibilidade, Notificador, Pagamentos, Registro
        from tests.fabrica import criar

        ORDEM = ["disponibilidade.esta_disponivel", "calculadora.calcular", "pagamentos.cobrar",
                 "registro.registrar", "notificador.enviar"]


        def montar(indisponiveis=(), recusar=False):
            log = []
            registro, notificador = Registro(log), Notificador(log)
            facade = AtendimentoFacade(Disponibilidade(indisponiveis, log), Calculadora(log),
                                       Pagamentos(log, recusar), registro, notificador)
            return facade, log, registro, notificador


        def test_caminho_feliz_na_ordem_certa():
            facade, log, registro, notificador = montar()
            item = criar()
            resultado = facade.concluir(@@R0@@, item)
            assert resultado["ok"] is True and resultado["protocolo"] == 1 and resultado["total"] == item.total
            assert log == ORDEM
            assert registro.buscar(1)["recurso"] == @@R0@@
            assert len(notificador.enviadas) == 1


        def test_indisponivel_aborta_antes_de_cobrar():
            facade, log, _, _ = montar(indisponiveis=[@@R0@@])
            assert facade.concluir(@@R0@@, criar()) == {"ok": False, "motivo": "indisponivel"}
            assert log == ORDEM[:1]


        def test_pagamento_recusado_nao_registra_nem_notifica():
            facade, log, registro, notificador = montar(recusar=True)
            assert facade.concluir(@@R0@@, criar()) == {"ok": False, "motivo": "pagamento recusado"}
            assert "registro.registrar" not in log and notificador.enviadas == []


        @pytest.mark.parametrize("indisponiveis, recusar", [((), False), ((@@R0@@,), False), ((), True)])
        def test_equivale_a_orquestracao_na_mao(indisponiveis, recusar):
            facade, log_fachada, _, _ = montar(indisponiveis, recusar)
            log_mao = []
            na_mao = atender_na_mao(@@R0@@, criar(), Disponibilidade(indisponiveis, log_mao), Calculadora(log_mao),
                                    Pagamentos(log_mao, recusar), Registro(log_mao), Notificador(log_mao))
            assert facade.concluir(@@R0@@, criar()) == na_mao
            assert log_fachada == log_mao


        def test_protocolos_sequenciais():
            facade, _, _, _ = montar()
            assert facade.concluir(@@R0@@, criar())["protocolo"] == 1
            assert facade.concluir(@@R1@@, criar(1))["protocolo"] == 2
        ''', R0=r0, R1=r1)


# ----------------------------------------------------------------- decorator
def gerar_antes_extras(s):
    params = ", ".join(f"{x[3]}=False" for x in s.extras)
    ifs = "\n".join(f"if {x[3]}:\n    total += {x[1]!r}" for x in s.extras)
    return render(r'''
        """ANTES — o smell do Decorator: uma pilha de flags e ifs (cada extra novo = parâmetro + if)."""


        def preco_com_flags(item, @@PARAMS@@):
            total = item.total
            @@IFS@@
            return round(total, 2)
        ''', PARAMS=params, IFS=ifs)


def gerar_extras(s):
    blocos = []
    for cls, valor, texto, _ in s.extras:
        blocos.append(render(r'''
            class Com@@C@@(Adicional):
                """Soma @@VALOR@@ (@@TEXTO@@) ao que está DENTRO."""

                VALOR = @@V@@

                def preco(self):
                    return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

                def descricao(self):
                    return self._componente.descricao() + " + @@TEXTO@@"
            ''', C=cls, V=lit(valor), VALOR=f"R$ {valor:.2f}", TEXTO=texto))
    pc, pf, pt = s.perc
    blocos.append(render(r'''
        class Com@@C@@(Adicional):
            """MUDA comportamento: multiplica TUDO o que está dentro por @@F@@ — aqui a ORDEM importa."""

            FATOR = @@F@@

            def preco(self):
                return round(self._componente.preco() * self.FATOR, 2)

            def descricao(self):
                return self._componente.descricao() + " (@@TEXTO@@)"
        ''', C=pc, F=lit(pf), TEXTO=pt))
    return render(r'''
        """
        @@SISTEMA@@ — DECORATOR (Aula 10): somar opcionais empilhando embrulhos.

        COMPONENTE       @@ENT@@Base(item)  → preco() / descricao()
        DECORADOR BASE   Adicional          → guarda o embrulhado e DELEGA
        DECORADORES      Com…               → chamam o de DENTRO e somam a SUA parte
        Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro: EMPILHA.
        Quando NÃO usar: extras que só somam valor fixo → lista + sum() basta.
        O @decorator do Python decora FUNÇÕES; este padrão decora OBJETOS.
        """


        class @@ENT@@Base:
            """COMPONENTE: expõe a @@ENT@@ pela interface preco()/descricao()."""

            def __init__(self, item):
                self._item = item

            def preco(self):
                return self._item.total

            def descricao(self):
                return f"@@ENT@@ de {self._item.@@IDENT@@} ({self._item.@@QTD@@} @@UNIDADE@@)"


        class Adicional:
            """DECORADOR BASE: mesma interface; guarda o objeto de dentro e, por padrão, só repassa."""

            def __init__(self, componente):
                self._componente = componente  # pode ser @@ENT@@Base OU outro Adicional → por isso empilha

            def preco(self):
                return self._componente.preco()

            def descricao(self):
                return self._componente.descricao()


        @@BLOCOS@@
        ''', SISTEMA=s.sistema, ENT=s.ent, IDENT=s.ident, QTD=s.qtd, UNIDADE=s.unidade,
        BLOCOS="\n\n".join(blocos))


def gerar_test_extras(s):
    flags = ", ".join(f'Com{x[0]}: "{x[3]}"' for x in s.extras)
    imports = ", ".join(["Adicional", f"{s.ent}Base"] + sorted([f"Com{x[0]}" for x in s.extras] + [f"Com{s.perc[0]}"]))
    (e1, v1, t1, _), (e2, v2, t2, _) = s.extras[0], s.extras[1]
    return render(r'''
        """Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
        import itertools

        import pytest

        from nucleo.antes_extras import preco_com_flags
        from nucleo.extras import @@IMPORTS@@
        from tests.fabrica import criar

        FLAGS = {@@FLAGS@@}
        COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


        @pytest.mark.parametrize("combinacao", COMBINACOES)
        def test_qualquer_combinacao_bate_com_as_flags(combinacao):
            item = criar()
            componente = @@ENT@@Base(item)
            for extra in combinacao:
                componente = extra(componente)
            esperado = preco_com_flags(item, **{FLAGS[e]: True for e in combinacao})
            assert componente.preco() == pytest.approx(esperado)


        def test_componente_entrega_o_total():
            item = criar()
            assert @@ENT@@Base(item).preco() == item.total


        def test_decorador_base_so_delega():
            item = criar()
            assert Adicional(@@ENT@@Base(item)).preco() == item.total


        def test_descricao_segue_a_ordem_do_embrulho():
            item = criar()
            componente = Com@@E2@@(Com@@E1@@(@@ENT@@Base(item)))
            base = f"@@ENT@@ de {item.@@IDENT@@} ({item.@@QTD@@} @@UNIDADE@@)"
            assert componente.descricao() == base + " + @@T1@@" + " + @@T2@@"


        def test_mesmo_extra_duas_vezes():
            item = criar()
            assert Com@@E1@@(Com@@E1@@(@@ENT@@Base(item))).preco() == pytest.approx(item.total + 2 * @@V1@@)


        def test_com_camada_que_multiplica_a_ordem_importa():
            item = criar()
            base = item.total
            por_fora = Com@@PERC@@(Com@@E1@@(@@ENT@@Base(item)))
            por_dentro = Com@@E1@@(Com@@PERC@@(@@ENT@@Base(item)))
            assert por_fora.preco() == pytest.approx(round((base + @@V1@@) * @@F@@, 2))
            assert por_dentro.preco() == pytest.approx(round(round(base * @@F@@, 2) + @@V1@@, 2))
            assert por_fora.preco() != por_dentro.preco()


        @pytest.mark.parametrize("classe", [Adicional, @@CLASSES@@])
        def test_todo_decorador_mantem_a_interface(classe):
            embrulho = classe(@@ENT@@Base(criar()))
            assert callable(embrulho.preco) and callable(embrulho.descricao)
        ''', IMPORTS=imports, FLAGS=flags, ENT=s.ent, IDENT=s.ident, QTD=s.qtd, UNIDADE=s.unidade,
        E1=e1, E2=e2, T1=t1, T2=t2, V1=lit(v1), PERC=s.perc[0], F=lit(s.perc[1]),
        CLASSES=", ".join([f"Com{x[0]}" for x in s.extras] + [f"Com{s.perc[0]}"]))


# =============================================================================
# 4b. GoF — os padrões que não estavam nas aulas (criação · estruturais · comportamentais)
#     Cada um: módulo aplicado + antes_*.py (o smell) + testes. Só dependem de nucleo/entidades.py.
# =============================================================================
def rotulo(nome):
    return nome.replace("_", " ").capitalize()


# ----------------------------------------------------------------- singleton
def gerar_configuracao(s):
    return render(r'''
        """
        @@SISTEMA@@ — SINGLETON (GoF · criação): UMA configuração para o sistema inteiro.

        ANTES (nucleo/antes_configuracao.py): cada parte criava a sua ConfiguracaoAntiga(); mudar a taxa
        numa não mudava nas outras → caixa e relatório cobrando valores diferentes.
        DEPOIS (aqui):
          * __new__ devolve SEMPRE o mesmo objeto (guardado no atributo de CLASSE _instancia);
          * quem precisa chama Configuracao() e recebe a única que existe;
          * reiniciar() existe só para os testes começarem do zero.
        Quando NÃO usar: em Python um MÓDULO já é único — uma variável no módulo resolve sem cerimônia.
        Singleton é estado global escondido: prefira injetar a dependência quando der.
        """


        class Configuracao:
            """SINGLETON: a única configuração do @@SISTEMA@@ (moeda e taxa de serviço)."""

            _instancia = None  # o objeto único fica guardado na CLASSE

            def __new__(cls):
                # __new__ CRIA o objeto (roda antes do __init__): aqui decidimos devolver o que já existe.
                if cls._instancia is None:
                    instancia = super().__new__(cls)
                    instancia.moeda = "R$"
                    instancia.taxa_servico = 0.0
                    cls._instancia = instancia
                return cls._instancia

            @classmethod
            def reiniciar(cls):
                """Apaga a instância única (usado pelos testes para começar do zero)."""
                cls._instancia = None


        def total_com_taxa(item):
            """Total da @@ENT@@ + a taxa de serviço da configuração ÚNICA."""
            return round(item.total * (1 + Configuracao().taxa_servico), 2)


        def formatar(valor):
            """Valor com a moeda da configuração ÚNICA (quem calcula e quem formata leem a mesma)."""
            return f"{Configuracao().moeda} {valor:.2f}"
        ''', SISTEMA=s.sistema, ENT=s.ent)


def gerar_antes_configuracao(s):
    return render(r'''
        """ANTES — o smell do Singleton: cada parte do sistema cria a SUA configuração (e elas divergem)."""


        class ConfiguracaoAntiga:
            def __init__(self):
                self.moeda = "R$"
                self.taxa_servico = 0.0


        # Cada módulo guardava a sua cópia:
        CONFIG_DO_CAIXA = ConfiguracaoAntiga()
        CONFIG_DO_RELATORIO = ConfiguracaoAntiga()


        def total_no_caixa(item):
            return round(item.total * (1 + CONFIG_DO_CAIXA.taxa_servico), 2)


        def total_no_relatorio(item):
            return round(item.total * (1 + CONFIG_DO_RELATORIO.taxa_servico), 2)
        ''')


def gerar_test_configuracao(s):
    return render(r'''
        """Testes do SINGLETON: um objeto só, visto por todos; na versão antiga as cópias divergem."""
        import pytest

        from nucleo import antes_configuracao
        from nucleo.configuracao import Configuracao, formatar, total_com_taxa
        from tests.fabrica import criar


        @pytest.fixture(autouse=True)
        def configuracao_limpa():
            Configuracao.reiniciar()
            yield
            Configuracao.reiniciar()


        def test_sempre_o_mesmo_objeto():
            assert Configuracao() is Configuracao()


        def test_valores_iniciais():
            cfg = Configuracao()
            assert (cfg.moeda, cfg.taxa_servico) == ("R$", 0.0)


        def test_mudanca_vale_para_todos():
            Configuracao().taxa_servico = 0.1
            item = criar()
            assert total_com_taxa(item) == round(item.total * 1.1, 2)


        def test_chamar_de_novo_nao_apaga_o_que_mudou():
            Configuracao().moeda = "US$"
            Configuracao()
            assert formatar(10) == "US$ 10.00"


        def test_reiniciar_comeca_do_zero():
            primeira = Configuracao()
            Configuracao.reiniciar()
            assert Configuracao() is not primeira


        def test_antes_as_copias_divergem():
            item = criar()
            antes_configuracao.CONFIG_DO_CAIXA.taxa_servico = 0.1
            try:
                assert antes_configuracao.total_no_caixa(item) != antes_configuracao.total_no_relatorio(item)
            finally:
                antes_configuracao.CONFIG_DO_CAIXA.taxa_servico = 0.0
        ''')


# ----------------------------------------------------------------- factory method
def gerar_avisos(s):
    return render(r'''
        """
        @@SISTEMA@@ — FACTORY METHOD (GoF · criação): quem decide QUAL canal criar é a SUBCLASSE.

        ANTES (nucleo/antes_avisos.py): avisar_antigo(item, canal) com if/elif para montar cada canal.
        DEPOIS (aqui):
          * Avisador.avisar(item) é o algoritmo comum (monta a mensagem e envia);
          * o passo "qual canal usar" é o MÉTODO FÁBRICA criar_canal(), que cada subclasse sobrescreve;
          * canal novo = produto novo + criador novo; Avisador não muda (OCP).
        Quando NÃO usar: um tipo só de canal, ou escolha resolvida por dicionário {nome: Classe} —
        em Python dá até para passar a própria CLASSE como parâmetro.
        """


        class Canal:
            """PRODUTO: o que todo canal sabe fazer."""

            def enviar(self, destino, mensagem):
                raise NotImplementedError


        class CanalEmail(Canal):
            def enviar(self, destino, mensagem):
                return f"[e-mail] para {destino}: {mensagem}"


        class CanalSms(Canal):
            def enviar(self, destino, mensagem):
                return f"[sms] {destino}: {mensagem[:60]}"  # SMS tem limite de tamanho


        class Avisador:
            """CRIADOR: tem o algoritmo; deixa para a subclasse o MÉTODO FÁBRICA criar_canal()."""

            def criar_canal(self):
                """MÉTODO FÁBRICA: cada subclasse decide QUAL produto (canal) criar."""
                raise NotImplementedError("a subclasse escolhe o canal")

            def avisar(self, item):
                """Monta a mensagem da @@ENT@@ e envia pelo canal que a subclasse criou."""
                mensagem = f"Confirmação de @@ENT@@: R$ {item.total:.2f}"
                canal = self.criar_canal()  # ← o único ponto que muda entre os avisadores
                return canal.enviar(item.@@IDENT@@, mensagem)


        class AvisadorEmail(Avisador):
            def criar_canal(self):
                return CanalEmail()


        class AvisadorSms(Avisador):
            def criar_canal(self):
                return CanalSms()


        class CanalWhatsapp(Canal):
            """Produto NOVO (extensão): nenhum código existente muda."""

            def enviar(self, destino, mensagem):
                return f"[whatsapp] {destino}: {mensagem}"


        class AvisadorWhatsapp(Avisador):
            def criar_canal(self):
                return CanalWhatsapp()
        ''', SISTEMA=s.sistema, ENT=s.ent, IDENT=s.ident)


def gerar_antes_avisos(s):
    return render(r'''
        """ANTES — o smell do Factory Method: if/elif para CRIAR o canal certo dentro do algoritmo."""


        def avisar_antigo(item, canal):
            mensagem = f"Confirmação de @@ENT@@: R$ {item.total:.2f}"
            if canal == "email":
                return f"[e-mail] para {item.@@IDENT@@}: {mensagem}"
            elif canal == "sms":
                return f"[sms] {item.@@IDENT@@}: {mensagem[:60]}"
            else:
                raise ValueError(f"canal desconhecido: {canal}")
        ''', ENT=s.ent, IDENT=s.ident)


def gerar_test_avisos(s):
    return render(r'''
        """Testes do FACTORY METHOD: mesma mensagem da versão antiga; canal novo sem mexer no criador."""
        import pytest

        from nucleo.antes_avisos import avisar_antigo
        from nucleo.avisos import (Avisador, AvisadorEmail, AvisadorSms, AvisadorWhatsapp, CanalEmail, CanalSms,
                                   CanalWhatsapp)
        from tests.fabrica import criar, itens_exemplo


        @pytest.mark.parametrize("canal, avisador", [("email", AvisadorEmail), ("sms", AvisadorSms)])
        @pytest.mark.parametrize("indice", range(4))
        def test_refatoracao_preserva_a_mensagem(canal, avisador, indice):
            item = itens_exemplo()[indice]
            assert avisador().avisar(item) == avisar_antigo(item, canal)


        @pytest.mark.parametrize("avisador, produto", [(AvisadorEmail, CanalEmail), (AvisadorSms, CanalSms),
                                                       (AvisadorWhatsapp, CanalWhatsapp)])
        def test_cada_criador_cria_o_seu_produto(avisador, produto):
            assert isinstance(avisador().criar_canal(), produto)


        def test_criador_base_nao_escolhe_canal():
            with pytest.raises(NotImplementedError):
                Avisador().avisar(criar())


        def test_canal_novo_sem_mudar_o_avisador():
            item = criar()
            assert AvisadorWhatsapp().avisar(item).startswith(f"[whatsapp] {item.@@IDENT@@}:")


        def test_versao_com_if_nao_conhece_o_canal_novo():
            with pytest.raises(ValueError):
                avisar_antigo(criar(), "whatsapp")


        def test_mensagem_tem_o_total():
            item = criar()
            assert f"R$ {item.total:.2f}" in AvisadorEmail().avisar(item)
        ''', IDENT=s.ident)


# ----------------------------------------------------------------- abstract factory
def gerar_kits(s):
    return render(r'''
        """
        @@SISTEMA@@ — ABSTRACT FACTORY (GoF · criação): FAMÍLIAS de peças que combinam entre si.

        ANTES (nucleo/antes_kits.py): cada peça do relatório (cabeçalho, linha, rodapé) tinha o seu
        "if formato"; bastava esquecer um para misturar texto com HTML no mesmo relatório.
        DEPOIS (aqui):
          * KitRelatorio (a FÁBRICA ABSTRATA) declara criar_cabecalho / criar_linha / criar_rodape;
          * cada kit concreto (KitTexto, KitHtml) cria TODAS as peças da MESMA família;
          * montar_relatorio(kit, itens) só conhece a interface → família nova = kit novo (KitMarkdown).
        Quando NÃO usar: só uma família (ou uma peça) — Factory Method ou a classe direta bastam.
        """


        class KitRelatorio:
            """FÁBRICA ABSTRATA: o que toda família de peças precisa saber criar."""

            def criar_cabecalho(self, titulo):
                raise NotImplementedError

            def criar_linha(self, rotulo, valor):
                raise NotImplementedError

            def criar_rodape(self, total):
                raise NotImplementedError


        class KitTexto(KitRelatorio):
            """Família TEXTO: todas as peças em texto puro."""

            def criar_cabecalho(self, titulo):
                return f"== {titulo} =="

            def criar_linha(self, rotulo, valor):
                return f"{rotulo}: R$ {valor:.2f}"

            def criar_rodape(self, total):
                return f"TOTAL: R$ {total:.2f}"


        class KitHtml(KitRelatorio):
            """Família HTML: todas as peças em HTML (nunca se misturam com texto)."""

            def criar_cabecalho(self, titulo):
                return f"<h1>{titulo}</h1>"

            def criar_linha(self, rotulo, valor):
                return f"<li>{rotulo}: R$ {valor:.2f}</li>"

            def criar_rodape(self, total):
                return f"<p><strong>TOTAL: R$ {total:.2f}</strong></p>"


        class KitMarkdown(KitRelatorio):
            """Família NOVA (extensão): entra sem mudar montar_relatorio."""

            def criar_cabecalho(self, titulo):
                return f"# {titulo}"

            def criar_linha(self, rotulo, valor):
                return f"- {rotulo}: R$ {valor:.2f}"

            def criar_rodape(self, total):
                return f"**TOTAL: R$ {total:.2f}**"


        def montar_relatorio(kit, itens):
            """CLIENTE: usa só a interface do kit → todas as peças vêm da MESMA família."""
            partes = [kit.criar_cabecalho("@@SISTEMA@@")]
            partes += [kit.criar_linha(item.@@IDENT@@, item.total) for item in itens]
            partes.append(kit.criar_rodape(round(sum(item.total for item in itens), 2)))
            return "\n".join(partes)
        ''', SISTEMA=s.sistema, IDENT=s.ident)


def gerar_antes_kits(s):
    return render(r'''
        """ANTES — o smell do Abstract Factory: um if por PEÇA; esquecer um mistura as famílias."""


        def montar_relatorio_antigo(itens, formato):
            if formato == "texto":
                partes = ["== @@SISTEMA@@ =="]
            else:
                partes = ["<h1>@@SISTEMA@@</h1>"]
            for item in itens:
                if formato == "texto":
                    partes.append(f"{item.@@IDENT@@}: R$ {item.total:.2f}")
                else:
                    partes.append(f"<li>{item.@@IDENT@@}: R$ {item.total:.2f}</li>")
            total = round(sum(item.total for item in itens), 2)
            if formato == "texto":
                partes.append(f"TOTAL: R$ {total:.2f}")
            else:
                partes.append(f"<p><strong>TOTAL: R$ {total:.2f}</strong></p>")
            return "\n".join(partes)
        ''', SISTEMA=s.sistema, IDENT=s.ident)


def gerar_test_kits(s):
    return render(r'''
        """Testes do ABSTRACT FACTORY: relatórios idênticos à versão antiga e famílias que não se misturam."""
        import pytest

        from nucleo.antes_kits import montar_relatorio_antigo
        from nucleo.kits import KitHtml, KitMarkdown, KitRelatorio, KitTexto, montar_relatorio
        from tests.fabrica import itens_exemplo


        @pytest.mark.parametrize("formato, kit", [("texto", KitTexto), ("html", KitHtml)])
        def test_refatoracao_preserva_o_relatorio(formato, kit):
            itens = itens_exemplo()
            assert montar_relatorio(kit(), itens) == montar_relatorio_antigo(itens, formato)


        def test_kit_html_so_cria_pecas_html():
            texto = montar_relatorio(KitHtml(), itens_exemplo())
            assert all(linha.startswith("<") for linha in texto.splitlines())


        def test_kit_texto_nao_tem_html():
            assert "<" not in montar_relatorio(KitTexto(), itens_exemplo())


        def test_familia_nova_sem_mudar_o_cliente():
            linhas = montar_relatorio(KitMarkdown(), itens_exemplo()).splitlines()
            assert linhas[0] == "# @@SISTEMA@@" and linhas[-1].startswith("**TOTAL")


        def test_fabrica_abstrata_nao_cria_nada():
            with pytest.raises(NotImplementedError):
                KitRelatorio().criar_cabecalho("x")


        def test_uma_linha_por_item_mais_cabecalho_e_rodape():
            itens = itens_exemplo()
            assert len(montar_relatorio(KitTexto(), itens).splitlines()) == len(itens) + 2
        ''', SISTEMA=s.sistema)


# ----------------------------------------------------------------- builder
def gerar_construtor(s):
    req = [a["nome"] for a in s.atributos if a["regra"] != "livre"]
    metodos = []
    for a in s.atributos:
        metodos.append(render(r'''
            def com_@@N@@(self, valor):
                """Informa @@N@@ e devolve o PRÓPRIO builder (para encadear)."""
                self._valores["@@N@@"] = valor
                return self
            ''', N=a["nome"]))
    padrao = {k: v for k, v in s.dados_exemplo(0).items() if k != s.ident}
    return render(r'''
        """
        @@SISTEMA@@ — BUILDER (GoF · criação): montar a @@ENT@@ PASSO A PASSO, com nomes.

        ANTES (nucleo/antes_construtor.py): nova_@@ENTVAR@@_antiga(...) com todos os argumentos na ORDEM —
        dois números trocados de lugar passam despercebidos e não há receitas prontas.
        DEPOIS (aqui):
          * @@ENT@@Builder tem um com_<campo>() por atributo; cada um devolve o próprio builder
            (interface FLUENTE: b.com_x(...).com_y(...));
          * construir() confere o que falta e só então cria a @@ENT@@ (os setters validam cada valor);
          * DiretorDe@@ENT@@ guarda "receitas" de montagem que se repetem.
        Quando NÃO usar: poucos campos — em Python, argumentos NOMEADOS já resolvem a ordem.
        """
        from nucleo.entidades import @@ENT@@

        OBRIGATORIOS = @@OBRIG@@


        class @@ENT@@Builder:
            """BUILDER: junta os valores aos poucos e cria a @@ENT@@ no final."""

            def __init__(self):
                self._valores = {}

            @@METODOS@@

            def faltando(self):
                """Campos obrigatórios que ainda não foram informados."""
                return [campo for campo in OBRIGATORIOS if campo not in self._valores]

            def construir(self):
                """Cria a @@ENT@@. Faltou campo → ValueError dizendo QUAL; valor inválido → o setter barra."""
                falta = self.faltando()
                if falta:
                    raise ValueError(f"faltam campos: {', '.join(falta)}")
                return @@ENT@@(**self._valores)


        class DiretorDe@@ENT@@:
            """DIRETOR: receitas de montagem que se repetem (o passo a passo fica num lugar só)."""

            PADRAO = @@PADRAO@@

            def basico(self, @@IDENT@@):
                builder = @@ENT@@Builder().com_@@IDENT@@(@@IDENT@@)
                for campo, valor in self.PADRAO.items():
                    getattr(builder, f"com_{campo}")(valor)
                return builder.construir()
        ''', SISTEMA=s.sistema, ENT=s.ent, ENTVAR=s.ent_var, OBRIG=lit(req), METODOS="\n\n".join(metodos),
        PADRAO=dict_lit(padrao), IDENT=s.ident)


def gerar_antes_construtor(s):
    req = [a["nome"] for a in s.atributos if a["regra"] != "livre"]
    livres = [a["nome"] for a in s.atributos if a["regra"] == "livre"]
    params = ", ".join(req + [f'{n}=""' for n in livres])
    return render(r'''
        """ANTES — o smell do Builder: construtor com muitos argumentos POSICIONAIS (a ordem é decorada)."""
        from nucleo.entidades import @@ENT@@


        def nova_@@ENTVAR@@_antiga(@@PARAMS@@):
            # Quem chama precisa lembrar a ORDEM: trocar dois números de lugar não dá erro, dá objeto errado.
            return @@ENT@@(@@ARGS@@)
        ''', ENT=s.ent, ENTVAR=s.ent_var, PARAMS=params, ARGS=", ".join(req + livres))


def gerar_test_construtor(s):
    return render(r'''
        """Testes do BUILDER: monta o mesmo que o construtor, avisa o que falta e encadeia."""
        import pytest

        from nucleo.antes_construtor import nova_@@ENTVAR@@_antiga
        from nucleo.construtor import DiretorDe@@ENT@@, @@ENT@@Builder
        from tests.fabrica import DADOS_EXEMPLO


        def construir_com(dados):
            builder = @@ENT@@Builder()
            for campo, valor in dados.items():
                getattr(builder, f"com_{campo}")(valor)
            return builder.construir()


        @pytest.mark.parametrize("indice", range(4))
        def test_builder_monta_os_mesmos_valores(indice):
            dados = DADOS_EXEMPLO[indice]
            feito = construir_com(dados)
            for campo, valor in dados.items():
                assert getattr(feito, campo) == valor


        @pytest.mark.parametrize("indice", range(4))
        def test_igual_a_versao_posicional(indice):
            dados = DADOS_EXEMPLO[indice]
            antigo = nova_@@ENTVAR@@_antiga(*dados.values())
            assert vars(construir_com(dados)) == vars(antigo)


        def test_interface_fluente_devolve_o_proprio_builder():
            builder = @@ENT@@Builder()
            assert builder.com_@@IDENT@@("@@NOME@@") is builder


        def test_falta_campo_obrigatorio_diz_qual():
            with pytest.raises(ValueError, match="@@QTD@@"):
                @@ENT@@Builder().com_@@IDENT@@("@@NOME@@").construir()


        def test_valor_invalido_e_barrado_pela_entidade():
            with pytest.raises(ValueError):
                construir_com(dict(DADOS_EXEMPLO[0], @@QTD@@=0))


        def test_diretor_monta_a_receita_padrao():
            obj = DiretorDe@@ENT@@().basico("@@NOME@@")
            assert obj.@@IDENT@@ == "@@NOME@@" and obj.total >= 0


        def test_ordem_dos_passos_nao_importa():
            dados = DADOS_EXEMPLO[1]
            invertido = dict(reversed(list(dados.items())))
            assert vars(construir_com(invertido)) == vars(construir_com(dados))
        ''', ENT=s.ent, ENTVAR=s.ent_var, IDENT=s.ident, NOME=s.nomes[0], QTD=s.qtd)


# ----------------------------------------------------------------- prototype
def gerar_prototipos(s):
    return render(r'''
        """
        @@SISTEMA@@ — PROTOTYPE (GoF · criação): criar COPIANDO um modelo pronto (clone).

        ANTES (nucleo/antes_prototipos.py): copiar_na_mao(original) lista campo por campo — se a @@ENT@@
        ganhar um dado novo, a cópia esquece dele sem avisar.
        DEPOIS (aqui):
          * clonar(original) usa copy.deepcopy: copia TUDO, inclusive listas internas (cópia PROFUNDA);
          * RegistroDePrototipos guarda modelos prontos por nome e devolve sempre um CLONE;
          * as mudanças do clone passam pelos setters → continuam validadas.
        Quando NÃO usar: objeto simples, criado em uma linha. Cuidado: copy.copy (cópia RASA)
        compartilharia as listas internas com o original.
        """
        import copy


        def clonar(original, **mudancas):
            """Cópia PROFUNDA do original; as mudanças passam pelos setters (validadas)."""
            novo = copy.deepcopy(original)
            for campo, valor in mudancas.items():
                if not hasattr(novo, campo):
                    raise AttributeError(f"a @@ENT@@ não tem o campo {campo!r}")
                setattr(novo, campo, valor)
            return novo


        class RegistroDePrototipos:
            """Guarda MODELOS por nome; entregar = clonar (o modelo guardado nunca muda)."""

            def __init__(self):
                self._modelos = {}

            def registrar(self, nome, modelo):
                self._modelos[nome] = modelo

            def nomes(self):
                return sorted(self._modelos)

            def criar(self, nome, **mudancas):
                if nome not in self._modelos:
                    raise KeyError(f"modelo desconhecido: {nome}")
                return clonar(self._modelos[nome], **mudancas)
        ''', SISTEMA=s.sistema, ENT=s.ent)


def gerar_antes_prototipos(s):
    kwargs = ", ".join(f"{a['nome']}=original.{a['nome']}" for a in s.atributos)
    return render(r'''
        """ANTES — o smell do Prototype: copiar campo por campo, na mão (e esquecer o que é novo)."""
        from nucleo.entidades import @@ENT@@


        def copiar_na_mao(original):
            return @@ENT@@(@@KWARGS@@)
        ''', ENT=s.ent, KWARGS=kwargs)


def gerar_test_prototipos(s):
    return render(r'''
        """Testes do PROTOTYPE: clone independente, profundo e validado; o registro entrega cópias."""
        import pytest

        from nucleo.antes_prototipos import copiar_na_mao
        from nucleo.prototipos import RegistroDePrototipos, clonar
        from tests.fabrica import criar


        def test_clone_e_outro_objeto_com_os_mesmos_dados():
            original = criar()
            copia = clonar(original)
            assert copia is not original and vars(copia) == vars(original)


        def test_mudar_o_clone_nao_muda_o_original():
            original = criar()
            copia = clonar(original, @@QTD@@=original.@@QTD@@ + 1)
            assert copia.@@QTD@@ == original.@@QTD@@ + 1 and vars(original) == vars(criar())


        def test_mudanca_invalida_e_barrada():
            with pytest.raises(ValueError):
                clonar(criar(), @@QTD@@=0)


        def test_campo_inexistente_e_recusado():
            with pytest.raises(AttributeError):
                clonar(criar(), campo_que_nao_existe=1)


        def test_copia_profunda_nao_compartilha_listas():
            original = criar()
            original.etiquetas = ["original"]  # dado novo, que a @@ENT@@ não conhecia
            copia = clonar(original)
            copia.etiquetas.append("so na copia")
            assert original.etiquetas == ["original"]


        def test_copia_na_mao_esquece_o_dado_novo():
            original = criar()
            original.etiquetas = ["original"]
            assert copiar_na_mao(original).total == original.total
            assert not hasattr(copiar_na_mao(original), "etiquetas")
            assert clonar(original).etiquetas == ["original"]


        def test_registro_entrega_clones_do_modelo():
            registro = RegistroDePrototipos()
            registro.registrar("padrao", criar())
            a = registro.criar("padrao")
            b = registro.criar("padrao", @@IDENT@@="@@NOME@@")
            assert a is not b and b.@@IDENT@@ == "@@NOME@@" and registro.nomes() == ["padrao"]


        def test_modelo_desconhecido():
            with pytest.raises(KeyError):
                RegistroDePrototipos().criar("nao existe")
        ''', QTD=s.qtd, ENT=s.ent, IDENT=s.ident, NOME=s.nomes[1])


# ----------------------------------------------------------------- bridge
def gerar_comprovantes(s):
    return render(r'''
        """
        @@SISTEMA@@ — BRIDGE (GoF · estrutural): duas dimensões que variam SEPARADAS.

        ANTES (nucleo/antes_comprovantes.py): uma classe para cada COMBINAÇÃO (Simples×Texto, Simples×Html,
        Detalhado×Texto, Detalhado×Html) — 2 tipos × 2 formatos = 4 classes com código repetido; um formato
        novo exigiria uma classe para CADA tipo.
        DEPOIS (aqui):
          * ABSTRAÇÃO: Comprovante (Simples, Detalhado) decide O QUE mostrar;
          * IMPLEMENTAÇÃO: Formato (FormatoTexto, FormatoHtml) decide COMO escrever;
          * a "ponte" é o atributo self.formato: o comprovante TEM-UM formato (composição) e delega;
          * formato novo (FormatoMarkdown) vale para TODOS os tipos: N + M classes em vez de N × M.
        Quando NÃO usar: só uma dimensão varia → herança simples ou Strategy resolvem.
        """


        class Formato:
            """IMPLEMENTAÇÃO: como escrever um título e uma linha."""

            def titulo(self, texto):
                raise NotImplementedError

            def linha(self, rotulo, valor):
                raise NotImplementedError


        class FormatoTexto(Formato):
            def titulo(self, texto):
                return texto.upper()

            def linha(self, rotulo, valor):
                return f"{rotulo}: {valor}"


        class FormatoHtml(Formato):
            def titulo(self, texto):
                return f"<h2>{texto}</h2>"

            def linha(self, rotulo, valor):
                return f"<p>{rotulo}: {valor}</p>"


        class FormatoMarkdown(Formato):
            """Formato NOVO: vale para todos os comprovantes sem criar combinações."""

            def titulo(self, texto):
                return f"## {texto}"

            def linha(self, rotulo, valor):
                return f"- **{rotulo}**: {valor}"


        class Comprovante:
            """ABSTRAÇÃO: TEM-UM formato (a ponte) e decide o conteúdo."""

            def __init__(self, formato):
                self.formato = formato

            def gerar(self, item):
                raise NotImplementedError


        class ComprovanteSimples(Comprovante):
            def gerar(self, item):
                return "\n".join([self.formato.titulo("Comprovante"),
                                  self.formato.linha("Total", f"R$ {item.total:.2f}")])


        class ComprovanteDetalhado(Comprovante):
            def gerar(self, item):
                return "\n".join([self.formato.titulo("Comprovante detalhado"),
                                  self.formato.linha("@@RI@@", item.@@IDENT@@),
                                  self.formato.linha("@@RQ@@", item.@@QTD@@),
                                  self.formato.linha("@@RP@@", f"R$ {item.@@PRECO@@:.2f}"),
                                  self.formato.linha("Total", f"R$ {item.total:.2f}")])
        ''', SISTEMA=s.sistema, IDENT=s.ident, QTD=s.qtd, PRECO=s.preco,
        RI=rotulo(s.ident), RQ=rotulo(s.qtd), RP=rotulo(s.preco))


def gerar_antes_comprovantes(s):
    return render(r'''
        """ANTES — o smell do Bridge: uma classe por COMBINAÇÃO (tipos × formatos), com código repetido."""


        class SimplesTexto:
            def gerar(self, item):
                return "\n".join(["COMPROVANTE", f"Total: R$ {item.total:.2f}"])


        class SimplesHtml:
            def gerar(self, item):
                return "\n".join(["<h2>Comprovante</h2>", f"<p>Total: R$ {item.total:.2f}</p>"])


        class DetalhadoTexto:
            def gerar(self, item):
                return "\n".join(["COMPROVANTE DETALHADO", f"@@RI@@: {item.@@IDENT@@}", f"@@RQ@@: {item.@@QTD@@}",
                                  f"@@RP@@: R$ {item.@@PRECO@@:.2f}", f"Total: R$ {item.total:.2f}"])


        class DetalhadoHtml:
            def gerar(self, item):
                return "\n".join(["<h2>Comprovante detalhado</h2>", f"<p>@@RI@@: {item.@@IDENT@@}</p>",
                                  f"<p>@@RQ@@: {item.@@QTD@@}</p>", f"<p>@@RP@@: R$ {item.@@PRECO@@:.2f}</p>",
                                  f"<p>Total: R$ {item.total:.2f}</p>"])
        ''', IDENT=s.ident, QTD=s.qtd, PRECO=s.preco, RI=rotulo(s.ident), RQ=rotulo(s.qtd), RP=rotulo(s.preco))


def gerar_test_comprovantes(s):
    return render(r'''
        """Testes do BRIDGE: cada combinação = a classe antiga; formato novo serve a todos os tipos."""
        import pytest

        from nucleo import antes_comprovantes
        from nucleo.comprovantes import (Comprovante, ComprovanteDetalhado, ComprovanteSimples, Formato, FormatoHtml,
                                         FormatoMarkdown, FormatoTexto)
        from tests.fabrica import itens_exemplo

        COMBINACOES = [(ComprovanteSimples, FormatoTexto, "SimplesTexto"), (ComprovanteSimples, FormatoHtml, "SimplesHtml"),
                       (ComprovanteDetalhado, FormatoTexto, "DetalhadoTexto"),
                       (ComprovanteDetalhado, FormatoHtml, "DetalhadoHtml")]


        @pytest.mark.parametrize("tipo, formato, antiga", COMBINACOES)
        @pytest.mark.parametrize("indice", range(4))
        def test_cada_combinacao_igual_a_classe_antiga(tipo, formato, antiga, indice):
            item = itens_exemplo()[indice]
            assert tipo(formato()).gerar(item) == getattr(antes_comprovantes, antiga)().gerar(item)


        @pytest.mark.parametrize("tipo", [ComprovanteSimples, ComprovanteDetalhado])
        def test_formato_novo_vale_para_todos_os_tipos(tipo):
            texto = tipo(FormatoMarkdown()).gerar(itens_exemplo()[0])
            assert texto.startswith("## ") and "**Total**" in texto


        def test_trocar_o_formato_em_tempo_de_execucao():
            comprovante = ComprovanteSimples(FormatoTexto())
            comprovante.formato = FormatoHtml()
            assert comprovante.gerar(itens_exemplo()[0]).startswith("<h2>")


        def test_partes_abstratas():
            with pytest.raises(NotImplementedError):
                Comprovante(FormatoTexto()).gerar(itens_exemplo()[0])
            with pytest.raises(NotImplementedError):
                Formato().titulo("x")
        ''')


# ----------------------------------------------------------------- composite
def gerar_pacotes(s):
    return render(r'''
        """
        @@SISTEMA@@ — COMPOSITE (GoF · estrutural): item e PACOTE de itens tratados do mesmo jeito.

        ANTES (nucleo/antes_pacotes.py): total_antigo(coisa) pergunta com isinstance se é lista ou @@ENT@@
        e se chama de novo para as listas — cada operação nova repete essa checagem.
        DEPOIS (aqui):
          * Componente define a interface comum: preco() e descricao();
          * Unitario (FOLHA) embrulha uma @@ENT@@;
          * Pacote (COMPOSTO) guarda filhos (folhas OU outros pacotes) e repassa a pergunta a eles;
          * quem usa chama pacote.preco() sem saber a profundidade da árvore.
        Quando NÃO usar: lista plana, sem pacotes dentro de pacotes → sum() numa lista basta.
        """


        class Componente:
            """Interface comum de folha e composto."""

            def preco(self):
                raise NotImplementedError

            def descricao(self, nivel=0):
                raise NotImplementedError


        class Unitario(Componente):
            """FOLHA: uma @@ENT@@ sozinha."""

            def __init__(self, item):
                self.item = item

            def preco(self):
                return self.item.total

            def descricao(self, nivel=0):
                return "  " * nivel + f"{self.item.@@IDENT@@}: R$ {self.preco():.2f}"


        class Pacote(Componente):
            """COMPOSTO: tem filhos (folhas ou pacotes) e trata todos pela mesma interface."""

            def __init__(self, nome, desconto=0.0):
                self.nome = nome
                self.desconto = desconto  # ex.: 0.1 = pacote com 10% de desconto
                self.filhos = []

            def adicionar(self, componente):
                self.filhos.append(componente)
                return self  # permite encadear

            def preco(self):
                soma = sum(filho.preco() for filho in self.filhos)  # recursão: cada filho sabe o seu preço
                return round(soma * (1 - self.desconto), 2)

            def descricao(self, nivel=0):
                linhas = ["  " * nivel + f"[{self.nome}] R$ {self.preco():.2f}"]
                linhas += [filho.descricao(nivel + 1) for filho in self.filhos]
                return "\n".join(linhas)
        ''', SISTEMA=s.sistema, ENT=s.ent, IDENT=s.ident)


def gerar_antes_pacotes(s):
    return render(r'''
        """ANTES — o smell do Composite: isinstance para saber se é lista ou item (em cada operação)."""


        def total_antigo(coisa):
            if isinstance(coisa, list):
                return round(sum(total_antigo(parte) for parte in coisa), 2)
            return coisa.total
        ''')


def gerar_test_pacotes(s):
    return render(r'''
        """Testes do COMPOSITE: folha e pacote com a mesma interface; árvore de qualquer profundidade."""
        from nucleo.antes_pacotes import total_antigo
        from nucleo.pacotes import Componente, Pacote, Unitario
        from tests.fabrica import itens_exemplo


        def montar():
            a, b, c, d = itens_exemplo()
            interno = Pacote("interno").adicionar(Unitario(c)).adicionar(Unitario(d))
            externo = Pacote("externo").adicionar(Unitario(a)).adicionar(Unitario(b)).adicionar(interno)
            return externo, [a, b, [c, d]]


        def test_folha_vale_o_total_da_entidade():
            item = itens_exemplo()[0]
            assert Unitario(item).preco() == item.total


        def test_pacote_soma_os_filhos_em_qualquer_profundidade():
            pacote, lista = montar()
            assert pacote.preco() == total_antigo(lista)


        def test_pacote_vazio_vale_zero():
            assert Pacote("vazio").preco() == 0


        def test_desconto_do_pacote():
            a, b, _, _ = itens_exemplo()
            pacote = Pacote("promo", desconto=0.1).adicionar(Unitario(a)).adicionar(Unitario(b))
            assert pacote.preco() == round((a.total + b.total) * 0.9, 2)


        def test_folha_e_pacote_tem_a_mesma_interface():
            pacote, _ = montar()
            for componente in [pacote, *pacote.filhos]:
                assert isinstance(componente, Componente)
                assert isinstance(componente.preco(), (int, float))


        def test_descricao_mostra_a_arvore():
            pacote, _ = montar()
            linhas = pacote.descricao().splitlines()
            assert linhas[0].startswith("[externo]")
            assert any(linha.startswith("  [interno]") for linha in linhas)
            assert len(linhas) == 6
        ''')


# ----------------------------------------------------------------- flyweight
def tipos_literal(s):
    return "{" + ", ".join(f'"{x[3]}": ("{x[0]}", {x[1]!r})' for x in s.variantes + [s.vnova]) + "}"


def gerar_tipos_compartilhados(s):
    return render(r'''
        """
        @@SISTEMA@@ — FLYWEIGHT (GoF · estrutural): COMPARTILHAR o que se repete em milhares de objetos.

        ANTES (nucleo/antes_tipos_compartilhados.py): cada registro criava o SEU objeto de @@CONCEITO@@
        (nome + fator) — 10 000 registros = 10 000 objetos iguais na memória.
        DEPOIS (aqui):
          * TipoCompartilhado guarda só o estado INTRÍNSECO (nome, fator): igual para todos e IMUTÁVEL;
          * FabricaDeTipos.obter(chave) devolve SEMPRE o mesmo objeto para a mesma chave (cache);
          * o estado EXTRÍNSECO (a @@ENT@@ de cada registro) entra por parâmetro: tipo.valor(item).
        Quando NÃO usar: poucos objetos, ou objetos que mudam — o ganho de memória não paga a complexidade.
        """

        TIPOS = @@TIPOS@@  # chave → (nome, fator)


        class TipoCompartilhado:
            """FLYWEIGHT: estado intrínseco (nome, fator), compartilhado e IMUTÁVEL."""

            __slots__ = ("_nome", "_fator")  # sem __dict__: cada flyweight ocupa o mínimo

            def __init__(self, nome, fator):
                object.__setattr__(self, "_nome", nome)
                object.__setattr__(self, "_fator", fator)

            def __setattr__(self, campo, valor):
                raise AttributeError("flyweight é imutável: ele é compartilhado por todos")

            @property
            def nome(self):
                return self._nome

            @property
            def fator(self):
                return self._fator

            def valor(self, item):
                """Estado EXTRÍNSECO (o item) chega por parâmetro — o flyweight não guarda nada dele."""
                return round(item.total * self._fator, 2)


        class FabricaDeTipos:
            """Entrega flyweights: cria na primeira vez, depois devolve o MESMO objeto."""

            def __init__(self):
                self._cache = {}

            def obter(self, chave):
                if chave not in self._cache:
                    nome, fator = TIPOS[chave]  # KeyError se a chave não existir
                    self._cache[chave] = TipoCompartilhado(nome, fator)
                return self._cache[chave]

            def quantidade(self):
                """Quantos flyweights existem de verdade na memória."""
                return len(self._cache)


        class Registro:
            """Um lançamento: a @@ENT@@ (extrínseco) + uma REFERÊNCIA ao tipo compartilhado."""

            def __init__(self, item, tipo):
                self.item = item
                self.tipo = tipo

            def valor(self):
                return self.tipo.valor(self.item)
        ''', SISTEMA=s.sistema, CONCEITO=s.conceito, ENT=s.ent, TIPOS=tipos_literal(s))


def gerar_antes_tipos_compartilhados(s):
    return render(r'''
        """ANTES — o smell do Flyweight: um objeto de @@CONCEITO@@ NOVO para cada registro."""


        class TipoAntigo:
            def __init__(self, nome, fator):
                self.nome = nome
                self.fator = fator


        TIPOS_ANTIGOS = @@TIPOS@@


        def registrar_antigo(item, chave):
            nome, fator = TIPOS_ANTIGOS[chave]
            return item, TipoAntigo(nome, fator)  # cópia repetida a cada registro


        def valor_antigo(registro):
            item, tipo = registro
            return round(item.total * tipo.fator, 2)
        ''', CONCEITO=s.conceito, TIPOS=tipos_literal(s))


def gerar_test_tipos_compartilhados(s):
    return render(r'''
        """Testes do FLYWEIGHT: mesma chave → mesmo objeto; mil registros, poucos flyweights."""
        import pytest

        from nucleo.antes_tipos_compartilhados import registrar_antigo, valor_antigo
        from nucleo.tipos_compartilhados import TIPOS, FabricaDeTipos, Registro
        from tests.fabrica import itens_exemplo

        CHAVES = sorted(TIPOS)


        def test_mesma_chave_mesmo_objeto():
            fabrica = FabricaDeTipos()
            assert fabrica.obter(CHAVES[0]) is fabrica.obter(CHAVES[0])


        def test_mil_registros_poucos_flyweights():
            fabrica = FabricaDeTipos()
            itens = itens_exemplo()
            registros = [Registro(itens[i % 4], fabrica.obter(CHAVES[i % len(CHAVES)])) for i in range(1000)]
            assert len(registros) == 1000 and fabrica.quantidade() == len(CHAVES)


        def test_antes_cria_um_objeto_por_registro():
            item = itens_exemplo()[0]
            assert registrar_antigo(item, CHAVES[0])[1] is not registrar_antigo(item, CHAVES[0])[1]


        @pytest.mark.parametrize("chave", CHAVES)
        @pytest.mark.parametrize("indice", range(4))
        def test_mesmo_valor_que_a_versao_antiga(chave, indice):
            item = itens_exemplo()[indice]
            assert Registro(item, FabricaDeTipos().obter(chave)).valor() == valor_antigo(registrar_antigo(item, chave))


        def test_flyweight_e_imutavel():
            tipo = FabricaDeTipos().obter(CHAVES[0])
            with pytest.raises(AttributeError):
                tipo.fator = 0


        def test_chave_desconhecida():
            with pytest.raises(KeyError):
                FabricaDeTipos().obter("nao_existe")
        ''')


# ----------------------------------------------------------------- proxy
def gerar_acesso(s):
    return render(r'''
        """
        @@SISTEMA@@ — PROXY (GoF · estrutural): um SUBSTITUTO com a mesma interface que controla o acesso.

        ANTES (nucleo/antes_acesso.py): quem consulta faz o cache e confere a permissão na mão, misturado
        com a chamada — cada ponto de uso repete (ou esquece) essas regras.
        DEPOIS (aqui):
          * ConsultaDePreco é o objeto REAL (imagine que é lento: banco, rede);
          * ConsultaComCache (proxy de CACHE) guarda respostas e só chama o real na primeira vez;
          * ConsultaProtegida (proxy de PROTEÇÃO) só deixa passar perfis autorizados;
          * todos têm o MESMO método calcular(item) → quem usa não percebe (e os proxies empilham).
        Proxy × Decorator: os dois embrulham com a mesma interface; o Decorator ACRESCENTA comportamento,
        o Proxy CONTROLA o acesso ao objeto real (cache, permissão, criação tardia, chamada remota).
        """

        PERFIS_AUTORIZADOS = ("gerente", "atendente")


        class ConsultaDePreco:
            """SUJEITO REAL: o cálculo "caro" (conta quantas vezes foi chamado)."""

            def __init__(self):
                self.chamadas = 0

            def calcular(self, item):
                self.chamadas += 1
                return item.total


        class ConsultaComCache:
            """PROXY DE CACHE: mesma interface; só chama o real quando ainda não sabe a resposta."""

            def __init__(self, real):
                self._real = real
                self._cache = {}

            def calcular(self, item):
                chave = (item.@@IDENT@@, item.@@QTD@@, item.@@PRECO@@)  # tudo que muda o resultado
                if chave not in self._cache:
                    self._cache[chave] = self._real.calcular(item)
                return self._cache[chave]


        class ConsultaProtegida:
            """PROXY DE PROTEÇÃO: mesma interface; barra quem não tem permissão."""

            def __init__(self, real, perfil):
                self._real = real
                self.perfil = perfil

            def calcular(self, item):
                if self.perfil not in PERFIS_AUTORIZADOS:
                    raise PermissionError(f"perfil sem acesso: {self.perfil}")
                return self._real.calcular(item)
        ''', SISTEMA=s.sistema, IDENT=s.ident, QTD=s.qtd, PRECO=s.preco)


def gerar_antes_acesso(s):
    return render(r'''
        """ANTES — o smell do Proxy: cache e permissão feitos na mão por quem consulta."""

        CACHE = {}


        def consultar_antigo(consulta, item, perfil):
            if perfil not in ("gerente", "atendente"):
                raise PermissionError(f"perfil sem acesso: {perfil}")
            chave = (item.@@IDENT@@, item.@@QTD@@, item.@@PRECO@@)
            if chave not in CACHE:
                CACHE[chave] = consulta.calcular(item)
            return CACHE[chave]
        ''', IDENT=s.ident, QTD=s.qtd, PRECO=s.preco)


def gerar_test_acesso(s):
    return render(r'''
        """Testes do PROXY: cache transparente, proteção por perfil e proxies empilhados."""
        import pytest

        from nucleo import antes_acesso
        from nucleo.acesso import ConsultaComCache, ConsultaDePreco, ConsultaProtegida
        from tests.fabrica import criar, itens_exemplo


        def test_cache_chama_o_real_uma_vez_so():
            real = ConsultaDePreco()
            proxy = ConsultaComCache(real)
            item = criar()
            assert [proxy.calcular(item) for _ in range(5)] == [item.total] * 5
            assert real.chamadas == 1


        def test_cache_separa_itens_diferentes():
            real = ConsultaDePreco()
            proxy = ConsultaComCache(real)
            for item in itens_exemplo():
                proxy.calcular(item)
            assert real.chamadas == 4


        @pytest.mark.parametrize("perfil", ["gerente", "atendente"])
        def test_protecao_deixa_passar_quem_pode(perfil):
            item = criar()
            assert ConsultaProtegida(ConsultaDePreco(), perfil).calcular(item) == item.total


        def test_protecao_barra_quem_nao_pode():
            with pytest.raises(PermissionError):
                ConsultaProtegida(ConsultaDePreco(), "visitante").calcular(criar())


        def test_proxies_empilham_porque_tem_a_mesma_interface():
            real = ConsultaDePreco()
            consulta = ConsultaProtegida(ConsultaComCache(real), "gerente")
            item = criar()
            consulta.calcular(item)
            consulta.calcular(item)
            assert real.chamadas == 1


        def test_igual_a_versao_feita_na_mao():
            antes_acesso.CACHE.clear()
            item = criar()
            real_antigo, real_novo = ConsultaDePreco(), ConsultaDePreco()
            proxy = ConsultaProtegida(ConsultaComCache(real_novo), "gerente")
            for _ in range(3):
                assert proxy.calcular(item) == antes_acesso.consultar_antigo(real_antigo, item, "gerente")
            assert real_antigo.chamadas == real_novo.chamadas == 1
        ''')


# ----------------------------------------------------------------- chain of responsibility
def gerar_aprovacao(s):
    return render(r'''
        """
        @@SISTEMA@@ — CHAIN OF RESPONSIBILITY (GoF · comportamental): o pedido passa por uma CADEIA.

        ANTES (nucleo/antes_aprovacao.py): quem_aprova_antigo(item) com if/elif de alçadas — incluir um
        nível novo (ex.: supervisor) obriga a reescrever a função.
        DEPOIS (aqui):
          * cada Aprovador conhece só a SUA alçada e o PRÓXIMO da cadeia;
          * aprovar(item): se pode, responde; se não, repassa ao próximo; no fim, ninguém aprovou;
          * a cadeia é montada de fora (encadear) → incluir/remover um nível não mexe nos outros.
        Quando NÃO usar: regras fixas e poucas — um if/elif curto é mais simples de ler.
        """


        class Aprovador:
            """ELO da cadeia: decide se aprova; se não, repassa ao próximo."""

            nome = "aprovador"
            limite = 0.0

            def __init__(self):
                self.proximo = None

            def encadear(self, proximo):
                """Liga o próximo elo e o DEVOLVE (permite a.encadear(b).encadear(c))."""
                self.proximo = proximo
                return proximo

            def aprovar(self, item):
                if item.total <= self.limite:
                    return self.nome
                if self.proximo is None:
                    return "sem aprovador"  # fim da cadeia: ninguém tinha alçada
                return self.proximo.aprovar(item)


        class Atendente(Aprovador):
            nome, limite = "atendente", 500.0


        class Gerente(Aprovador):
            nome, limite = "gerente", 2000.0


        class Diretoria(Aprovador):
            nome, limite = "diretoria", 10000.0


        class Supervisor(Aprovador):
            """Nível NOVO: entra na cadeia sem mudar nenhum outro aprovador."""

            nome, limite = "supervisor", 1000.0


        def cadeia_padrao():
            """Monta atendente → gerente → diretoria e devolve o PRIMEIRO elo."""
            inicio = Atendente()
            inicio.encadear(Gerente()).encadear(Diretoria())
            return inicio
        ''', SISTEMA=s.sistema)


def gerar_antes_aprovacao(s):
    return render(r'''
        """ANTES — o smell do Chain of Responsibility: if/elif com todas as alçadas num lugar só."""


        def quem_aprova_antigo(item):
            if item.total <= 500.0:
                return "atendente"
            elif item.total <= 2000.0:
                return "gerente"
            elif item.total <= 10000.0:
                return "diretoria"
            else:
                return "sem aprovador"
        ''')


def gerar_test_aprovacao(s):
    return render(r'''
        """Testes do CHAIN OF RESPONSIBILITY: mesmo resultado do if/elif; nível novo sem mexer nos outros."""
        import pytest

        from nucleo.antes_aprovacao import quem_aprova_antigo
        from nucleo.aprovacao import Atendente, Diretoria, Gerente, Supervisor, cadeia_padrao
        from tests.fabrica import criar

        VALORES = [0.0, 100.0, 500.0, 500.01, 1500.0, 2000.0, 9999.99, 10000.0, 10000.01, 50000.0]


        def item_de(valor):
            return criar(@@QTD@@=1, @@PRECO@@=valor)


        @pytest.mark.parametrize("valor", VALORES)
        def test_cadeia_igual_ao_if_elif(valor):
            item = item_de(valor)
            assert cadeia_padrao().aprovar(item) == quem_aprova_antigo(item)


        @pytest.mark.parametrize("valor, esperado", [(100.0, "atendente"), (1500.0, "gerente"),
                                                     (5000.0, "diretoria"), (50000.0, "sem aprovador")])
        def test_cada_elo_aprova_a_sua_alcada(valor, esperado):
            assert cadeia_padrao().aprovar(item_de(valor)) == esperado


        def test_nivel_novo_entra_sem_mudar_os_outros():
            inicio = Atendente()
            inicio.encadear(Supervisor()).encadear(Gerente()).encadear(Diretoria())
            assert inicio.aprovar(item_de(800.0)) == "supervisor"
            assert inicio.aprovar(item_de(1500.0)) == "gerente"


        def test_elo_sozinho_sem_alcada_nao_aprova():
            assert Atendente().aprovar(item_de(600.0)) == "sem aprovador"


        def test_encadear_devolve_o_proximo():
            gerente = Gerente()
            assert Atendente().encadear(gerente) is gerente
        ''', QTD=s.qtd, PRECO=s.preco)


# ----------------------------------------------------------------- command
def gerar_comandos(s):
    return render(r'''
        """
        @@SISTEMA@@ — COMMAND (GoF · comportamental): cada AÇÃO vira um objeto (dá para desfazer e refazer).

        ANTES (nucleo/antes_comandos.py): alterar_antigo(item, campo, valor) muda o objeto direto — não
        sobra registro do valor anterior, então não há como desfazer.
        DEPOIS (aqui):
          * AlterarCampo guarda O QUE fazer (campo, valor novo) e lembra o valor ANTIGO para desfazer;
          * Historico (o INVOCADOR) executa comandos e os empilha: desfazer() e refazer() em ordem;
          * a @@ENT@@ (o RECEPTOR) não sabe nada de histórico — os setters continuam validando.
        Quando NÃO usar: ação simples que nunca será desfeita, enfileirada ou registrada.
        """


        class Comando:
            """Interface: todo comando sabe executar e desfazer."""

            def executar(self):
                raise NotImplementedError

            def desfazer(self):
                raise NotImplementedError


        class AlterarCampo(Comando):
            """Comando CONCRETO: troca um campo da @@ENT@@ e lembra o valor anterior."""

            def __init__(self, item, campo, valor):
                self.item = item
                self.campo = campo
                self.valor = valor
                self.anterior = None

            def executar(self):
                self.anterior = getattr(self.item, self.campo)
                setattr(self.item, self.campo, self.valor)  # o setter valida (pode levantar ValueError)

            def desfazer(self):
                setattr(self.item, self.campo, self.anterior)

            def __repr__(self):
                return f"AlterarCampo({self.campo}={self.valor!r})"


        class Historico:
            """INVOCADOR: executa, empilha e desfaz/refaz comandos."""

            def __init__(self):
                self._feitos = []
                self._desfeitos = []

            def executar(self, comando):
                comando.executar()  # se falhar (ValueError), nada entra no histórico
                self._feitos.append(comando)
                self._desfeitos.clear()  # ação nova apaga o que dava para refazer

            def desfazer(self):
                if not self._feitos:
                    return False
                comando = self._feitos.pop()
                comando.desfazer()
                self._desfeitos.append(comando)
                return True

            def refazer(self):
                if not self._desfeitos:
                    return False
                comando = self._desfeitos.pop()
                comando.executar()
                self._feitos.append(comando)
                return True

            def acoes(self):
                return [repr(comando) for comando in self._feitos]
        ''', SISTEMA=s.sistema, ENT=s.ent)


def gerar_antes_comandos(s):
    return render(r'''
        """ANTES — o smell do Command: a ação acontece direto e some (não dá para desfazer)."""


        def alterar_antigo(item, campo, valor):
            setattr(item, campo, valor)
        ''')


def gerar_test_comandos(s):
    return render(r'''
        """Testes do COMMAND: executar, desfazer e refazer em ordem; comando inválido não entra."""
        import pytest

        from nucleo.antes_comandos import alterar_antigo
        from nucleo.comandos import AlterarCampo, Historico
        from tests.fabrica import criar


        def test_executar_muda_o_campo():
            item = criar()
            Historico().executar(AlterarCampo(item, "@@QTD@@", item.@@QTD@@ + 1))
            assert item.@@QTD@@ == criar().@@QTD@@ + 1


        def test_mesmo_efeito_da_versao_antiga():
            a, b = criar(), criar()
            alterar_antigo(a, "@@QTD@@", a.@@QTD@@ + 2)
            Historico().executar(AlterarCampo(b, "@@QTD@@", b.@@QTD@@ + 2))
            assert vars(a) == vars(b)


        def test_desfazer_volta_ao_valor_anterior():
            item = criar()
            historico = Historico()
            historico.executar(AlterarCampo(item, "@@QTD@@", item.@@QTD@@ + 1))
            assert historico.desfazer() is True and vars(item) == vars(criar())


        def test_desfaz_na_ordem_inversa_e_refaz():
            item = criar()
            q0 = item.@@QTD@@
            historico = Historico()
            historico.executar(AlterarCampo(item, "@@QTD@@", q0 + 1))
            historico.executar(AlterarCampo(item, "@@QTD@@", q0 + 2))
            historico.desfazer()
            assert item.@@QTD@@ == q0 + 1
            historico.desfazer()
            assert item.@@QTD@@ == q0
            historico.refazer()
            assert item.@@QTD@@ == q0 + 1


        def test_comando_invalido_nao_entra_no_historico():
            item = criar()
            historico = Historico()
            with pytest.raises(ValueError):
                historico.executar(AlterarCampo(item, "@@QTD@@", 0))
            assert historico.acoes() == [] and historico.desfazer() is False


        def test_acao_nova_apaga_o_refazer():
            item = criar()
            historico = Historico()
            historico.executar(AlterarCampo(item, "@@QTD@@", item.@@QTD@@ + 1))
            historico.desfazer()
            historico.executar(AlterarCampo(item, "@@PRECO@@", item.@@PRECO@@ + 1))
            assert historico.refazer() is False
        ''', QTD=s.qtd, PRECO=s.preco)


# ----------------------------------------------------------------- interpreter
def gerar_regras(s):
    return render(r'''
        """
        @@SISTEMA@@ — INTERPRETER (GoF · comportamental): regras escritas numa MINI-LINGUAGEM.

        ANTES (nucleo/antes_regras.py): regra_antiga(item) com a condição fixa no código — toda mudança
        ("a partir de 3 @@UNIDADE@@") exige programar e publicar de novo.
        DEPOIS (aqui):
          * cada pedaço da gramática é uma classe com interpretar(item): Comparacao, E, Ou;
          * ler_regra("@@QTD@@ >= 3 e total > 500") monta a ÁRVORE dessas classes;
          * a regra vira DADO (texto): dá para guardar no banco e trocar sem mexer no código.
        Gramática:  regra := termo ("ou" termo)*      termo := comparacao ("e" comparacao)*
                    comparacao := CAMPO OPERADOR NUMERO   (CAMPO: @@QTD@@, @@PRECO@@ ou total)
        Quando NÃO usar: linguagem grande (use uma biblioteca de parsing) ou regra que nunca muda.
        Nunca use eval() no lugar disto: eval executa QUALQUER código.
        """
        import operator

        OPERADORES = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}
        CAMPOS = ("@@QTD@@", "@@PRECO@@", "total")


        class Comparacao:
            """Expressão TERMINAL: campo operador número (ex.: total > 500)."""

            def __init__(self, campo, simbolo, numero):
                if campo not in CAMPOS:
                    raise ValueError(f"campo desconhecido: {campo}")
                if simbolo not in OPERADORES:
                    raise ValueError(f"operador desconhecido: {simbolo}")
                self.campo, self.simbolo, self.numero = campo, simbolo, numero

            def interpretar(self, item):
                return OPERADORES[self.simbolo](getattr(item, self.campo), self.numero)


        class E:
            """Expressão NÃO TERMINAL: verdadeira se TODAS as partes forem."""

            def __init__(self, *partes):
                self.partes = partes

            def interpretar(self, item):
                return all(parte.interpretar(item) for parte in self.partes)


        class Ou:
            """Expressão NÃO TERMINAL: verdadeira se ALGUMA parte for."""

            def __init__(self, *partes):
                self.partes = partes

            def interpretar(self, item):
                return any(parte.interpretar(item) for parte in self.partes)


        def ler_comparacao(texto):
            partes = texto.split()
            if len(partes) != 3:
                raise ValueError(f"comparação mal escrita: {texto!r} (use: campo operador número)")
            campo, simbolo, numero = partes
            try:
                valor = float(numero)
            except ValueError:
                raise ValueError(f"número inválido: {numero!r}") from None
            return Comparacao(campo, simbolo, valor)


        def ler_regra(texto):
            """Transforma o TEXTO da regra na árvore de expressões ("e" vale antes de "ou")."""
            termos = []
            for termo in texto.strip().split(" ou "):
                termos.append(E(*[ler_comparacao(parte) for parte in termo.split(" e ")]))
            return Ou(*termos)
        ''', SISTEMA=s.sistema, UNIDADE=s.unidade, QTD=s.qtd, PRECO=s.preco)


def gerar_antes_regras(s):
    return render(r'''
        """ANTES — o smell do Interpreter: a regra está ESCRITA NO CÓDIGO (mudar = programar de novo)."""


        def regra_antiga(item):
            return item.@@QTD@@ >= 3 and item.total > 500 or item.@@PRECO@@ == 0
        ''', QTD=s.qtd, PRECO=s.preco)


def gerar_test_regras(s):
    return render(r'''
        """Testes do INTERPRETER: o texto interpretado = a regra no código; regra nova sem programar."""
        import pytest

        from nucleo.antes_regras import regra_antiga
        from nucleo.regras import E, Comparacao, Ou, ler_regra
        from tests.fabrica import criar, itens_exemplo

        REGRA = "@@QTD@@ >= 3 e total > 500 ou @@PRECO@@ == 0"


        @pytest.mark.parametrize("indice", range(4))
        def test_texto_interpretado_igual_a_regra_no_codigo(indice):
            item = itens_exemplo()[indice]
            assert ler_regra(REGRA).interpretar(item) == regra_antiga(item)


        @pytest.mark.parametrize("qtd, preco", [(1, 1000.0), (3, 100.0), (3, 300.0), (4, 0.0), (1, 0.0)])
        def test_casos_variados(qtd, preco):
            item = criar(@@QTD@@=qtd, @@PRECO@@=preco)
            assert ler_regra(REGRA).interpretar(item) == regra_antiga(item)


        def test_arvore_montada_a_mao_equivale_ao_texto():
            arvore = Ou(E(Comparacao("@@QTD@@", ">=", 3), Comparacao("total", ">", 500)),
                        E(Comparacao("@@PRECO@@", "==", 0)))
            for item in itens_exemplo():
                assert arvore.interpretar(item) == ler_regra(REGRA).interpretar(item)


        def test_regra_nova_sem_mudar_codigo():
            item = criar(@@QTD@@=2, @@PRECO@@=50.0)
            assert ler_regra("total <= 100").interpretar(item) is True
            assert ler_regra("@@QTD@@ > 2").interpretar(item) is False


        @pytest.mark.parametrize("ruim", ["total >", "campo_inexistente > 3", "total ~ 3", "total > muito"])
        def test_regra_mal_escrita_e_recusada(ruim):
            with pytest.raises(ValueError):
                ler_regra(ruim)
        ''', QTD=s.qtd, PRECO=s.preco)


# ----------------------------------------------------------------- iterator
def gerar_colecao(s):
    return render(r'''
        """
        @@SISTEMA@@ — ITERATOR (GoF · comportamental): percorrer a coleção sem conhecer o que tem dentro.

        ANTES (nucleo/antes_colecao.py): quem usava lia colecao._itens[i] com índice — dependia da lista
        interna; trocar a lista por dicionário quebraria todos os laços.
        DEPOIS (aqui):
          * Colecao@@ENT@@ guarda as @@ENT@@s do jeito que quiser (aqui: dicionário por @@IDENT@@);
          * __iter__ devolve um ITERADOR (IteradorDeItens, com __next__) → funciona com for, list() e sum();
          * percursos especiais (acima_de, ordenados_por_total) não expõem o interior.
        Quando NÃO usar: lista e dicionário já são iteráveis em Python; a classe de iterador só vale para
        percurso especial (filtrado, em ordem própria). Um gerador (yield) é o atalho pythônico.
        """


        class IteradorDeItens:
            """ITERADOR: guarda a POSIÇÃO do percurso (cada for ganha o seu)."""

            def __init__(self, itens):
                self._itens = itens
                self._posicao = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self._posicao >= len(self._itens):
                    raise StopIteration  # avisa o for que acabou
                item = self._itens[self._posicao]
                self._posicao += 1
                return item


        class Colecao@@ENT@@:
            """AGREGADO: guarda as @@ENT@@s por @@IDENT@@ (a estrutura interna é segredo dela)."""

            def __init__(self):
                self._por_chave = {}

            def adicionar(self, item):
                self._por_chave[item.@@IDENT@@] = item

            def __len__(self):
                return len(self._por_chave)

            def __iter__(self):
                """Percurso padrão: na ordem em que foram adicionadas."""
                return IteradorDeItens(list(self._por_chave.values()))

            def acima_de(self, valor):
                """Percurso FILTRADO: só os de total acima do valor (gerador = iterador pronto do Python)."""
                for item in self._por_chave.values():
                    if item.total > valor:
                        yield item

            def ordenados_por_total(self):
                """Percurso em OUTRA ORDEM, sem mudar a coleção."""
                return IteradorDeItens(sorted(self._por_chave.values(), key=lambda item: item.total))
        ''', SISTEMA=s.sistema, ENT=s.ent, IDENT=s.ident)


def gerar_antes_colecao(s):
    return render(r'''
        """ANTES — o smell do Iterator: quem usa conhece a LISTA interna e percorre por índice."""


        class ColecaoAntiga:
            def __init__(self):
                self._itens = []

            def adicionar(self, item):
                self._itens.append(item)


        def totais_antigo(colecao):
            totais = []
            i = 0
            while i < len(colecao._itens):  # depende do detalhe interno (_itens é uma lista)
                totais.append(colecao._itens[i].total)
                i += 1
            return totais
        ''')


def gerar_test_colecao(s):
    return render(r'''
        """Testes do ITERATOR: for/list/sum funcionam, percursos independentes, filtrado e ordenado."""
        import pytest

        from nucleo.antes_colecao import ColecaoAntiga, totais_antigo
        from nucleo.colecao import Colecao@@ENT@@, IteradorDeItens
        from tests.fabrica import itens_exemplo


        def cheia():
            colecao = Colecao@@ENT@@()
            for item in itens_exemplo():
                colecao.adicionar(item)
            return colecao


        def test_for_percorre_na_ordem_de_entrada():
            assert [item.@@IDENT@@ for item in cheia()] == [item.@@IDENT@@ for item in itens_exemplo()]


        def test_mesmos_totais_que_o_laco_por_indice():
            antiga = ColecaoAntiga()
            for item in itens_exemplo():
                antiga.adicionar(item)
            assert [item.total for item in cheia()] == totais_antigo(antiga)


        def test_iterador_avisa_o_fim():
            with pytest.raises(StopIteration):
                next(IteradorDeItens([]))


        def test_dois_percursos_independentes():
            colecao = cheia()
            a, b = iter(colecao), iter(colecao)
            next(a)
            assert next(b).@@IDENT@@ == itens_exemplo()[0].@@IDENT@@


        def test_percurso_filtrado():
            colecao = cheia()
            limite = sorted(item.total for item in colecao)[1]
            filtrados = list(colecao.acima_de(limite))
            assert all(item.total > limite for item in filtrados)
            assert len(filtrados) == sum(1 for item in colecao if item.total > limite)


        def test_percurso_ordenado_nao_muda_a_colecao():
            colecao = cheia()
            totais = [item.total for item in colecao.ordenados_por_total()]
            assert totais == sorted(totais)
            assert [item.@@IDENT@@ for item in colecao] == [item.@@IDENT@@ for item in itens_exemplo()]


        def test_funciona_com_as_funcoes_do_python():
            colecao = cheia()
            assert len(colecao) == 4
            assert round(sum(item.total for item in colecao), 2) == round(sum(i.total for i in itens_exemplo()), 2)
        ''', ENT=s.ent, IDENT=s.ident)


# ----------------------------------------------------------------- mediator
def fatores_literal(s):
    return "{" + ", ".join(f'"{x[3]}": {x[1]!r}' for x in s.variantes + [s.vnova]) + "}"


def gerar_mediador(s):
    return render(r'''
        """
        @@SISTEMA@@ — MEDIATOR (GoF · comportamental): os componentes conversam por um CENTRO, não entre si.

        ANTES (nucleo/antes_mediador.py): o campo de @@QTD@@ conhecia o resumo e o botão e mexia neles direto —
        cada componente novo obrigava a mexer nos outros (todos acoplados a todos).
        DEPOIS (aqui):
          * cada componente só conhece o MEDIADOR e avisa: mediador.notificar(self, evento);
          * FormularioMediador decide quem reage: recalcula o resumo e liga/desliga o botão;
          * componente novo conversa só com o mediador (N ligações em vez de N × N).
        Quando NÃO usar: 2–3 objetos que conversam pouco. Cuidado para o mediador não virar "objeto deus".
        """

        FATORES = @@FATORES@@  # @@CONCEITO@@ → fator


        class Componente:
            """Todo componente conhece SÓ o mediador."""

            def __init__(self, mediador):
                self.mediador = mediador


        class Campo@@QC@@(Componente):
            def __init__(self, mediador):
                super().__init__(mediador)
                self.valor = 1

            def digitar(self, valor):
                self.valor = valor
                self.mediador.notificar(self, "mudou")  # não sabe QUEM vai reagir


        class SeletorTipo(Componente):
            def __init__(self, mediador):
                super().__init__(mediador)
                self.valor = "@@T0@@"

            def escolher(self, chave):
                self.valor = chave
                self.mediador.notificar(self, "mudou")


        class Resumo(Componente):
            def __init__(self, mediador):
                super().__init__(mediador)
                self.texto = ""


        class BotaoConfirmar(Componente):
            def __init__(self, mediador):
                super().__init__(mediador)
                self.habilitado = False


        class FormularioMediador:
            """MEDIADOR: conhece todos os componentes e coordena as reações."""

            def __init__(self, preco):
                self.preco = preco
                self.quantidade = Campo@@QC@@(self)
                self.tipo = SeletorTipo(self)
                self.resumo = Resumo(self)
                self.botao = BotaoConfirmar(self)
                self.notificar(self.quantidade, "inicio")

            def notificar(self, origem, evento):
                valido = isinstance(self.quantidade.valor, int) and self.quantidade.valor >= 1
                if valido:
                    valor = round(self.quantidade.valor * self.preco * FATORES[self.tipo.valor], 2)
                    self.resumo.texto = f"{self.quantidade.valor} @@UNIDADE@@ · R$ {valor:.2f}"
                else:
                    self.resumo.texto = "@@QTD@@ inválido(a)"
                self.botao.habilitado = valido
        ''', SISTEMA=s.sistema, QTD=s.qtd, FATORES=fatores_literal(s), CONCEITO=s.conceito,
        QC=camel(s.qtd), T0=s.variantes[0][3], UNIDADE=s.unidade)


def gerar_antes_mediador(s):
    return render(r'''
        """ANTES — o smell do Mediator: cada componente conhece e altera os outros (todos acoplados)."""

        FATORES = @@FATORES@@


        class ResumoAntigo:
            def __init__(self):
                self.texto = ""


        class BotaoAntigo:
            def __init__(self):
                self.habilitado = False


        class SeletorAntigo:
            def __init__(self):
                self.valor = "@@T0@@"


        class CampoAntigo:
            def __init__(self, preco, seletor, resumo, botao):
                # o campo precisa conhecer TODOS os outros para atualizar a tela
                self.preco, self.seletor, self.resumo, self.botao = preco, seletor, resumo, botao
                self.valor = 1

            def digitar(self, valor):
                self.valor = valor
                if isinstance(valor, int) and valor >= 1:
                    total = round(valor * self.preco * FATORES[self.seletor.valor], 2)
                    self.resumo.texto = f"{valor} @@UNIDADE@@ · R$ {total:.2f}"
                    self.botao.habilitado = True
                else:
                    self.resumo.texto = "@@QTD@@ inválido(a)"
                    self.botao.habilitado = False
        ''', FATORES=fatores_literal(s), T0=s.variantes[0][3], UNIDADE=s.unidade, QTD=s.qtd)


def gerar_test_mediador(s):
    return render(r'''
        """Testes do MEDIATOR: o mediador coordena; os componentes só conhecem o mediador."""
        import pytest

        from nucleo.antes_mediador import BotaoAntigo, CampoAntigo, ResumoAntigo, SeletorAntigo
        from nucleo.mediador import FATORES, FormularioMediador
        from tests.fabrica import DADOS_EXEMPLO

        PRECO = DADOS_EXEMPLO[0]["@@PRECO@@"]


        def test_comeca_valido_com_um():
            form = FormularioMediador(PRECO)
            assert form.botao.habilitado and form.resumo.texto.startswith("1 ")


        @pytest.mark.parametrize("qtd", [1, 2, 3])
        def test_digitar_recalcula_o_resumo(qtd):
            form = FormularioMediador(PRECO)
            form.quantidade.digitar(qtd)
            assert form.resumo.texto.endswith(f"R$ {round(qtd * PRECO * FATORES['@@T0@@'], 2):.2f}")


        def test_valor_invalido_desliga_o_botao():
            form = FormularioMediador(PRECO)
            form.quantidade.digitar(0)
            assert not form.botao.habilitado and "inválido" in form.resumo.texto


        def test_trocar_o_tipo_aplica_o_fator():
            form = FormularioMediador(PRECO)
            form.quantidade.digitar(2)
            form.tipo.escolher("@@T1@@")
            assert form.resumo.texto.endswith(f"R$ {round(2 * PRECO * FATORES['@@T1@@'], 2):.2f}")


        def test_componentes_so_conhecem_o_mediador():
            form = FormularioMediador(PRECO)
            for componente in (form.quantidade, form.tipo, form.resumo, form.botao):
                ligados = [valor for valor in vars(componente).values() if hasattr(valor, "__dict__")]
                assert ligados == [form]


        @pytest.mark.parametrize("qtd", [0, 1, 3])
        def test_mesmo_resultado_da_versao_acoplada(qtd):
            seletor, resumo, botao = SeletorAntigo(), ResumoAntigo(), BotaoAntigo()
            CampoAntigo(PRECO, seletor, resumo, botao).digitar(qtd)
            form = FormularioMediador(PRECO)
            form.quantidade.digitar(qtd)
            assert (form.resumo.texto, form.botao.habilitado) == (resumo.texto, botao.habilitado)
        ''', PRECO=s.preco, T0=s.variantes[0][3], T1=s.variantes[1][3])


# ----------------------------------------------------------------- memento
def gerar_versoes(s):
    return render(r'''
        """
        @@SISTEMA@@ — MEMENTO (GoF · comportamental): guardar e restaurar o ESTADO sem expor o interior.

        ANTES (nucleo/antes_versoes.py): para "voltar atrás", quem usava copiava os campos internos (_x) na
        mão — dependia do interior da @@ENT@@ e esquecia campos novos.
        DEPOIS (aqui):
          * Editor@@ENT@@ (o ORIGINADOR) cria um Memento com o próprio estado e sabe restaurar a partir dele;
          * Memento é uma "caixa fechada": guarda uma CÓPIA do estado; só o originador abre;
          * HistoricoDeVersoes (o ZELADOR) só empilha mementos — nunca olha dentro.
        Memento × Command: o Command desfaz UMA ação (sabe o inverso dela); o Memento volta o ESTADO inteiro.
        Quando NÃO usar: estado enorme e muitas versões (memória) — guarde só as diferenças ou use Command.
        """
        import copy


        class Memento:
            """Caixa fechada com uma cópia do estado (o rótulo é público; o conteúdo, não)."""

            def __init__(self, estado, rotulo):
                self._estado = copy.deepcopy(estado)
                self.rotulo = rotulo


        class Editor@@ENT@@:
            """ORIGINADOR: edita a @@ENT@@ e sabe salvar/restaurar o próprio estado."""

            def __init__(self, item):
                self.item = item

            def alterar(self, campo, valor):
                setattr(self.item, campo, valor)  # continua passando pelo setter (validado)

            def salvar(self, rotulo=""):
                return Memento(vars(self.item), rotulo)

            def restaurar(self, memento):
                # O estado guardado já foi válido: volta inteiro (cópia, para o memento seguir intacto).
                self.item.__dict__.update(copy.deepcopy(memento._estado))


        class HistoricoDeVersoes:
            """ZELADOR: guarda os mementos em ordem; não sabe o que tem dentro deles."""

            def __init__(self):
                self._versoes = []

            def guardar(self, memento):
                self._versoes.append(memento)

            def ultima(self):
                return self._versoes.pop() if self._versoes else None

            def rotulos(self):
                return [memento.rotulo for memento in self._versoes]
        ''', SISTEMA=s.sistema, ENT=s.ent)


def gerar_antes_versoes(s):
    campos = ", ".join((f'"_{a["nome"]}": item._{a["nome"]}' if a["regra"] != "livre"
                        else f'"{a["nome"]}": item.{a["nome"]}') for a in s.atributos)
    return render(r'''
        """ANTES — o smell do Memento: copiar o interior (_campos) na mão para poder voltar atrás."""


        def salvar_antigo(item):
            return {@@CAMPOS@@}


        def restaurar_antigo(item, copia):
            for campo, valor in copia.items():
                setattr(item, campo, valor)
        ''', CAMPOS=campos)


def gerar_test_versoes(s):
    return render(r'''
        """Testes do MEMENTO: salvar, restaurar várias versões e não expor o interior."""
        import pytest

        from nucleo.antes_versoes import restaurar_antigo, salvar_antigo
        from nucleo.versoes import Editor@@ENT@@, HistoricoDeVersoes
        from tests.fabrica import criar


        def test_restaurar_volta_ao_estado_salvo():
            item = criar()
            editor = Editor@@ENT@@(item)
            versao = editor.salvar("original")
            editor.alterar("@@QTD@@", item.@@QTD@@ + 1)
            editor.restaurar(versao)
            assert vars(item) == vars(criar())


        def test_memento_e_uma_copia():
            item = criar()
            versao = Editor@@ENT@@(item).salvar()
            item.@@QTD@@ = item.@@QTD@@ + 1
            assert versao._estado != vars(item)


        def test_historico_volta_varias_versoes():
            item = criar()
            editor, historico = Editor@@ENT@@(item), HistoricoDeVersoes()
            q0 = item.@@QTD@@
            for passo in (1, 2):
                historico.guardar(editor.salvar(f"antes do passo {passo}"))
                editor.alterar("@@QTD@@", q0 + passo)
            assert historico.rotulos() == ["antes do passo 1", "antes do passo 2"]
            editor.restaurar(historico.ultima())
            assert item.@@QTD@@ == q0 + 1
            editor.restaurar(historico.ultima())
            assert item.@@QTD@@ == q0
            assert historico.ultima() is None


        def test_alteracao_invalida_continua_barrada():
            with pytest.raises(ValueError):
                Editor@@ENT@@(criar()).alterar("@@QTD@@", 0)


        def test_mesmo_resultado_da_copia_na_mao():
            a, b = criar(), criar()
            copia = salvar_antigo(a)
            versao = Editor@@ENT@@(b).salvar()
            a.@@QTD@@ = a.@@QTD@@ + 1
            b.@@QTD@@ = b.@@QTD@@ + 1
            restaurar_antigo(a, copia)
            Editor@@ENT@@(b).restaurar(versao)
            assert vars(a) == vars(b)
        ''', ENT=s.ent, QTD=s.qtd)


# ----------------------------------------------------------------- observer
def gerar_eventos(s):
    return render(r'''
        """
        @@SISTEMA@@ — OBSERVER (GoF · comportamental): quem se INSCREVE é avisado quando algo muda.

        ANTES (nucleo/antes_eventos.py): alterar_antigo(...) chamava, um por um, o painel e o log — cada
        interessado novo obrigava a editar a função (e ela conhecia todos).
        DEPOIS (aqui):
          * @@ENT@@Observavel (o SUJEITO) guarda a lista de observadores e avisa todos: notificar(evento);
          * cada observador implementa atualizar(evento) e decide o que fazer;
          * interessado novo = inscrever(obj) — o sujeito não muda.
        Quando NÃO usar: um único interessado, fixo — chame-o direto. Cadeias de observadores escondem o fluxo.
        """


        class @@ENT@@Observavel:
            """SUJEITO: embrulha a @@ENT@@ e avisa os inscritos a cada mudança."""

            def __init__(self, item):
                self.item = item
                self._observadores = []

            def inscrever(self, observador):
                self._observadores.append(observador)

            def cancelar(self, observador):
                self._observadores.remove(observador)

            def alterar(self, campo, valor):
                anterior = self.item.total
                setattr(self.item, campo, valor)  # o setter valida ANTES de avisar alguém
                self.notificar({"campo": campo, "valor": valor, "total_anterior": anterior, "total": self.item.total})

            def notificar(self, evento):
                for observador in list(self._observadores):  # cópia: alguém pode se cancelar no meio
                    observador.atualizar(evento)


        class PainelObservador:
            """Mostra sempre o total mais recente."""

            def __init__(self):
                self.total = None

            def atualizar(self, evento):
                self.total = evento["total"]


        class LogObservador:
            """Registra cada mudança em texto."""

            def __init__(self):
                self.linhas = []

            def atualizar(self, evento):
                self.linhas.append(f"{evento['campo']} -> {evento['valor']} (total R$ {evento['total']:.2f})")


        class AlertaObservador:
            """Observador NOVO: alerta quando o total passa do limite (o sujeito não mudou)."""

            def __init__(self, limite):
                self.limite = limite
                self.alertas = []

            def atualizar(self, evento):
                if evento["total"] > self.limite >= evento["total_anterior"]:
                    self.alertas.append(f"total passou de R$ {self.limite:.2f}")
        ''', SISTEMA=s.sistema, ENT=s.ent)


def gerar_antes_eventos(s):
    return render(r'''
        """ANTES — o smell do Observer: quem altera chama cada interessado na mão (conhece todos)."""


        def alterar_antigo(item, campo, valor, painel, log):
            setattr(item, campo, valor)
            painel["total"] = item.total
            log.append(f"{campo} -> {valor} (total R$ {item.total:.2f})")
        ''')


def gerar_test_eventos(s):
    return render(r'''
        """Testes do OBSERVER: todos os inscritos são avisados; cancelar funciona; inválido não avisa."""
        import pytest

        from nucleo.antes_eventos import alterar_antigo
        from nucleo.eventos import AlertaObservador, LogObservador, PainelObservador, @@ENT@@Observavel
        from tests.fabrica import criar


        def test_todos_os_inscritos_sao_avisados():
            sujeito = @@ENT@@Observavel(criar())
            painel, log = PainelObservador(), LogObservador()
            sujeito.inscrever(painel)
            sujeito.inscrever(log)
            sujeito.alterar("@@QTD@@", 3)
            assert painel.total == sujeito.item.total and len(log.linhas) == 1


        def test_cancelado_nao_recebe_mais():
            sujeito = @@ENT@@Observavel(criar())
            log = LogObservador()
            sujeito.inscrever(log)
            sujeito.alterar("@@QTD@@", 3)
            sujeito.cancelar(log)
            sujeito.alterar("@@QTD@@", 4)
            assert len(log.linhas) == 1


        def test_alteracao_invalida_nao_avisa_ninguem():
            sujeito = @@ENT@@Observavel(criar())
            log = LogObservador()
            sujeito.inscrever(log)
            with pytest.raises(ValueError):
                sujeito.alterar("@@QTD@@", 0)
            assert log.linhas == []


        def test_observador_novo_sem_mudar_o_sujeito():
            sujeito = @@ENT@@Observavel(criar(@@QTD@@=1))
            limite = sujeito.item.total + 0.01
            alerta = AlertaObservador(limite)
            sujeito.inscrever(alerta)
            sujeito.alterar("@@QTD@@", 2)
            assert alerta.alertas == [f"total passou de R$ {limite:.2f}"]


        def test_mesmo_efeito_da_versao_antiga():
            a, b = criar(), criar()
            painel_antigo, log_antigo = {}, []
            alterar_antigo(a, "@@QTD@@", 3, painel_antigo, log_antigo)
            sujeito = @@ENT@@Observavel(b)
            painel, log = PainelObservador(), LogObservador()
            sujeito.inscrever(painel)
            sujeito.inscrever(log)
            sujeito.alterar("@@QTD@@", 3)
            assert (painel.total, log.linhas) == (painel_antigo["total"], log_antigo)
        ''', ENT=s.ent, QTD=s.qtd)


# ----------------------------------------------------------------- state
def gerar_situacao(s):
    return render(r'''
        """
        @@SISTEMA@@ — STATE (GoF · comportamental): o comportamento muda conforme o ESTADO do objeto.

        ANTES (nucleo/antes_situacao.py): cada método tinha um if/elif sobre self.status ("aberto",
        "confirmado"...) — a mesma escada repetida em confirmar, concluir e cancelar.
        DEPOIS (aqui):
          * cada estado é uma classe (Aberto, Confirmado, Concluido, Cancelado) que sabe as SUAS transições;
          * Situacao@@ENT@@ (o CONTEXTO) guarda o estado atual e DELEGA: self.estado.confirmar(self);
          * transição proibida levanta TransicaoInvalida; estado novo = classe nova.
        State × Strategy: mesma estrutura (contexto delega a um objeto); no State o PRÓPRIO estado troca o
        objeto do contexto (Aberto → Confirmado); no Strategy quem escolhe é o cliente.
        Quando NÃO usar: 2 estados e uma regra (um booleano basta).
        """


        class TransicaoInvalida(Exception):
            """Ação que não faz sentido no estado atual."""


        class Estado:
            """Estado BASE: por padrão, nenhuma ação é permitida."""

            nome = "?"

            def confirmar(self, contexto):
                raise TransicaoInvalida(f"não dá para confirmar: está {self.nome}")

            def concluir(self, contexto):
                raise TransicaoInvalida(f"não dá para concluir: está {self.nome}")

            def cancelar(self, contexto):
                raise TransicaoInvalida(f"não dá para cancelar: está {self.nome}")


        class Aberto(Estado):
            nome = "aberto"

            def confirmar(self, contexto):
                contexto.estado = Confirmado()

            def cancelar(self, contexto):
                contexto.estado = Cancelado()


        class Confirmado(Estado):
            nome = "confirmado"

            def concluir(self, contexto):
                contexto.estado = Concluido()

            def cancelar(self, contexto):
                contexto.estado = Cancelado()


        class Concluido(Estado):
            nome = "concluido"


        class Cancelado(Estado):
            nome = "cancelado"


        class Situacao@@ENT@@:
            """CONTEXTO: a @@ENT@@ + o estado atual. As ações são DELEGADAS ao estado."""

            def __init__(self, item):
                self.item = item
                self.estado = Aberto()

            @property
            def status(self):
                return self.estado.nome

            def confirmar(self):
                self.estado.confirmar(self)

            def concluir(self):
                self.estado.concluir(self)

            def cancelar(self):
                self.estado.cancelar(self)
        ''', SISTEMA=s.sistema, ENT=s.ent)


def gerar_antes_situacao(s):
    return render(r'''
        """ANTES — o smell do State: a mesma escada de if/elif sobre o status em CADA método."""


        class SituacaoAntiga:
            def __init__(self, item):
                self.item = item
                self.status = "aberto"

            def confirmar(self):
                if self.status == "aberto":
                    self.status = "confirmado"
                else:
                    raise ValueError(f"não dá para confirmar: está {self.status}")

            def concluir(self):
                if self.status == "confirmado":
                    self.status = "concluido"
                else:
                    raise ValueError(f"não dá para concluir: está {self.status}")

            def cancelar(self):
                if self.status in ("aberto", "confirmado"):
                    self.status = "cancelado"
                else:
                    raise ValueError(f"não dá para cancelar: está {self.status}")
        ''')


def gerar_test_situacao(s):
    return render(r'''
        """Testes do STATE: mesmo comportamento da escada de ifs; transições proibidas; estado novo."""
        import pytest

        from nucleo.antes_situacao import SituacaoAntiga
        from nucleo.situacao import Confirmado, Estado, Situacao@@ENT@@, TransicaoInvalida
        from tests.fabrica import criar

        SEQUENCIAS = [[], ["confirmar"], ["confirmar", "concluir"], ["cancelar"], ["confirmar", "cancelar"],
                      ["concluir"], ["confirmar", "concluir", "cancelar"], ["cancelar", "confirmar"]]


        def aplicar(situacao, acoes):
            for acao in acoes:
                try:
                    getattr(situacao, acao)()
                except (TransicaoInvalida, ValueError):
                    return f"erro em {acao}"
            return situacao.status


        @pytest.mark.parametrize("acoes", SEQUENCIAS)
        def test_mesmo_comportamento_da_escada_de_ifs(acoes):
            assert aplicar(Situacao@@ENT@@(criar()), acoes) == aplicar(SituacaoAntiga(criar()), acoes)


        def test_fluxo_feliz():
            situacao = Situacao@@ENT@@(criar())
            situacao.confirmar()
            situacao.concluir()
            assert situacao.status == "concluido"


        @pytest.mark.parametrize("acoes, proibida", [([], "concluir"), (["confirmar", "concluir"], "cancelar"),
                                                     (["cancelar"], "confirmar")])
        def test_transicao_proibida(acoes, proibida):
            situacao = Situacao@@ENT@@(criar())
            for acao in acoes:
                getattr(situacao, acao)()
            with pytest.raises(TransicaoInvalida):
                getattr(situacao, proibida)()


        def test_estado_novo_sem_mudar_o_contexto():
            class EmEspera(Estado):
                nome = "em espera"

                def confirmar(self, contexto):
                    contexto.estado = Confirmado()

            situacao = Situacao@@ENT@@(criar())
            situacao.estado = EmEspera()
            situacao.confirmar()
            assert situacao.status == "confirmado"
        ''', ENT=s.ent)


# ----------------------------------------------------------------- template method
def gerar_fechamento(s):
    nome, fator, cls, _ = s.variante_template()
    return render(r'''
        """
        @@SISTEMA@@ — TEMPLATE METHOD (GoF · comportamental): o ROTEIRO é fixo; só alguns passos mudam.

        ANTES (nucleo/antes_fechamento.py): fechar_padrao_antigo e fechar_com_taxa_antigo eram cópias quase
        iguais do mesmo roteiro (validar → calcular → ajustar → formatar) — corrigir um passo exigia lembrar
        de corrigir em todas as cópias.
        DEPOIS (aqui):
          * Fechamento.fechar(item) é o MÉTODO TEMPLATE: define a ORDEM dos passos e não é sobrescrito;
          * os passos que variam (ajustar) são sobrescritos pelas subclasses; o GANCHO tem padrão vazio;
          * fechamento novo = subclasse que muda só o passo dela.
        Template Method × Strategy: aqui a variação vem por HERANÇA (subclasse); no Strategy, por
        COMPOSIÇÃO (objeto injetado). Quando NÃO usar: só um passo varia → passe uma função (Strategy).
        """


        class Fechamento:
            """CLASSE ABSTRATA com o método template fechar()."""

            def fechar(self, item):
                """MÉTODO TEMPLATE: a ordem dos passos é sempre a mesma."""
                self.validar(item)
                valor = self.calcular(item)
                valor = self.ajustar(valor)
                return self.formatar(valor)

            def validar(self, item):
                if item.total < 0:
                    raise ValueError("total negativo")

            def calcular(self, item):
                return item.total

            def ajustar(self, valor):
                """GANCHO: por padrão não muda nada."""
                return valor

            def formatar(self, valor):
                return f"R$ {valor:.2f}"


        class FechamentoPadrao(Fechamento):
            """Usa o roteiro sem mudar nenhum passo."""


        class FechamentoComTaxa(Fechamento):
            TAXA = 0.1

            def ajustar(self, valor):
                return round(valor * (1 + self.TAXA), 2)


        class Fechamento@@VC@@(Fechamento):
            """Fechamento NOVO (@@VN@@): só o passo ajustar muda."""

            def ajustar(self, valor):
                return round(valor * @@VF@@, 2)
        ''', SISTEMA=s.sistema, VC=cls, VN=nome, VF=lit(fator))


def gerar_antes_fechamento(s):
    return render(r'''
        """ANTES — o smell do Template Method: o mesmo roteiro COPIADO em cada variação."""


        def fechar_padrao_antigo(item):
            if item.total < 0:
                raise ValueError("total negativo")
            valor = item.total
            return f"R$ {valor:.2f}"


        def fechar_com_taxa_antigo(item):
            if item.total < 0:
                raise ValueError("total negativo")
            valor = item.total
            valor = round(valor * 1.1, 2)
            return f"R$ {valor:.2f}"
        ''')


def gerar_test_fechamento(s):
    _, fator, cls, _ = s.variante_template()
    return render(r'''
        """Testes do TEMPLATE METHOD: mesmo resultado das cópias; ordem fixa; subclasse muda um passo."""
        import pytest

        from nucleo.antes_fechamento import fechar_com_taxa_antigo, fechar_padrao_antigo
        from nucleo.fechamento import Fechamento, Fechamento@@VC@@, FechamentoComTaxa, FechamentoPadrao
        from tests.fabrica import itens_exemplo


        @pytest.mark.parametrize("indice", range(4))
        def test_mesmo_resultado_das_copias_antigas(indice):
            item = itens_exemplo()[indice]
            assert FechamentoPadrao().fechar(item) == fechar_padrao_antigo(item)
            assert FechamentoComTaxa().fechar(item) == fechar_com_taxa_antigo(item)


        def test_a_ordem_dos_passos_e_fixa():
            chamadas = []

            class Espiao(Fechamento):
                def validar(self, item):
                    chamadas.append("validar")

                def calcular(self, item):
                    chamadas.append("calcular")
                    return 10.0

                def ajustar(self, valor):
                    chamadas.append("ajustar")
                    return valor

                def formatar(self, valor):
                    chamadas.append("formatar")
                    return str(valor)

            Espiao().fechar(itens_exemplo()[0])
            assert chamadas == ["validar", "calcular", "ajustar", "formatar"]


        def test_gancho_padrao_nao_muda_o_valor():
            assert Fechamento().ajustar(123.45) == 123.45


        def test_subclasse_nova_muda_so_um_passo():
            item = itens_exemplo()[0]
            assert Fechamento@@VC@@().fechar(item) == f"R$ {round(item.total * @@VF@@, 2):.2f}"


        def test_subclasses_nao_sobrescrevem_o_template():
            for classe in (FechamentoPadrao, FechamentoComTaxa, Fechamento@@VC@@):
                assert "fechar" not in vars(classe)
        ''', VC=cls, VF=lit(fator))


# ----------------------------------------------------------------- visitor
def gerar_orcamento(s):
    return render(r'''
        """
        @@SISTEMA@@ — VISITOR (GoF · comportamental): operações NOVAS sobre uma estrutura, sem mexer nela.

        ANTES (nucleo/antes_orcamento.py): total_antigo e texto_antigo percorriam as linhas perguntando o
        tipo — cada operação nova repetia a escada; cada tipo de linha novo mexia em todas.
        DEPOIS (aqui):
          * cada tipo de linha tem aceitar(visitante) e chama o método CERTO do visitante (despacho duplo);
          * cada OPERAÇÃO é um visitante (CalculoDoTotal, TextoDoOrcamento) com um visitar_* por tipo;
          * operação nova = visitante novo (ContagemPorTipo) — as linhas não mudam.
        Quando NÃO usar: se os TIPOS de elemento mudam muito (cada tipo novo obriga a mexer em todos os
        visitantes) — aí prefira polimorfismo comum (um método em cada classe).
        """


        class Linha@@ENT@@:
            def __init__(self, item):
                self.item = item

            def aceitar(self, visitante):
                return visitante.visitar_@@EV@@(self)


        class LinhaExtra:
            def __init__(self, descricao, valor):
                self.descricao = descricao
                self.valor = valor

            def aceitar(self, visitante):
                return visitante.visitar_extra(self)


        class LinhaDesconto:
            def __init__(self, valor):
                self.valor = valor  # valor positivo que será SUBTRAÍDO

            def aceitar(self, visitante):
                return visitante.visitar_desconto(self)


        class Orcamento:
            """ESTRUTURA: guarda as linhas e deixa um visitante passar por todas."""

            def __init__(self, linhas):
                self.linhas = list(linhas)

            def aceitar(self, visitante):
                for linha in self.linhas:
                    linha.aceitar(visitante)
                return visitante.resultado()


        class CalculoDoTotal:
            """Visitante 1: soma o orçamento."""

            def __init__(self):
                self.total = 0.0

            def visitar_@@EV@@(self, linha):
                self.total += linha.item.total

            def visitar_extra(self, linha):
                self.total += linha.valor

            def visitar_desconto(self, linha):
                self.total -= linha.valor

            def resultado(self):
                return round(self.total, 2)


        class TextoDoOrcamento:
            """Visitante 2: descreve cada linha."""

            def __init__(self):
                self.linhas = []

            def visitar_@@EV@@(self, linha):
                self.linhas.append(f"{linha.item.@@IDENT@@}: R$ {linha.item.total:.2f}")

            def visitar_extra(self, linha):
                self.linhas.append(f"+ {linha.descricao}: R$ {linha.valor:.2f}")

            def visitar_desconto(self, linha):
                self.linhas.append(f"- desconto: R$ {linha.valor:.2f}")

            def resultado(self):
                return "\n".join(self.linhas)


        class ContagemPorTipo:
            """Visitante NOVO: entrou sem mudar nenhuma linha."""

            def __init__(self):
                self.contagem = {"@@EV@@": 0, "extra": 0, "desconto": 0}

            def visitar_@@EV@@(self, linha):
                self.contagem["@@EV@@"] += 1

            def visitar_extra(self, linha):
                self.contagem["extra"] += 1

            def visitar_desconto(self, linha):
                self.contagem["desconto"] += 1

            def resultado(self):
                return dict(self.contagem)
        ''', SISTEMA=s.sistema, ENT=s.ent, EV=s.ent_var, IDENT=s.ident)


def gerar_antes_orcamento(s):
    return render(r'''
        """ANTES — o smell do Visitor: cada operação percorre as linhas perguntando o TIPO (if/elif)."""


        def total_antigo(linhas):
            total = 0.0
            for linha in linhas:
                if linha[0] == "@@EV@@":
                    total += linha[1].total
                elif linha[0] == "extra":
                    total += linha[2]
                elif linha[0] == "desconto":
                    total -= linha[1]
            return round(total, 2)


        def texto_antigo(linhas):
            partes = []
            for linha in linhas:
                if linha[0] == "@@EV@@":
                    partes.append(f"{linha[1].@@IDENT@@}: R$ {linha[1].total:.2f}")
                elif linha[0] == "extra":
                    partes.append(f"+ {linha[1]}: R$ {linha[2]:.2f}")
                elif linha[0] == "desconto":
                    partes.append(f"- desconto: R$ {linha[1]:.2f}")
            return "\n".join(partes)
        ''', EV=s.ent_var, IDENT=s.ident)


def gerar_test_orcamento(s):
    extras = "[" + ", ".join(f'("{x[2]}", {x[1]!r})' for x in s.extras[:2]) + "]"
    return render(r'''
        """Testes do VISITOR: mesmas operações da versão com if; operação nova sem mexer nas linhas."""
        from nucleo.antes_orcamento import texto_antigo, total_antigo
        from nucleo.orcamento import (CalculoDoTotal, ContagemPorTipo, Linha@@ENT@@, LinhaDesconto, LinhaExtra, Orcamento,
                                      TextoDoOrcamento)
        from tests.fabrica import itens_exemplo

        EXTRAS = @@EXTRAS@@  # (descrição, valor)


        def montar():
            a, b, _, _ = itens_exemplo()
            linhas = [Linha@@ENT@@(a), Linha@@ENT@@(b), LinhaExtra(*EXTRAS[0]), LinhaExtra(*EXTRAS[1]), LinhaDesconto(5.0)]
            tuplas = [("@@EV@@", a), ("@@EV@@", b), ("extra", *EXTRAS[0]), ("extra", *EXTRAS[1]), ("desconto", 5.0)]
            return Orcamento(linhas), tuplas


        def test_total_igual_a_versao_com_if():
            orcamento, tuplas = montar()
            assert orcamento.aceitar(CalculoDoTotal()) == total_antigo(tuplas)


        def test_texto_igual_a_versao_com_if():
            orcamento, tuplas = montar()
            assert orcamento.aceitar(TextoDoOrcamento()) == texto_antigo(tuplas)


        def test_operacao_nova_sem_mudar_as_linhas():
            orcamento, _ = montar()
            assert orcamento.aceitar(ContagemPorTipo()) == {"@@EV@@": 2, "extra": 2, "desconto": 1}


        def test_despacho_duplo_chama_o_metodo_do_tipo():
            chamadas = []

            class Espiao:
                def visitar_@@EV@@(self, linha):
                    chamadas.append("@@EV@@")

                def visitar_extra(self, linha):
                    chamadas.append("extra")

                def visitar_desconto(self, linha):
                    chamadas.append("desconto")

                def resultado(self):
                    return chamadas

            orcamento, _ = montar()
            assert orcamento.aceitar(Espiao()) == ["@@EV@@", "@@EV@@", "extra", "extra", "desconto"]


        def test_orcamento_vazio():
            assert Orcamento([]).aceitar(CalculoDoTotal()) == 0
        ''', ENT=s.ent, EV=s.ent_var, EXTRAS=extras)


GERADORES = {
    "polimorfismo": [("nucleo/categorias.py", gerar_categorias), ("nucleo/antes_categorias.py", gerar_antes_categorias),
                     ("tests/test_categorias.py", gerar_test_categorias)],
    "strategy": [("nucleo/politicas.py", gerar_politicas), ("nucleo/antes_politicas.py", gerar_antes_politicas),
                 ("tests/test_politicas.py", gerar_test_politicas)],
    "srp": [("nucleo/recibo.py", gerar_recibo), ("nucleo/antes_recibo.py", gerar_antes_recibo),
            ("tests/test_recibo.py", gerar_test_recibo)],
    "service": [("nucleo/relatorio.py", gerar_relatorio), ("nucleo/antes_relatorio.py", gerar_antes_relatorio),
                ("tests/test_relatorio.py", gerar_test_relatorio)],
    "mvvm": [("nucleo/painel.py", gerar_painel), ("nucleo/antes_painel.py", gerar_antes_painel),
             ("tests/test_painel.py", gerar_test_painel)],
    "adapter": [("nucleo/integracao.py", gerar_integracao), ("nucleo/integracao_base.py", gerar_integracao_base),
                ("nucleo/antes_integracao.py", gerar_antes_integracao), ("tests/test_integracao.py", gerar_test_integracao)],
    "facade": [("nucleo/atendimento.py", gerar_atendimento), ("nucleo/atendimento_base.py", gerar_atendimento_base),
               ("nucleo/antes_atendimento.py", gerar_antes_atendimento), ("tests/test_atendimento.py", gerar_test_atendimento)],
    "decorator": [("nucleo/extras.py", gerar_extras), ("nucleo/antes_extras.py", gerar_antes_extras),
                  ("tests/test_extras.py", gerar_test_extras)],
}

LIGACOES = {
    "encapsulamento": "`tests/fabrica.py` cria `@@ENT@@` válidas (`nucleo/entidades.py`) para TODOS os testes",
    "polimorfismo": "`nucleo/categorias.py` é independente da entidade (só herança + sobrescrita)",
    "strategy": "`nucleo/politicas.py` → `Cobranca` usa `item.total` da `@@ENT@@`",
    "srp": "`nucleo/recibo.py` → `ReciboFormatter` lê a `@@ENT@@`; `nucleo/antes_recibo.py` herda dela",
    "service": "`nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)",
    "mvvm": "`nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict",
    "adapter": "`nucleo/integracao.py` → `@@GW@@Adapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`",
    "facade": "`nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`",
    "decorator": "`nucleo/extras.py` → `@@ENT@@Base` embrulha a `@@ENT@@`; os `Com…` embrulham o componente",
}

# Os GoF novos seguem o mesmo trio: módulo aplicado + antes_*.py + testes.
_NOVOS_GOF = {
    "singleton": ("configuracao", gerar_configuracao, gerar_antes_configuracao, gerar_test_configuracao),
    "factory_method": ("avisos", gerar_avisos, gerar_antes_avisos, gerar_test_avisos),
    "abstract_factory": ("kits", gerar_kits, gerar_antes_kits, gerar_test_kits),
    "builder": ("construtor", gerar_construtor, gerar_antes_construtor, gerar_test_construtor),
    "prototype": ("prototipos", gerar_prototipos, gerar_antes_prototipos, gerar_test_prototipos),
    "bridge": ("comprovantes", gerar_comprovantes, gerar_antes_comprovantes, gerar_test_comprovantes),
    "composite": ("pacotes", gerar_pacotes, gerar_antes_pacotes, gerar_test_pacotes),
    "flyweight": ("tipos_compartilhados", gerar_tipos_compartilhados, gerar_antes_tipos_compartilhados,
                  gerar_test_tipos_compartilhados),
    "proxy": ("acesso", gerar_acesso, gerar_antes_acesso, gerar_test_acesso),
    "chain": ("aprovacao", gerar_aprovacao, gerar_antes_aprovacao, gerar_test_aprovacao),
    "command": ("comandos", gerar_comandos, gerar_antes_comandos, gerar_test_comandos),
    "interpreter": ("regras", gerar_regras, gerar_antes_regras, gerar_test_regras),
    "iterator": ("colecao", gerar_colecao, gerar_antes_colecao, gerar_test_colecao),
    "mediator": ("mediador", gerar_mediador, gerar_antes_mediador, gerar_test_mediador),
    "memento": ("versoes", gerar_versoes, gerar_antes_versoes, gerar_test_versoes),
    "observer": ("eventos", gerar_eventos, gerar_antes_eventos, gerar_test_eventos),
    "state": ("situacao", gerar_situacao, gerar_antes_situacao, gerar_test_situacao),
    "template_method": ("fechamento", gerar_fechamento, gerar_antes_fechamento, gerar_test_fechamento),
    "visitor": ("orcamento", gerar_orcamento, gerar_antes_orcamento, gerar_test_orcamento),
}
for _p, (_mod, _g, _ga, _gt) in _NOVOS_GOF.items():
    GERADORES[_p] = [(f"nucleo/{_mod}.py", _g), (f"nucleo/antes_{_mod}.py", _ga), (f"tests/test_{_mod}.py", _gt)]

LIGACOES.update({
    "singleton": "`nucleo/configuracao.py` → `Configuracao` única, lida por `total_com_taxa` (usa `item.total` da `@@ENT@@`) e `formatar`",
    "factory_method": "`nucleo/avisos.py` → cada `Avisador…` cria o seu `Canal…`; `avisar` lê `@@IDENT@@` e `total` da `@@ENT@@`",
    "abstract_factory": "`nucleo/kits.py` → `montar_relatorio` pede as peças a um `Kit…` e lê as `@@ENT@@`s",
    "builder": "`nucleo/construtor.py` → `@@ENT@@Builder` cria a `@@ENT@@` de `nucleo/entidades.py`",
    "prototype": "`nucleo/prototipos.py` → `clonar` copia qualquer `@@ENT@@` (os setters validam as mudanças)",
    "bridge": "`nucleo/comprovantes.py` → cada `Comprovante…` TEM-UM `Formato…` e lê a `@@ENT@@`",
    "composite": "`nucleo/pacotes.py` → `Unitario` embrulha a `@@ENT@@`; `Pacote` guarda componentes",
    "flyweight": "`nucleo/tipos_compartilhados.py` → `Registro` liga a `@@ENT@@` a um `TipoCompartilhado` da `FabricaDeTipos`",
    "proxy": "`nucleo/acesso.py` → os proxies embrulham `ConsultaDePreco`, que lê `item.total`",
    "chain": "`nucleo/aprovacao.py` → a cadeia de `Aprovador` lê `item.total`",
    "command": "`nucleo/comandos.py` → `AlterarCampo` muda a `@@ENT@@` pelos setters; `Historico` empilha",
    "interpreter": "`nucleo/regras.py` → `ler_regra` monta `Comparacao`/`E`/`Ou`, que leem campos da `@@ENT@@`",
    "iterator": "`nucleo/colecao.py` → `Colecao@@ENT@@` guarda `@@ENT@@`s e entrega `IteradorDeItens`",
    "mediator": "`nucleo/mediador.py` → os componentes avisam o `FormularioMediador` (independente da entidade)",
    "memento": "`nucleo/versoes.py` → `Editor@@ENT@@` salva/restaura o estado da `@@ENT@@` em `Memento`s",
    "observer": "`nucleo/eventos.py` → `@@ENT@@Observavel` embrulha a `@@ENT@@` e avisa os observadores",
    "state": "`nucleo/situacao.py` → `Situacao@@ENT@@` TEM-UMA `@@ENT@@` e um `Estado`",
    "template_method": "`nucleo/fechamento.py` → `Fechamento.fechar` lê `item.total` da `@@ENT@@`",
    "visitor": "`nucleo/orcamento.py` → `Linha@@ENT@@` embrulha a `@@ENT@@`; os visitantes percorrem o `Orcamento`",
})


# =============================================================================
# 5. MODELOS — CAMADA WEB (Django · MVT)
# =============================================================================
def django_dados(s, i=0):
    """Literal dict para o model (float → Decimal com 2 casas)."""
    partes = []
    for a in s.atributos:
        if a["regra"] == "livre":
            continue
        v = s.valor_exemplo(a, i)
        partes.append(f'"{a["nome"]}": ' + (f'Decimal("{v:.2f}")' if a["tipo"] == "float" else lit(v)))
    partes.append(f'"tipo": "{s.variantes[0][3]}"')
    return "{" + ", ".join(partes) + "}"


def django_form(s, i=0):
    partes = []
    for a in s.atributos:
        v = s.valor_exemplo(a, i)
        if a["regra"] == "livre":
            partes.append(f'"{a["nome"]}": ""')
        elif a["tipo"] == "float":
            partes.append(f'"{a["nome"]}": "{v:.2f}"')
        elif a["tipo"] == "bool":
            if v:                                   # checkbox: marcado envia "on"; desmarcado não envia nada
                partes.append(f'"{a["nome"]}": "on"')
        else:
            partes.append(f'"{a["nome"]}": "{v}"')
    partes.append(f'"tipo": "{s.variantes[0][3]}"')
    return "{" + ", ".join(partes) + "}"


def django_invalidos(s):
    casos = []
    for a in s.atributos:
        n = a["nome"]
        if a["tipo"] == "bool":
            casos.append(f'("{n}", "talvez")')               # nem True nem False
        elif a["tipo"] == "data":
            casos.append(f'("{n}", "2026-02-30")')           # dia que não existe
        elif a["regra"] == "lista":                          # fora da lista fechada (choices)
            casos.append(f'("{n}", "valor fora da lista")' if a["tipo"] == "str" else f'("{n}", {max(a["opcoes"]) + 1})')
        elif a["regra"] == "obrigatorio":
            casos.append(f'("{n}", "")')
        elif a["tipo"] == "int":
            casos.append(f'("{n}", {a["min"] - 1})')
            if a["regra"] == "faixa":
                casos.append(f'("{n}", {a["max"] + 1})')
        elif a["tipo"] == "float":
            casos.append(f'("{n}", Decimal("{a["min"] - 1:.2f}"))')
            if a["regra"] == "faixa":
                casos.append(f'("{n}", Decimal("{a["max"] + 1:.2f}"))')
    return "[" + ", ".join(casos) + "]"


def django_json(s, i=0):
    """Dados VÁLIDOS da entidade como um cliente da API REST manda (JSON): inteiro é número, sim/não é
    true/false e decimal vai como TEXTO ("12.50"), como no Django REST framework (sem erro de float)."""
    partes = []
    for a in s.atributos:
        v = s.valor_exemplo(a, i)
        if a["regra"] == "livre":
            partes.append(f'"{a["nome"]}": ""')
        elif a["tipo"] == "float":
            partes.append(f'"{a["nome"]}": "{v:.2f}"')
        elif a["tipo"] in ("int", "bool"):
            partes.append(f'"{a["nome"]}": {v!r}')
        else:
            partes.append(f'"{a["nome"]}": "{v}"')
    partes.append(f'"tipo": "{s.variantes[0][3]}"')
    return "{" + ", ".join(partes) + "}"


def gerar_drf(s):
    """API com o DRF (Django REST Framework) — só quando o perfil do domínio pede (a Prova P3).

    Fica AO LADO da API em Django puro (api.py): a mesma regra (os validators do model) em dois estilos.
    Serializer (model ↔ JSON + validação) · ViewSet (o CRUD REST inteiro) · router (as rotas) em /api/<recurso>/ ·
    testes com o APIClient do DRF.
    """
    app, ent = s.app, s.ent
    recurso = plural(s.ent_var).replace("_", "-")
    arq = {}
    arq[f"web/{app}/serializers.py"] = render(r'''
        """
        SERIALIZER do DRF: converte o @@ENT@@ (model) em JSON e VALIDA o que chega na API.

        O ModelSerializer lê os campos e os validators do model — a mesma regra das telas (ModelForm) e da API em
        Django puro (api.py): o limite de cada campo mora num lugar só (no model).
        """
        from rest_framework import serializers

        from .models import @@ENT@@


        class @@ENT@@Serializer(serializers.ModelSerializer):
            class Meta:
                model = @@ENT@@
                fields = "__all__"
        ''', ENT=ent)
    arq[f"web/{app}/api_drf.py"] = render(r'''
        """
        API com o DRF (Django REST Framework) — compare com api.py (Django puro: JsonResponse e os métodos à mão).

        Um ModelViewSet faz o CRUD REST inteiro e o router cria as rotas (incluídas em /api/ pelo projeto):
          GET    /api/@@RECURSO@@/        lista            POST   /api/@@RECURSO@@/        cria (201 / 400)
          GET    /api/@@RECURSO@@/<pk>/   um registro      PUT    /api/@@RECURSO@@/<pk>/   altera tudo
          PATCH  /api/@@RECURSO@@/<pk>/   altera parte     DELETE /api/@@RECURSO@@/<pk>/   exclui (204)
        No navegador, /api/ abre a Browsable API do DRF (dá para testar os endpoints por ali).
        """
        from rest_framework import viewsets
        from rest_framework.routers import DefaultRouter

        from .models import @@ENT@@
        from .serializers import @@ENT@@Serializer


        class @@ENT@@ViewSet(viewsets.ModelViewSet):
            queryset = @@ENT@@.objects.all().order_by("pk")
            serializer_class = @@ENT@@Serializer


        router = DefaultRouter()
        router.register("@@RECURSO@@", @@ENT@@ViewSet, basename="@@BASE@@")
        urlpatterns = router.urls
        ''', ENT=ent, RECURSO=recurso, BASE=s.ent_var)
    arq[f"web/{app}/tests/test_drf.py"] = render(r'''
        """Testes da API do DRF com o APIClient (rest_framework.test): CRUD, validação (400) e o 404."""
        import pytest
        from django.urls import reverse
        from rest_framework.test import APIClient

        from @@APP@@.models import @@ENT@@

        pytestmark = pytest.mark.django_db
        VALIDO = @@VALIDO@@


        @pytest.fixture
        def api():
            return APIClient()


        def test_lista_vazia_e_post_cria(api):
            lista = reverse("@@BASE@@-list")
            assert api.get(lista).status_code == 200 and api.get(lista).json() == []
            resposta = api.post(lista, VALIDO, format="json")
            assert resposta.status_code == 201, resposta.json()
            assert resposta.json()["@@IDENT@@"] == VALIDO["@@IDENT@@"] and @@ENT@@.objects.count() == 1


        def test_post_invalido_devolve_400_com_o_campo(api):
            resposta = api.post(reverse("@@BASE@@-list"), {**VALIDO, "@@QTD@@": 0}, format="json")
            assert resposta.status_code == 400 and "@@QTD@@" in resposta.json()
            assert @@ENT@@.objects.count() == 0


        def test_get_patch_put_delete_de_um_registro(api):
            criado = api.post(reverse("@@BASE@@-list"), VALIDO, format="json").json()
            url = reverse("@@BASE@@-detail", args=[criado["id"]])
            assert api.get(url).json()["id"] == criado["id"]
            assert api.patch(url, {"@@QTD@@": 2}, format="json").json()["@@QTD@@"] == 2
            assert api.put(url, {**VALIDO, "@@QTD@@": 3}, format="json").json()["@@QTD@@"] == 3
            assert api.delete(url).status_code == 204
            assert api.get(url).status_code == 404


        def test_a_raiz_da_api_lista_o_recurso(api):
            assert "@@RECURSO@@" in api.get("/api/", HTTP_ACCEPT="application/json").json()
        ''', APP=app, ENT=ent, BASE=s.ent_var, VALIDO=django_json(s), IDENT=s.ident, QTD=s.qtd, RECURSO=recurso)
    return arq


def secao_perfil(s):
    """Seção do README de um sistema com PERFIL (a Prova P3): o que o guia manda fazer × onde está no sistema."""
    recurso = plural(s.ent_var).replace("_", "-")
    web = s.web
    admin = "gestao" if web["seguranca"] == "baseline" else "admin"
    return render(r'''

        ## @@NOME@@ — o ambiente do guia, já montado

        Gerado com o **perfil** do domínio (`dominios.PERFIS`), igual ao guia
        `ProvaPraticaP3/GUIA_Ambiente_Django_Maquinas_FATEC*.pdf`. A pasta `web/` faz o papel da pasta de trabalho
        do guia (lá, `~/provaP3`; aqui o caminho é **relativo**: `sistemas_gerados/@@PASTA@@/web`).

        | No guia | Aqui |
        |---|---|
        | `pip install django djangorestframework pytest pytest-django` | `requirements.txt` (`bash iniciar.sh deps`) |
        | `django-admin startproject @@PROJETO@@ .` | `web/manage.py` + `web/@@PROJETO@@/` (settings, urls, wsgi) |
        | `python manage.py startapp @@APP@@` | `web/@@APP@@/` (models, forms, views, api.py, serializers.py, api_drf.py, tests/) |
        | `"rest_framework"` e `"@@APP@@"` em `INSTALLED_APPS` | `web/@@PROJETO@@/settings.py` |
        | `pytest.ini`: `DJANGO_SETTINGS_MODULE = @@PROJETO@@.settings` · `python_files = @@ARQUIVOS@@` | `web/pytest.ini` |

        Rotas: `/` leva a `/@@ROTA@@` (telas do CRUD) · `/@@ROTA@@api/v1/` (API em Django puro, `JsonResponse`) ·
        `/api/@@RECURSO@@/` (API com o **DRF**: Serializer + ViewSet + router; `/api/` abre a Browsable API) ·
        `/@@ADMIN@@/` (Django Admin).

        Na tela do SGS: `sgs provap3` gera e prepara tudo (.venv, dependências, .env, migrations, admin);
        `sgs rodar NN` sobe o site. No terminal (com o .venv ativado):

        ```bash
        cd sistemas_gerados/@@PASTA@@/web
        python manage.py migrate
        python manage.py runserver
        python -m pytest
        ```
        ''', NOME=s.perfil.get("nome", s.sistema), PASTA=s.pasta or "", PROJETO=s.projeto, APP=s.app,
        ARQUIVOS=s.pytest_arquivos, ROTA=s.rota, RECURSO=recurso, ADMIN=admin)


def gerar_api_rest(s):
    """API REST (JSON) + settings da app + testes — para TODA app Django gerada (a principal e os módulos).

    Sem dependência extra (só Django): o MESMO ModelForm valida o site e a API, e o CSRF continua ligado.
    """
    app, ent = s.app, s.ent
    prefixo = app.upper()
    arq = {}
    arq[f"web/{app}/settings.py"] = render(r'''
        """
        SETTINGS DA APP @@APP@@ — as configurações deste módulo num lugar só.

        Cada valor tem um PADRÃO aqui e pode ser trocado no config/settings.py do projeto com o prefixo
        @@PREFIXO@@_ (ex.: @@PREFIXO@@_API_LIMITE = 20). O código da app lê sempre por valor("..."), nunca direto:
        assim o projeto manda, e a app continua funcionando sozinha se ninguém configurar nada.
        """
        from django.conf import settings

        PADROES = {
            "API_LIMITE": 100,    # máximo de registros que a lista da API REST devolve por vez (?limite=N)
            "API_ESCRITA": True,  # False = API só de leitura (POST, PUT, PATCH e DELETE respondem 405)
            # Campos de cada endpoint — só o que MUDOU do padrão: {"v1": {"campo": False}, "resumo": {"campo": True}}.
            # Padrão: o v1 (REST) mostra id, os campos do model, total e valor_final; o resumo (api/) mostra id,
            # codigo, titulo e valor. O `sgs api config` grava a escolha no config/settings.py do projeto.
            "API_CAMPOS": {},
        }


        def valor(nome):
            """O valor da configuração: o do projeto (@@PREFIXO@@_<NOME>), se houver; senão o padrão desta app."""
            return getattr(settings, f"@@PREFIXO@@_{nome}", PADROES[nome])
        ''', APP=app, PREFIXO=prefixo)
    arq[f"web/{app}/api.py"] = render(r'''
        """
        API REST da app @@APP@@ (JSON, só com Django — sem pacote extra):

            GET    api/v1/          lista (?limite=N; no máximo @@PREFIXO@@_API_LIMITE)   → 200
            POST   api/v1/          cria (corpo JSON)                                 → 201 | 400
            GET    api/v1/<pk>/     um registro                                       → 200 | 404
            PUT    api/v1/<pk>/     troca TODOS os campos                             → 200 | 400
            PATCH  api/v1/<pk>/     troca só os campos enviados                       → 200 | 400
            DELETE api/v1/<pk>/     apaga                                             → 204
            GET    api/v1/campos/   os campos de cada endpoint (disponíveis e expostos)  → 200
            GET    api/             RESUMO do painel (o link "API" do site): itens + total → 200

        CAMPOS DE CADA ENDPOINT: cada endpoint ("v1" e "resumo") mostra só os campos EXPOSTOS. O projeto escolhe
        campo a campo em config/settings.py (@@PREFIXO@@_API_CAMPOS — o que o `sgs api config` escreve), e quem
        chama ainda pode pedir só alguns, entre os expostos: ?campos=a,b (campo oculto não aparece nem pedindo).

        A validação é a MESMA das telas: o @@ENT@@Form (ModelForm com os validators do model). O valor final
        vem do @@ENT@@Service (Strategy do núcleo). O CSRF continua ligado: quem chama de fora manda o cookie
        csrftoken e o cabeçalho X-CSRFToken (como o fetch() de uma página do próprio site).
        """
        import json

        from django.forms.models import model_to_dict
        from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

        from . import settings as config_app
        from .forms import @@ENT@@Form
        from .models import @@ENT@@
        from .services import @@ENT@@Service
        from .viewmodels import ItemVM, PainelVM

        ENDPOINTS = ("v1", "resumo")
        CALCULADOS = ("total", "valor_final", "codigo", "titulo", "valor")
        PADRAO_RESUMO = ("id", "codigo", "titulo", "valor")


        def campos_disponiveis():
            """Tudo o que um endpoint PODE mostrar: o id, os campos do model e os valores calculados."""
            return ["id"] + [c.name for c in @@ENT@@._meta.fields if not c.primary_key] + list(CALCULADOS)


        def exposto_por_padrao(endpoint, campo):
            if endpoint == "resumo":
                return campo in PADRAO_RESUMO
            return campo not in ("codigo", "titulo", "valor")   # v1: o registro inteiro + total e valor_final


        def campos_expostos(endpoint, request=None):
            """Os campos do endpoint: o padrão + o que o projeto mudou (API_CAMPOS) e, com ?campos=, só os pedidos."""
            escolhas = (config_app.valor("API_CAMPOS") or {}).get(endpoint, {})
            campos = [c for c in campos_disponiveis() if escolhas.get(c, exposto_por_padrao(endpoint, c))]
            pedidos = request.GET.get("campos") if request is not None else None
            if pedidos:
                quer = {c.strip() for c in pedidos.split(",") if c.strip()}
                campos = [c for c in campos if c in quer]
            return campos


        def serializar(obj, campos=None):
            """Model → dict pronto para JSON (decimal, data e UUID viram texto), só com os campos expostos."""
            campos = campos_expostos("v1") if campos is None else campos
            dados, calculado = {}, None
            for campo in campos:
                if campo == "id":
                    dados["id"] = obj.pk if isinstance(obj.pk, int) else str(obj.pk)
                elif campo == "total":
                    dados["total"] = str(obj.total)
                elif campo in ("valor_final", "valor", "codigo", "titulo"):
                    if calculado is None:                     # calcula uma vez só (Strategy do núcleo)
                        final = @@ENT@@Service().valor_final(obj)
                        calculado = (ItemVM(obj, final), round(final, 2))
                    vm, final = calculado
                    dados[campo] = {"valor_final": final, "valor": vm.valor_formatado, "codigo": vm.codigo,
                                    "titulo": vm.titulo}[campo]
                else:
                    valor = getattr(obj, obj._meta.get_field(campo).attname)
                    dados[campo] = valor if valor is None or isinstance(valor, (bool, int, str)) else str(valor)
            return dados


        def resumo(request):
            """GET api/: o RESUMO do painel (o link "API" do site) — itens com os campos do endpoint resumo + total."""
            if request.method != "GET":
                return HttpResponseNotAllowed(["GET"])
            objetos = @@ENT@@.objects.order_by("pk")
            campos = campos_expostos("resumo", request)
            painel = PainelVM(objetos, @@ENT@@Service())
            return JsonResponse({"itens": [serializar(o, campos) for o in objetos], "total": painel.total_formatado})


        def campos(request):
            """GET api/v1/campos/: o que cada endpoint PODE mostrar e o que mostra agora."""
            return JsonResponse({"disponiveis": campos_disponiveis(),
                                 "expostos": {endpoint: campos_expostos(endpoint) for endpoint in ENDPOINTS}})


        def ler_corpo(request):
            """O corpo JSON (um objeto) ou None se não for JSON válido."""
            try:
                dados = json.loads(request.body or b"{}")
            except (ValueError, UnicodeDecodeError):
                return None
            return dados if isinstance(dados, dict) else None


        def para_form(dados):
            """JSON → dados de formulário: sim/não vira "on"/ausente (exatamente o que o navegador manda)."""
            convertidos = {}
            for chave, valor in dados.items():
                if isinstance(valor, bool):
                    if valor:
                        convertidos[chave] = "on"
                    continue
                convertidos[chave] = "" if valor is None else str(valor)
            return convertidos


        def erros(form):
            return {campo: [e["message"] for e in lista] for campo, lista in form.errors.get_json_data().items()}


        def metodos_permitidos(*todos):
            """Com @@PREFIXO@@_API_ESCRITA = False, só o GET continua valendo."""
            return list(todos) if config_app.valor("API_ESCRITA") else ["GET"]


        def colecao(request):
            """GET lista · POST cria."""
            permitidos = metodos_permitidos("GET", "POST")
            if request.method not in permitidos:
                return HttpResponseNotAllowed(permitidos)
            if request.method == "GET":
                maximo = config_app.valor("API_LIMITE")
                try:
                    limite = int(request.GET.get("limite", maximo))
                except ValueError:
                    limite = maximo
                limite = max(1, min(limite, maximo))
                objetos = @@ENT@@.objects.order_by("pk")[:limite]
                campos_v1 = campos_expostos("v1", request)
                return JsonResponse({"itens": [serializar(o, campos_v1) for o in objetos], "limite": limite,
                                     "total_registros": @@ENT@@.objects.count()})
            dados = ler_corpo(request)
            if dados is None:
                return JsonResponse({"erro": "envie um objeto JSON no corpo"}, status=400)
            form = @@ENT@@Form(para_form(dados))
            if not form.is_valid():  # os validators do model valem aqui também
                return JsonResponse({"erros": erros(form)}, status=400)
            return JsonResponse(serializar(form.save()), status=201)


        def item(request, pk):
            """GET um · PUT troca tudo · PATCH troca parte · DELETE apaga."""
            permitidos = metodos_permitidos("GET", "PUT", "PATCH", "DELETE")
            if request.method not in permitidos:
                return HttpResponseNotAllowed(permitidos)
            obj = @@ENT@@.objects.filter(pk=pk).first()
            if obj is None:
                return JsonResponse({"erro": "registro não encontrado"}, status=404)
            if request.method == "GET":
                return JsonResponse(serializar(obj, campos_expostos("v1", request)))
            if request.method == "DELETE":
                obj.delete()
                return HttpResponse(status=204)
            dados = ler_corpo(request)
            if dados is None:
                return JsonResponse({"erro": "envie um objeto JSON no corpo"}, status=400)
            if request.method == "PATCH":  # parte: completa com o que o registro já tem
                atuais = model_to_dict(obj, fields=@@ENT@@Form._meta.fields)
                dados = {**{k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in atuais.items()}, **dados}
            form = @@ENT@@Form(para_form(dados), instance=obj)
            if not form.is_valid():
                return JsonResponse({"erros": erros(form)}, status=400)
            return JsonResponse(serializar(form.save()))
        ''', APP=app, ENT=ent, PREFIXO=prefixo)
    arq[f"web/{app}/tests/test_api.py"] = render(r'''
        """Testes da API REST: o mesmo ModelForm valida as telas e a API; o settings da app manda nos limites."""
        import json

        import pytest
        from django.test import Client, override_settings
        from django.urls import reverse

        from @@APP@@.models import @@ENT@@

        pytestmark = pytest.mark.django_db
        VALIDO = @@VALIDO@@


        @pytest.fixture(autouse=True)
        def api_no_padrao(settings):
            """Estes testes conferem o PADRÃO: o que o projeto escolheu no sgs api config não muda o resultado deles."""
            settings.@@PREFIXO@@_API_CAMPOS = {}


        def enviar(client, metodo, url, dados):
            return getattr(client, metodo)(url, data=json.dumps(dados), content_type="application/json")


        def colecao():
            return reverse("@@APP@@:api_colecao")


        def test_post_cria_e_get_lista(client):
            resposta = enviar(client, "post", colecao(), VALIDO)
            assert resposta.status_code == 201
            criado = resposta.json()
            assert criado["@@IDENT@@"] == VALIDO["@@IDENT@@"] and "total" in criado and "valor_final" in criado
            lista = client.get(colecao()).json()
            assert lista["total_registros"] == 1 and lista["itens"][0]["id"] == criado["id"]


        def test_post_invalido_devolve_400_com_os_erros(client):
            resposta = enviar(client, "post", colecao(), {**VALIDO, "@@QTD@@": 0})
            assert resposta.status_code == 400 and "@@QTD@@" in resposta.json()["erros"]
            assert @@ENT@@.objects.count() == 0


        def test_get_put_patch_delete_de_um_registro(client):
            criado = enviar(client, "post", colecao(), VALIDO).json()
            url = reverse("@@APP@@:api_item", args=[criado["id"]])
            assert client.get(url).json()["id"] == criado["id"]
            parcial = enviar(client, "patch", url, {"@@QTD@@": 2})           # PATCH: só o campo enviado muda
            assert parcial.status_code == 200 and parcial.json()["@@QTD@@"] == 2
            assert parcial.json()["@@IDENT@@"] == VALIDO["@@IDENT@@"]
            inteiro = enviar(client, "put", url, {**VALIDO, "@@QTD@@": 3})   # PUT: o registro inteiro
            assert inteiro.status_code == 200 and inteiro.json()["@@QTD@@"] == 3
            assert enviar(client, "put", url, {**VALIDO, "@@QTD@@": 0}).status_code == 400
            assert client.delete(url).status_code == 204
            assert client.get(url).status_code == 404


        def test_metodo_nao_permitido_e_json_invalido(client):
            assert client.delete(colecao()).status_code == 405
            assert client.post(colecao(), data="{isto não é json", content_type="application/json").status_code == 400


        def test_api_so_leitura_pelo_settings_da_app(client):
            with override_settings(@@PREFIXO@@_API_ESCRITA=False):
                assert enviar(client, "post", colecao(), VALIDO).status_code == 405
                assert client.get(colecao()).status_code == 200


        def test_limite_da_lista_vem_do_settings_da_app(client):
            for _ in range(3):
                enviar(client, "post", colecao(), VALIDO)
            with override_settings(@@PREFIXO@@_API_LIMITE=2):
                dados = client.get(colecao()).json()
            assert len(dados["itens"]) == 2 and dados["total_registros"] == 3
            assert len(client.get(colecao(), {"limite": 1}).json()["itens"]) == 1


        def test_csrf_continua_valendo_na_api():
            """Sem o token CSRF, escrever é recusado (403): a API não abre uma porta nos fundos."""
            assert enviar(Client(enforce_csrf_checks=True), "post", colecao(), VALIDO).status_code == 403


        # ---------------------------------------------------------------- campos de cada endpoint (sgs api config)
        def test_campos_de_cada_endpoint_vem_do_settings(client):
            enviar(client, "post", colecao(), VALIDO)
            padrao = client.get(colecao()).json()["itens"][0]
            assert "@@IDENT@@" in padrao and "valor_final" in padrao and "titulo" not in padrao
            resumo = client.get(reverse("@@APP@@:api")).json()["itens"][0]
            assert set(resumo) == {"id", "codigo", "titulo", "valor"}           # o resumo do painel (link "API")
            escolha = {"v1": {"@@IDENT@@": False, "titulo": True}, "resumo": {"@@QTD@@": True, "codigo": False}}
            with override_settings(@@PREFIXO@@_API_CAMPOS=escolha):
                item = client.get(colecao()).json()["itens"][0]
                assert "@@IDENT@@" not in item and "titulo" in item
                resumo = client.get(reverse("@@APP@@:api")).json()["itens"][0]
                assert resumo["@@QTD@@"] == VALIDO["@@QTD@@"] and "codigo" not in resumo
                campos = client.get(reverse("@@APP@@:api_campos")).json()
                assert "@@IDENT@@" in campos["disponiveis"] and "@@IDENT@@" not in campos["expostos"]["v1"]


        def test_quem_chama_escolhe_entre_os_campos_expostos(client):
            criado = enviar(client, "post", colecao(), VALIDO).json()
            item = client.get(colecao(), {"campos": "@@IDENT@@,total"}).json()["itens"][0]
            assert set(item) == {"@@IDENT@@", "total"}
            um = client.get(reverse("@@APP@@:api_item", args=[criado["id"]]), {"campos": "id"}).json()
            assert um == {"id": criado["id"]}
            with override_settings(@@PREFIXO@@_API_CAMPOS={"v1": {"total": False}}):   # oculto não volta nem pedindo
                assert set(client.get(colecao(), {"campos": "@@IDENT@@,total"}).json()["itens"][0]) == {"@@IDENT@@"}
        ''', APP=app, ENT=ent, VALIDO=django_json(s), IDENT=s.ident, QTD=s.qtd, PREFIXO=prefixo)
    return arq


def gerar_web(s):
    arq = {}
    app, ent = s.app, s.ent
    app_camel = camel(app)
    campos = []
    for a in s.atributos:
        n, rot = a["nome"], a["nome"].replace("_", " ")
        # Campo acrescentado depois (sgs incrementar): "padrao" vira default — as linhas que JÁ estão no banco
        # recebem esse valor na migration (sem ele, o makemigrations travaria pedindo um valor).
        if "padrao" not in a:
            pad = ""
        elif a["tipo"] == "float":
            pad = f', default=Decimal("{float(a["padrao"]):.2f}")'
        else:
            pad = f", default={a['padrao']!r}"
        if a["regra"] == "lista":
            escolhas = ", ".join(f"({o!r}, {str(o)!r})" for o in a["opcoes"])
            if a["tipo"] == "str":
                tamanho = max(60, max(len(o) for o in a["opcoes"]))
                campos.append(f'{n} = models.CharField("{rot}", max_length={tamanho}, choices=[{escolhas}]{pad})  '
                              "# lista fechada: o form vira uma lista de escolha")
            else:
                campos.append(f'{n} = models.IntegerField("{rot}", choices=[{escolhas}]{pad})  # lista fechada')
            continue
        if a["tipo"] == "str":
            if a["regra"] == "obrigatorio":
                campos.append(f'{n} = models.CharField("{rot}", max_length=120{pad})  # obrigatório: blank=False é o padrão')
            else:
                campos.append(f'{n} = models.CharField("{rot}", max_length=200, blank=True, default="")  # sem regra')
            continue
        if a["tipo"] == "bool":
            campos.append(f'{n} = models.BooleanField("{rot}", default=False)  # sim/não: caixa de marcar no form')
            continue
        if a["tipo"] == "data":
            campos.append(f'{n} = models.DateField("{rot}"{pad})  # data válida (o form aceita AAAA-MM-DD)')
            continue
        val = []
        if a["tipo"] == "int":
            val.append(f"MinValueValidator({a['min']})")
            if a["regra"] == "faixa":
                val.append(f"MaxValueValidator({a['max']})")
            campos.append(f'{n} = models.IntegerField("{rot}", validators=[{", ".join(val)}]{pad})')
        else:
            val.append(f'MinValueValidator(Decimal("{a["min"]}"))')
            if a["regra"] == "faixa":
                val.append(f'MaxValueValidator(Decimal("{a["max"]}"))')
            campos.append(f'{n} = models.DecimalField("{rot}", max_digits=10, decimal_places=2, '
                          f'validators=[{", ".join(val)}]{pad})')
    tipos = ",\n".join(f'    ("{x[3]}", "{x[0]}")' for x in s.variantes + [s.vnova])
    campos_form = ", ".join(f'"{a["nome"]}"' for a in s.atributos) + ', "tipo"'
    politicas = ", ".join(sorted(f"Politica{x[2]}" for x in s.variantes + [s.vnova]))
    mapa = ",\n".join(f'    "{x[3]}": Politica{x[2]}(),' .rstrip(",") for x in s.variantes + [s.vnova])
    fatores = ", ".join(f'("{x[3]}", {x[1]!r})' for x in s.variantes + [s.vnova])
    total0 = s.total_exemplo(0)
    k2, f2 = s.variantes[1][3], s.variantes[1][1]

    arq["web/manage.py"] = render(r'''
        #!/usr/bin/env python
        """Utilitário de linha de comando do Django (gerado)."""
        import os
        import sys


        def main():
            # Se herdado do SGS (manage.py da tela), limpa antes do setdefault para usar o settings deste sistema.
            if os.environ.get("DJANGO_SETTINGS_MODULE") == "sgs_web.settings":
                os.environ.pop("DJANGO_SETTINGS_MODULE", None)
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)


        if __name__ == "__main__":
            main()
        ''')
    arq["web/config/__init__.py"] = ""
    arq["web/config/env.py"] = render(r'''
        """Leitor MÍNIMO de .env (sem dependência extra): linhas CHAVE=valor; linhas com # são comentário."""
        import os


        def ler_env(caminho):
            """Devolve {chave: valor} do arquivo; aspas em volta do valor são retiradas. Sem arquivo → {}."""
            try:
                with open(caminho, encoding="utf-8") as arquivo:
                    texto = arquivo.read()
            except FileNotFoundError:
                return {}
            valores = {}
            for linha in texto.splitlines():
                linha = linha.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                chave, valor = linha.split("=", 1)
                valor = valor.strip()
                if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                    valor = valor[1:-1]
                valores[chave.strip()] = valor
            return valores


        def carregar_env(caminho):
            """Coloca o .env em os.environ SEM sobrescrever o que já existe (variável do ambiente manda)."""
            for chave, valor in ler_env(caminho).items():
                os.environ.setdefault(chave, valor)
        ''')
    arq["web/.env.example"] = render(r'''
        # Modelo do web/.env do @@SISTEMA@@ (gerado).
        # `bash iniciar.sh env` copia este arquivo para web/.env e gera uma SECRET_KEY nova.
        # O web/.env NÃO vai para o git (tem senha e chave secreta) — veja o .gitignore.
        SECRET_KEY=troque-esta-chave
        DEBUG=1
        ALLOWED_HOSTS=localhost,127.0.0.1,testserver

        # Superusuário criado/atualizado por `python manage.py garantir_admin` (bash iniciar.sh admin).
        # Troque a senha antes de usar fora da sua máquina.
        DJANGO_SUPERUSER_USERNAME=admin
        DJANGO_SUPERUSER_EMAIL=admin@exemplo.com
        DJANGO_SUPERUSER_PASSWORD=admin123

        # Porta usada por `bash iniciar.sh rodar` quando nenhuma é informada.
        PORTA=8000

        # PWA=1: o site abre numa JANELA DE APP isolada das abas (Edge/Chrome --app) · PWA=0: abre numa aba comum.
        PWA=1

        # Endereço do Django Admin (com a barra no fim).
        ADMIN_URL=@@ADMIN@@
        @@BASELINE@@
        ''', SISTEMA=s.sistema, ADMIN="gestao/" if s.web["seguranca"] == "baseline" else "admin/",
        BASELINE="" if s.web["seguranca"] != "baseline" else (
            "\n# Segurança (Instruções §12–14). CSP começa em Report-Only; CSP_IMPOR=1 passa a impor.\n"
            "CSP_IMPOR=0\n# Origens confiáveis do CSRF em produção, com esquema: https://seu-dominio\n"
            "CSRF_TRUSTED_ORIGINS="))
    arq["web/config/settings.py"] = render(r'''
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
        DEBUG = os.environ.get("DEBUG", "@@DEBUG@@") == "1"
        ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
        ADMIN_URL = os.environ.get("ADMIN_URL", "@@ADMIN@@")  # endereço do Django Admin (lido em config/urls.py)

        INSTALLED_APPS = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            @@APPS_DO_PROJETO@@
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
        @@SEGURANCA@@
        ''', APP=app, APPS_DO_PROJETO=('"rest_framework",  # DRF: Django REST Framework (API com Serializer/ViewSet)\n'
                                       if s.drf else "") + f'"{app}",',
        DEBUG="0" if s.web["seguranca"] == "baseline" else "1",
        ADMIN="gestao/" if s.web["seguranca"] == "baseline" else "admin/",
        SEGURANCA=SETTINGS_BASELINE if s.web["seguranca"] == "baseline" else "")
    # Rotas do projeto. Perfil com rota (Prova P3: "citricultura/"): o app fica em /citricultura/ e a raiz leva
    # até ele; com DRF, a API do DRF (router) fica em /api/. Sem perfil: o app na raiz, como sempre.
    rotas_app = []
    if s.drf:
        rotas_app.append(f'path("api/", include("{app}.api_drf")),  # API com o DRF (router + ViewSet): /api/…')
    rotas_app.append(f'path("{s.rota}", include("{app}.urls")),')
    if s.rota:
        rotas_app.append(f'path("", RedirectView.as_view(url="/{s.rota}", permanent=False)),  # a raiz leva ao app')
    arq["web/config/urls.py"] = render(r'''
        from django.conf import settings
        from django.contrib import admin
        from django.urls import include, path
        @@IMPORTA_REDIRECT@@

        from . import pwa

        urlpatterns = [
            path(settings.ADMIN_URL, admin.site.urls),
            # PWA: manifest e service worker ficam na RAIZ do site (o service worker só controla o que está abaixo dele)
            path("manifest.webmanifest", pwa.manifest, name="manifest"),
            path("sw.js", pwa.service_worker, name="service_worker"),
            @@ROTAS_APP@@
        ]
        ''', ROTAS_APP="\n".join(rotas_app),
        IMPORTA_REDIRECT="from django.views.generic import RedirectView" if s.rota else "")
    if not s.rota:      # sem a linha vazia que o marcador deixaria (a saída de sempre não muda)
        arq["web/config/urls.py"] = arq["web/config/urls.py"].replace("import include, path\n\n\nfrom", "import include, path\n\nfrom")
    arq["web/config/pwa.py"] = render(r'''
        """
        PWA (Progressive Web App): o site pode ser INSTALADO e abrir numa janela própria, isolada das abas.

        Três peças, servidas pelo próprio Django (sem dependência extra):
          * /manifest.webmanifest — nome, cores, ícones e display "standalone" (janela de app);
          * /sw.js — o service worker (na RAIZ do site, para valer em todas as páginas): rede primeiro,
            e a última cópia de cada página quando a rede cair;
          * os ícones PNG em @@APP@@/static/@@APP@@/.
        O iniciar.sh abre o site em modo app (Edge/Chrome --app=URL) quando PWA=1 no web/.env.
        Em 127.0.0.1 o navegador já considera o site "seguro" (exigência do service worker).
        """
        import json

        from django.http import HttpResponse
        from django.templatetags.static import static

        SERVICE_WORKER = """
        const CACHE = "pwa-@@APP@@-v1";
        self.addEventListener("install", () => self.skipWaiting());
        self.addEventListener("activate", (evento) => evento.waitUntil(self.clients.claim()));
        self.addEventListener("fetch", (evento) => {
          if (evento.request.method !== "GET") return;
          evento.respondWith(
            fetch(evento.request)
              .then((resposta) => {
                const copia = resposta.clone();
                caches.open(CACHE).then((cache) => cache.put(evento.request, copia));
                return resposta;
              })
              .catch(() => caches.match(evento.request))
          );
        });
        """


        def manifest(request):
            """O "RG" do app: o navegador lê isto para instalar e abrir em janela própria."""
            dados = {
                "name": "@@SISTEMA@@",
                "short_name": "@@CURTO@@",
                "start_url": "/",
                "scope": "/",
                "display": "standalone",
                "background_color": "#0c0c0c",
                "theme_color": "#0c0c0c",
                "icons": [{"src": static("@@APP@@/icone-192.png"), "sizes": "192x192", "type": "image/png"},
                          {"src": static("@@APP@@/icone-512.png"), "sizes": "512x512", "type": "image/png"}],
            }
            return HttpResponse(json.dumps(dados, ensure_ascii=False), content_type="application/manifest+json")


        def service_worker(request):
            resposta = HttpResponse(SERVICE_WORKER, content_type="application/javascript")
            resposta["Service-Worker-Allowed"] = "/"
            return resposta
        ''', APP=app, SISTEMA=s.sistema, CURTO=s.sistema.split()[0][:12])
    arq[f"web/{app}/static/{app}/icone-192.png"] = icone_png(192)
    arq[f"web/{app}/static/{app}/icone-512.png"] = icone_png(512)
    arq["web/config/wsgi.py"] = render(r'''
        import os

        from django.core.wsgi import get_wsgi_application

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        application = get_wsgi_application()
        ''')
    arq["web/pytest.ini"] = render(r'''
        [pytest]
        DJANGO_SETTINGS_MODULE = config.settings
        pythonpath = . ..
        python_files = @@ARQUIVOS_TESTE@@
        ''', ARQUIVOS_TESTE=s.pytest_arquivos)
    arq[f"web/{app}/__init__.py"] = ""
    arq[f"web/{app}/apps.py"] = render(r'''
        from django.apps import AppConfig


        class @@C@@Config(AppConfig):
            default_auto_field = "django.db.models.BigAutoField"
            name = "@@APP@@"
        ''', C=app_camel, APP=app)
    w = s.web
    importacoes = ["from decimal import Decimal", ""]
    if w["id_publico"] == "uuid":
        importacoes.insert(0, "import uuid")
    importacoes += ["from django.core.validators import MaxValueValidator, MinValueValidator", "from django.db import models"]
    antes_classe, campos_id, metodos = "", [], ""
    if w["id_publico"] == "uuid":
        campos_id.append("# Instruções §10.4: chave UUIDv4 — o próximo registro não dá para adivinhar (anti-enumeração).")
        campos_id.append("id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)")
    if w["id_interno"]:
        importacoes[-2:] = ["from django.core.exceptions import ValidationError",
                            "from django.core.validators import MaxValueValidator, MinValueValidator",
                            "from django.db import IntegrityError, models, transaction", "", "from . import lnnl"]
        antes_classe = render(r'''
            # ID interno LNNL (motor-id-interno): legível por pessoas, NÃO substitui a chave primária.
            TIPO_LNNL = "@@TIPO@@"  # código de tipo desta entidade (11–99, sem zero; 93 é reservado)


            def validar_codigo_lnnl(valor):
                """Validator: só aceita um LNNL válido do tipo desta entidade (verificadores módulo 79)."""
                resultado = lnnl.validar(valor, TIPO_LNNL)
                if not resultado:
                    raise ValidationError(f"código LNNL inválido: {resultado.erro}")


            ''', TIPO=w["lnnl_tipo"])
        # Nome próprio (id_interno, reservado no gerador) para não colidir com um atributo do domínio (ex.: "codigo").
        campos_id.append('id_interno = models.CharField("ID interno", max_length=14, unique=True, editable=False, '
                         'blank=True, validators=[validar_codigo_lnnl])')
        metodos = render(r'''
            @property
            def id_interno_formatado(self):
                """O ID interno na máscara de exibição LNNL-LNNL-LNL-LNL (ex.: K21W-F92M-T5R-Q7L)."""
                return lnnl.formatar(self.id_interno)

            def save(self, *args, **kwargs):
                """Gera o ID interno na primeira gravação. Regra do motor: sorteia, INSERE e, se colidir
                (UNIQUE), tenta de novo — nunca "consulta antes e insere depois"."""
                if self.id_interno:
                    return super().save(*args, **kwargs)
                for _ in range(5):
                    self.id_interno = lnnl.gerar(TIPO_LNNL)
                    try:
                        with transaction.atomic():
                            return super().save(*args, **kwargs)
                    except IntegrityError:
                        self.id_interno = ""
                raise IntegrityError("não foi possível gerar um ID interno LNNL único")
            ''')
    arq[f"web/{app}/models.py"] = render(r'''
        """
        MODEL (o "M" do MVT). Encapsulamento no MUNDO DJANGO (Aula 03):
          * a regra de cada campo vai em validators — o ModelForm, o admin e o full_clean() as executam;
          * @property aqui só para dado CALCULADO (total); setter em campo quebraria form/admin/ORM;
          * pegadinha: save() sozinho NÃO valida (ver tests/test_models.py).
        """
        @@IMPORTS@@

        @@ANTES@@
        class @@ENT@@(models.Model):
            TIPOS = [
            @@TIPOS@@
            ]

            @@CAMPOSID@@
            @@CAMPOS@@
            tipo = models.CharField("@@CONCEITO@@", max_length=30, choices=TIPOS, default="@@T0@@")

            @property
            def total(self):
                """Dado CALCULADO (@@QTD@@ × @@PRECO@@): nunca guardado, nunca desatualizado."""
                return self.@@QTD@@ * self.@@PRECO@@

            @@METODOS@@

            def __str__(self):
                return f"{self.@@IDENT@@} - {self.@@QTD@@} @@UNIDADE@@"
        ''', ENT=ent, TIPOS=tipos, CAMPOS="\n".join(campos), CONCEITO=s.conceito, T0=s.variantes[0][3],
        QTD=s.qtd, PRECO=s.preco, IDENT=s.ident, UNIDADE=s.unidade, IMPORTS="\n".join(importacoes),
        ANTES=antes_classe.rstrip("\n") + "\n\n" if antes_classe else "", CAMPOSID="\n".join(campos_id), METODOS=metodos)
    if w["id_interno"]:
        if not MOTOR_LNNL.exists():
            raise ErroGerador(f"motor-id-interno não encontrado: {MOTOR_LNNL}")
        arq[f"web/{app}/lnnl.py"] = MOTOR_LNNL.read_text(encoding="utf-8")   # cópia fiel da referência
    arq[f"web/{app}/forms.py"] = render(r'''
        """ModelForm: reaproveita os validators do model (a regra mora num lugar só)."""
        from django import forms

        from .models import @@ENT@@


        class @@ENT@@Form(forms.ModelForm):
            class Meta:
                @@META@@
            @@BOOTSTRAP@@
        ''', ENT=ent, META=f"model = {ent}\nfields = [{campos_form}]" + (
            "\n# Data: <input type=\"date\"> mostra o calendário do navegador (o valor vai como AAAA-MM-DD).\n"
            "widgets = {" + ", ".join(f'"{a["nome"]}": forms.DateInput(attrs={{"type": "date"}}, format="%Y-%m-%d")'
                                      for a in s.atributos if a["tipo"] == "data") + "}"
            if any(a["tipo"] == "data" for a in s.atributos) else ""), BOOTSTRAP="\n" + render(r'''
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Bootstrap: cada campo ganha a classe do componente (o HTML continua vindo do Django).
                for campo in self.fields.values():
                    @@CLASSE@@
            ''', CLASSE=(
                'if isinstance(campo.widget, forms.CheckboxInput):\n'
                '    campo.widget.attrs["class"] = "form-check-input"  # caixa de marcar (sim/não)\n'
                'else:\n'
                '    campo.widget.attrs["class"] = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"'
                if any(a["tipo"] == "bool" for a in s.atributos) else
                'campo.widget.attrs["class"] = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"'))
            if w["estilo"] in ("bootstrap", "web") else "")
    if w["id_interno"]:
        arq[f"web/{app}/admin.py"] = render(r'''
            from django.contrib import admin

            from .models import @@ENT@@


            @admin.register(@@ENT@@)
            class @@ENT@@Admin(admin.ModelAdmin):
                list_display = ("id_interno_formatado", "__str__")
                readonly_fields = ("id_interno",)  # o ID interno LNNL é gerado no save(), nunca digitado
                search_fields = ("id_interno", "@@IDENT@@")
            ''', ENT=ent, IDENT=s.ident)
    else:
        arq[f"web/{app}/admin.py"] = render(r'''
            from django.contrib import admin

            from .models import @@ENT@@

            admin.site.register(@@ENT@@)
            ''', ENT=ent)
    arq[f"web/{app}/services.py"] = render(r'''
        """
        SERVICE (Aula 07): a regra de negócio da camada web — NÃO conhece request, HTML nem template.
        Reaproveita o STRATEGY do núcleo (nucleo/politicas.py): o campo `tipo` do model escolhe a política.
        """
        from nucleo.politicas import @@POLITICAS@@

        # Raiz de composição: um DICIONÁRIO escolhe a estratégia (não é if/elif — política nova = 1 linha aqui).
        POLITICAS = {
        @@MAPA@@
        }


        class @@ENT@@Service:
            def valor_final(self, obj):
                """Total do model (Decimal) → float → política do núcleo."""
                return POLITICAS[obj.tipo].aplicar(float(obj.total))

            def resumo(self, objetos):
                """Devolve DADOS: ([(obj, valor_final), ...], soma)."""
                itens = [(obj, self.valor_final(obj)) for obj in objetos]
                return itens, round(sum(valor for _, valor in itens), 2)
        ''', POLITICAS=politicas, MAPA=mapa, ENT=ent)
    arq[f"web/{app}/viewmodels.py"] = render(r'''
        """
        VIEWMODEL (Aula 08): prepara o que a tela mostra. Recebe dados do Service; não sabe desenhar.
        No servidor não há binding (isso é do Alpine.js no navegador): aqui é só preparação antes do render.
        """


        class ItemVM:
            def __init__(self, obj, valor_final):
                self.id = obj.pk
                self.codigo = @@CODIGO@@
                self.titulo = f"{obj.@@IDENT@@} — {obj.@@QTD@@} @@UNIDADE@@"
                self.tipo_label = obj.get_tipo_display()
                self.valor_formatado = f"R$ {valor_final:.2f}"
                self.tem_desconto = valor_final < float(obj.total)
                self.selo = "com desconto" if self.tem_desconto else "valor cheio"


        class PainelVM:
            def __init__(self, objetos, servico):
                itens, total = servico.resumo(objetos)
                self.itens = [ItemVM(obj, valor) for obj, valor in itens]
                self.total_formatado = f"R$ {total:.2f}"
                if self.itens:
                    self.rodape = f"{len(self.itens)} registro(s) · total {self.total_formatado}"
                else:
                    self.rodape = "Nenhum registro ainda"


        class DetalheVM(ItemVM):
            """Um registro na tela de detalhe: tudo do ItemVM + cada campo já com rótulo e valor legível."""

            def __init__(self, obj, valor_final):
                super().__init__(obj, valor_final)
                self.campos = []
                for campo in obj._meta.fields:
                    if campo.primary_key:
                        continue
                    valor = getattr(obj, f"get_{campo.name}_display")() if campo.choices else getattr(obj, campo.name)
                    if isinstance(valor, bool):
                        valor = "Sim" if valor else "Não"
                    self.campos.append((str(campo.verbose_name).capitalize(), valor if valor not in ("", None) else "—"))
        ''', IDENT=s.ident, QTD=s.qtd, UNIDADE=s.unidade,
        CODIGO='obj.id_interno_formatado  # ID interno LNNL, pronto para exibir' if w["id_interno"] else '""')
    arq[f"web/{app}/views.py"] = render(r'''
        """
        VIEWS (o "V" do MVT = a lógica/orquestração; o "Controller" do MVC). FINAS:
        buscam os dados, delegam a regra ao Service e a exibição ao ViewModel, e renderizam.
        """
        from django.shortcuts import get_object_or_404, redirect, render

        from .forms import @@ENT@@Form
        from .models import @@ENT@@
        from .services import @@ENT@@Service
        from .viewmodels import DetalheVM, PainelVM


        def lista(request):
            painel = PainelVM(@@ENT@@.objects.order_by("pk"), @@ENT@@Service())
            return render(request, "@@APP@@/lista.html", {"painel": painel})


        def criar(request):
            """CRUD · CREATE."""
            form = @@ENT@@Form(request.POST or None)
            if request.method == "POST" and form.is_valid():  # is_valid() executa os validators do model
                form.save()
                return redirect("@@APP@@:lista")
            return render(request, "@@APP@@/form.html", {"form": form})


        def detalhe(request, pk):
            """CRUD · READ (um registro): o DetalheVM prepara o que a tela mostra."""
            obj = get_object_or_404(@@ENT@@, pk=pk)
            return render(request, "@@APP@@/detalhe.html", {"item": DetalheVM(obj, @@ENT@@Service().valor_final(obj))})


        def editar(request, pk):
            """CRUD · UPDATE: o MESMO ModelForm, preenchido com o registro (as validações continuam valendo)."""
            obj = get_object_or_404(@@ENT@@, pk=pk)
            form = @@ENT@@Form(request.POST or None, instance=obj)
            if request.method == "POST" and form.is_valid():
                form.save()
                return redirect("@@APP@@:detalhe", pk=obj.pk)
            return render(request, "@@APP@@/form.html", {"form": form, "obj": obj})


        def excluir(request, pk):
            """CRUD · DELETE: o GET só mostra a confirmação; apagar exige POST (GET nunca altera dados)."""
            obj = get_object_or_404(@@ENT@@, pk=pk)
            if request.method == "POST":
                obj.delete()
                return redirect("@@APP@@:lista")
            return render(request, "@@APP@@/confirmar_exclusao.html", {"obj": obj})
        @@VIEW_EXERCICIOS@@
        ''', ENT=ent, APP=app, VIEW_EXERCICIOS="\n\n" + render(r'''
            def exercicios(request):
                """Questionário de revisão (modo exercício): só exibe — cada resposta fica oculta até "Ver resposta"."""
                return render(request, "@@APP@@/exercicios.html")
            ''', APP=app) if s.exercicio else "")
    arq[f"web/{app}/urls.py"] = render(r'''
        from django.urls import path

        from . import api, views

        app_name = "@@APP@@"
        urlpatterns = [
            # CRUD básico: lista e detalhe (Read), criar (Create), editar (Update), excluir (Delete)
            path("", views.lista, name="lista"),
            path("novo/", views.criar, name="criar"),
            path("<@@CONV@@:pk>/", views.detalhe, name="detalhe"),
            path("<@@CONV@@:pk>/editar/", views.editar, name="editar"),
            path("<@@CONV@@:pk>/excluir/", views.excluir, name="excluir"),
            # API REST (JSON): a coleção (GET lista, POST cria) e um registro (GET, PUT, PATCH, DELETE);
            # os campos de cada endpoint são configuráveis (sgs api config) e quem chama escolhe com ?campos=
            path("api/v1/", api.colecao, name="api_colecao"),
            path("api/v1/campos/", api.campos, name="api_campos"),
            path("api/v1/<@@CONV@@:pk>/", api.item, name="api_item"),
            @@ROTAS_FINAIS@@
        ]
        ''', APP=app, CONV="uuid" if s.web["id_publico"] == "uuid" else "int",
        ROTAS_FINAIS='path("api/", api.resumo, name="api"),  # resumo do painel (itens + total) — o link "API"' + (
            '\npath("exercicios/", views.exercicios, name="exercicios"),  # questionário (modo exercício)'
            if s.exercicio else ""))
    arq.update(gerar_api_rest(s))
    arq.update(gerar_paginas_web(s))
    arq[f"web/{app}/tests/__init__.py"] = ""
    arq[f"web/{app}/tests/test_models.py"] = render(r'''
        """Testes do MODEL: a validação mora nos validators (mundo Django) — e save() sozinho não valida."""
        from decimal import Decimal

        import pytest
        from django.core.exceptions import ValidationError

        from @@APP@@.models import @@ENT@@


        def dados(**mudancas):
            copia = @@DADOS@@
            copia.update(mudancas)
            return copia


        @pytest.mark.django_db
        def test_cria_e_calcula_total():
            obj = @@ENT@@.objects.create(**dados())
            assert obj.total == Decimal("@@TOTAL@@")


        @pytest.mark.django_db
        def test_dados_validos_passam_no_full_clean():
            @@ENT@@(**dados()).full_clean()


        @pytest.mark.django_db
        @pytest.mark.parametrize("campo, valor", @@INVALIDOS@@)
        def test_full_clean_recusa_valor_invalido(campo, valor):
            with pytest.raises(ValidationError) as erro:
                @@ENT@@(**dados(**{campo: valor})).full_clean()
            assert campo in erro.value.message_dict


        @pytest.mark.django_db
        def test_save_sozinho_nao_valida():
            """Pegadinha dos 'dois mundos' (Aula 03): save() não chama full_clean()."""
            @@ENT@@(**dados(@@QTD@@=0)).save()
            assert @@ENT@@.objects.count() == 1
        ''', APP=app, ENT=ent, DADOS=django_dados(s), TOTAL=f"{total0:.2f}", INVALIDOS=django_invalidos(s), QTD=s.qtd)
    arq[f"web/{app}/tests/test_services.py"] = render(r'''
        """Testes do SERVICE web: regra sem HTTP, reaproveitando o Strategy do núcleo."""
        import ast
        import inspect
        import textwrap
        from decimal import Decimal

        import pytest

        from @@APP@@.models import @@ENT@@
        from @@APP@@.services import POLITICAS, @@ENT@@Service


        def novo(**mudancas):
            copia = @@DADOS@@
            copia.update(mudancas)
            return @@ENT@@(**copia)  # objeto em memória: nem precisa de banco


        @pytest.mark.parametrize("tipo, fator", [@@FATORES@@])
        def test_valor_final_usa_a_politica_do_nucleo(tipo, fator):
            obj = novo(tipo=tipo)
            assert @@ENT@@Service().valor_final(obj) == round(float(obj.total) * fator, 2)


        def test_todo_tipo_do_model_tem_politica():
            assert set(POLITICAS) == {chave for chave, _ in @@ENT@@.TIPOS}


        def test_resumo_soma_os_valores():
            itens, total = @@ENT@@Service().resumo([novo(), novo(tipo="@@K2@@")])
            assert len(itens) == 2 and total == round(sum(v for _, v in itens), 2)


        def test_service_nao_conhece_web():
            arvore = ast.parse(textwrap.dedent(inspect.getsource(@@ENT@@Service)))
            nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
            nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
            nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
            for palavra in ("request", "http", "template", "render"):
                assert not any(palavra in nome for nome in nomes), palavra
        ''', APP=app, ENT=ent, DADOS=django_dados(s), FATORES=fatores, K2=k2)
    arq[f"web/{app}/tests/test_views.py"] = render(r'''
        """Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
        import pytest
        from django.urls import reverse

        from @@APP@@.models import @@ENT@@


        def form_data(**mudancas):
            copia = @@FORM@@
            copia.update(mudancas)
            return copia


        @pytest.mark.django_db
        def test_lista_vazia(client):
            resposta = client.get(reverse("@@APP@@:lista"))
            assert resposta.status_code == 200
            assert "Nenhum registro ainda" in resposta.content.decode()


        @pytest.mark.django_db
        def test_criar_valido_salva_e_redireciona(client):
            resposta = client.post(reverse("@@APP@@:criar"), form_data())
            assert resposta.status_code == 302
            assert @@ENT@@.objects.count() == 1


        @pytest.mark.django_db
        def test_criar_invalido_nao_salva(client):
            resposta = client.post(reverse("@@APP@@:criar"), form_data(@@QTD@@="0"))
            assert resposta.status_code == 200
            assert @@ENT@@.objects.count() == 0


        @pytest.mark.django_db
        def test_lista_mostra_o_valor_com_a_politica(client):
            client.post(reverse("@@APP@@:criar"), form_data(tipo="@@K2@@"))
            html = client.get(reverse("@@APP@@:lista")).content.decode()
            assert "R$ @@VALOR2@@" in html


        @pytest.mark.django_db
        def test_api_devolve_json(client):
            client.post(reverse("@@APP@@:criar"), form_data())
            dados = client.get(reverse("@@APP@@:api")).json()
            assert len(dados["itens"]) == 1 and dados["total"] == "R$ @@VALOR1@@"


        # ---------------------------------------------------------------- CRUD: detalhe, editar e excluir
        def criado(client):
            client.post(reverse("@@APP@@:criar"), form_data())
            return @@ENT@@.objects.get()


        @pytest.mark.django_db
        def test_detalhe_mostra_o_registro(client):
            obj = criado(client)
            html = client.get(reverse("@@APP@@:detalhe", args=[obj.pk])).content.decode()
            assert str(obj.@@IDENT@@) in html and "Valor final" in html


        @pytest.mark.django_db
        def test_editar_altera_o_registro(client):
            obj = criado(client)
            resposta = client.post(reverse("@@APP@@:editar", args=[obj.pk]), form_data(@@QTD@@="3"))
            assert resposta.status_code == 302
            obj.refresh_from_db()
            assert obj.@@QTD@@ == 3


        @pytest.mark.django_db
        def test_editar_invalido_nao_altera(client):
            obj = criado(client)
            antes = obj.@@QTD@@
            resposta = client.post(reverse("@@APP@@:editar", args=[obj.pk]), form_data(@@QTD@@="0"))
            assert resposta.status_code == 200
            obj.refresh_from_db()
            assert obj.@@QTD@@ == antes


        @pytest.mark.django_db
        def test_excluir_so_com_post(client):
            obj = criado(client)
            assert client.get(reverse("@@APP@@:excluir", args=[obj.pk])).status_code == 200   # GET só confirma
            assert @@ENT@@.objects.count() == 1
            assert client.post(reverse("@@APP@@:excluir", args=[obj.pk])).status_code == 302
            assert @@ENT@@.objects.count() == 0


        @pytest.mark.django_db
        def test_registro_inexistente_da_404(client):
            obj = criado(client)
            pk = obj.pk
            obj.delete()
            for rota in ("@@APP@@:detalhe", "@@APP@@:editar", "@@APP@@:excluir"):
                assert client.get(reverse(rota, args=[pk])).status_code == 404
        ''', APP=app, ENT=ent, FORM=django_form(s), QTD=s.qtd, K2=k2, IDENT=s.ident,
        VALOR2=f"{round(total0 * f2, 2):.2f}", VALOR1=f"{round(total0 * s.variantes[0][1], 2):.2f}")
    arq.update(gerar_web_pronto(s))
    return arq


SETTINGS_BASELINE = '''
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
'''

CSS_CMD = """/* Estilo CMD: tela preta de terminal (gerado pelo SGS). */
:root { --fundo: #0c0c0c; --texto: #cccccc; --verde: #16c60c; --ciano: #61d6d6; --amarelo: #e5c07b; --borda: #2c2c2c; }
html, body { margin: 0; background: var(--fundo); color: var(--texto);
             font: 15px/1.55 "Cascadia Mono", Consolas, "DejaVu Sans Mono", monospace; }
.cmd-topo { color: var(--verde); font-weight: 700; padding: 14px 18px 0; }
.cmd-topo a { color: var(--verde); text-decoration: none; }
main { padding: 6px 18px 40px; max-width: 1000px; }
h1 { font-size: 1.1rem; color: var(--amarelo); margin: 10px 0; }
h1::before { content: "$ "; color: var(--verde); }
a { color: var(--ciano); }
.lista { list-style: none; padding: 0; }
.lista li::before { content: "> "; color: var(--verde); }
.acoes { display: flex; gap: 18px; margin: 8px 0 14px; }
input, select, textarea { background: #151515; color: var(--texto); border: 1px solid var(--verde); font: inherit; padding: 3px 6px; }
button { background: transparent; color: var(--verde); border: 1px solid var(--verde); font: inherit; padding: 3px 14px; cursor: pointer; }
button:hover { background: var(--verde); color: var(--fundo); }
.errorlist { color: #f14c4c; list-style: none; padding: 0; }
.apresentacao { border: 1px dashed var(--amarelo); color: var(--amarelo); padding: 6px 10px; margin: 8px 0; }
dt { color: var(--ciano); }
dd { margin: 0 0 6px 18px; }
.rodape { color: #7c7c7c; }
"""
CSS_BOOTSTRAP = """/* Ajustes do SGS sobre o Bootstrap (sem estilo inline nas páginas). */
.apresentacao { margin-bottom: 1rem; }
.tabela-vazia { color: var(--bs-secondary-color); }
"""
CSS_EIXOS = """/* Eixos de estilo (Instruções §11.10): atributos data-* no <html>, sem regenerar páginas. */
html[data-raio="reto"] { --bs-border-radius: 0; --bs-border-radius-sm: 0; --bs-border-radius-lg: 0; }
html[data-raio="arredondado"] { --bs-border-radius: .75rem; --bs-border-radius-lg: 1rem; }
html[data-raio="pilula"] { --bs-border-radius: 1rem; --bs-border-radius-lg: 1.25rem; }
html[data-raio="pilula"] .btn { border-radius: 50rem; }
html[data-sombra="nenhuma"] .card { box-shadow: none; }
html[data-sombra="suave"] .card { box-shadow: 0 1px 3px rgba(0, 0, 0, .08); }
html[data-sombra="marcada"] .card { box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .18); }
html[data-sombra="difusa"] .card { box-shadow: 0 .75rem 2rem rgba(0, 0, 0, .08); }
html[data-movimento="expressivo"] .card { transition: transform .2s ease; }
html[data-movimento="expressivo"] .card:hover { transform: translateY(-3px); }
html[data-tipografia="serifa-titulos"] h1, html[data-tipografia="serifa-titulos"] .navbar-brand { font-family: Georgia, "Times New Roman", serif; }
html[data-tipografia="arredondada"] body { font-family: "Segoe UI Rounded", "Nunito", system-ui, sans-serif; }
html[data-acessivel="sim"] body { font-size: 1.0625rem; }
html[data-acessivel="sim"] .form-control, html[data-acessivel="sim"] .form-select { border-width: 2px; }
html[data-acessivel="sim"] :focus-visible { outline: 3px solid var(--sgs-destaque); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
.apresentacao { margin-bottom: 1rem; }
"""
APP_JS = """// Script do site (arquivo estático: sem JavaScript inline, compatível com a CSP).
(function () {
  // PWA: registra o service worker (o site pode ser instalado e abrir numa janela própria).
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(function () {});
  }
  // Notas de apresentação: o botão mostra/oculta; a escolha fica guardada neste navegador.
  var botao = document.querySelector("[data-alternar-apresentacao]");
  if (!botao) {
    return;
  }
  var chave = "apresentacao-oculta";
  var oculta = false;
  try { oculta = localStorage.getItem(chave) === "1"; } catch (erro) {}
  function aplicar() {
    document.querySelectorAll("[data-apresentacao]").forEach(function (nota) { nota.hidden = oculta; });
    botao.setAttribute("aria-pressed", String(!oculta));
    botao.textContent = oculta ? "mostrar notas de apresentação" : "ocultar notas de apresentação";
  }
  aplicar();
  botao.addEventListener("click", function () {
    oculta = !oculta;
    try { localStorage.setItem(chave, oculta ? "1" : "0"); } catch (erro) {}
    aplicar();
  });
})();
"""


def gerar_paginas_web(s):
    """Templates (base.html fina + páginas) e estáticos conforme o ESTILO e as notas de apresentação.

    As páginas de domínio só preenchem blocos (title, page_title, toolbar_actions, content, extra_js):
    trocar o estilo/tema muda base.html e os CSS, não a regra (Instruções §11.5).
    """
    import temas_web
    arq, app, ent, w = {}, s.app, s.ent, s.web
    sistema_html = html.escape(s.sistema, quote=False)   # "Casa & Obra" → "Casa &amp; Obra"
    estilo, notas = w["estilo"], w["comentarios_web"]
    bs = estilo in ("bootstrap", "web")
    estatico = f"web/{app}/static/{app}"
    atributos_html, css = "", []
    cor_tema = {"simples": "#FFFFFF", "cmd": "#0C0C0C", "bootstrap": "#0D6EFD"}.get(estilo)
    if bs:
        for nome in ("bootstrap.min.css", "bootstrap.bundle.min.js", "LICENSE"):
            arq[f"{estatico}/vendor/bootstrap/{nome}"] = (BOOTSTRAP / nome).read_bytes()
        css.append("vendor/bootstrap/bootstrap.min.css")
    if estilo == "cmd":
        arq[f"{estatico}/css/estilo.css"] = CSS_CMD
        css.append("css/estilo.css")
    elif estilo == "bootstrap":
        arq[f"{estatico}/css/estilo.css"] = CSS_BOOTSTRAP
        css.append("css/estilo.css")
    elif estilo == "web":
        t = temas_web.resolver(w["tema"], w["tom"], w["paleta"])
        arq[f"{estatico}/css/tema.css"] = temas_web.css(w["tema"], w["tom"], w["paleta"])
        arq[f"{estatico}/css/base.css"] = CSS_EIXOS
        css += ["css/base.css", "css/tema.css"]
        cor_tema = t["destaque"]
        atributos_html = (f' data-bs-theme="{"dark" if t["escuro"] else "light"}" data-raio="{t["raio"]}"'
                          f' data-sombra="{t["sombra"]}" data-movimento="{t["movimento"]}"'
                          f' data-tipografia="{t["tipografia"]}" data-acessivel="{"sim" if t["acessivel"] else "nao"}"')
    arq[f"{estatico}/js/app.js"] = APP_JS
    links = "\n".join(f'<link rel="stylesheet" href="{{% static \'{app}/{c}\' %}}">' for c in css)
    scripts = [f'<script src="{{% static \'{app}/js/app.js\' %}}" defer></script>']
    if bs:
        scripts.insert(0, f'<script src="{{% static \'{app}/vendor/bootstrap/bootstrap.bundle.min.js\' %}}" defer></script>')
    classe_nota = "apresentacao alert alert-info small" if bs else "apresentacao"
    alternar = ('<button type="button" class="' + ("btn btn-sm btn-outline-secondary" if bs else "alternar")
                + '" data-alternar-apresentacao>ocultar notas de apresentação</button>') if notas else ""
    if bs:
        navbar_cls = "navbar navbar-expand navbar-sgs" if estilo == "web" else "navbar navbar-expand bg-primary"
        tema_nav = "" if estilo == "web" else ' data-bs-theme="dark"'
        topo = render(r'''
            <nav class="@@NAV@@"@@TEMANAV@@>
              <div class="container">
                <a class="navbar-brand" href="{% url '@@APP@@:lista' %}">@@SISTEMA@@</a>
                <div class="navbar-nav">
                  <a class="nav-link" href="{% url '@@APP@@:lista' %}">Lista</a>
                  <a class="nav-link" href="{% url '@@APP@@:criar' %}">Cadastrar</a>
                  <a class="nav-link" href="{% url '@@APP@@:api' %}">API</a>
                  @@LINK_EXERCICIOS@@
                </div>
              </div>
            </nav>
            ''', NAV=navbar_cls, TEMANAV=tema_nav, APP=app, SISTEMA=sistema_html,
            LINK_EXERCICIOS=(f'<a class="nav-link" href="{{% url \'{app}:exercicios\' %}}">Exercícios</a>'
                             if s.exercicio else "")).rstrip("\n")
        topo = "\n".join(linha for linha in topo.split("\n") if linha.strip())   # sem link → sem linha vazia
        corpo_abre, h1 = '<main class="container py-4">', '<h1 class="h3 mb-1">'
    elif estilo == "cmd":
        topo = f'<header class="cmd-topo"><a href="{{% url \'{app}:lista\' %}}">{sistema_html}</a></header>'
        corpo_abre, h1 = "<main>", "<h1>"
    else:
        topo, corpo_abre, h1 = "", "<main>", "<h1>"
    arq[f"web/{app}/templates/{app}/base.html"] = render(r'''
        {% load static %}<!doctype html>
        <html lang="pt-br"@@ATRIBUTOS@@>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta name="theme-color" content="@@COR@@">
          <link rel="manifest" href="/manifest.webmanifest">
          <link rel="icon" href="{% static '@@APP@@/icone-192.png' %}">
          @@LINKS@@
          <title>{% block title %}@@SISTEMA@@{% endblock %}</title>
        </head>
        <body>
          @@TOPO@@
          @@MAIN@@
            @@H1@@{% block page_title %}@@SISTEMA@@{% endblock %}</h1>
            {% block page_subtitle %}{% endblock %}
            @@ALTERNAR@@
            {% block toolbar_actions %}{% endblock %}
            {% block content %}{% endblock %}
          </main>
          @@SCRIPTS@@
          {% block extra_js %}{% endblock %}
        </body>
        </html>
        ''', ATRIBUTOS=atributos_html, COR=cor_tema, APP=app, LINKS=links, SISTEMA=sistema_html, TOPO=topo,
        MAIN=corpo_abre, H1=h1, ALTERNAR=alternar, SCRIPTS="\n".join(scripts))

    def nota(texto):
        return f'<aside class="{classe_nota}" data-apresentacao><strong>Apresentação ·</strong> {texto}</aside>' if notas else ""

    notas_lista = [nota(f"Esta página (view <code>lista</code>) é FINA: busca os registros, pede os valores ao "
                        f"<code>{ent}Service</code> e entrega tudo ao <code>PainelVM</code> (MVVM). O template só exibe."),
                   nota(f"O valor de cada linha passa pela política de {s.conceito} do núcleo (Strategy, "
                        "<code>nucleo/politicas.py</code>); o selo “com desconto / valor cheio” é decidido no "
                        "<code>ItemVM</code>.")]
    if w["id_interno"]:
        notas_lista.append(nota(f"A coluna ID interno é o código LNNL (motor-id-interno): 14 caracteres, tipo "
                                f"{w['lnnl_tipo']} e 2 dígitos verificadores módulo 79 — feito para pessoas lerem e ditarem."))
    if w["id_publico"] == "uuid":
        notas_lista.append(nota("A chave de cada registro é um UUIDv4 (Instruções §10.4): não dá para adivinhar o próximo."))
    if s.exercicio:
        notas_lista.append(nota("Modo exercício: o código deste site está completo. O questionário de revisão fica em "
                                "<code>/exercicios/</code> — cada pergunta esconde a resposta atrás do botão "
                                "<strong>Ver resposta</strong>."))
    rotulo_estilo = ESTILOS[estilo] + (f" — tema {w['tema']} {temas_web.TEMAS[w['tema']]['nome']}, "
                                       f"{temas_web.NOMES_TONS[w['tom']]}" if estilo == "web" else "")
    notas_lista.append(nota(f"Formatação: estilo <code>{estilo}</code> ({rotulo_estilo}). Trocar o estilo muda só "
                            "<code>base.html</code> e os CSS — as páginas de domínio não mudam."))
    notas_form = [nota(f"Formulário = <code>{ent}Form</code> (ModelForm): reaproveita os validators do model — "
                       "a mesma regra do encapsulamento, agora no mundo Django."),
                  nota("Ao salvar, <code>form.is_valid()</code> roda as validações; <code>save()</code> sozinho não "
                       "validaria (pegadinha testada em <code>tests/test_models.py</code>).")]
    acoes = (f'<p class="{"d-flex gap-2 my-3" if bs else "acoes"}">'
             f'<a class="{"btn btn-primary" if bs else ""}" href="{{% url \'{app}:criar\' %}}">Cadastrar {ent}</a> '
             f'<a class="{"btn btn-outline-primary" if bs else ""}" href="{{% url \'{app}:api\' %}}">API (JSON)</a>'
             + (f' <a href="{{% url \'{app}:exercicios\' %}}">Exercícios</a>' if s.exercicio and not bs else "")
             + "</p>")
    acoes = acoes.replace(' class=""', "")
    # Voltar do formulário: na edição volta ao detalhe do registro; no cadastro, à lista.
    voltar = f"{{% if obj %}}{{% url '{app}:detalhe' obj.pk %}}{{% else %}}{{% url '{app}:lista' %}}{{% endif %}}"
    if bs:
        col_codigo =("<th>ID interno</th>", "<td><code>{{ item.codigo }}</code></td>") if w["id_interno"] else ("", "")
        conteudo_lista = render(r'''
            <div class="card">
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead><tr>@@THC@@<th>Registro</th><th>@@CONCEITO@@</th><th class="text-end">Valor</th><th></th><th></th></tr></thead>
                  <tbody>
                  {% for item in painel.itens %}
                    <tr>@@TDC@@<td><a href="{% url '@@APP@@:detalhe' item.id %}">{{ item.titulo }}</a></td><td>{{ item.tipo_label }}</td>
                      <td class="text-end">{{ item.valor_formatado }}</td>
                      <td><span class="badge @@SELO@@">{{ item.selo }}</span></td>
                      <td class="text-end text-nowrap">
                        <a class="btn btn-sm btn-outline-primary" href="{% url '@@APP@@:editar' item.id %}">Editar</a>
                        <a class="btn btn-sm btn-outline-danger" href="{% url '@@APP@@:excluir' item.id %}">Excluir</a>
                      </td></tr>
                  {% endfor %}
                  </tbody>
                </table>
              </div>
              <div class="card-footer text-body-secondary small">{{ painel.rodape }}</div>
            </div>
            ''', THC=col_codigo[0], TDC=col_codigo[1], CONCEITO=s.conceito.capitalize(), APP=app,
            SELO="badge-destaque" if estilo == "web" else "text-bg-primary").rstrip("\n")
        conteudo_form = render(r'''
            <div class="card"><div class="card-body">
              <form method="post">
                {% csrf_token %}
                {% for erro in form.non_field_errors %}<div class="alert alert-danger">{{ erro }}</div>{% endfor %}
                {% for campo in form %}
                <div class="mb-3">
                  <label class="form-label" for="{{ campo.id_for_label }}">{{ campo.label }}</label>
                  {{ campo }}
                  {% for erro in campo.errors %}<div class="invalid-feedback d-block">{{ erro }}</div>{% endfor %}
                </div>
                {% endfor %}
                <button type="submit" class="btn btn-primary">Salvar</button>
                <a class="btn btn-outline-primary" href="@@VOLTAR@@">Voltar</a>
              </form>
            </div></div>
            ''', VOLTAR=voltar).rstrip("\n")
    else:
        codigo = "{{ item.codigo }} · " if w["id_interno"] else ""
        conteudo_lista = render(r'''
            <ul class="lista">
            {% for item in painel.itens %}
              <li>@@COD@@<a href="{% url '@@APP@@:detalhe' item.id %}">{{ item.titulo }}</a> · {{ item.tipo_label }} · {{ item.valor_formatado }} ({{ item.selo }})
                · <a href="{% url '@@APP@@:editar' item.id %}">editar</a> · <a href="{% url '@@APP@@:excluir' item.id %}">excluir</a></li>
            {% endfor %}
            </ul>
            <p class="rodape">{{ painel.rodape }}</p>
            ''', COD=codigo, APP=app).rstrip("\n")
        conteudo_form = render(r'''
            <form method="post">
              {% csrf_token %}
              {{ form.as_p }}
              <button type="submit">Salvar</button>
            </form>
            <p><a href="@@VOLTAR@@">Voltar</a></p>
            ''', VOLTAR=voltar).rstrip("\n")
    arq[f"web/{app}/templates/{app}/lista.html"] = render(r'''
        {% extends "@@APP@@/base.html" %}
        {% block toolbar_actions %}@@ACOES@@{% endblock %}
        {% block content %}
        @@NOTAS@@
        @@CONTEUDO@@
        {% endblock %}
        ''', APP=app, ACOES=acoes, NOTAS="\n".join(n for n in notas_lista if n), CONTEUDO=conteudo_lista)
    arq[f"web/{app}/templates/{app}/form.html"] = render(r'''
        {% extends "@@APP@@/base.html" %}
        {% block title %}{% if obj %}Editar{% else %}Cadastrar{% endif %} @@ENT@@ — @@SISTEMA@@{% endblock %}
        {% block page_title %}{% if obj %}Editar{% else %}Cadastrar{% endif %} @@ENT@@{% endblock %}
        {% block content %}
        @@NOTAS@@
        @@CONTEUDO@@
        {% endblock %}
        ''', APP=app, ENT=ent, SISTEMA=sistema_html, NOTAS="\n".join(n for n in notas_form if n), CONTEUDO=conteudo_form)
    # ---- CRUD: detalhe (Read de um registro) e confirmação da exclusão (Delete só por POST)
    nota_detalhe = nota("Detalhe = view <code>detalhe</code> (fina) + <code>DetalheVM</code>, que prepara cada campo "
                        "com rótulo e valor legível (MVVM). O valor final vem do Service com o Strategy do núcleo.")
    nota_excluir = nota("Excluir: o GET só mostra esta confirmação; apagar exige POST com o token CSRF — um link "
                        "aberto por engano (ou por um robô) nunca apaga nada.")
    if bs:
        dados_detalhe = render(r'''
            <div class="card"><div class="card-body">
              <dl class="row mb-0">
              {% for rotulo, valor in item.campos %}
                <dt class="col-sm-4">{{ rotulo }}</dt><dd class="col-sm-8">{{ valor }}</dd>
              {% endfor %}
                <dt class="col-sm-4">Valor final</dt>
                <dd class="col-sm-8">{{ item.valor_formatado }} <span class="badge @@SELO@@">{{ item.selo }}</span></dd>
              </dl>
            </div></div>
            <p class="d-flex gap-2 my-3">
              <a class="btn btn-primary" href="{% url '@@APP@@:editar' item.id %}">Editar</a>
              <a class="btn btn-outline-danger" href="{% url '@@APP@@:excluir' item.id %}">Excluir</a>
              <a class="btn btn-outline-primary" href="{% url '@@APP@@:lista' %}">Voltar</a>
            </p>
            ''', APP=app, SELO="badge-destaque" if estilo == "web" else "text-bg-primary").rstrip("\n")
        dados_excluir = render(r'''
            <div class="card"><div class="card-body">
              <p>Excluir “{{ obj }}”? Esta ação não pode ser desfeita.</p>
              <form method="post" class="d-flex gap-2">
                {% csrf_token %}
                <button type="submit" class="btn btn-danger">Excluir</button>
                <a class="btn btn-outline-primary" href="{% url '@@APP@@:detalhe' obj.pk %}">Cancelar</a>
              </form>
            </div></div>
            ''', APP=app).rstrip("\n")
    else:
        dados_detalhe = render(r'''
            <dl>
            {% for rotulo, valor in item.campos %}
              <dt>{{ rotulo }}</dt><dd>{{ valor }}</dd>
            {% endfor %}
              <dt>Valor final</dt><dd>{{ item.valor_formatado }} ({{ item.selo }})</dd>
            </dl>
            <p class="acoes"><a href="{% url '@@APP@@:editar' item.id %}">Editar</a>
              <a href="{% url '@@APP@@:excluir' item.id %}">Excluir</a> <a href="{% url '@@APP@@:lista' %}">Voltar</a></p>
            ''', APP=app).rstrip("\n")
        dados_excluir = render(r'''
            <p>Excluir “{{ obj }}”? Esta ação não pode ser desfeita.</p>
            <form method="post">
              {% csrf_token %}
              <button type="submit">Excluir</button>
            </form>
            <p><a href="{% url '@@APP@@:detalhe' obj.pk %}">Cancelar</a></p>
            ''', APP=app).rstrip("\n")
    arq[f"web/{app}/templates/{app}/detalhe.html"] = render(r'''
        {% extends "@@APP@@/base.html" %}
        {% block title %}{{ item.titulo }} — @@SISTEMA@@{% endblock %}
        {% block page_title %}{{ item.titulo }}{% endblock %}
        {% block content %}
        @@NOTA@@
        @@CONTEUDO@@
        {% endblock %}
        ''', APP=app, SISTEMA=sistema_html, NOTA=nota_detalhe, CONTEUDO=dados_detalhe)
    arq[f"web/{app}/templates/{app}/confirmar_exclusao.html"] = render(r'''
        {% extends "@@APP@@/base.html" %}
        {% block title %}Excluir @@ENT@@ — @@SISTEMA@@{% endblock %}
        {% block page_title %}Excluir @@ENT@@{% endblock %}
        {% block content %}
        @@NOTA@@
        @@CONTEUDO@@
        {% endblock %}
        ''', APP=app, ENT=ent, SISTEMA=sistema_html, NOTA=nota_excluir, CONTEUDO=dados_excluir)
    if s.exercicio:
        # Questionário de revisão: conteúdo fixo, gerado aqui; {% verbatim %} garante que nada vire tag do Django.
        nota_exercicios = nota("Questionário gerado dos mesmos textos do README e dos ADRs. Sem JavaScript: "
                               "cada resposta é um <code>&lt;details&gt;</code> que só abre no botão.")
        arq[f"web/{app}/templates/{app}/exercicios.html"] = render(r'''
            {% extends "@@APP@@/base.html" %}
            {% block title %}Exercícios — @@SISTEMA@@{% endblock %}
            {% block page_title %}Exercícios — @@SISTEMA@@{% endblock %}
            {% block content %}
            @@NOTA@@
            {% verbatim %}
            @@CONTEUDO@@
            {% endverbatim %}
            {% endblock %}
            ''', APP=app, SISTEMA=sistema_html, NOTA=nota_exercicios, CONTEUDO=html_questionario(s, bs))
        arq[f"web/{app}/tests/test_exercicios.py"] = render(r'''
            """Página de exercícios (modo exercício): questionário com a resposta oculta atrás de "Ver resposta"."""
            import re

            import pytest
            from django.urls import reverse


            @pytest.mark.django_db
            def test_pagina_de_exercicios_mostra_o_questionario(client):
                resposta = client.get(reverse("@@APP@@:exercicios"))
                assert resposta.status_code == 200
                html = resposta.content.decode()
                assert html.count("<details") == @@N@@                 # uma resposta oculta por pergunta
                assert html.count(">Ver resposta</summary>") == @@N@@
                assert "style=" not in html and "onclick" not in html.lower()
                assert not re.search(r"<script(?![^>]*\bsrc=)", html)   # nenhum script inline (CSP)


            @pytest.mark.django_db
            def test_lista_tem_link_para_os_exercicios(client):
                html = client.get(reverse("@@APP@@:lista")).content.decode()
                assert reverse("@@APP@@:exercicios") in html
            ''', APP=app, N=total_perguntas(s))
    return arq


def gerar_testes_opcoes_web(s):
    """Testes das opções web: estilo (sem estilo/script inline — Instruções §22.1 nº 15), notas de
    apresentação, ID interno LNNL, UUIDv4 e o baseline de segurança."""
    arq, app, ent, w = {}, s.app, s.ent, s.web
    arq[f"web/{app}/tests/test_estilo.py"] = render(r'''
        """Testes do ESTILO "@@ESTILO@@": páginas com os estáticos certos e sem estilo/script inline (CSP)."""
        import re

        import pytest
        from django.contrib.staticfiles import finders
        from django.urls import reverse

        ESTATICOS = @@ESTATICOS@@
        NOTAS = @@NOTAS@@


        @pytest.mark.django_db
        @pytest.mark.parametrize("rota", ["@@APP@@:lista", "@@APP@@:criar"])
        def test_pagina_usa_os_estaticos_do_estilo(client, rota):
            html = client.get(reverse(rota)).content.decode()
            for caminho in ESTATICOS:
                assert caminho in html
                assert finders.find(caminho), caminho


        @pytest.mark.django_db
        @pytest.mark.parametrize("rota", ["@@APP@@:lista", "@@APP@@:criar"])
        def test_sem_estilo_nem_script_inline(client, rota):
            html = client.get(reverse(rota)).content.decode()
            assert "style=" not in html and "onclick=" not in html
            assert not re.search(r"<script(?![^>]*\bsrc=)", html)


        @pytest.mark.django_db
        def test_notas_de_apresentacao(client):
            html = client.get(reverse("@@APP@@:lista")).content.decode()
            assert ("data-apresentacao" in html) is NOTAS
            assert ("data-alternar-apresentacao" in html) is NOTAS
        ''', ESTILO=w["estilo"], APP=app, NOTAS=lit(w["comentarios_web"]),
        ESTATICOS=lit([f"{app}/js/app.js"] + ([f"{app}/vendor/bootstrap/bootstrap.min.css"]
                                               if w["estilo"] in ("bootstrap", "web") else [])
                      + ([f"{app}/css/estilo.css"] if w["estilo"] in ("cmd", "bootstrap") else [])
                      + ([f"{app}/css/tema.css", f"{app}/css/base.css"] if w["estilo"] == "web" else [])))
    if w["id_interno"]:
        arq[f"web/{app}/tests/test_lnnl.py"] = render(r'''
            """Testes do ID interno LNNL (motor-id-interno): gerado no save(), válido, legível e único."""
            import re
            from decimal import Decimal

            import pytest
            from django.core.exceptions import ValidationError

            from @@APP@@ import lnnl
            from @@APP@@.models import TIPO_LNNL, @@ENT@@, validar_codigo_lnnl


            def novo(**mudancas):
                copia = @@DADOS@@
                copia.update(mudancas)
                return @@ENT@@.objects.create(**copia)


            @pytest.mark.django_db
            def test_id_interno_gerado_no_save_e_valido_do_tipo():
                obj = novo()
                assert lnnl.validar(obj.id_interno, TIPO_LNNL) and lnnl.extrair_tipo(obj.id_interno) == TIPO_LNNL


            @pytest.mark.django_db
            def test_id_interno_formatado_na_mascara_lnnl():
                mascara = r"[A-Z][1-9]{2}[A-Z]-[A-Z][1-9]{2}[A-Z]-[A-Z][1-9][A-Z]-[A-Z][1-9][A-Z]"   # LNNL-LNNL-LNL-LNL
                assert re.fullmatch(mascara, novo().id_interno_formatado)


            @pytest.mark.django_db
            def test_salvar_de_novo_nao_troca_o_id_interno():
                obj = novo()
                antes = obj.id_interno
                obj.save()
                assert obj.id_interno == antes


            @pytest.mark.django_db
            def test_colisao_insere_e_tenta_de_novo(monkeypatch):
                primeiro = novo()
                sorteios = iter([primeiro.id_interno, lnnl.gerar(TIPO_LNNL)])   # 1º sorteio repete um ID
                monkeypatch.setattr(lnnl, "gerar", lambda tipo: next(sorteios))
                assert novo().id_interno != primeiro.id_interno


            def test_validador_recusa_codigo_invalido():
                codigo = lnnl.gerar(TIPO_LNNL)
                errado = codigo[:13] + ("A" if codigo[13] != "A" else "B")   # troca a última letra
                with pytest.raises(ValidationError):
                    validar_codigo_lnnl(errado)


            @pytest.mark.django_db
            def test_api_mostra_o_codigo(client):
                obj = novo()
                from django.urls import reverse
                assert client.get(reverse("@@APP@@:api")).json()["itens"][0]["codigo"] == obj.id_interno_formatado
            ''', APP=app, ENT=ent, DADOS=django_dados(s))
    if w["id_publico"] == "uuid":
        arq[f"web/{app}/tests/test_uuid.py"] = render(r'''
            """Teste do identificador UUIDv4 (Instruções §10.4)."""
            import uuid
            from decimal import Decimal

            import pytest

            from @@APP@@.models import @@ENT@@


            @pytest.mark.django_db
            def test_chave_primaria_e_uuid4():
                obj = @@ENT@@.objects.create(**@@DADOS@@)
                assert isinstance(obj.pk, uuid.UUID) and obj.pk.version == 4
            ''', APP=app, ENT=ent, DADOS=django_dados(s))
    if w["seguranca"] == "baseline":
        arq["web/conftest.py"] = render(r'''
            """Testes com o baseline de segurança: o cliente de testes fala HTTP, então sem redirecionar para HTTPS."""
            import pytest


            @pytest.fixture(autouse=True)
            def _sem_https_nos_testes(settings):
                settings.SECURE_SSL_REDIRECT = False
            ''')
        arq[f"web/{app}/tests/test_seguranca.py"] = render(r'''
            """Testes do baseline de segurança (Instruções §12–14 e §22.1: cabeçalhos, cookies, CSP, admin)."""
            import pytest
            from django.urls import reverse


            @pytest.mark.django_db
            def test_cabecalhos_de_seguranca(client):
                resposta = client.get(reverse("@@APP@@:lista"))
                assert resposta["X-Frame-Options"] == "DENY"
                assert resposta["X-Content-Type-Options"] == "nosniff"
                assert resposta["Referrer-Policy"] == "same-origin"
                assert resposta["Cross-Origin-Opener-Policy"] == "same-origin"
                politica = resposta.get("Content-Security-Policy-Report-Only") or resposta["Content-Security-Policy"]
                assert "default-src 'self'" in politica and "frame-ancestors 'none'" in politica


            def test_cookies_e_limites(settings):
                assert settings.SESSION_COOKIE_HTTPONLY is True
                assert settings.SESSION_COOKIE_SAMESITE == settings.CSRF_COOKIE_SAMESITE == "Lax"
                assert settings.DATA_UPLOAD_MAX_MEMORY_SIZE == 1_048_576


            @pytest.mark.django_db
            def test_admin_fora_do_endereco_padrao(client, settings):
                assert settings.ADMIN_URL != "admin/"
                assert client.get("/admin/").status_code == 404


            @pytest.mark.django_db
            def test_get_nao_altera_estado(client):
                from @@APP@@.models import @@ENT@@
                client.get(reverse("@@APP@@:criar"))
                assert @@ENT@@.objects.count() == 0
            ''', APP=app, ENT=ent)
    return arq


def gerar_web_pronto(s):
    """O que deixa o site pronto para subir: comando do superusuário, testes dele e o iniciar.sh."""
    arq, app = {}, s.app
    arq[f"web/{app}/management/__init__.py"] = ""
    arq[f"web/{app}/management/commands/__init__.py"] = ""
    arq[f"web/{app}/management/commands/garantir_admin.py"] = render(r'''
        """
        `python manage.py garantir_admin`: cria (ou atualiza) o superusuário a partir do ambiente / web/.env.

        Usa as mesmas variáveis do `createsuperuser --noinput` do Django:
        DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD.
        Diferença: pode rodar quantas vezes quiser — se o usuário já existe, atualiza e-mail e senha.
        """
        import os

        from django.contrib.auth import get_user_model
        from django.core.management.base import BaseCommand, CommandError


        class Command(BaseCommand):
            help = "Cria ou atualiza o superusuário com os dados do web/.env (pode rodar várias vezes)."

            def handle(self, *args, **opcoes):
                usuario = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
                email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
                senha = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
                if not usuario or not senha:
                    raise CommandError("defina DJANGO_SUPERUSER_USERNAME e DJANGO_SUPERUSER_PASSWORD no web/.env")
                modelo = get_user_model()
                obj, criado = modelo.objects.get_or_create(username=usuario, defaults={"email": email})
                obj.email = email
                obj.is_staff = obj.is_superuser = True
                obj.set_password(senha)  # guarda o HASH da senha, nunca o texto
                obj.save()
                self.stdout.write(self.style.SUCCESS(f"superusuário {'criado' if criado else 'atualizado'}: {usuario}"))
        ''')
    arq[f"web/{app}/tests/test_admin.py"] = render(r'''
        """Testes da preparação do site: comando garantir_admin, leitor de .env e tela de login do admin."""
        import pytest
        from django.contrib.auth import authenticate, get_user_model
        from django.core.management import call_command
        from django.core.management.base import CommandError

        from config.env import ler_env


        @pytest.fixture
        def credenciais(monkeypatch):
            monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "professor")
            monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "professor@exemplo.com")
            monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "senha-de-teste-1")


        @pytest.mark.django_db
        def test_cria_o_superusuario(credenciais):
            call_command("garantir_admin")
            usuario = get_user_model().objects.get(username="professor")
            assert usuario.is_superuser and usuario.is_staff
            assert authenticate(username="professor", password="senha-de-teste-1") is not None


        @pytest.mark.django_db
        def test_rodar_de_novo_atualiza_a_senha(credenciais, monkeypatch):
            call_command("garantir_admin")
            monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "outra-senha-2")
            call_command("garantir_admin")
            assert get_user_model().objects.filter(username="professor").count() == 1
            assert authenticate(username="professor", password="outra-senha-2") is not None


        @pytest.mark.django_db
        def test_sem_senha_explica_o_que_falta(monkeypatch):
            monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "professor")
            monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
            with pytest.raises(CommandError):
                call_command("garantir_admin")


        def test_leitor_de_env(tmp_path):
            arquivo = tmp_path / ".env"
            arquivo.write_text('# comentário\nA=1\nB = "com espaço"\n\nlinha sem igual\nC=x=y\n', encoding="utf-8")
            assert ler_env(arquivo) == {"A": "1", "B": "com espaço", "C": "x=y"}


        def test_env_que_nao_existe_nao_quebra(tmp_path):
            assert ler_env(tmp_path / "nao_existe") == {}


        @pytest.mark.django_db
        def test_admin_pede_login(client):
            from django.urls import reverse
            resposta = client.get(reverse("admin:index"))   # o endereço vem do ADMIN_URL (web/.env)
            assert resposta.status_code == 302 and reverse("admin:login") in resposta["Location"]
        ''')
    arq[f"web/{app}/tests/test_pwa.py"] = render(r'''
        """Testes do PWA: manifest (janela de app), service worker na raiz, ícones e páginas apontando para eles."""
        import json

        import pytest
        from django.contrib.staticfiles import finders
        from django.urls import reverse


        def test_manifest_abre_como_app(client):
            resposta = client.get("/manifest.webmanifest")
            dados = json.loads(resposta.content)
            assert resposta.status_code == 200 and resposta["Content-Type"].startswith("application/manifest+json")
            assert dados["display"] == "standalone" and dados["start_url"] == "/"
            assert {icone["sizes"] for icone in dados["icons"]} == {"192x192", "512x512"}


        def test_service_worker_na_raiz(client):
            resposta = client.get("/sw.js")
            assert resposta.status_code == 200 and "javascript" in resposta["Content-Type"]
            assert resposta["Service-Worker-Allowed"] == "/" and "fetch" in resposta.content.decode()


        @pytest.mark.parametrize("tamanho", [192, 512])
        def test_icones_sao_png(tamanho):
            with open(finders.find(f"@@APP@@/icone-{tamanho}.png"), "rb") as arquivo:
                assert arquivo.read(8) == b"\x89PNG\r\n\x1a\n"


        @pytest.mark.django_db
        @pytest.mark.parametrize("rota", ["@@APP@@:lista", "@@APP@@:criar"])
        def test_paginas_apontam_para_o_manifest(client, rota):
            html = client.get(reverse(rota)).content.decode()
            assert 'rel="manifest"' in html and "js/app.js" in html


        def test_app_js_registra_o_service_worker():
            with open(finders.find("@@APP@@/js/app.js"), encoding="utf-8") as arquivo:
                assert "serviceWorker" in arquivo.read()
        ''', APP=app)
    arq.update(gerar_testes_opcoes_web(s))
    arq["iniciar.sh"] = render(r'''
        #!/usr/bin/env bash
        unset DJANGO_SETTINGS_MODULE
        # =============================================================================
        # iniciar.sh — prepara e sobe o site Django do sistema "@@SISTEMA@@" (gerado).
        #
        #   bash iniciar.sh                 tudo: venv → deps → .env → migrations → admin → servidor
        #   bash iniciar.sh tudo 8001       tudo, em outra porta
        #   bash iniciar.sh preparar        tudo, MENOS subir o servidor
        #   source iniciar.sh ativar        prepara se precisar e ATIVA o .venv no seu terminal atual
        #   bash iniciar.sh venv            cria .venv nesta pasta (se não existir)
        #   bash iniciar.sh deps            instala o requirements.txt (só se faltar alguma dependência)
        #   bash iniciar.sh env             cria web/.env a partir de web/.env.example (nunca sobrescreve)
        #   bash iniciar.sh migrar          makemigrations @@APP@@ + migrate
        #   bash iniciar.sh admin           cria/atualiza o superusuário (dados do web/.env)
        #   bash iniciar.sh testar          testes do núcleo e da web
        #   bash iniciar.sh rodar [porta]   sobe o servidor em http://127.0.0.1:porta (Ctrl+C para parar)
        #
        # O site abre sozinho no navegador: PWA=1 (padrão, no web/.env) = janela de app isolada das abas;
        # PWA=0 = aba comum; ABRIR=0 = não abre nada.
        #
        # Variáveis opcionais:
        #   VENV=/caminho/.venv   usa um ambiente virtual que já existe (ex.: o do SGS, Gerador_Sistemas/.venv)
        #   PY=/caminho/python    usa um Python específico (ignora VENV)
        #   PWA=0|1, ABRIR=0      como (e se) abrir o navegador
        #   DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD   têm prioridade sobre o web/.env
        # =============================================================================

        _foi_sourced() { [ "${BASH_SOURCE[0]}" != "$0" ]; }

        RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        WEB="$RAIZ/web"
        _VENV_EXPLICITO="${VENV:-}"
        _PY_EXPLICITO="${PY:-}"

        _python_do_venv() {
          local v="$1"
          if [ -x "$v/bin/python" ]; then echo "$v/bin/python"; return 0; fi
          if [ -x "$v/Scripts/python.exe" ]; then echo "$v/Scripts/python.exe"; return 0; fi
          echo "$v/bin/python"
        }

        _activate_do_venv() {
          local v="$1"
          if [ -f "$v/bin/activate" ]; then echo "$v/bin/activate"; return 0; fi
          if [ -f "$v/Scripts/activate" ]; then echo "$v/Scripts/activate"; return 0; fi
          return 1
        }

        _resolver_venv() {
          if [ -n "$_VENV_EXPLICITO" ]; then
            VENV="$_VENV_EXPLICITO"
          elif [ -x "$RAIZ/.venv/bin/python" ] || [ -x "$RAIZ/.venv/Scripts/python.exe" ]; then
            VENV="$RAIZ/.venv"
          elif [ "${1:-}" != "venv" ] && { [ -x "$RAIZ/../../.venv/bin/python" ] || [ -x "$RAIZ/../../.venv/Scripts/python.exe" ]; }; then
            VENV="$(cd "$RAIZ/../.." && pwd)/.venv"
          else
            VENV="$RAIZ/.venv"
          fi
          if [ -n "$_PY_EXPLICITO" ]; then
            PY="$_PY_EXPLICITO"
          else
            PY="$(_python_do_venv "$VENV")"
          fi
        }

        passo() { printf '\n==> %s\n' "$*"; }

        achar_python_base() {
          local cand
          for cand in python3 python3.14 python3.13 python3.12 python; do
            if command -v "$cand" >/dev/null 2>&1; then
              if "$cand" -c 'import sys; sys.exit(sys.version_info < (@@PYMAJ@@, @@PYMIN@@))' 2>/dev/null; then
                echo "$cand"
                return 0
              fi
            fi
          done
          return 1
        }

        criar_venv() {
          if [ -x "$PY" ]; then echo "ambiente ok: $PY"; return 0; fi
          # O Python exigido está no cabeçalho do requirements.txt (o pip não instala Python).
          local py_base
          if ! py_base="$(achar_python_base)"; then
            echo "ERRO: este sistema precisa do Python @@PYMAJ@@.@@PYMIN@@ ou mais novo — achei $(python3 --version 2>&1 || python --version 2>&1 || echo 'nenhum Python')" >&2
            return 1
          fi
          passo "criando o ambiente virtual em $VENV (com $py_base)"
          if ! "$py_base" -m venv "$VENV"; then
            rm -rf "$VENV"
            echo "ERRO: falhou ao criar o ambiente virtual em $VENV." >&2
            echo "      No Ubuntu/WSL, instale o pacote venv:  sudo apt update && sudo apt install -y python3-venv" >&2
            return 1
          fi
          PY="$(_python_do_venv "$VENV")"
        }

        instalar_deps() {
          [ -f "$RAIZ/requirements.txt" ] || return 0
          # Tudo do requirements.txt já instalado? (--no-index: o pip só confere o que já está aqui, sem internet)
          if "$PY" -m pip install -q --disable-pip-version-check --no-index -r "$RAIZ/requirements.txt" \
               >/dev/null 2>&1; then
            echo "dependências ok (todas as do requirements.txt já estão instaladas)"
            return 0
          fi
          passo "instalando as dependências do requirements.txt"
          "$PY" -m pip install --upgrade pip >/dev/null 2>&1 || true
          "$PY" -m pip install -r "$RAIZ/requirements.txt"
        }

        criar_env() {
          [ -f "$WEB/.env.example" ] || { echo "web/.env.example não encontrado — pulando .env"; return 0; }
          if [ -f "$WEB/.env" ]; then echo "web/.env ok (já existe — não sobrescrevo)"; return 0; fi
          passo "criando web/.env a partir de web/.env.example"
          cp "$WEB/.env.example" "$WEB/.env"
          local py="$PY"
          [ -x "$py" ] || py="$(achar_python_base || echo python3)"
          "$py" -c 'import pathlib, re, secrets, sys; p = pathlib.Path(sys.argv[1]); p.write_text(re.sub(r"^SECRET_KEY=.*$", "SECRET_KEY=" + secrets.token_urlsafe(40), p.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8", newline="\n")' "$WEB/.env"
        }

        migrar() {
          [ -f "$WEB/manage.py" ] || return 0
          passo "migrations"
          (unset DJANGO_SETTINGS_MODULE; cd "$WEB" && "$PY" manage.py makemigrations @@APP@@ && "$PY" manage.py migrate)
        }

        criar_admin() {
          [ -f "$WEB/manage.py" ] || return 0
          passo "superusuário"
          (unset DJANGO_SETTINGS_MODULE; cd "$WEB" && "$PY" manage.py garantir_admin)
        }

        testar() {
          passo "testes do núcleo"
          (unset DJANGO_SETTINGS_MODULE; cd "$RAIZ" && "$PY" -m pytest -q -p no:cacheprovider)
          passo "testes da web"
          (unset DJANGO_SETTINGS_MODULE; cd "$WEB" && "$PY" -m pytest -q -p no:cacheprovider)
        }

        abrir_navegador() {
          # PWA=1: janela de app (--app = sem abas nem barra de endereço) · PWA=0: aba comum do navegador padrão.
          local url="$1" exe="" pwa="${PWA:-}"
          [ "${ABRIR:-1}" = "0" ] && return 0
          [ -z "$pwa" ] && [ -f "$WEB/.env" ] && pwa="$(sed -n 's/^PWA=//p' "$WEB/.env" | tail -1)"
          for candidato in "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
                           "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
                           "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"; do
            if [ -x "$candidato" ]; then exe="$candidato"; break; fi
          done
          if [ "${pwa:-1}" = "1" ] && [ -n "$exe" ]; then ("$exe" --app="$url" >/dev/null 2>&1 &)
          elif command -v wslview >/dev/null 2>&1; then (wslview "$url" >/dev/null 2>&1 &)
          elif [ -x /mnt/c/Windows/System32/cmd.exe ]; then (cd /mnt/c && /mnt/c/Windows/System32/cmd.exe /c start "" "$url" >/dev/null 2>&1 &)
          elif command -v xdg-open >/dev/null 2>&1; then (xdg-open "$url" >/dev/null 2>&1 &)
          fi
          return 0
        }

        porta_livre() {
          "$PY" -c "import socket, sys; s = socket.socket(); rc = s.connect_ex(('127.0.0.1', int(sys.argv[1]))); s.close(); sys.exit(0 if rc != 0 else 1)" "$1"
        }

        rodar() {
          local porta="${1:-}"
          if [ -z "$porta" ] && [ -f "$WEB/.env" ]; then porta="$(sed -n 's/^PORTA=//p' "$WEB/.env" | tail -1)"; fi
          porta="${porta:-8000}"
          if ! porta_livre "$porta"; then
            echo "ERRO: a porta $porta já está em uso. Tente outra porta:  bash iniciar.sh rodar $((porta + 1))" >&2
            return 1
          fi
          local admin=""
          [ -f "$WEB/.env" ] && admin="$(sed -n 's/^ADMIN_URL=//p' "$WEB/.env" | tail -1)"
          passo "site em http://127.0.0.1:$porta/  ·  admin em http://127.0.0.1:$porta/${admin:-admin/}  ·  Ctrl+C para parar"
          (sleep 2; abrir_navegador "http://127.0.0.1:$porta/") &   # abre depois que o servidor sobe
          unset DJANGO_SETTINGS_MODULE
          cd "$WEB"
          # shellcheck disable=SC2086  # RUNSERVER_OPCOES pode ter várias opções (ex.: --noreload)
          exec "$PY" manage.py runserver "127.0.0.1:$porta" ${RUNSERVER_OPCOES:-}
        }

        _resolver_venv "${1:-tudo}"

        if _foi_sourced; then
          criar_venv || return 1
          instalar_deps || return 1
          criar_env || return 1
          _ACT="$(_activate_do_venv "$VENV")" || { echo "ERRO: activate não encontrado em $VENV" >&2; return 1; }
          # shellcheck disable=SC1090
          source "$_ACT"
          echo "ambiente ativado: $VENV"
          return 0
        fi

        set -euo pipefail
        case "${1:-tudo}" in
          tudo)      criar_venv; instalar_deps; criar_env; migrar; criar_admin; rodar "${2:-}" ;;
          preparar)  criar_venv; instalar_deps; criar_env; migrar; criar_admin ;;
          ativar)    criar_venv; instalar_deps; echo "Para ativar no terminal atual, rode:  source iniciar.sh ativar" ;;
          venv)      criar_venv ;;
          deps)      criar_venv; instalar_deps ;;
          env)       criar_env ;;
          migrar)    migrar ;;
          admin)     criar_admin ;;
          testar)    testar ;;
          rodar)     rodar "${2:-}" ;;
          ajuda|-h|--help) awk 'NR > 1 && /^_foi_sourced/ { exit } NR > 1 && !/^# =/ { sub(/^# ?/, ""); print }' "$0" ;;
          *) echo "comando desconhecido: $1  (veja: bash iniciar.sh ajuda)" >&2; exit 2 ;;
        esac
        ''', SISTEMA=s.sistema, APP=app, PYMAJ=str(PYTHON_MINIMO[0]), PYMIN=str(PYTHON_MINIMO[1]))
    return arq


# =============================================================================
# 6. DOCUMENTAÇÃO GERADA (README + ADRs)
# =============================================================================
def gerar_readme(s, nome_pasta):
    tv = s.textos()
    padroes_txt = ", ".join(PADROES[p]["titulo"] for p in s.padroes)
    if s.origem.get("assunto"):
        a = s.origem
        dom = f"`{a['dominio']}`" + (f" (palavras: {', '.join(a['dominio_palavras'])})" if a["dominio_palavras"]
                                     else " (nenhuma palavra de domínio reconhecida → domínio genérico)")
        linhas_p = [f"| {PADROES[p]['titulo']} | {', '.join(a['padroes_palavras'][p])} |"
                    for p in s.padroes if p in a["padroes_palavras"]]
        decisao = (f"Assunto informado: _\"{a['assunto']}\"_\n\n- Domínio escolhido: {dom}\n"
                   + ("- Nenhuma palavra de padrão reconhecida → gerados os 9 padrões cobrados na P3 (grupo `prova`).\n"
                      if a.get("sem_padrao") else "")
                   + "\n| Padrão | Palavras do assunto que o indicaram |\n|---|---|\n"
                   + ("\n".join(linhas_p) if linhas_p else "| (grupo prova) | — |")
                   + "\n\nA entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.")
    else:
        decisao = (f"Escolha explícita: domínio **{s.origem.get('dominio_rotulo', 'personalizado')}**, padrões: "
                   f"{', '.join(s.padroes)}.")
    if s.origem.get("notas"):
        decisao += "\n\n" + "\n".join(f"> {n}" for n in s.origem["notas"])
    return _montar_readme(s, tv, padroes_txt, decisao, nome_pasta)


def _montar_readme(s, tv, padroes_txt, decisao, nome_pasta):
    def entra(caminho):
        return s.estudo or "/antes_" not in caminho

    arvore = ["nucleo/", f"  entidades.py              ← {s.ent} com @property (base de tudo)"]
    arvore += ["  " + c.split("/", 1)[1] for p in s.padroes for c, _ in GERADORES.get(p, [])
               if c.startswith("nucleo/") and entra(c)]
    arvore += ["tests/", f"  fabrica.py                ← cria {s.ent} válidas para os testes", "  test_entidades.py"]
    arvore += ["  " + c.split("/", 1)[1] for p in s.padroes for c, _ in GERADORES.get(p, []) if c.startswith("tests/")]
    if s.estudo:
        arvore += ["docs/                       ← um ADR por padrão"]
    arvore += ["especificacao.json          ← a entrada usada (dá para editar e regenerar)"]
    if s.django:
        arvore += ["requirements.txt            ← o Python exigido, o Django e o que ele usa, os testes e as deste sistema",
                   "iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin",
                   "web/                        ← projeto Django (MVT) que usa o núcleo",
                   "  .env.example              ← modelo do .env (chave secreta, admin, porta)",
                   f"  {s.app}/  settings · models · forms · services · viewmodels · views · api (REST) · urls · "
                   "templates/ · tests/"]
    if s.exercicio:
        arvore += ["exercicios.html             ← questionário de revisão (resposta oculta em \"Ver resposta\")"]
    ligacoes = [f"- {subst(LIGACOES[p], {**tv, 'GW': s.gw})}" for p in s.padroes]
    if not s.estudo:
        ligacoes = [re.sub(r";[^;]*antes_[^;]*$", "", linha) for linha in ligacoes]
    if s.django:
        ligacoes.append(f"- `web/{s.app}/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → "
                        "`viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem")
    secoes = []
    if not s.estudo:   # "só gerar": uma tabela curta no lugar das seções didáticas
        linhas = [f"| {PADROES[p]['titulo']} | `nucleo/{PADROES[p]['modulo']}.py` | {subst(PADROES[p]['conceito'], tv)} |"
                  for p in s.padroes]
        secoes.append("| Padrão | Arquivo | Ideia |\n|---|---|---|\n" + "\n".join(linhas))
    for i, p in enumerate(s.padroes if s.estudo else [], 1):
        info = PADROES[p]
        arquivos = f"`nucleo/{info['modulo']}.py`" + (f" · antes: `nucleo/{info['antes']}.py`" if info["antes"] else "")
        testes = "test_entidades.py" if p == "encapsulamento" else f"test_{info['modulo']}.py"
        secoes.append(render(r'''
            ### 4.@@I@@ @@TITULO@@

            _@@FAMILIA@@_ · @@ARQUIVOS@@ · testes: `tests/@@TESTES@@`

            **Problema (smell):** @@PROBLEMA@@

            **Conceito:** @@CONCEITOTXT@@

            | Peça | No código |
            |---|---|
            @@PECAS@@

            **Quando NÃO usar:** @@QUANDO@@

            **Tripé da P3** (o professor sorteia a função e pergunta):

            | Função | O que faz | Por que assim | O que muda se alterar |
            |---|---|---|---|
            @@TRIPE@@
            ''', I=i, TITULO=info["titulo"], FAMILIA=info["familia"], ARQUIVOS=arquivos, TESTES=testes,
            PROBLEMA=subst(info["problema"], tv), CONCEITOTXT=subst(info["conceito"], tv),
            PECAS="\n".join(f"| {subst(a, tv)} | {subst(b, tv)} |" for a, b in info["pecas"]),
            QUANDO=subst(info["quando_nao"], tv),
            TRIPE="\n".join(f"| {subst(f, tv)} | {subst(o, tv)} | {subst(q, tv)} | {subst(e, tv)} |"
                            for f, o, q, e in info["tripe"])))
    web = ""
    if s.django:
        web = render(r'''
            ## 6. Camada web (Django · MVT)

            | Camada | Arquivo | Papel |
            |---|---|---|
            | Model | `web/@@APP@@/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
            | Form | `web/@@APP@@/forms.py` | `ModelForm` reaproveita os validators |
            | Service | `web/@@APP@@/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
            | ViewModel | `web/@@APP@@/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
            | View | `web/@@APP@@/views.py` | **fina**: busca → Service/ViewModel → render |
            | API REST | `web/@@APP@@/api.py` | JSON em `api/v1/` (GET/POST) e `api/v1/<id>/` (GET/PUT/PATCH/DELETE), validado pelo **mesmo** Form |
            | Settings da app | `web/@@APP@@/settings.py` | `API_LIMITE` e `API_ESCRITA`, trocáveis no projeto com o prefixo `@@PREFIXO@@_` |
            | Template | `web/@@APP@@/templates/@@APP@@/` | só exibe |

            Pegadinha testada em `tests/test_models.py`: `save()` sozinho **não** valida — quem valida é
            `full_clean()` / o `ModelForm`.

            ### Subir o site (no WSL, dentro desta pasta)

            Tudo de uma vez — cria o `.venv`, instala o `requirements.txt`, copia `web/.env.example` para
            `web/.env` (com uma chave secreta nova), roda as migrations, cria o superusuário e sobe o servidor:

            ```bash
            bash iniciar.sh
            ```

            O site abre sozinho em **modo PWA** — uma janela de app isolada das abas (Edge/Chrome `--app`); com
            `PWA=0` no `web/.env` abre numa aba comum, e `ABRIR=0 bash iniciar.sh` não abre nada. Endereços:
            http://127.0.0.1:8000/ (site) e http://127.0.0.1:8000/admin/ (usuário e senha do `web/.env`:
            `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD`). Outra porta: `bash iniciar.sh tudo 8001`.
            O site é instalável (manifest em `/manifest.webmanifest`, service worker em `/sw.js`, ícones em `static/`).

            Os mesmos passos, separados (cada um pode ser repetido sem estragar nada):

            ```bash
            bash iniciar.sh venv        # cria .venv nesta pasta (se não existir)
            bash iniciar.sh deps        # instala requirements.txt (se faltar algo)
            bash iniciar.sh env         # web/.env a partir de web/.env.example (não sobrescreve)
            bash iniciar.sh migrar      # makemigrations @@APP@@ + migrate
            bash iniciar.sh admin       # cria/atualiza o superusuário com os dados do web/.env
            bash iniciar.sh testar      # testes do núcleo e da web
            bash iniciar.sh rodar 8000  # sobe o servidor (Ctrl+C para parar)
            ```

            Sem o script (comandos puros do Django):

            ```bash
            python3 -m venv .venv && source .venv/bin/activate
            pip install -r requirements.txt
            cp web/.env.example web/.env
            cd web
            python manage.py makemigrations @@APP@@ && python manage.py migrate
            python manage.py garantir_admin
            python manage.py runserver 127.0.0.1:8000
            ```

            Reaproveitar um `.venv` que já tem Django (ex.: o do SGS, `Gerador_Sistemas/.venv`):
            `VENV=/caminho/.venv bash iniciar.sh`. As dependências estão explicadas no `requirements.txt` (o Python
            exigido, o Django e o que ele usa, os testes e as pontuais deste sistema).
            ''', APP=s.app, PREFIXO=s.app.upper())
    exerc = ""
    if s.exercicio:
        exerc = render(r'''
            ## 7. Modo exercício (questionário)

            O código deste sistema está **completo e correto** — não há nada para corrigir. O exercício é um
            **questionário de revisão** no formato da P3, com @@N@@ perguntas sobre os padrões aplicados aqui
            (o smell, como foi aplicado, o tripé de cada função, quando não usar, a alternativa descartada).
            Cada resposta fica **oculta** até você clicar em **Ver resposta**.

            - Abra `exercicios.html` (nesta pasta) direto no navegador — não precisa de servidor.
            @@WEBEX@@
            ''', N=total_perguntas(s), WEBEX="" if not s.django else (
            "- Com o site no ar, o mesmo questionário está em `/exercicios/` (link **Exercícios** no topo ou na lista)."))
    roteiro = ""
    if s.estudo:
        roteiro = render(r'''
            ## 5. Roteiro de estudo (30–40 min)

            1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
            2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
            3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
            4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
            5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
            6. Gere de novo em modo exercício e refaça sem olhar:
               `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/@@PASTA@@/especificacao.json --exercicio --nome @@PASTA@@_treino`
            ''', PASTA=nome_pasta)
    modo = ("para **estudo** (smell `antes_*.py`, ADRs, tripé)" if s.estudo else "**só gerar** (sem material de estudo)")
    modo += " · " + ("código **comentado**" if s.comentarios else "**apenas o código** (sem comentários)")
    return render(r'''
        # @@SISTEMA@@ — sistema gerado

        > Gerado por `Gerador_Sistemas/gerar_sistema.py` v@@VERSAO@@ — **determinístico, sem IA**: a mesma
        > entrada gera sempre os mesmos arquivos. Modo: @@MODO@@.
        > Padrões (@@NPADROES@@): @@PADROES@@.

        ## 1. Como o gerador decidiu

        @@DECISAO@@

        ## 2. Mapa dos arquivos

        ```
        @@ARVORE@@
        ```

        **Ligações entre os arquivos:**

        @@LIGACOES@@

        ## 3. Como rodar

        Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

        ```bash
        python -m pytest -v
        ```

        ## 4. Os padrões deste sistema

        @@SECOES@@

        @@ROTEIRO@@

        @@WEB@@

        @@EXERC@@
        ''', SISTEMA=s.sistema, VERSAO=VERSAO, MODO=modo, NPADROES=len(s.padroes), PADROES=padroes_txt,
        DECISAO=decisao, ARVORE="\n".join(arvore), LIGACOES="\n".join(ligacoes), SECOES="\n\n".join(secoes),
        ROTEIRO=roteiro, WEB=web, EXERC=exerc)


def gerar_adr(s, numero, p):
    info, tv = PADROES[p], s.textos()
    testes = "test_entidades.py" if p == "encapsulamento" else f"test_{info['modulo']}.py"
    return subst(textwrap.dedent(f"""
        # ADR {numero:03d} — {info['titulo']} em {s.sistema}

        - Status: aceito (exemplo de estudo gerado)
        - Família: {info['familia']}

        ## Contexto
        {info['problema']}

        ## Decisão
        APLICAMOS **{info['titulo']}**. {info['conceito']}

        ## Alternativa descartada
        {info['alternativa']}

        ## Consequências
        {info['consequencia']}
        Quando NÃO usar: {info['quando_nao']}

        ## Onde está no código
        `nucleo/{info['modulo']}.py`{f" (antes: `nucleo/{info['antes']}.py`)" if info['antes'] else ""} · testes: `tests/{testes}`
        """), tv).lstrip("\n")


# =============================================================================
# 7. MONTAGEM DO SISTEMA
# =============================================================================
def md_html(texto):
    """Texto dos catálogos (markdown simples) → HTML seguro: escapa tudo; `código` → <code>, **x** → <strong>."""
    seguro = html.escape(texto, quote=False)
    seguro = re.sub(r"`([^`]+)`", r"<code>\1</code>", seguro)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", seguro)


def perguntas_exercicio(s):
    """Modo exercício = QUESTIONÁRIO de revisão sobre os padrões DESTE sistema (formato da P3).

    O código do sistema sai sempre completo e correto; aqui só se pergunta sobre ele. Tudo vem dos textos
    do catálogo PADROES (os mesmos do README e dos ADRs), já com os nomes do domínio.
    Devolve [(titulo, familia, [(pergunta_html, resposta_html), ...]), ...] — um bloco por padrão.
    """
    tv = s.textos()

    def t(texto):
        return md_html(subst(texto, tv))

    blocos = []
    for p in s.padroes:
        info = PADROES[p]
        titulo = info["titulo"]
        itens = [(t(f"Que problema (smell) leva a usar {titulo} neste sistema?"), t(info["problema"])),
                 (t(f"Como {titulo} aparece no código deste sistema?"), t(info["conceito"]))]
        for funcao, faz, porque, muda in info.get("tripe", []):
            itens.append((t(f"Sobre {funcao}: o que faz, por que foi feito assim e o que muda se for diferente?"),
                          f"<strong>O que faz:</strong> {t(faz)}<br>\n<strong>Por que assim:</strong> {t(porque)}<br>\n"
                          f"<strong>O que muda se:</strong> {t(muda)}"))
        itens.append((t(f"Quando NÃO vale a pena usar {titulo}?"), t(info["quando_nao"])))
        itens.append((t("Que alternativa foi descartada e qual a consequência da escolha feita?"),
                      f"<strong>Alternativa descartada:</strong> {t(info['alternativa'])}<br>\n"
                      f"<strong>Consequência:</strong> {t(info['consequencia'])}"))
        blocos.append((md_html(titulo), md_html(info["familia"]), itens))
    return blocos


def total_perguntas(s):
    return sum(len(itens) for _, _, itens in perguntas_exercicio(s))


def html_questionario(s, bootstrap=False):
    """Corpo do questionário: cada resposta fica num <details> — só aparece no botão "Ver resposta" (sem JS)."""
    partes, n = [], 0
    for i, (titulo, familia, itens) in enumerate(perguntas_exercicio(s), 1):
        if bootstrap:
            partes.append(f'<section class="mb-4">\n<h2 class="h5 mt-4">{i}. {titulo}</h2>\n'
                          f'<p class="text-body-secondary small">{familia}</p>')
        else:
            partes.append(f'<section class="padrao">\n<h2>{i}. {titulo}</h2>\n<p class="familia">{familia}</p>')
        for pergunta, resposta in itens:
            n += 1
            if bootstrap:
                partes.append(f'<div class="card mb-2"><div class="card-body">\n'
                              f'<p class="mb-2"><strong>Pergunta {n}.</strong> {pergunta}</p>\n'
                              f'<details><summary class="btn btn-sm btn-outline-primary">Ver resposta</summary>\n'
                              f'<div class="mt-2">{resposta}</div>\n</details>\n</div></div>')
            else:
                partes.append(f'<article class="pergunta">\n<p><strong>Pergunta {n}.</strong> {pergunta}</p>\n'
                              f'<details><summary>Ver resposta</summary>\n<div class="resposta">{resposta}</div>\n'
                              f'</details>\n</article>')
        partes.append("</section>")
    return "\n".join(partes)


CSS_EXERCICIOS = """
body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; max-width: 52rem; margin: 0 auto;
       padding: 1.5rem 1rem 3rem; line-height: 1.55; color: #1c1c1c; background: #ffffff; }
h1 { font-size: 1.6rem; margin-bottom: .25rem; }
h2 { font-size: 1.15rem; margin: 2rem 0 .1rem; border-bottom: 1px solid #d0d7de; padding-bottom: .3rem; }
.familia, .intro { color: #57606a; }
.pergunta { border: 1px solid #d0d7de; border-radius: .5rem; padding: .75rem 1rem; margin: .75rem 0; }
.pergunta p { margin: 0 0 .5rem; }
summary { display: inline-block; cursor: pointer; padding: .25rem .8rem; border: 1px solid #0969da;
          border-radius: .4rem; color: #0969da; list-style: none; user-select: none; }
summary::-webkit-details-marker { display: none; }
details[open] summary { background: #0969da; color: #ffffff; }
.resposta { margin-top: .6rem; padding: .6rem .8rem; background: #f6f8fa; border-left: 3px solid #0969da; }
code { background: #eff1f3; padding: 0 .25rem; border-radius: .25rem; font-size: .92em; }
@media (prefers-color-scheme: dark) {
  body { color: #e6edf3; background: #0d1117; }
  h2, .pergunta { border-color: #30363d; }
  .familia, .intro { color: #8b949e; }
  summary { border-color: #4493f8; color: #4493f8; }
  details[open] summary { background: #4493f8; color: #0d1117; }
  .resposta { background: #161b22; border-left-color: #4493f8; }
  code { background: #262c36; }
}
"""


def gerar_exercicios_html(s):
    """exercicios.html na raiz do sistema: abre direto no navegador (arquivo local, sem servidor e sem JS)."""
    return render(r'''
        <!doctype html>
        <html lang="pt-br">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Exercícios — @@SISTEMA@@</title>
        <style>
        @@CSS@@
        </style>
        </head>
        <body>
        <h1>Exercícios — @@SISTEMA@@</h1>
        <p class="intro">Questionário de revisão sobre os @@QTD@@ padrões deste sistema (formato da P3: o que faz, por que
        assim, o que muda se). Responda de cabeça e depois abra a resposta no botão. O código do sistema está completo —
        não há nada para corrigir; consulte <code>README.md</code>, <code>docs/</code> e <code>nucleo/</code>.</p>
        @@CORPO@@
        </body>
        </html>
        ''', SISTEMA=html.escape(s.sistema, quote=False), CSS=CSS_EXERCICIOS.strip("\n"), QTD=len(s.padroes),
        CORPO=html_questionario(s))


def gerar_test_exercicios(s):
    return render(r'''
        """Modo exercício: o questionário exercicios.html existe e cada pergunta esconde a resposta."""
        from pathlib import Path

        PAGINA = Path(__file__).resolve().parent.parent / "exercicios.html"


        def test_questionario_tem_uma_resposta_oculta_por_pergunta():
            html = PAGINA.read_text(encoding="utf-8")
            assert html.count("<details>") == @@N@@
            assert html.count("<summary>Ver resposta</summary>") == @@N@@


        def test_questionario_nao_usa_javascript():
            assert "<script" not in PAGINA.read_text(encoding="utf-8")
        ''', N=total_perguntas(s))


def _e_docstring(no):
    return isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str)


def _sem_docstrings(arvore):
    """Árvore sem docstrings (corpo que só tinha a docstring vira `pass`) — usada para CONFERIR a limpeza."""
    class Tirar(ast.NodeTransformer):
        def limpar(self, no):
            self.generic_visit(no)
            if no.body and _e_docstring(no.body[0]):
                no.body = no.body[1:] or ([] if isinstance(no, ast.Module) else [ast.Pass()])
            return no

        visit_Module = visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = limpar

    return Tirar().visit(arvore)


def _juntar_linhas(linhas):
    """Remonta o arquivo: sem brancos no início, logo após 'def ...:'/'class ...:' nem mais de 2 seguidos."""
    saida = []
    for linha in linhas:
        if not linha.strip():
            if not saida or saida[-1].rstrip().endswith(":"):
                continue
            if len(saida) >= 2 and not saida[-1].strip() and not saida[-2].strip():
                continue
        saida.append(linha.rstrip())
    while saida and not saida[-1].strip():
        saida.pop()
    return "\n".join(saida) + "\n" if saida else ""


def remover_comentarios(codigo):
    """Modo "apenas o código": tira comentários (#) e docstrings SEM mudar o que o código faz.

    Os # são achados pelo tokenize (um # dentro de string não é comentário); as docstrings, pela AST.
    No fim compara as duas AST (sem docstrings): se diferirem, é bug do gerador e nada é escrito.
    """
    arvore = ast.parse(codigo)
    linhas = codigo.split("\n")
    apagar, trocar = set(), {}
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) \
                and no.body and _e_docstring(no.body[0]):
            doc = no.body[0]
            faixa = range(doc.lineno - 1, doc.end_lineno)
            if len(no.body) == 1 and not isinstance(no, ast.Module):   # só havia a docstring: vira `pass`
                trocar[doc.lineno - 1] = " " * doc.col_offset + "pass"
            apagar.update(i for i in faixa if i not in trocar)
    for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
        if tok.type == tokenize.COMMENT:
            i, coluna = tok.start[0] - 1, tok.start[1]
            resto = linhas[i][:coluna].rstrip()
            if resto:
                linhas[i] = resto                       # comentário no fim de uma linha de código
            else:
                apagar.add(i)                           # linha que era só comentário
    novo = _juntar_linhas(trocar.get(i, linha) for i, linha in enumerate(linhas) if i in trocar or i not in apagar)
    if ast.dump(_sem_docstrings(ast.parse(codigo))) != ast.dump(_sem_docstrings(ast.parse(novo))):
        raise RuntimeError("remover_comentarios mudaria o código")  # pragma: no cover - bug do gerador
    return novo


def remover_referencias_antes(codigo):
    """Modo "só gerar": tira dos testes tudo o que depende de nucleo/antes_*.py (que não é gerado).

    Remove os imports de antes_*, cada teste/função/variável/classe que use esses nomes e, em cadeia,
    o que dependia do que foi removido (inclusive testes que pediam uma fixture removida).
    """
    arvore = ast.parse(codigo)
    nomes, apagar, removidos = set(), set(), set()
    for no in arvore.body:
        if isinstance(no, ast.ImportFrom) and no.module:
            modulo_antes = no.module.split(".")[-1].startswith("antes_")
            do_antes = [a for a in no.names if modulo_antes or a.name.startswith("antes_")]
            if do_antes and len(do_antes) != len(no.names):  # pragma: no cover - os modelos não misturam
                raise RuntimeError("import misturando antes_* com outros nomes")
            if do_antes:
                nomes |= {a.asname or a.name for a in do_antes}
                apagar.update(range(no.lineno - 1, no.end_lineno))
    if not nomes:
        return codigo

    def usa(no):
        if any(isinstance(n, ast.Name) and n.id in nomes for n in ast.walk(no)):
            return True
        return isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(a.arg in nomes for a in no.args.args)

    mudou = True
    while mudou:                                       # em cadeia: o que usava algo removido também sai
        mudou = False
        for no in arvore.body:
            if id(no) in removidos or not isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                                          ast.Assign)):
                continue
            if usa(no):
                removidos.add(id(no))
                mudou = True
                if isinstance(no, ast.Assign):
                    nomes |= {t.id for t in no.targets if isinstance(t, ast.Name)}
                else:
                    nomes.add(no.name)
                inicio = min([no.lineno] + [d.lineno for d in getattr(no, "decorator_list", [])])
                apagar.update(range(inicio - 1, no.end_lineno))
    novo = _juntar_linhas(linha for i, linha in enumerate(codigo.split("\n")) if i not in apagar)
    ast.parse(novo)
    return novo


def mover_para_apps(arq, s):
    """Estrutura das Instruções §9.2: a app vai para web/apps/<app>/ (AppConfig name = "apps.<app>").

    Só muda o CAMINHO e o PACOTE Python; o rótulo da app, os templates (<app>/…), os estáticos (<app>/…)
    e os nomes de rota (<app>:…) continuam iguais — por isso nada mais precisa ser regenerado.
    """
    app = s.app
    pacote = re.compile(rf"\b(from|import) {re.escape(app)}(?=[.\s])")
    novo = {}
    for caminho, conteudo in arq.items():
        if caminho.startswith(f"web/{app}/"):
            caminho = f"web/apps/{app}/" + caminho[len(f"web/{app}/"):]
        if caminho.endswith(".py") and caminho.startswith("web/") and isinstance(conteudo, str):
            conteudo = pacote.sub(lambda m: f"{m.group(1)} apps.{app}", conteudo)
            conteudo = conteudo.replace(f'include("{app}.urls")', f'include("apps.{app}.urls")')
            conteudo = conteudo.replace(f'    "{app}",\n]', f'    "apps.{app}",\n]')          # INSTALLED_APPS
            if caminho.endswith(f"/{app}/apps.py"):
                conteudo = re.sub(rf'^(\s*)name = "{re.escape(app)}"$', rf'\1name = "apps.{app}"\n\1label = "{app}"',
                                  conteudo, flags=re.M)
        novo[caminho] = conteudo
    novo["web/apps/__init__.py"] = '"""Apps do projeto (Instruções §9.2): cada uma em apps/<nome>/, desacoplada."""\n'
    novo[f"web/apps/{app}/README.md"] = render(r'''
        # App `@@APP@@` — @@SISTEMA@@

        Documentação individual da app (Instruções de desenvolvimento DJANGO §9.3).

        | Item | Conteúdo |
        |---|---|
        | Finalidade | Cadastro e listagem de `@@ENT@@` com o valor calculado pela política de @@CONCEITO@@ (Strategy do núcleo). Não faz autenticação nem pagamento. |
        | Dependências | `nucleo/` (Python puro, `nucleo.politicas`); Django; chaves do `web/.env`. |
        | Modelos | `@@ENT@@`@@ID@@ — sem escopo de tenant (modo `single`). |
        | Serviços públicos | `@@ENT@@Service.valor_final(obj)` e `@@ENT@@Service.resumo(objetos)` (`services.py`). |
        | URLs | `@@APP@@:lista` (`/`), `@@APP@@:criar` (`/novo/`), `@@APP@@:api` (`/api/`). |
        | API REST | `@@APP@@:api_colecao` (`/api/v1/`: GET, POST) e `@@APP@@:api_item` (`/api/v1/<id>/`: GET, PUT, PATCH, DELETE). |
        | Settings | `settings.py` da app: `API_LIMITE`, `API_ESCRITA` (no projeto: `@@PREFIXO@@_API_LIMITE`…). |
        | Instalação em outro projeto | `INSTALLED_APPS += ["apps.@@APP@@"]`, `path("", include("apps.@@APP@@.urls"))`, `python manage.py migrate`. |
        | Testes | `cd web && python -m pytest apps/@@APP@@` |
        ''', APP=app, SISTEMA=s.sistema, ENT=s.ent, CONCEITO=s.conceito, PREFIXO=app.upper(),
        ID=(" (chave UUIDv4)" if s.web["id_publico"] == "uuid" else "") + (" com ID interno LNNL" if s.web["id_interno"] else ""))
    return novo


PROJETO_PADRAO = "config"     # o pacote do projeto Django (web/config/settings.py) quando o perfil não diz outro
_REF_PROJETO = re.compile(r"\bconfig(?=[./](?:settings|urls|wsgi|env|pwa)\b)")


def renomear_projeto_django(arq, projeto):
    """Troca o pacote do projeto Django "config" por outro (perfil: a Prova P3 usa "cooperativa"): a pasta
    web/config/ e toda referência a ele — config.settings, config/urls.py, from config.env… — nos textos."""
    novo = {}
    for caminho, conteudo in arq.items():
        if caminho.startswith(f"web/{PROJETO_PADRAO}/"):
            caminho = f"web/{projeto}/" + caminho[len(f"web/{PROJETO_PADRAO}/"):]
        if isinstance(conteudo, str):
            conteudo = _REF_PROJETO.sub(projeto, conteudo)
        novo[caminho] = conteudo
    return novo


def pacote_do_projeto(projeto):
    """O pacote do projeto Django de um sistema JÁ gerado (lido do web/manage.py): "config" ou o do perfil."""
    try:
        texto = (Path(projeto) / "web" / "manage.py").read_text(encoding="utf-8")
    except OSError:
        return PROJETO_PADRAO
    achado = re.search(r'DJANGO_SETTINGS_MODULE", "(\w+)\.settings"', texto)
    return achado.group(1) if achado else PROJETO_PADRAO


def dependencias_pontuais(s):
    """As dependências que só ESTE sistema usa, pelas opções escolhidas: [(requisito, para quê)]."""
    pontuais = []
    if s.django and s.drf:
        pontuais.append(("djangorestframework>=3.15", "DRF: a API com Serializer, ViewSet e router (/api/)"))
    if s.django and s.web["seguranca"] == "baseline":
        pontuais.append(("argon2-cffi>=23.1", "senhas com Argon2id (segurança baseline, §16.1)"))
    return pontuais


def requisitos_txt(s):
    """requirements.txt do sistema: o Python exigido (cabeçalho — o pip não instala Python), o Django e o que ele
    usa (com camada web), os testes e as dependências pontuais deste sistema. Uma linha por pacote, com o porquê."""
    py = ".".join(map(str, PYTHON_MINIMO))
    instalar = "python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    linhas = ["# " + "=" * 77,
              f'# requirements.txt — sistema "{s.sistema}" (gerado pelo SGS)',
              "#",
              f"# Python: {py} ou mais novo (" + ("o Django 6 exige; " if s.django else "")
              + f"o núcleo conta com o sum() exato do {py}+).",
              "#         Confira: python3 --version" + ("  ·  o iniciar.sh confere sozinho antes de criar o .venv"
                                                     if s.django else ""),
              "#",
              f"# Instalar: {instalar}"]
    if s.django:
        linhas.append("#           (ou: bash iniciar.sh deps)")
    linhas.append("# " + "=" * 77)

    def bloco(titulo, itens):
        largura = max(len(r) for r, _ in itens)
        return ["", f"# --- {titulo} ---", *(f"{r:<{largura}}  # {porque}" for r, porque in itens)]

    if s.django:
        linhas += bloco("Django e o que ele usa", DEPENDENCIAS_DJANGO)
    linhas += bloco("testes", DEPENDENCIAS_TESTES if s.django else DEPENDENCIAS_TESTES[:1])
    pontuais = dependencias_pontuais(s)
    if pontuais:
        linhas += bloco("deste sistema", pontuais)
    else:
        linhas += ["", "# --- deste sistema ---",
                   "# (nenhuma a mais: " + ("além do Django e dos testes, " if s.django else "além dos testes, ")
                   + "só a biblioteca padrão do Python)"]
    return "\n".join(linhas) + "\n"


def gitignore_sistema(django):
    """.gitignore de cada sistema gerado: o conjunto mínimo global das Instruções de desenvolvimento DJANGO
    (AGENT_INSTRUCTIONS_DJANGO.md §4.7) + SQLite local + o que é só desta máquina no site (web/)."""
    texto = ("# Conjunto mínimo das Instruções de desenvolvimento DJANGO (§4.7) + SQLite local.\n"
             ".venv/\n.env\n*.pyc\n__pycache__/\n*.log\n.DS_Store\nmedia/\nstaticfiles/\ndb.sqlite3\n"
             ".env.*\n!.env.example\n.pytest_cache/\n"
             "# Marcas do Windows ao baixar/copiar arquivos.\n*Zone.Identifier\n*.identifier\n*.Identifier\n")
    if django:
        texto += ("# Site Django: segredos (o modelo web/.env.example sobe), banco local, log do servidor,\n"
                  "# estáticos coletados e uploads.\n"
                  "web/.env\nweb/db.sqlite3\nweb/servidor.log\nweb/staticfiles/\nweb/media/\n")
    return texto


def montar_arquivos(s, nome_pasta):
    arq = {}
    arq["nucleo/__init__.py"] = f'"""Núcleo em Python puro do sistema {s.sistema} (gerado)."""\n'
    arq["nucleo/entidades.py"] = gerar_entidades(s)
    arq["tests/__init__.py"] = ""
    arq["tests/fabrica.py"] = gerar_fabrica(s)
    arq["tests/test_entidades.py"] = gerar_test_entidades(s)
    for p in s.padroes:
        for caminho, funcao in GERADORES.get(p, []):
            arq[caminho] = funcao(s)
    if not s.estudo:
        # "Só gerar": sem os arquivos do smell (antes_*.py) e sem os testes de comparação com eles.
        for caminho in [k for k in arq if re.fullmatch(r"nucleo/antes_\w+\.py", k)]:
            del arq[caminho]
        for caminho in [k for k in arq if k.startswith("tests/test_")]:
            arq[caminho] = remover_referencias_antes(arq[caminho])
    arq["pytest.ini"] = "[pytest]\npythonpath = .\ntestpaths = tests\n"
    arq["requirements.txt"] = requisitos_txt(s)
    arq[".gitignore"] = gitignore_sistema(s.django)
    if s.estudo:
        for n, p in enumerate(s.padroes, 1):
            arq[f"docs/ADR-{n:03d}-{p}.md"] = gerar_adr(s, n, p)
    if s.django:
        arq.update(gerar_web(s))
        if s.drf:
            arq.update(gerar_drf(s))
        if s.web["estrutura"] == "apps":
            arq = mover_para_apps(arq, s)
        if s.projeto != "config":
            arq = renomear_projeto_django(arq, s.projeto)
    if s.exercicio:
        # Modo exercício = questionário de revisão (resposta oculta em "Ver resposta"). O código NÃO muda:
        # sai completo e correto, igual ao modo normal — não há nada para o aluno corrigir.
        arq["exercicios.html"] = gerar_exercicios_html(s)
        arq["tests/test_exercicios.py"] = gerar_test_exercicios(s)
    if not s.comentarios:
        # "Apenas o código": comentários e docstrings saem de todo .py (o comportamento é conferido igual).
        for caminho in [k for k in arq if k.endswith(".py") and not k.endswith("/lnnl.py")]:   # lnnl.py: cópia fiel
            arq[caminho] = remover_comentarios(arq[caminho])
    especificacao = dict(s.dados)
    especificacao["padroes"] = s.padroes
    especificacao["django"] = s.django
    especificacao["estudo"] = s.estudo
    especificacao["comentarios"] = s.comentarios
    especificacao["web"] = s.web
    arq["especificacao.json"] = json.dumps(especificacao, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    arq["README.md"] = gerar_readme(s, nome_pasta)
    if s.perfil and s.django:
        arq["README.md"] += "\n" + secao_perfil(s)
    arq[MARCADOR] = f"gerar_sistema.py v{VERSAO}\n"
    # checagem final: todo .py gerado precisa ser Python válido
    for caminho, conteudo in arq.items():
        if caminho.endswith(".py"):
            try:
                ast.parse(conteudo)
            except SyntaxError as erro:  # pragma: no cover - indica bug do gerador
                raise RuntimeError(f"código gerado inválido em {caminho}: {erro}") from erro
    return arq


def nome_saida(s):
    """Nome da pasta: SÓ letras minúsculas, números e "_" (nada de +, -, espaço) — simples de digitar e de importar.

    <sistema>__<padrões>[_web[_estilo]][_exercicio][_direto][_sem_comentarios]; grupos inteiros viram o nome do grupo.
    Domínio com perfil de pasta fixa (a Prova P3 → provaP3): o nome do perfil, sempre o mesmo.
    """
    if s.pasta:
        return s.pasta
    escolhidos = set(s.padroes)
    pad = None
    for grupo in ("todos", "gof", "prova", "criacao", "estrutural", "comportamental", "fundamentos"):
        if escolhidos == set(GRUPOS[grupo]) | {"encapsulamento"}:
            pad = grupo
            break
    for grupo in ("gof", "prova", "criacao", "estrutural", "comportamental", "fundamentos"):
        membros = set(GRUPOS[grupo]) - {"encapsulamento"}
        if pad is None and membros <= escolhidos:          # um grupo inteiro + alguns soltos: "criacao_strategy"
            resto = [p for p in s.padroes if p not in membros and p != "encapsulamento"]
            if len(grupo) + len("_".join(resto)) < 60:
                pad = "_".join([grupo] + resto)
    if pad is None:
        pad = "_".join(p for p in s.padroes if p != "encapsulamento") or "encapsulamento"
        if len(pad) > 60:   # muitos padrões soltos: nome curto + resumo estável (mesma lista → mesmo nome)
            pad = f"{len(s.padroes)}padroes_" + hashlib.sha1(pad.encode()).hexdigest()[:6]
    web = ""
    if s.django:
        estilo = s.web["estilo"]
        web = "_web" + {"simples": "", "cmd": "_cmd", "bootstrap": "_bootstrap"}.get(
            estilo, f"_{s.web['tema'].lower()}_{s.web['tom']}")
    nome = (f"{s.slug}__{pad}" + web + ("_exercicio" if s.exercicio else "")
            + ("" if s.estudo else "_direto") + ("" if s.comentarios else "_sem_comentarios"))
    return re.sub(r"[^a-z0-9_]", "_", nome)               # garantia final: nenhum símbolo passa


def preparar_destino(destino, forcar):
    if destino.exists():
        if not (destino / MARCADOR).exists():
            raise ErroGerador(f"{destino} já existe e não foi criado pelo gerador — escolha outro --nome/--saida.")
        if not forcar:
            raise ErroGerador(f"{destino} já existe. Use --forcar para gerar de novo (a pasta será substituída).")
        shutil.rmtree(destino)
    destino.mkdir(parents=True)


def escrever(destino, arquivos):
    for caminho in sorted(arquivos):
        alvo = destino / caminho
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(arquivos[caminho], bytes):            # ícones PNG do PWA
            alvo.write_bytes(arquivos[caminho])
            continue
        with open(alvo, "w", encoding="utf-8", newline="\n") as f:
            f.write(arquivos[caminho])
        if caminho.endswith(".sh"):
            alvo.chmod(0o755)   # scripts já saem executáveis (./iniciar.sh também funciona)


def modelo_spec():
    d = copy.deepcopy(DOMINIOS["hotel"])
    d.pop("palavras")
    d["dominio_base"] = "hotel"
    d["padroes"] = ["todos"]
    d["django"] = False
    d["_comentario"] = ("Edite os valores e rode: gerar_sistema.py --spec ESTE_ARQUIVO.json. "
                        "Regras: obrigatorio/livre para str; minimo (min) ou faixa (min,max) para int/float. "
                        "'quantidade' = int com min 1; 'preco' = float com regra minimo e min 0.")
    return d


def aplicar_campos(dados, campos, origem):
    """Campos pedidos → atributos NOVOS da entidade (depois dos do domínio, antes dos de texto livre).

    O tipo vem do pedido/da resposta ou do IDENTIFICADOR DE TIPOS (tipos_campos.identificar). Nome que já
    existe no domínio ou que é reservado é ignorado com uma nota — o sistema continua gerando certo.
    """
    import tipos_campos
    nomes = {a["nome"] for a in dados["atributos"]}
    novos, origem["campos"] = [], []
    for c in tipos_campos.analisar(campos):
        n = c["nome"]
        if n in nomes:
            origem["notas"].append(f"campo {n!r} já existe na entidade (veio do domínio): mantido o original.")
            continue
        if n in RESERVADOS or n in RESERVADOS_DJANGO or keyword.iskeyword(n) or not n.isidentifier():
            origem["notas"].append(f"campo {n!r} ignorado: nome reservado pelo gerador — use outro nome.")
            continue
        nomes.add(n)
        novos.append(A(n, c["tipo"], c["regra"], c["min"], c["max"]))
        origem["campos"].append(c)
        if c["certeza"] == "duvida":
            origem["notas"].append(f"campo {n!r}: o tipo não é óbvio pelo nome — usado {tipos_campos.rotulo(c['tipo'])}. "
                                   "Para escolher, informe junto (ex.: " + f"{n}:int) ou responda no questionário.")
    posicao = max([i + 1 for i, a in enumerate(dados["atributos"]) if a["regra"] != "livre"] or [0])
    dados["atributos"][posicao:posicao] = novos
    return novos


def gerar(dominio=None, assunto=None, spec=None, padroes=None, sistema=None, entidade=None,
          django=False, exercicio=False, saida=None, nome=None, forcar=False, estudo=True, comentarios=True,
          web=None, campos=None, regerar_fixa=False):
    """API programática: gera o sistema e devolve (pasta, Spec).

    Pasta FIXA (perfil do domínio, ex.: provaP3): se ela já existe, NÃO é substituída — é onde se trabalha
    (as tarefas da prova); só com regerar_fixa=True (sgs provap3, depois de perguntar).
    estudo=False → "só gerar" (sem antes_*.py, sem ADRs, README curto);
    comentarios=False → "apenas o código" (sem comentários nem docstrings nos .py);
    web → dict com as opções da camada Django (ver WEB_PADRAO);
    campos → campos a MAIS na entidade ("nome, idade:int", ["peso:float"], [{"nome", "tipo"}]); sem tipo,
             o identificador de tipos (tipos_campos.py) deduz pelo nome. Sem `campos`, valem os que o
             assunto listar ("… com os campos nome, raça e idade").
    """
    s = montar_spec(dominio=dominio, assunto=assunto, spec=spec, padroes=padroes, sistema=sistema, entidade=entidade,
                    django=django, exercicio=exercicio, estudo=estudo, comentarios=comentarios, web=web, campos=campos)
    pasta_saida = Path(saida) if saida else PASTA_PADRAO
    destino = pasta_saida / (nome or nome_saida(s))
    if s.pasta and not nome and destino.exists() and not regerar_fixa:
        raise ErroGerador(f"{destino.name} já existe e é a pasta de trabalho de {s.perfil.get('nome', s.sistema)} — "
                          "não substituo (o que foi feito nela se perderia). Para gerar de novo do zero: sgs provap3 "
                          "(pergunta antes)")
    arquivos = montar_arquivos(s, destino.name)
    preparar_destino(destino, forcar or (regerar_fixa and bool(s.pasta)))
    escrever(destino, arquivos)
    return destino, s


def montar_spec(dominio=None, assunto=None, spec=None, padroes=None, sistema=None, entidade=None,
                django=False, exercicio=False, estudo=True, comentarios=True, web=None, campos=None, atributos=None):
    """A Spec (a entrada já decidida e validada) SEM escrever nada — o que gerar() e preparar_modulo() usam.

    spec: caminho de um especificacao.json ou o próprio dict · atributos: troca a lista de atributos inteira
    (sgs incrementar: a classe refeita com o campo novo ou modificado)."""
    origem = {"notas": []}
    web_spec = {}
    if isinstance(spec, dict):
        entrada, caminho = copy.deepcopy(spec), Path("especificacao.json")
    elif spec:
        caminho = Path(spec)
        if not caminho.exists():
            raise ErroGerador(f"arquivo de especificação não encontrado: {spec}")
        try:
            entrada = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erro:
            raise ErroGerador(f"JSON inválido em {spec}: {erro}") from erro
    if spec:
        if not isinstance(entrada, dict):
            raise ErroGerador("o JSON de especificação deve ser um objeto { ... }")
        base = entrada.pop("dominio_base", "generico")
        if base not in DOMINIOS:
            raise ErroGerador(f"dominio_base desconhecido: {base!r}")
        padroes_spec = entrada.pop("padroes", None)
        django_spec = bool(entrada.pop("django", False))
        estudo = estudo and bool(entrada.pop("estudo", True))
        comentarios = comentarios and bool(entrada.pop("comentarios", True))
        web_spec = entrada.pop("web", None) or {}
        campos = campos or entrada.pop("campos", None)
        entrada.pop("campos", None)
        entrada.pop("_comentario", None)
        padroes = padroes or padroes_spec
        django = django or django_spec
        dados = copy.deepcopy(DOMINIOS[base])
        dados.update(entrada)
        origem["dominio_rotulo"] = f"{base} (personalizado por {caminho.name})"
    else:
        if assunto:
            analise = analisar_assunto(assunto)
            origem.update(analise)
            origem["assunto"] = assunto
            dominio = dominio or analise["dominio"]
            if not padroes:
                if analise["padroes"]:
                    padroes = analise["padroes"]
                else:
                    padroes = ["prova"]       # nenhuma palavra de padrão: os 9 cobrados na P3
                    origem["sem_padrao"] = True
            if dominio == "generico" and not sistema and analise["sistema"]:
                sistema = analise["sistema"]
            if campos is None and analise["campos"]:
                campos = analise["campos"]
        dominio = dominio or "hotel"
        if dominio not in DOMINIOS:
            raise ErroGerador(f"domínio desconhecido: {dominio!r}. Opções: {', '.join(DOMINIOS)}")
        dados = copy.deepcopy(DOMINIOS[dominio])
        origem["dominio_rotulo"] = dominio
    if sistema:
        dados["sistema"] = sistema.strip()
    if entidade:
        dados["entidade"] = camel(entidade)
    dados.pop("palavras", None)
    if atributos is not None:
        dados["atributos"] = copy.deepcopy(atributos)
    if campos:
        aplicar_campos(dados, campos, origem)
    pedidos = padroes or ["todos"]
    lista = normalizar_padroes(pedidos)
    if django and "strategy" not in lista:
        lista = normalizar_padroes(lista + ["strategy"])
        origem["notas"].append("--django incluiu o Strategy: o Service da camada web reaproveita as políticas do núcleo.")
    return Spec(dados, lista, django=django, exercicio=exercicio, origem=origem,
                estudo=estudo, comentarios=comentarios, web={**web_spec, **(web or {})})


# =============================================================================
# 7b. MÓDULOS: mais uma app Django num sistema que já existe (sgs app NN <pedido>)
# =============================================================================
MODULOS = "modulos.json"   # na raiz do sistema: os módulos acrescentados (na ordem)
APPS_RESERVADAS = {"admin", "auth", "contenttypes", "sessions", "messages", "staticfiles", "config", "apps",
                   "nucleo", "tests", "web", "api", "novo", "exercicios", "static", "media", "templates",
                   "manifest", "sw", "docs", "gestao", "django", "management", "migrations"}


def ler_modulos(projeto):
    """[{"app", "pacote", "entidade", …}] dos módulos do sistema (vazio se não houver)."""
    try:
        dados = json.loads((Path(projeto) / MODULOS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(dados, list):
        return []
    return [m for m in dados if isinstance(m, dict) and isinstance(m.get("app"), str)]


def apps_do_projeto(projeto):
    """Rótulos das apps Django que o sistema já tem (web/<app> ou web/apps/<app>)."""
    web = Path(projeto) / "web"
    return sorted({p.parent.name for p in list(web.glob("*/apps.py")) + list(web.glob("apps/*/apps.py"))})


def _nucleo_dentro_da_app(texto, pacote):
    """O núcleo do módulo mora DENTRO da app: nucleo.x → <pacote>.nucleo.x; tests.fabrica → <pacote>.tests.nucleo…"""
    texto = re.sub(r"\b(from|import) nucleo(?=[.\s])", rf"\1 {pacote}.nucleo", texto)
    return re.sub(r"\b(from|import) tests\.fabrica\b", rf"\1 {pacote}.tests.nucleo.fabrica", texto)


PALAVRAS_DE_PEDIDO = {"cadastro", "cadastros", "cadastrar", "controle", "controlar", "gestao", "gerenciar", "registro",
                      "registros", "modulo", "app", "sistema", "tela", "lista", "de", "do", "da", "dos", "das", "e",
                      "o", "a", "os", "as", "um", "uma", "uns", "umas", "com", "para", "por", "no", "na", "nos", "nas",
                      "novo", "nova", "novos", "novas", "mais"}


def singular(palavra):
    """Singular simples (o contrário do plural() das apps): destinos→destino, voos→voo, opcoes→opcao."""
    for fim, troca in (("oes", "ao"), ("aes", "ao"), ("ais", "al"), ("eis", "el"), ("ois", "ol"), ("ns", "m"),
                       ("res", "r"), ("zes", "z"), ("ses", "s")):
        if palavra.endswith(fim) and len(palavra) > len(fim) + 1:
            return palavra[: -len(fim)] + troca
    return palavra[:-1] if palavra.endswith("s") and len(palavra) > 3 else palavra


def nome_do_pedido(pedido):
    """O NOME da funcionalidade nova pelo contexto do pedido (determinístico): a 1ª palavra que não é
    "cadastro de", "controle de"… no singular, como classe — "destinos de viagem" → Destino,
    "cadastro de horários de voos" → Horario. Sem palavra útil → None (fica o nome do domínio)."""
    for palavra in re.findall(r"[a-z0-9]+", normalizar(pedido or "")):
        if palavra not in PALAVRAS_DE_PEDIDO and not palavra.isdigit() and len(palavra) > 2:
            return camel(singular(palavra))
    return None


def preparar_modulo(projeto, assunto, entidade=None, campos=None, padroes=None, dominio=None):
    """PLANEJA um módulo (mais uma app Django) para o sistema da pasta `projeto`, sem escrever nada.

    O módulo é gerado pelo MESMO gerador, com as opções web/estudo/comentários do sistema: sai com o form
    (ModelForm), o CRUD completo, a API REST, o settings da app, models, views, testes e os padrões do pedido —
    o núcleo dele vai para DENTRO da app (<app>/nucleo/, testes em <app>/tests/nucleo/). O NOME da classe vem de
    `entidade` ou do contexto do pedido (nome_do_pedido: "destinos…" → Destino); os atributos vêm do domínio.
    Nome de app que já existe (ou reservado) → ErroGerador com a dica entidade=Nome. Devolve o plano para
    aplicar_modulo().
    """
    entidade = entidade or nome_do_pedido(assunto)
    # Módulo sem palavra de padrão no pedido: só o Strategy (o Service da app usa) — não os 9 da prova.
    padroes = padroes or analisar_assunto(assunto)["padroes"] or ["strategy"]
    projeto = Path(projeto)
    if not (projeto / "web" / "manage.py").exists():
        raise ErroGerador(f"{projeto.name} não tem o site Django (web/manage.py) — um módulo é uma app Django")
    s = _spec_do_modulo(projeto, assunto, entidade, campos, padroes, dominio)
    app = s.app
    existentes = apps_do_projeto(projeto)
    dica = "escolha outro nome para a entidade do módulo: entidade=Nome (ex.: entidade=Vacina)"
    if app in existentes:
        raise ErroGerador(f"o sistema já tem uma app {app!r} (a entidade {s.ent} vira a app {app}) — {dica}")
    if app in APPS_RESERVADAS or not re.fullmatch(r"[a-z][a-z0-9_]*", app):
        raise ErroGerador(f"{app!r} é um nome reservado (Django, rotas ou pastas do sistema) — {dica}")
    arquivos, modulo = _arquivos_do_modulo(projeto, s, assunto)
    return {"arquivos": arquivos, "modulo": modulo, "spec": s}


def _spec_do_modulo(projeto, assunto, entidade, campos=None, padroes=None, dominio=None, atributos=None):
    """A Spec de um módulo com as opções web/estudo/comentários do sistema (especificacao.json)."""
    try:
        espec = json.loads((Path(projeto) / "especificacao.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        espec = {}
    espec = espec if isinstance(espec, dict) else {}
    web = dict(espec.get("web")) if isinstance(espec.get("web"), dict) else {}
    web["estrutura"] = "apps" if (Path(projeto) / "web" / "apps").is_dir() else "plana"   # vale o que está no disco
    return montar_spec(assunto=assunto, entidade=entidade, campos=campos, padroes=padroes, django=True, dominio=dominio,
                       sistema=espec.get("sistema") or None, estudo=bool(espec.get("estudo", True)),
                       comentarios=bool(espec.get("comentarios", True)), web=web, atributos=atributos)


def _arquivos_do_modulo(projeto, s, assunto):
    """Os arquivos da app do módulo (o núcleo dentro dela) a partir da Spec — o "transplante" do sistema gerado."""
    projeto, app = Path(projeto), s.app
    pacote = f"apps.{app}" if s.web["estrutura"] == "apps" else app
    base_app = f"web/{pacote.replace('.', '/')}"
    tem_admin = any((projeto / "web").glob("**/management/commands/garantir_admin.py"))
    arquivos = {}
    for caminho, conteudo in montar_arquivos(s, projeto.name).items():
        if caminho.startswith(base_app + "/"):
            if "/management/" in caminho and tem_admin:
                continue                               # o garantir_admin já vem da app principal
            arquivos[caminho] = conteudo
        elif caminho.startswith(("nucleo/", "docs/")):
            arquivos[f"{base_app}/{caminho}"] = conteudo
        elif caminho.startswith("tests/") and caminho != "tests/test_exercicios.py":
            arquivos[f"{base_app}/tests/nucleo/{caminho[len('tests/'):]}"] = conteudo
    for caminho in [c for c in arquivos if c.endswith(".py")]:
        arquivos[caminho] = _nucleo_dentro_da_app(arquivos[caminho], pacote)
    modulo = {"app": app, "pacote": pacote, "caminho": base_app[len("web/"):], "entidade": s.ent,
              "assunto": assunto, "dominio": s.origem.get("dominio_rotulo", ""), "padroes": s.padroes,
              "campos": [a["nome"] for a in s.atributos],
              "atributos": copy.deepcopy(s.atributos)}     # as regras de cada campo (sgs incrementar refaz daqui)
    arquivos[f"{base_app}/README.md"] = render(r'''
        # Módulo `@@APP@@` — @@ENT@@ (acrescentado por `sgs app`)

        Pedido: _"@@ASSUNTO@@"_ · domínio: `@@DOMINIO@@`

        | Item | Conteúdo |
        |---|---|
        | Pacote | `@@PACOTE@@` (registrado em `INSTALLED_APPS` de `web/config/settings.py`) |
        | Entidade | `@@ENT@@` — campos: @@CAMPOS@@, `tipo` |
        | Padrões | @@PADROES@@ — o núcleo deste módulo fica em `nucleo/` (dentro da app) |
        | Form | `@@ENT@@Form` (`forms.py`): o MESMO ModelForm valida as telas e a API |
        | CRUD (telas) | `/@@APP@@/` · `/@@APP@@/novo/` · `/@@APP@@/<id>/` · `/@@APP@@/<id>/editar/` · `/@@APP@@/<id>/excluir/` |
        | API REST | `/@@APP@@/api/v1/` (GET, POST) · `/@@APP@@/api/v1/<id>/` (GET, PUT, PATCH, DELETE) |
        | Settings | `settings.py` desta app: `API_LIMITE`, `API_ESCRITA` (no projeto: `@@PREFIXO@@_API_LIMITE`…) |
        | Arquivos | `settings.py` · `models.py` · `forms.py` · `services.py` · `viewmodels.py` · `views.py` · `api.py` · `urls.py` · `templates/` · `static/` · `nucleo/` · `tests/` |
        | Testes | `cd web && python -m pytest @@CAMINHO@@` (telas, API e o núcleo em `tests/nucleo/`) |
        | Banco | `bash iniciar.sh migrar` (o `makemigrations` já inclui `@@APP@@`) |
        ''', APP=app, ENT=s.ent, ASSUNTO=assunto, DOMINIO=modulo["dominio"], PACOTE=pacote,
        CAMPOS=", ".join(f"`{n}`" for n in modulo["campos"]), PADROES=", ".join(PADROES[p]["titulo"] for p in s.padroes),
        PREFIXO=app.upper(), CAMINHO=modulo["caminho"])
    for caminho, conteudo in arquivos.items():
        if caminho.endswith(".py"):
            try:
                ast.parse(conteudo)
            except SyntaxError as erro:  # pragma: no cover - indica bug do gerador
                raise RuntimeError(f"código gerado inválido em {caminho}: {erro}") from erro
    return arquivos, modulo


def aplicar_modulo(projeto, plano):
    """Escreve o módulo planejado e o REGISTRA no projeto: INSTALLED_APPS, a rota /<app>/ (antes da raiz),
    o makemigrations do iniciar.sh, modulos.json e uma seção no README."""
    projeto = Path(projeto)
    m = plano["modulo"]
    app, pacote = m["app"], m["pacote"]
    if (projeto / "web" / m["caminho"]).exists():
        raise ErroGerador(f"web/{m['caminho']} já existe neste sistema")
    pacote_projeto = pacote_do_projeto(projeto)                # "config" ou o do perfil ("cooperativa")
    settings_py = projeto / "web" / pacote_projeto / "settings.py"
    urls_py = projeto / "web" / pacote_projeto / "urls.py"
    texto_settings = settings_py.read_text(encoding="utf-8")
    lista = re.search(r"INSTALLED_APPS = \[\n(.*?)\n\]", texto_settings, re.S)
    texto_urls = urls_py.read_text(encoding="utf-8")
    # O 1º include das rotas (o do app principal, na raiz ou em /<rota>/ do perfil): o módulo entra antes dele.
    raiz = re.search(r'^(\s*)path\("[\w/-]*", include\(', texto_urls, re.M)
    if lista is None or raiz is None:
        raise ErroGerador(f"não achei INSTALLED_APPS em web/{pacote_projeto}/settings.py ou o include das rotas em "
                          f"web/{pacote_projeto}/urls.py — o projeto foi editado à mão?")
    escrever(projeto, plano["arquivos"])
    if f'"{pacote}"' not in lista.group(1):
        texto_settings = (texto_settings[:lista.end(1)] + f'\n    "{pacote}",  # módulo (sgs app)'
                          + texto_settings[lista.end(1):])
        settings_py.write_text(texto_settings, encoding="utf-8")
    rota = f'{raiz.group(1)}path("{app}/", include("{pacote}.urls")),  # módulo (sgs app): antes da raiz\n'
    urls_py.write_text(texto_urls[:raiz.start()] + rota + texto_urls[raiz.start():], encoding="utf-8")
    iniciar = projeto / "iniciar.sh"
    if iniciar.exists():
        texto_iniciar = iniciar.read_text(encoding="utf-8")
        iniciar.write_text(re.sub(r"(makemigrations(?: \w+)+)", lambda r: f"{r.group(1)} {app}", texto_iniciar),
                           encoding="utf-8")
    modulos = ler_modulos(projeto) + [m]
    (projeto / MODULOS).write_text(json.dumps(modulos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = projeto / "README.md"
    if readme.exists():
        with open(readme, "a", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(f"\n\n## Módulo `{app}` ({m['entidade']})\n\nApp Django acrescentada por `sgs app` "
                          f"(pedido: _\"{m['assunto']}\"_). Telas em `/{app}/`, API REST em `/{app}/api/v1/`, "
                          f"padrões: {', '.join(m['padroes'])}. Detalhes: `web/{m['caminho']}/README.md`.\n")
    plano["migrations"] = atualizar_migrations(projeto)      # site que já subiu: a app nova ganha a migration
    return projeto / "web" / m["caminho"]


def gerar_modulo(projeto, assunto, entidade=None, campos=None, padroes=None, dominio=None):
    """Planeja e aplica (no próprio projeto). A tela usa as duas etapas separadas para copiar antes (versão)."""
    plano = preparar_modulo(projeto, assunto, entidade=entidade, campos=campos, padroes=padroes, dominio=dominio)
    return aplicar_modulo(projeto, plano), plano


# =============================================================================
# 7c. LIGAÇÕES: um campo de referência de uma classe para outra (Viagcert.destino → Destino)
# =============================================================================
ARQ_LIGACOES = "ligacoes.json"   # na raiz do sistema: as referências acrescentadas (sgs ligar / sgs app … ligar=)


def entidades_do_projeto(projeto):
    """{Classe: {"app", "pacote", "caminho"}} das classes (models) de cada app do sistema, lidas do disco."""
    web = Path(projeto) / "web"
    achadas = {}
    for apps_py in sorted(list(web.glob("*/apps.py")) + list(web.glob("apps/*/apps.py"))):
        pasta = apps_py.parent
        try:
            texto = (pasta / "models.py").read_text(encoding="utf-8")
        except OSError:
            continue
        caminho = pasta.relative_to(web).as_posix()
        for classe in re.findall(r"^class (\w+)\(models\.Model\):", texto, re.M):
            achadas[classe] = {"app": pasta.name, "pacote": caminho.replace("/", "."), "caminho": caminho}
    return achadas


def ler_ligacoes(projeto):
    try:
        dados = json.loads((Path(projeto) / ARQ_LIGACOES).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [x for x in dados if isinstance(x, dict)] if isinstance(dados, list) else []


def achar_classe(entidades, nome):
    """O nome da classe como está no projeto (sem diferença de maiúsculas/acentos), ou None."""
    alvo = camel(nome or "").lower()
    return next((c for c in entidades if c.lower() == alvo), None)


def planejar_ligacao(projeto, origem, campo, alvo, novas=None):
    """Confere uma ligação origem.campo → alvo SEM escrever nada; devolve {"origem", "campo", "alvo"} já resolvido.

    `novas`: classes que ainda vão entrar (o módulo planejado agora), para planejar antes de copiar/escrever.
    Erro (ErroGerador) se a classe não existir, se o campo já existir ou se o nome não servir de campo.
    """
    entidades = dict(entidades_do_projeto(projeto))
    entidades.update(novas or {})
    o, a = achar_classe(entidades, origem), achar_classe(entidades, alvo)
    if o is None or a is None:
        falta = origem if o is None else alvo
        raise ErroGerador(f"não existe a classe {falta!r} neste sistema — classes: {', '.join(sorted(entidades))}")
    if o == a:
        raise ErroGerador("a ligação precisa de duas classes diferentes (origem e alvo)")
    campo = camel_para_snake(camel(campo)) if campo else camel_para_snake(a)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", campo) or keyword.iskeyword(campo) or campo in RESERVADOS \
            or campo in RESERVADOS_DJANGO or campo in ("tipo", "id_interno"):
        raise ErroGerador(f"{campo!r} não serve de nome de campo — escolha outro (ex.: {camel_para_snake(a)}_ref)")
    if o not in (novas or {}):
        modelo = (Path(projeto) / "web" / entidades[o]["caminho"] / "models.py").read_text(encoding="utf-8")
        if re.search(rf"^\s+{re.escape(campo)} = models\.", modelo, re.M):
            raise ErroGerador(f"a classe {o} já tem um campo {campo!r} — escolha outro nome (ex.: {campo}_ref)")
    return {"origem": o, "campo": campo, "alvo": a}


def ligar_classes(projeto, origem, campo, alvo, comentarios=True):
    """Acrescenta origem.campo = ForeignKey(alvo) — OPCIONAL (null/blank) e SET_NULL (apagar o alvo só limpa o campo).

    Mexe só no que precisa, sempre do mesmo jeito: models.py (o campo, antes do `tipo`), forms.py (o campo no
    Meta.fields), um teste novo da ligação, ligacoes.json e uma seção no README. Se o projeto já tem migrations,
    cria a migration nova (makemigrations) para o banco e os testes acompanharem. Devolve o dict da ligação.
    """
    projeto = Path(projeto)
    lig = planejar_ligacao(projeto, origem, campo, alvo)
    _escrever_ligacao(projeto, lig, comentarios)
    campo, o = lig["campo"], entidades_do_projeto(projeto)[lig["origem"]]
    ligacoes = [x for x in ler_ligacoes(projeto) if (x.get("origem"), x.get("campo")) != (lig["origem"], campo)]
    (projeto / ARQ_LIGACOES).write_text(json.dumps(ligacoes + [dict(lig)], ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    readme = projeto / "README.md"
    if readme.exists():
        with open(readme, "a", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(f"\n\n## Ligação `{lig['origem']}.{campo}` → `{lig['alvo']}`\n\nCampo de referência "
                          f"(ForeignKey) opcional, acrescentado por `sgs ligar`: aparece no formulário e na API REST "
                          f"de `{o['app']}` (o id do {lig['alvo']}); apagar o {lig['alvo']} só limpa o campo "
                          f"(SET_NULL). Teste: `web/{o['caminho']}/tests/test_ligacao_{campo}.py`.\n")
    lig["migrations"] = atualizar_migrations(projeto)
    return lig


def _escrever_ligacao(projeto, lig, comentarios=True):
    """Só os ARQUIVOS da ligação: o campo no models.py, no Meta.fields do form, o "—" do detalhe e o teste.
    Usado ao ligar e, depois de um sgs incrementar refazer a classe, para pôr a ligação de volta."""
    projeto = Path(projeto)
    entidades = entidades_do_projeto(projeto)
    o, a, campo = entidades[lig["origem"]], entidades[lig["alvo"]], lig["campo"]
    pasta = projeto / "web" / o["caminho"]
    models_py, forms_py = pasta / "models.py", pasta / "forms.py"
    modelo, form = models_py.read_text(encoding="utf-8"), forms_py.read_text(encoding="utf-8")
    tipo = re.search(r"^(\s+)tipo = models\.CharField\(", modelo, re.M)
    meta = re.search(r'(fields = \[[^\]]*?)("tipo"\])', form)
    if tipo is None or meta is None:
        raise ErroGerador(f"não reconheci o models.py/forms.py de {lig['origem']} (foi editado à mão?)")
    rotulo = campo.replace("_", " ")
    nota = (f"  # ligação (sgs ligar): opcional; apagar o {lig['alvo']} só limpa este campo" if comentarios else "")
    linha = (f'{tipo.group(1)}{campo} = models.ForeignKey("{a["app"]}.{lig["alvo"]}", verbose_name="{rotulo}", '
             f'null=True, blank=True, on_delete=models.SET_NULL, related_name="{o["app"]}_{campo}"){nota}\n')
    models_py.write_text(modelo[:tipo.start()] + linha + modelo[tipo.start():], encoding="utf-8")
    forms_py.write_text(form[:meta.start(2)] + f'"{campo}", ' + form[meta.start(2):], encoding="utf-8")
    viewmodels = pasta / "viewmodels.py"
    if viewmodels.exists():                       # detalhe: referência vazia aparece como "—" (não como None)
        texto_vm = viewmodels.read_text(encoding="utf-8")
        viewmodels.write_text(texto_vm.replace('valor if valor != "" else "—"', 'valor if valor not in ("", None) else "—"'),
                              encoding="utf-8")
    api = (pasta / "api.py").exists()
    teste = render(r'''
        """Ligação @@O@@.@@CAMPO@@ → @@A@@ (sgs ligar): referência OPCIONAL entre classes de apps diferentes."""
        import pytest

        from @@PKO@@.forms import @@O@@Form
        from @@PKO@@.models import @@O@@
        from @@PKO@@.tests.test_models import dados as dados_@@APPO@@
        from @@PKA@@.models import @@A@@
        from @@PKA@@.tests.test_models import dados as dados_@@APPA@@

        pytestmark = pytest.mark.django_db


        def test_o_campo_e_opcional_e_aponta_para_a_classe():
            campo = @@O@@._meta.get_field("@@CAMPO@@")
            assert campo.related_model is @@A@@ and campo.null and campo.blank
            assert "@@CAMPO@@" in @@O@@Form().fields


        def test_ligar_e_apagar_o_alvo_so_limpa_a_referencia():
            alvo = @@A@@.objects.create(**dados_@@APPA@@())
            obj = @@O@@.objects.create(**dados_@@APPO@@(), @@CAMPO@@=alvo)
            assert obj.@@CAMPO@@ == alvo and obj in alvo.@@REL@@.all()
            alvo.delete()
            obj.refresh_from_db()
            assert obj.@@CAMPO@@ is None
        @@TESTE_API@@
        ''', O=lig["origem"], A=lig["alvo"], CAMPO=campo, PKO=o["pacote"], PKA=a["pacote"], APPO=o["app"],
        APPA=a["app"], REL=f"{o['app']}_{campo}", TESTE_API="" if not api else "\n\n" + render(r'''
            def test_a_api_le_e_grava_a_referencia(client, settings):
                import json

                from django.urls import reverse

                setattr(settings, "@@PREFIXO@@_API_CAMPOS", {})    # o padrão (o sgs api config pode ter ocultado)
                alvo = @@A@@.objects.create(**dados_@@APPA@@())
                obj = @@O@@.objects.create(**dados_@@APPO@@())
                url = reverse("@@APPO@@:api_item", args=[obj.pk])
                resposta = client.patch(url, data=json.dumps({"@@CAMPO@@": str(alvo.pk)}), content_type="application/json")
                assert resposta.status_code == 200 and str(resposta.json()["@@CAMPO@@"]) == str(alvo.pk)
            ''', A=lig["alvo"], O=lig["origem"], APPA=a["app"], APPO=o["app"], CAMPO=campo, PREFIXO=o["app"].upper()))
    if not comentarios:
        teste = remover_comentarios(teste)
    ast.parse(teste)
    (pasta / "tests" / f"test_ligacao_{campo}.py").write_text(teste, encoding="utf-8")


# =============================================================================
# 7d. INCREMENTAR: acrescentar ou modificar UM campo de uma classe, com a regra (o padrão) dele
# =============================================================================
ARQ_INCREMENTOS = "incrementos.json"   # na raiz do sistema: os campos acrescentados/modificados (sgs incrementar)
REGRAS_DE_CAMPO = [   # (exemplo, o que faz) — o catálogo que a tela mostra
    ("texto", "texto obrigatório (vazio é recusado)"),
    ("texto-livre", "texto opcional, sem regra (atributo simples)"),
    ("inteiro>=0", "inteiro com mínimo: negativo e letras são recusados (troque o 0)"),
    ("inteiro:1..30", "inteiro numa faixa (mínimo..máximo)"),
    ("decimal>=0", "número decimal com mínimo"),
    ("decimal:0..100", "número decimal numa faixa"),
    ("lista:janela,meio,corredor", "LISTA fechada: só um desses valores (inteiros também: lista:1,2,3)"),
    ("simnao", "sim/não (só True ou False)"),
    ("data", "data válida AAAA-MM-DD"),
]


def ler_regra(texto):
    """"inteiro>=0", "inteiro:1..30", "decimal>=0", "lista:a,b,c", "texto", "texto-livre", "simnao", "data"
    → {"tipo", "regra", "min", "max"[, "opcoes"]}. Erro (ErroGerador) com o catálogo se não entender."""
    t = normalizar(texto or "").replace(" ", "")
    numero = r"-?\d+(?:[.,]\d+)?"

    def num(valor, inteiro):
        valor = valor.replace(",", ".")
        return int(valor) if inteiro else float(valor)

    m = re.fullmatch(rf"(inteiro|int|decimal|float|numero)(?:>=|:min=?|min)({numero})", t)
    if m:
        inteiro = m.group(1) in ("inteiro", "int")
        if inteiro and not re.fullmatch(r"-?\d+", m.group(2)):
            raise ErroGerador("inteiro>=N: N precisa ser inteiro")
        return {"tipo": "int" if inteiro else "float", "regra": "minimo", "min": num(m.group(2), inteiro), "max": None}
    m = re.fullmatch(rf"(inteiro|int|decimal|float|numero|faixa):?({numero})\.\.({numero})", t)
    if m:
        inteiro = m.group(1) in ("inteiro", "int", "faixa") and "." not in m.group(2) + m.group(3).replace("..", "")
        minimo, maximo = num(m.group(2), inteiro), num(m.group(3), inteiro)
        if minimo >= maximo:
            raise ErroGerador("faixa: o mínimo precisa ser menor que o máximo (ex.: inteiro:1..30)")
        return {"tipo": "int" if inteiro else "float", "regra": "faixa", "min": minimo, "max": maximo}
    m = re.fullmatch(r"(?:lista|opcoes|valores):(.+)", normalizar(texto or "").strip())
    if m:
        bruto = [v.strip() for v in re.split(r"[,;|]", (texto or "").split(":", 1)[1]) if v.strip()]
        inteiros = all(re.fullmatch(r"-?\d+", v) for v in bruto)
        opcoes = [int(v) for v in bruto] if inteiros else bruto
        if len(opcoes) < 2 or len(set(opcoes)) != len(opcoes):
            raise ErroGerador("lista: pelo menos 2 valores diferentes (ex.: lista:janela,meio,corredor)")
        if not inteiros and any(PROIBIDO_EM_TEXTO.search(v) for v in opcoes):
            raise ErroGerador("lista: os valores não podem ter aspas, chaves ou barra invertida")
        return {"tipo": "int" if inteiros else "str", "regra": "lista", "min": None, "max": None, "opcoes": opcoes}
    simples = {"texto": ("str", "obrigatorio"), "obrigatorio": ("str", "obrigatorio"), "str": ("str", "obrigatorio"),
               "texto-livre": ("str", "livre"), "textolivre": ("str", "livre"), "livre": ("str", "livre"),
               "simnao": ("bool", "obrigatorio"), "sim/nao": ("bool", "obrigatorio"), "bool": ("bool", "obrigatorio"),
               "data": ("data", "obrigatorio")}
    if t in simples:
        tipo, regra = simples[t]
        return {"tipo": tipo, "regra": regra, "min": None, "max": None}
    raise ErroGerador(f"regra {texto!r} não reconhecida — use: " + " · ".join(r for r, _ in REGRAS_DE_CAMPO))


def regra_em_texto(a):
    """A regra de um atributo no formato do sgs incrementar (o inverso do ler_regra)."""
    if a["regra"] == "lista":
        return "lista:" + ",".join(str(o) for o in a["opcoes"])
    if a["tipo"] in ("int", "float"):
        nome = "inteiro" if a["tipo"] == "int" else "decimal"
        return f"{nome}>={a['min']}" if a["regra"] == "minimo" else f"{nome}:{a['min']}..{a['max']}"
    return {"bool": "simnao", "data": "data"}.get(a["tipo"], "texto-livre" if a["regra"] == "livre" else "texto")


def classes_do_projeto(projeto):
    """{Classe: {"app", "pacote", "caminho", "principal": bool, "atributos": [...]}} — as classes e os campos
    (com as regras) que o sgs incrementar pode mudar. A principal lê do especificacao.json; os módulos, do modulos.json."""
    projeto = Path(projeto)
    entidades = entidades_do_projeto(projeto)
    try:
        espec = json.loads((projeto / "especificacao.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        espec = {}
    saida = {}
    if isinstance(espec, dict) and isinstance(espec.get("entidade"), str) and isinstance(espec.get("atributos"), list):
        sem_web = {"app": None, "pacote": None, "caminho": None}           # sistema só com o núcleo (sem Django)
        saida[espec["entidade"]] = {**entidades.get(espec["entidade"], sem_web), "principal": True,
                                    "atributos": copy.deepcopy(espec["atributos"])}
    for m in ler_modulos(projeto):
        if m.get("entidade") not in entidades:
            continue
        atributos = m.get("atributos")
        if not isinstance(atributos, list):                 # módulo de antes do incrementar: refaz a Spec do pedido
            atributos = _spec_do_modulo(projeto, m["assunto"], m["entidade"], None, m.get("padroes"),
                                        m.get("dominio") or None).atributos
        saida[m["entidade"]] = {**entidades[m["entidade"]], "principal": False, "modulo": m,
                                "atributos": copy.deepcopy(atributos)}
    return saida


def valor_padrao(a):
    """O valor que as linhas que JÁ estão no banco recebem quando o campo é novo (vai para o default do model)."""
    if a["regra"] == "lista":
        return a["opcoes"][0]
    if a["tipo"] in ("int", "float"):
        return a["min"]
    return {"bool": False, "data": DATAS_EXEMPLO[0]}.get(a["tipo"], "")


def planejar_incremento(projeto, classe, campo, regra):
    """Acrescenta (campo novo) ou modifica (campo que já existe) UM campo da classe, com a regra pedida — sem
    escrever nada. A classe inteira é REFEITA pelo gerador a partir da Spec atualizada: o @property do núcleo, o
    model (validators/choices), o form, a API e os testes ficam coerentes. Devolve o plano para aplicar_incremento()."""
    projeto = Path(projeto)
    classes = classes_do_projeto(projeto)
    nome_classe = achar_classe(classes, classe)
    if nome_classe is None:
        raise ErroGerador(f"não existe a classe {classe!r} neste sistema (ou ela não foi gerada pelo SGS) — "
                          f"classes: {', '.join(sorted(classes)) or 'nenhuma'}")
    info = classes[nome_classe]
    campo = camel_para_snake(camel(campo or ""))
    if not re.fullmatch(r"[a-z][a-z0-9_]*", campo) or keyword.iskeyword(campo) or campo in RESERVADOS \
            or campo in RESERVADOS_DJANGO or campo in ("tipo", "id_interno"):
        raise ErroGerador(f"{campo!r} não serve de nome de campo — use letras, números e _ (ex.: assento, codigo_voo)")
    if any(x.get("origem") == nome_classe and x.get("campo") == campo for x in ler_ligacoes(projeto)):
        raise ErroGerador(f"{nome_classe}.{campo} é uma LIGAÇÃO (referência) — mude com sgs ligar, não com incrementar")
    nova = ler_regra(regra) if isinstance(regra, str) else dict(regra)
    atributos = info["atributos"]
    atual = next((a for a in atributos if a["nome"] == campo), None)
    if atual is not None:
        acao = "modificado"
        atual.update({k: nova.get(k) for k in ("tipo", "regra", "min", "max")})
        if nova["regra"] == "lista":
            atual["opcoes"] = nova["opcoes"]
        else:
            atual.pop("opcoes", None)
        if "padrao" in atual:                               # o default acompanha a regra nova
            atual["padrao"] = valor_padrao(atual)
    else:
        acao = "novo"
        novo = {"nome": campo, **{k: nova.get(k) for k in ("tipo", "regra", "min", "max")}}
        if nova["regra"] == "lista":
            novo["opcoes"] = nova["opcoes"]
        if novo["regra"] != "livre":
            novo["padrao"] = valor_padrao(novo)
        posicao = max([i + 1 for i, a in enumerate(atributos) if a["regra"] != "livre"] or [0])
        atributos.insert(posicao, novo)
    try:
        s, arquivos = _classe_refeita(projeto, info, atributos)
    except ErroGerador as erro:
        raise ErroGerador(f"{nome_classe}.{campo} com a regra {regra!r} não fecha com o resto da classe: {erro}") from erro
    alvo = next(a for a in s.atributos if a["nome"] == campo)
    return {"classe": nome_classe, "campo": campo, "acao": acao, "regra": regra_em_texto(alvo),
            "descricao": descrever_regra(alvo), "principal": info["principal"], "arquivos": arquivos,
            "atributos": s.atributos, "app": info["app"]}


def _classe_refeita(projeto, info, atributos):
    """(Spec, arquivos) da classe refeita pelo gerador com estes atributos — a principal pelo especificacao.json
    (sem README, iniciar.sh e config/, que têm o que os módulos acrescentaram), o módulo pelo modulos.json."""
    projeto = Path(projeto)
    if info["principal"]:
        espec = json.loads((projeto / "especificacao.json").read_text(encoding="utf-8"))
        espec["atributos"] = atributos
        s = montar_spec(spec=espec, exercicio=(projeto / "exercicios.html").exists())
        arquivos = montar_arquivos(s, projeto.name)
        for intocavel in ("README.md", "iniciar.sh", f"web/{s.projeto}/settings.py", f"web/{s.projeto}/urls.py"):
            arquivos.pop(intocavel, None)
        return s, arquivos
    m = info["modulo"]
    s = _spec_do_modulo(projeto, m["assunto"], m["entidade"], [], m.get("padroes"), m.get("dominio") or None,
                        atributos=atributos)
    return s, _arquivos_do_modulo(projeto, s, m["assunto"])[0]


def _escrever_classe(projeto, plano, comentarios=True):
    """Escreve só os arquivos que MUDARAM, põe de volta as ligações da classe e anota os atributos do módulo."""
    projeto = Path(projeto)
    mudaram = []
    for caminho, conteudo in plano["arquivos"].items():   # mesmo conteúdo = nem toca (data do arquivo e git quietos)
        alvo = projeto / caminho
        atual = alvo.read_bytes() if alvo.is_file() else None
        novo = conteudo if isinstance(conteudo, bytes) else conteudo.encode("utf-8")
        if atual != novo:
            escrever(projeto, {caminho: conteudo})
            mudaram.append(caminho)
    for lig in ler_ligacoes(projeto):                    # a classe foi refeita: as referências dela voltam
        if lig.get("origem") == plano["classe"]:
            _escrever_ligacao(projeto, lig, comentarios)
    if not plano["principal"]:
        modulos = ler_modulos(projeto)
        for m in modulos:
            if m.get("entidade") == plano["classe"]:
                m["atributos"] = plano["atributos"]
                m["campos"] = [a["nome"] for a in plano["atributos"]]
        (projeto / MODULOS).write_text(json.dumps(modulos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return mudaram


def refazer_classe(projeto, classe, comentarios=True):
    """Refaz a classe com as MESMAS regras, pelo gerador de hoje — a app ganha o que o gerador passou a fazer
    depois (ex.: os campos configuráveis da API). Determinístico; as ligações voltam. Devolve os arquivos que mudaram."""
    projeto = Path(projeto)
    classes = classes_do_projeto(projeto)
    nome = achar_classe(classes, classe)
    if nome is None:
        raise ErroGerador(f"não existe a classe {classe!r} neste sistema")
    s, arquivos = _classe_refeita(projeto, classes[nome], classes[nome]["atributos"])
    plano = {"classe": nome, "principal": classes[nome]["principal"], "arquivos": arquivos, "atributos": s.atributos}
    mudaram = _escrever_classe(projeto, plano, comentarios)
    atualizar_migrations(projeto)
    return mudaram


# --- API: os campos de cada endpoint (sgs api config) — gravados no config/settings.py do projeto ---------------
INICIO_API = "# --- API: campos de cada endpoint (sgs api config) — só o que mudou do padrão ---"
FIM_API = "# --- fim da API (sgs api config) ---"
ENDPOINTS_API = {"v1": "api/v1/", "resumo": "api/"}
CALCULADOS_API = ("total", "valor_final", "codigo", "titulo", "valor")


def exposto_por_padrao(endpoint, campo):
    """O mesmo padrão do api.py gerado: o v1 mostra o registro inteiro; o resumo, id, codigo, titulo e valor."""
    return campo in ("id", "codigo", "titulo", "valor") if endpoint == "resumo" else campo not in ("codigo", "titulo", "valor")


def ler_api_campos(projeto):
    """{app: {endpoint: {campo: bool}}} — o que o projeto mudou do padrão (o bloco do sgs api config)."""
    try:
        texto = (Path(projeto) / "web" / pacote_do_projeto(projeto) / "settings.py").read_text(encoding="utf-8")
    except OSError:
        return {}
    saida = {}
    for app, valor in re.findall(r"^([A-Z][A-Z0-9_]*)_API_CAMPOS = (.+)$", texto, re.M):
        try:
            dados = ast.literal_eval(valor)
        except (ValueError, SyntaxError):
            continue
        if isinstance(dados, dict):
            saida[app.lower()] = {e: {c: bool(v) for c, v in (d or {}).items()} for e, d in dados.items() if e in ENDPOINTS_API}
    return saida


def gravar_api_campos(projeto, escolhas):
    """Reescreve o bloco do sgs api config no fim do config/settings.py (o resto do arquivo não muda)."""
    caminho = Path(projeto) / "web" / pacote_do_projeto(projeto) / "settings.py"
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(rf"\n*{re.escape(INICIO_API)}.*?{re.escape(FIM_API)}\n?", "\n", texto, flags=re.S).rstrip("\n") + "\n"
    linhas = []
    for app in sorted(escolhas):
        limpo = {e: dict(sorted(c.items())) for e, c in sorted(escolhas[app].items()) if c}
        if limpo:
            linhas.append(f"{app.upper()}_API_CAMPOS = {limpo!r}")
    if linhas:
        texto += f"\n{INICIO_API}\n" + "\n".join(linhas) + f"\n{FIM_API}\n"
    caminho.write_text(texto, encoding="utf-8")


def endpoints_do_projeto(projeto):
    """Os endpoints de cada app do sistema, com cada campo e se está EXPOSTO:
    [{"app", "classe", "endpoint", "rota", "suporta", "campos": [(campo, exposto, mudado)]}]."""
    projeto = Path(projeto)
    try:
        espec = json.loads((projeto / "especificacao.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        espec = {}
    principal = espec.get("entidade") if isinstance(espec, dict) else None
    # O app principal fica na raiz — ou em /<rota>/ quando o perfil do domínio diz (Prova P3: /citricultura/).
    rota_principal = ((espec.get("perfil") or {}).get("rota") or "") if isinstance(espec, dict) else ""
    escolhas = ler_api_campos(projeto)
    saida = []
    for classe, info in sorted(entidades_do_projeto(projeto).items(), key=lambda par: (par[0] != principal, par[0])):
        pasta = projeto / "web" / info["caminho"]
        modelo = (pasta / "models.py").read_text(encoding="utf-8")
        corpo = modelo.split(f"class {classe}(models.Model):", 1)[-1]
        campos_model = [n for n in re.findall(r"^    (\w+) = models\.\w+\(", corpo, re.M) if n != "id"]
        try:
            suporta = "API_CAMPOS" in (pasta / "settings.py").read_text(encoding="utf-8")
        except OSError:
            suporta = False
        prefixo = f"/{rota_principal}" if classe == principal else f"/{info['app']}/"
        for endpoint, rota in ENDPOINTS_API.items():
            mudou = escolhas.get(info["app"], {}).get(endpoint, {})
            campos = [(c, mudou.get(c, exposto_por_padrao(endpoint, c)), c in mudou)
                      for c in ["id"] + campos_model + list(CALCULADOS_API)]
            saida.append({"app": info["app"], "classe": classe, "endpoint": endpoint, "rota": prefixo + rota,
                          "suporta": suporta, "campos": campos})
    return saida


def aplicar_incremento(projeto, plano, comentarios=True):
    """Escreve a classe refeita, põe de volta as ligações dela, anota (especificacao.json / modulos.json,
    incrementos.json, README) e cria a migration se o site já subiu."""
    projeto = Path(projeto)
    _escrever_classe(projeto, plano, comentarios)
    try:
        historico = json.loads((projeto / ARQ_INCREMENTOS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        historico = []
    registro = {k: plano[k] for k in ("classe", "campo", "acao", "regra")}
    (projeto / ARQ_INCREMENTOS).write_text(
        json.dumps((historico if isinstance(historico, list) else []) + [registro], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    readme = projeto / "README.md"
    if readme.exists():
        with open(readme, "a", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(f"\n\n## Campo `{plano['classe']}.{plano['campo']}` ({plano['acao']})\n\nRegra: "
                          f"{plano['descricao']} — `{plano['regra']}` (sgs incrementar). Vale no @property do núcleo, "
                          f"no model (validators/choices), no form e na API; os testes da classe foram refeitos.\n")
    plano["migrations"] = atualizar_migrations(projeto)
    return plano


def incrementar_campo(projeto, classe, campo, regra, comentarios=True):
    """Planeja e aplica no próprio projeto (a tela separa as etapas para copiar antes, na versão)."""
    return aplicar_incremento(projeto, planejar_incremento(projeto, classe, campo, regra), comentarios)


def atualizar_migrations(projeto):
    """Se o sistema JÁ tem migrations (o site já subiu), cria as novas (makemigrations de todas as apps) para o
    banco e os testes acompanharem a mudança. Sem migrations ainda: nada (o iniciar.sh cria na hora de subir)."""
    web = Path(projeto) / "web"
    if not any(web.glob("**/migrations/0*.py")):
        return "sem migrations ainda — o iniciar.sh cria quando o site subir"
    if importlib.util.find_spec("django") is None:
        return "Django não está instalado neste Python — rode: bash iniciar.sh migrar"
    apps = sorted({info["app"] for info in entidades_do_projeto(Path(projeto)).values()})
    r = subprocess.run([sys.executable, "manage.py", "makemigrations", *apps], cwd=web, capture_output=True,
                       text=True, timeout=300,
                       env=dict(os.environ, DJANGO_SETTINGS_MODULE=f"{pacote_do_projeto(projeto)}.settings"))
    saida = (r.stdout + r.stderr).strip().splitlines()
    if r.returncode:
        raise ErroGerador("makemigrations falhou: " + " | ".join(saida[-5:]))
    return " · ".join(linha.strip() for linha in saida if linha.strip()) or "nenhuma mudança"


# =============================================================================
# 8. INTERFACE (linha de comando e menu interativo)
# =============================================================================
def filtrar_dominios(termo=None):
    """[(chave, dados, info, palavras que bateram)] dos domínios cujo ID, nome, sistema, entidade, setor ou
    palavras contêm o termo (sem acento, sem diferença de maiúsculas). Sem termo: todos, na ordem do catálogo."""
    alvo = normalizar((termo or "").replace("_", " "))
    saida = []
    for chave, d in DOMINIOS.items():
        info = INFO_DOMINIOS[chave]
        campos = [info["id"], chave.replace("_", " "), d["sistema"], d["entidade"], info["setor"]]
        bateram = [p for p in d["palavras"] if alvo and alvo in normalizar(p)]
        if not alvo or bateram or any(alvo in normalizar(c) for c in campos):
            saida.append((chave, d, info, bateram))
    return saida


def listar(termo=None):
    achados = filtrar_dominios(termo)
    filtro = f" com “{termo}”" if termo else ""
    print(f"DOMÍNIOS (--dominio){filtro}: {len(achados)} de {len(DOMINIOS)}, por setor"
          + ("" if termo else " — filtre com: --listar <termo>  (ex.: --listar saude)"))
    setor_atual = None
    for chave, d, info, bateram in achados:
        if info["setor"] != setor_atual:
            setor_atual = info["setor"]
            print(f"\n  [{setor_atual}]")
        palavras = ", ".join((bateram or d["palavras"])[:6]) or "(usado quando o assunto não bate com nenhum)"
        print(f"    {info['id']} {chave:<19} {d['sistema']:<24} {d['entidade']:<16} palavras: {palavras}")
    if termo:
        return
    print("\nPADRÕES (--padrao, vários separados por espaço), por categoria:")
    for categoria, membros in CATEGORIAS.items():
        print(f"\n  [{categoria}] {NOMES_CATEGORIAS[categoria]}")
        for chave in membros:
            info = PADROES[chave]
            print(f"    {chave:<17} {info['titulo']:<28} palavras: {', '.join(info['palavras'][:5])}")
    print("\nGRUPOS (também valem em --padrao): todos (28) · gof (23) · prova (os 9 da P3) · "
          "criacao (5) · estrutural (7) · comportamental (11) · fundamentos (5)")
    print(f"Referência da lista GoF: Gerador_Sistemas/{REFERENCIA_GOF}")


def perguntar(texto, padrao=None):
    sufixo = f" [{padrao}]" if padrao else ""
    try:
        resposta = input(f"{texto}{sufixo}: ").strip()
    except EOFError:
        resposta = ""
    return resposta or (padrao or "")


def modo_interativo():
    print("=" * 64)
    print(" Gerador determinístico de sistemas de estudo — ILP-037 (P3)")
    print("=" * 64)
    print("1) Descrever o ASSUNTO em texto livre (o gerador escolhe domínio e padrões)")
    print("2) Escolher DOMÍNIO e PADRÕES no menu")
    print("3) Usar um arquivo de ESPECIFICAÇÃO (JSON)")
    modo = perguntar("Opção", "1")
    opcoes = {}
    if modo == "3":
        opcoes["spec"] = perguntar("Caminho do JSON")
    elif modo == "2":
        chaves = list(DOMINIOS)                       # o número é o ID do catálogo (001 hotel … 100 generico)
        setor_atual = None
        for i, chave in enumerate(chaves, 1):
            if INFO_DOMINIOS[chave]["setor"] != setor_atual:
                setor_atual = INFO_DOMINIOS[chave]["setor"]
                print(f"  [{setor_atual}]")
            print(f"  {i:>3}) {chave:<19} {DOMINIOS[chave]['sistema']}")
        escolha = perguntar("Domínio (número ou nome)", "1")
        opcoes["dominio"] = chaves[int(escolha) - 1] if escolha.isdigit() and 0 < int(escolha) <= len(chaves) else escolha
        if opcoes["dominio"] == "generico":
            opcoes["sistema"] = perguntar("Nome do sistema", "Sistema Exemplo")
            opcoes["entidade"] = perguntar("Nome da entidade principal (classe)", "Atendimento")
        for i, chave in enumerate(ORDEM_PADROES, 1):
            print(f"  {i:>2}) {chave:<17} {PADROES[chave]['titulo']}")
        escolha = perguntar("Padrões (números/nomes separados por vírgula, ou um grupo: todos, gof, prova, "
                            "criacao, estrutural, comportamental)", "prova")
        partes = [x.strip() for x in escolha.split(",") if x.strip()]
        opcoes["padroes"] = [ORDEM_PADROES[int(x) - 1] if x.isdigit() and 0 < int(x) <= len(ORDEM_PADROES) else x
                             for x in partes]
    else:
        opcoes["assunto"] = perguntar("Descreva o sistema/assunto",
                                      "loja em que o desconto depende do tipo de cliente e o pagamento usa API de terceiro")
    opcoes["django"] = perguntar("Gerar também a camada web Django? (s/n)", "n").lower().startswith("s")
    opcoes["exercicio"] = perguntar("Modo exercício (questionário com \"Ver resposta\"; o código sai completo)? (s/n)", "n").lower().startswith("s")
    opcoes["estudo"] = perguntar("Gerar para ESTUDO (antes_*.py, ADRs, README didático)? (s = estudo / n = só gerar)",
                                 "s").lower().startswith("s")
    opcoes["comentarios"] = perguntar("Com comentários explicativos? (s = comentado / n = apenas o código)",
                                      "s").lower().startswith("s")
    opcoes["forcar"] = True
    testar_ = perguntar("Rodar os testes ao final? (s/n)", "s").lower().startswith("s")
    return opcoes, testar_


def executar_testes(destino, s):
    """Roda o pytest do sistema gerado e DEVOLVE os resultados (quem imprime é testar() ou a tela).

    Cada item: {"rotulo", "resumo" (última linha do pytest), "codigo" (0 = passou), "conta"}.
    "conta" é False só para o que foi pulado (ex.: Django não instalado).
    """
    if importlib.util.find_spec("pytest") is None:
        return [{"rotulo": "pytest", "resumo": "pytest não está instalado neste Python: pip install pytest",
                 "codigo": 1, "conta": True}]
    resultados = []

    def rodar(rotulo, pasta, ambiente=None, conta=True):
        env = dict(os.environ, **(ambiente or {}))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                           cwd=pasta, capture_output=True, text=True, env=env)
        ultima = (r.stdout.strip().splitlines() or ["(sem saída)"])[-1]
        resultados.append({"rotulo": rotulo, "resumo": ultima, "codigo": r.returncode, "conta": conta})

    rodar("núcleo (Python puro)", destino)
    if s.django:
        if importlib.util.find_spec("django") and importlib.util.find_spec("pytest_django"):
            rodar("web (Django)", destino / "web")
        else:
            resultados.append({"rotulo": "web (Django)", "resumo": "pulado — instale com: pip install django pytest-django",
                               "codigo": 0, "conta": False})
    return resultados


def testar(destino, s):
    """Versão de terminal: imprime os resultados e devolve 0 se tudo que conta passou."""
    codigo = 0
    print("\nTestes:")
    for r in executar_testes(destino, s):
        print(f"  {r['rotulo']:<38} {r['resumo']}")
        if r["conta"]:
            codigo |= r["codigo"]
    return codigo


def opcoes_web_da_linha(a):
    """Só as opções web que foram de fato informadas (as outras ficam com o padrão / a especificação)."""
    web = {"estilo": a.estilo, "tema": a.tema, "tom": a.tom, "paleta": a.paleta}
    web = {k: v for k, v in web.items() if v}
    if a.notas_web:
        web["comentarios_web"] = True
    if a.uuid:
        web["id_publico"] = "uuid"
    if a.lnnl:
        web.update(id_interno=True, lnnl_tipo=a.lnnl)
    if a.apps:
        web["estrutura"] = "apps"
    if a.seguranca_baseline:
        web["seguranca"] = "baseline"
    return web


def principal(argv=None):
    p = argparse.ArgumentParser(description="Gerador DETERMINÍSTICO de sistemas de estudo (ILP-037 · P3).",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--listar", nargs="?", const="", metavar="TERMO",
                   help="mostra os 100 domínios (por setor) e os padrões; com TERMO, só os domínios que batem (ex.: saude)")
    p.add_argument("--dominio", help="um dos 100 domínios do catálogo (hotel, petshop, oficina… — veja --listar)")
    p.add_argument("--assunto", help="texto livre: o gerador escolhe domínio e padrões por palavras-chave")
    p.add_argument("--spec", help="arquivo JSON de especificação (veja --modelo-spec)")
    p.add_argument("--modelo-spec", action="store_true", help="imprime um JSON de especificação para editar")
    p.add_argument("--padrao", nargs="+", help="padrões (ex.: strategy decorator) ou grupo: todos, gof, prova, "
                                                "criacao, estrutural, comportamental, fundamentos")
    p.add_argument("--sistema", help="nome do sistema (renomeia o do domínio)")
    p.add_argument("--entidade", help="nome da classe principal (renomeia a do domínio)")
    p.add_argument("--campos", nargs="+", metavar="CAMPO",
                   help="campos a mais na entidade: nome:str idade:int peso:float vacinado:bool nascimento:data "
                        "(sem :tipo, o identificador de tipos deduz pelo nome)")
    p.add_argument("--django", action="store_true", help="gera também o projeto Django (MVT) com testes")
    p.add_argument("--exercicio", action="store_true", help="questionário de revisão (exercicios.html, resposta oculta em \"Ver resposta\"); o código sai completo")
    p.add_argument("--direto", action="store_true",
                   help="só gerar: sem antes_*.py, sem ADRs e com README curto (o padrão é gerar para estudo)")
    p.add_argument("--sem-comentarios", action="store_true",
                   help="apenas o código: tira comentários e docstrings dos .py")
    p.add_argument("--estilo", choices=list(ESTILOS), help="(--django) formatação das páginas: " + ", ".join(ESTILOS))
    p.add_argument("--tema", help="(estilo web) T01 a T10 — temas da pasta temas/")
    p.add_argument("--tom", help="(estilo web) claro, tom2, tom3, tom4, tom5 ou escuro")
    p.add_argument("--paleta", help="(tema T10) P01 a P20 — paletas das Instruções §11.9")
    p.add_argument("--notas-web", action="store_true", help="(--django) notas de apresentação visíveis nas páginas")
    p.add_argument("--uuid", action="store_true", help="(--django) chave UUIDv4 (Instruções §10.4)")
    p.add_argument("--lnnl", nargs="?", const="21", metavar="TIPO",
                   help="(--django) ID interno LNNL (motor-id-interno); TIPO de 2 dígitos 1–9, padrão 21")
    p.add_argument("--apps", action="store_true", help="(--django) app em apps/<nome>/ + README (Instruções §9.2)")
    p.add_argument("--seguranca-baseline", action="store_true",
                   help="(--django) baseline de segurança das Instruções §12–14 (cabeçalhos, cookies, CSP, ADMIN_URL)")
    p.add_argument("--saida", help=f"pasta onde criar o sistema (padrão: {PASTA_PADRAO})")
    p.add_argument("--nome", help="nome da pasta do sistema (padrão: <sistema>__<padroes>)")
    p.add_argument("--forcar", action="store_true", help="substitui uma pasta gerada anteriormente")
    p.add_argument("--testar", action="store_true", help="roda os testes do sistema gerado")
    a = p.parse_args(argv)
    try:
        if a.listar is not None:
            listar(a.listar or None)
            return 0
        if a.modelo_spec:
            print(json.dumps(modelo_spec(), ensure_ascii=False, indent=2))
            return 0
        if a.dominio or a.assunto or a.spec:
            opcoes = dict(dominio=a.dominio, assunto=a.assunto, spec=a.spec, padroes=a.padrao, sistema=a.sistema,
                          entidade=a.entidade, django=a.django, exercicio=a.exercicio, saida=a.saida,
                          nome=a.nome, forcar=a.forcar, estudo=not a.direto, comentarios=not a.sem_comentarios,
                          web=opcoes_web_da_linha(a), campos=a.campos)
            quer_testar = a.testar
        else:
            opcoes, quer_testar = modo_interativo()
            opcoes.update(saida=a.saida, nome=a.nome)
        destino, s = gerar(**opcoes)
    except ErroGerador as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    print(f"\nSistema gerado em: {destino}")
    print(f"  domínio/sistema: {s.sistema} · entidade: {s.ent}")
    print(f"  padrões ({len(s.padroes)}): {', '.join(s.padroes)}" + (" · + web Django" if s.django else "")
          + (" · modo exercício" if s.exercicio else "") + ("" if s.estudo else " · só gerar")
          + ("" if s.comentarios else " · apenas o código"))
    if s.django:
        print(f"  subir o site: cd \"{destino}\" && bash iniciar.sh   (ajuda: bash iniciar.sh ajuda)")
    if s.origem.get("assunto"):
        print(f"  decisão: domínio '{s.origem['dominio']}' ({', '.join(s.origem['dominio_palavras']) or 'genérico'})")
        for p_, palavras in s.origem["padroes_palavras"].items():
            print(f"           {p_:<15} ← {', '.join(palavras)}")
    if s.origem.get("campos"):
        import tipos_campos
        print("  campos novos: " + ", ".join(f"{c['nome']} ({tipos_campos.rotulo(c['tipo'])})" for c in s.origem["campos"]))
    for nota in s.origem.get("notas", []):
        print(f"  nota: {nota}")
    print(f"  leia primeiro: {destino / 'README.md'}")
    if quer_testar:
        return testar(destino, s)
    return 0


if __name__ == "__main__":
    sys.exit(principal())

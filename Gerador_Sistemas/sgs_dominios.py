#!/usr/bin/env python3
"""
sgs_dominios.py — módulo para adicionar, listar e remover DOMÍNIOS personalizados além dos 101 nativos.

Os 101 domínios nativos moram em catalogo_100_dominios.txt + dominios.py (intocados).
Domínios criados pelo usuário ficam salvos em dominios_extras.json (IDs a partir de 102) e são carregados
automaticamente por dominios.montar() — valendo em `sgs gerar`, `sgs dominios`, `sgs app` e na CLI.

Uso pela linha de comando (ou pela tela do SGS via `sgs dominios novo`):
    python sgs_dominios.py listar
    python sgs_dominios.py novo energia_eolica --sistema "Eólica Sul" --entidade Turbina \\
        --palavras "eolica, turbina, vento, aerogerador, parque eolico"
    python sgs_dominios.py remover energia_eolica
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ARQUIVO_PADRAO = AQUI / "dominios_extras.json"
SETOR_PADRAO = "Personalizados"
MINIMO_PALAVRAS = 3
PROIBIDO = re.compile(r'["\'\\{}]')
RESERVADOS_CAMPO = {
    "id", "pk", "tipo", "total", "valor", "valor_final", "observacao", "class", "def", "return", "from", "import",
    "self", "cls", "pass", "none", "true", "false", "delete", "save", "objects", "meta",
}


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "").lower().strip())
    return "".join(c for c in texto if not unicodedata.combining(c))


def _snake(texto):
    texto = re.sub(r"[^a-z0-9]+", "_", _normalizar(texto)).strip("_")
    return texto


def _camel(texto):
    partes = re.findall(r"[A-Za-z0-9]+", _normalizar(texto))
    return "".join(p.capitalize() for p in partes)


def _limpar_texto(texto, rotulo, limite=60):
    texto = (texto or "").strip()
    if not texto or PROIBIDO.search(texto) or len(texto) > limite:
        raise ValueError(f"{rotulo}: informe um texto de até {limite} caracteres, sem aspas, chaves ou barra invertida")
    return texto


def _limpar_campo(texto, rotulo):
    nome = _snake(texto)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nome) or nome in RESERVADOS_CAMPO:
        raise ValueError(f"{rotulo}: use um identificador válido (letras minúsculas, números e _; ex.: cliente, horas)")
    return nome


def limpar_palavras(palavras):
    """Aceita string separada por vírgula ou lista; remove duplicatas normalizadas e preserva frases (sem '_')."""
    if isinstance(palavras, str):
        brutas = re.split(r"[,;\n]+", palavras)
    elif isinstance(palavras, (list, tuple)):
        brutas = [str(p) for p in palavras]
    else:
        brutas = []
    resultado, vistas = [], set()
    for item in brutas:
        limpa = re.sub(r"\s+", " ", item.strip().replace("_", " "))
        if not limpa or PROIBIDO.search(limpa):
            continue
        chave = _normalizar(limpa)
        if chave and chave not in vistas:
            vistas.add(chave)
            resultado.append(limpa)
    if len(resultado) < MINIMO_PALAVRAS:
        raise ValueError(f"palavras: informe pelo menos {MINIMO_PALAVRAS} palavras-chave separadas por vírgula "
                         "(ex.: eolica, turbina, vento, aerogerador)")
    return resultado


def ler_extras(caminho=None):
    """Lista de dicts de domínios personalizados salvos em dominios_extras.json ([] se não existir)."""
    arq = Path(caminho) if caminho is not None else ARQUIVO_PADRAO
    if not arq.is_file():
        return []
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if isinstance(dados, dict) and isinstance(dados.get("dominios"), list):
        return [d for d in dados["dominios"] if isinstance(d, dict) and d.get("chave")]
    if isinstance(dados, list):
        return [d for d in dados if isinstance(d, dict) and d.get("chave")]
    return []


def gravar_extras(itens, caminho=None):
    arq = Path(caminho) if caminho is not None else ARQUIVO_PADRAO
    arq.parent.mkdir(parents=True, exist_ok=True)
    ordenados = sorted(itens, key=lambda d: int(d.get("id", 0)))
    arq.write_text(json.dumps({"dominios": ordenados}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def construir_dados_dominio(item, indice=0):
    """Monta a estrutura completa de domínio compatível com gerar_sistema.DOMINIOS (núcleo + 28 padrões + Django)."""
    import dominios as dom

    entidade = item["entidade"]
    sistema = item["sistema"]
    ident = item.get("ident") or "cliente"
    recurso = item.get("recurso") or "codigo"
    rotulo_rec = item.get("rotulo_recurso") or recurso.replace("_", " ")
    quantidade = item.get("quantidade") or "quantidade"
    maximo = int(item.get("quantidade_max") or 100)
    preco = item.get("preco") or "valor_unitario"
    unidade = item.get("unidade") or "unidade(s)"
    cat_unid = unidade.split("(")[0].strip() or "unidade"
    variantes = item.get("variantes") or "tipo de cliente: Comum 1, Fidelidade 0.9, Corporativo 0.85; Sazonal 0.8"
    categorias = item.get("categorias") or (
        f"{cat_unid}: {entidade}Padrao = {entidade} padrão 100; "
        f"{entidade}Plus = {entidade} plus 180; "
        f"{entidade}Premium = {entidade} premium 300; "
        f"{entidade}Especial = {entidade} especial 140"
    )
    extras = item.get("extras") or (
        "TaxaServico 35 taxa de serviço; SuportePrioritario 60 suporte prioritário; "
        "SeguroExtra 45 seguro extra; DescontoFidelidade 0.9 -10% fidelidade"
    )
    gateway = item.get("gateway") or f"Paga{entidade}"
    rot_cap = rotulo_rec.capitalize()
    painel = item.get("painel") or (
        f"{rot_cap} | disponível | EM USO | Reservar | (em uso) | "
        f"LOTADO - nenhum(a) {rotulo_rec} disponível | {rotulo_rec}(s) disponível(is)"
    )
    nomes = item.get("nomes") or [dom.NOMES[(4 * indice + j) % len(dom.NOMES)] for j in range(4)]
    dados = dom.D(
        ident, f"{recurso}:{rotulo_rec}:101 102 103", f"{quantidade}:{maximo}", preco, unidade,
        "100 80 150 0", variantes, categorias, extras, gateway, painel, nomes=nomes,
    )
    palavras = [p.strip().replace("_", " ") for p in item.get("palavras", []) if str(p).strip()]
    return {"sistema": sistema, "palavras": palavras, "entidade": entidade, **dados}


def cadastrar_dominio(chave, sistema, entidade, palavras, setor=SETOR_PADRAO, ident="cliente",
                      recurso="codigo", quantidade="quantidade", preco="valor_unitario",
                      unidade="unidade(s)", caminho=None, existentes=None):
    """Valida e grava um novo domínio personalizado em dominios_extras.json. Devolve o dict salvo."""
    import dominios as dom

    chave_limpa = _snake(chave)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", chave_limpa):
        raise ValueError("chave do domínio: use letras minúsculas, números e _ (ex.: energia_eolica, marcenaria)")
    sistema_limpo = _limpar_texto(sistema, "nome do sistema")
    entidade_limpa = _camel(entidade)
    if not entidade_limpa or not entidade_limpa.isidentifier() or not entidade_limpa[0].isupper():
        raise ValueError("entidade: informe um nome de classe válido (ex.: Turbina, Projeto)")
    setor_limpo = _limpar_texto(setor or SETOR_PADRAO, "setor")
    palavras_limpas = limpar_palavras(palavras)
    ident_l = _limpar_campo(ident, "campo identificador")
    rec_l = _limpar_campo(recurso, "campo recurso")
    qtd_l = _limpar_campo(quantidade, "campo quantidade")
    preco_l = _limpar_campo(preco, "campo preço")
    if len({ident_l, rec_l, qtd_l, preco_l}) < 4:
        raise ValueError("os campos identificador, recurso, quantidade e preço precisam ter nomes diferentes entre si")
    unidade_l = _limpar_texto(unidade or "unidade(s)", "unidade", limite=30)

    nativos = {c for _, c, _, _, _ in dom.ler_catalogo()}
    extras = ler_extras(caminho)
    ja_existe = nativos | {d["chave"] for d in extras} | set(existentes or ())
    if chave_limpa in ja_existe:
        raise ValueError(f"já existe um domínio com a chave '{chave_limpa}' — escolha outra chave")

    maior_id = max([num for num, *_ in dom.ler_catalogo()] + [int(d.get("id", 101)) for d in extras], default=101)
    novo = {
        "id": maior_id + 1,
        "chave": chave_limpa,
        "sistema": sistema_limpo,
        "entidade": entidade_limpa,
        "setor": setor_limpo,
        "palavras": palavras_limpas,
        "ident": ident_l,
        "recurso": rec_l,
        "quantidade": qtd_l,
        "preco": preco_l,
        "unidade": unidade_l,
    }
    # Valida a montagem completa antes de salvar
    construir_dados_dominio(novo, len(extras))
    extras.append(novo)
    gravar_extras(extras, caminho)
    return novo


def remover_dominio(alvo, caminho=None):
    """Remove um domínio personalizado (por chave ou ID >= 102). Protege os 101 domínios nativos."""
    import dominios as dom

    alvo_str = str(alvo or "").strip()
    nativos = {c: num for num, c, _, _, _ in dom.ler_catalogo()}
    if alvo_str.lower() in nativos or (alvo_str.isdigit() and 1 <= int(alvo_str) <= 101):
        raise ValueError(f"o domínio '{alvo_str}' é nativo do catálogo (001–101) e não pode ser removido")
    extras = ler_extras(caminho)
    alvo_norm = _snake(alvo_str)
    achado = next(
        (d for d in extras if d["chave"] == alvo_norm or (alvo_str.isdigit() and int(d.get("id", 0)) == int(alvo_str))),
        None,
    )
    if achado is None:
        raise ValueError(f"domínio personalizado '{alvo_str}' não encontrado (veja: sgs dominios)")
    restantes = [d for d in extras if d["chave"] != achado["chave"]]
    gravar_extras(restantes, caminho)
    return achado


def main(argv=None):
    p = argparse.ArgumentParser(description="Gerencia domínios personalizados do SGS (além dos 101 nativos).")
    sub = p.add_subparsers(dest="acao")
    sub.add_parser("listar", help="lista os domínios personalizados cadastrados")
    novo = sub.add_parser("novo", help="adiciona um domínio personalizado")
    novo.add_argument("chave", help="identificador do domínio (ex.: energia_eolica)")
    novo.add_argument("--sistema", required=True, help="nome do sistema (ex.: Eólica Sul)")
    novo.add_argument("--entidade", required=True, help="nome da classe principal (ex.: Turbina)")
    novo.add_argument("--palavras", required=True, help="palavras-chave separadas por vírgula (mínimo 3)")
    novo.add_argument("--setor", default=SETOR_PADRAO)
    novo.add_argument("--ident", default="cliente")
    novo.add_argument("--recurso", default="codigo")
    novo.add_argument("--quantidade", default="quantidade")
    novo.add_argument("--preco", default="valor_unitario")
    novo.add_argument("--unidade", default="unidade(s)")
    rem = sub.add_parser("remover", help="remove um domínio personalizado por chave ou ID")
    rem.add_argument("alvo")
    args = p.parse_args(argv)
    if args.acao == "listar" or not args.acao:
        extras = ler_extras()
        if not extras:
            print("Nenhum domínio personalizado cadastrado ainda (os 101 nativos estão ativos).")
            return 0
        for d in extras:
            print(f"{int(d['id']):03d} | {d['chave']} | {d['sistema']} | {d['entidade']} | "
                  f"{len(d['palavras'])} palavras ({d.get('setor', SETOR_PADRAO)})")
        return 0
    if args.acao == "novo":
        d = cadastrar_dominio(args.chave, args.sistema, args.entidade, args.palavras, setor=args.setor,
                              ident=args.ident, recurso=args.recurso, quantidade=args.quantidade,
                              preco=args.preco, unidade=args.unidade)
        print(f"✓ domínio {int(d['id']):03d} ({d['chave']} · {d['sistema']} · {d['entidade']}) cadastrado com "
              f"{len(d['palavras'])} palavras.")
        return 0
    if args.acao == "remover":
        d = remover_dominio(args.alvo)
        print(f"✓ domínio personalizado {int(d['id']):03d} ({d['chave']}) removido.")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

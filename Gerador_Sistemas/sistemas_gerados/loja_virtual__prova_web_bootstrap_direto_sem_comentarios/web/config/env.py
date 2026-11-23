import os


def ler_env(caminho):
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
    for chave, valor in ler_env(caminho).items():
        os.environ.setdefault(chave, valor)

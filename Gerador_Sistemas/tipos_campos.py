"""
tipos_campos.py — IDENTIFICADOR DE TIPOS dos campos pedidos (determinístico, sem IA).

O pedido chega em texto livre ("pet shop com os campos nome, raça, idade, peso e vacinado") e este módulo:
  1. extrair_campos(texto) — acha a LISTA DE CAMPOS que o pedido declarou. É conservador: só lê depois de
     um gatilho ("campos:", "com os campos", "atributos", "contendo", "dados:") e aceita o tipo escrito
     junto ("idade:int", "peso (decimal)");
  2. identificar(nome) — deduz o tipo pelo NOME do campo (listas fixas de palavras) e diz se é ÓBVIO ou se
     há DÚVIDA. Os duvidosos (codigo, numero, tamanho, status, nomes desconhecidos…) viram pergunta no
     questionário do SGS; os óbvios (nome → texto, idade → inteiro, peso → decimal…) não;
  3. tipo_da_resposta(texto) — entende a resposta do usuário ("inteiro", "INT", "string", "3"…).

Tipos que o gerador sabe validar no núcleo (@property) e no Django:
  str    String  texto              → recusa vazio            · CharField
  int    INT     número inteiro     → recusa bool e float     · IntegerField + MinValueValidator
  float  FLOAT   número com casas   → recusa bool e texto     · DecimalField (2 casas)
  bool   BOOL    sim/não            → só True ou False        · BooleanField (caixa de marcar)
  data   DATE    data AAAA-MM-DD    → texto ISO validado      · DateField
"""
from __future__ import annotations

import keyword
import re
import unicodedata

TIPOS = {
    "str": ("String", "texto"),
    "int": ("INT", "inteiro"),
    "float": ("FLOAT", "decimal"),
    "bool": ("BOOL", "sim/não"),
    "data": ("DATE", "data"),
}
ORDEM_TIPOS = list(TIPOS)

# Respostas aceitas para cada tipo (sem acento, minúsculas). "1".."5" seguem ORDEM_TIPOS.
_RESPOSTAS = {
    "str": ["str", "string", "texto", "text", "varchar", "char", "palavra", "letras", "s"],
    "int": ["int", "inteiro", "integer", "numero inteiro", "inteira", "i"],
    "float": ["float", "decimal", "real", "double", "numero real", "numero decimal", "moeda", "dinheiro",
              "numero com virgula", "numero com casas", "f"],
    "bool": ["bool", "boolean", "booleano", "logico", "sim/nao", "sim nao", "sim ou nao", "verdadeiro/falso",
             "checkbox", "caixa", "b"],
    "data": ["data", "date", "dia", "aaaa-mm-dd", "d"],
}

# --------------------------------------------------------------------------- palavras por tipo
TEXTO_LIVRE = {"observacao", "observacoes", "obs", "descricao", "complemento", "anotacao", "anotacoes",
               "comentario", "comentarios", "detalhes", "historico", "recado", "mensagem", "bio", "resumo"}
STR = {"nome", "sobrenome", "apelido", "email", "e_mail", "telefone", "celular", "whatsapp", "fone", "cpf",
       "cnpj", "rg", "cep", "endereco", "rua", "logradouro", "bairro", "cidade", "municipio", "uf", "estado",
       "pais", "placa", "raca", "especie", "cor", "marca", "modelo", "titulo", "autor", "editora", "isbn",
       "genero", "sexo", "categoria", "responsavel", "tutor", "dono", "proprietario", "cliente", "paciente",
       "aluno", "professor", "medico", "veterinario", "usuario", "login", "site", "url", "link", "foto",
       "imagem", "cargo", "profissao", "empresa", "nacionalidade", "idioma", "curso", "disciplina", "materia",
       "sabor", "pelagem", "porte", "documento", "instagram", "contato", "chassi", "renavam", "sigla",
       "bandeira", "fornecedor", "fabricante", "local", "destino", "origem", "assunto", "horario", "hora"}
INT = {"idade", "ano", "anos", "quantidade", "qtd", "qtde", "quant", "dias", "horas", "meses", "semanas",
       "minutos", "segundos", "andar", "parcelas", "estoque", "pontos", "pontuacao", "vagas", "lugares",
       "capacidade", "nivel", "serie", "unidades", "filhos", "pessoas", "hospedes", "quartos", "banheiros",
       "assentos", "lotacao", "faltas", "presencas", "aulas", "sessoes", "diarias", "noites", "volumes",
       "paginas", "edicao", "quilometragem", "km", "ninhada", "dependentes", "repeticoes", "series"}
FLOAT = {"preco", "valor", "peso", "altura", "largura", "comprimento", "profundidade", "salario", "taxa",
         "desconto", "media", "percentual", "porcentagem", "area", "distancia", "temperatura", "saldo", "custo",
         "frete", "comissao", "multa", "juros", "litros", "volume", "latitude", "longitude", "renda",
         "orcamento", "mensalidade", "gorjeta", "imc", "velocidade", "consumo", "metragem", "total", "subtotal"}
BOOL = {"ativo", "ativa", "inativo", "inativa", "vacinado", "vacinada", "castrado", "castrada", "pago", "paga",
        "disponivel", "confirmado", "confirmada", "aprovado", "aprovada", "entregue", "concluido", "concluida",
        "finalizado", "finalizada", "cancelado", "cancelada", "bloqueado", "bloqueada", "habilitado",
        "habilitada", "verificado", "verificada", "aceito", "aceite", "urgente", "favorito", "publicado",
        "publicada", "lido", "lida", "vegano", "vegetariano", "fumante", "alergico", "alergica", "casado",
        "casada", "matriculado", "matriculada", "assinante", "adotado", "adotada", "vermifugado",
        "vermifugada", "microchipado", "pedigree", "faturado", "emitido", "online", "presencial", "gratuito"}
DATA = {"nascimento", "vencimento", "validade", "admissao", "demissao", "emissao", "aniversario", "casamento",
        "agendamento", "matricula_em", "cadastro_em", "criado_em", "atualizado_em", "pago_em", "entregue_em"}
# Nomes que podem ser mais de um tipo: o questionário PERGUNTA (com uma sugestão).
DUVIDA = {"codigo": "str", "numero": "int", "tamanho": "str", "matricula": "str", "status": "str",
          "registro": "str", "prazo": "int", "nota": "float", "situacao": "str", "classificacao": "str",
          "turno": "str", "periodo": "str", "versao": "str", "protocolo": "str", "sala": "int", "turma": "str",
          "lote": "str", "referencia": "str", "grau": "int", "ordem": "int", "prioridade": "int",
          "conceito": "str", "resultado": "str", "inicio": "data", "fim": "data", "termino": "data",
          "entrega": "data", "retorno": "data", "senha": "str", "chave": "str", "tag": "str", "nivel_acesso": "str"}
PREFIXO_BOOL = ("e_", "eh_", "tem_", "possui_", "is_", "has_", "aceita_", "precisa_", "usa_", "foi_", "esta_")
PREFIXO_DATA = ("data_", "dt_")
SUFIXO_DATA = ("_em",)
SUFIXO_INT = ("_anos", "_dias", "_horas", "_meses", "_minutos", "_semanas", "_qtd")
SUFIXO_FLOAT = ("_kg", "_cm", "_m", "_km", "_reais", "_litros", "_percentual")

# Regras de validação padrão (as mesmas do catálogo de domínios: obrigatorio · minimo · faixa · livre).
FAIXAS = {"idade": (0, 130), "ano": (1900, 2100), "nota": (0, 10), "media": (0, 10), "percentual": (0, 100),
          "porcentagem": (0, 100), "desconto": (0, 100), "temperatura": (-100, 100), "latitude": (-90, 90),
          "longitude": (-180, 180), "pontuacao": (0, 100)}

# Palavras que NUNCA são nome de campo (evitam ler "campos obrigatórios e opcionais" como dois campos).
NAO_CAMPO = {"obrigatorio", "obrigatorios", "obrigatoria", "obrigatorias", "opcional", "opcionais", "valido",
             "validos", "invalido", "invalidos", "basico", "basicos", "seguinte", "seguintes", "abaixo", "acima",
             "necessario", "necessarios", "principal", "principais", "extra", "extras", "padrao", "padroes",
             "mesmo", "mesmos", "todos", "outros", "demais", "etc"}
_LIGACOES = {"de", "do", "da", "dos", "das", "o", "a", "os", "as", "um", "uma", "seu", "sua"}
_GATILHO = re.compile(r"(?P<gat>com\s+os\s+(?:seguintes\s+)?(?:campos|atributos)|\bcampos\b|\bcampo\b|"
                      r"\batributos?\b|\bcontendo\b|\bdados\b|\binformacoes\b)\s*(?P<dois>:)?\s*")
_FIM_LISTA = re.compile(r"[.;!?\n]|\s(?:que|onde|usando|cujo|cuja|no qual|na qual|em que|para|pelo|pela|"
                        r"com|padrao|padroes)\s")
_TIPO_JUNTO = re.compile(r"^(?P<nome>.+?)\s*(?::\s*(?P<t1>[a-z/ -]+?)|=\s*(?P<t3>[a-z/ -]+?)|\((?P<t2>[^)]*)\))\s*$")


def sem_acento(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def nome_campo(texto):
    """Texto do pedido → nome de campo em snake_case sem acento ("Data de nascimento" → data_nascimento)."""
    palavras = re.findall(r"[a-z0-9]+", sem_acento(texto).lower())
    palavras = [p for p in palavras if p not in _LIGACOES] or palavras
    nome = "_".join(palavras)[:40].strip("_")
    if nome and nome[0].isdigit():
        nome = "campo_" + nome
    return nome


def rotulo(tipo):
    """"texto (String)", "número inteiro (INT)"… — como o tipo aparece nas perguntas e nos resumos."""
    sigla, nome = TIPOS[tipo]
    return f"{nome} ({sigla})"


def tipo_da_resposta(texto):
    """Resposta do usuário → chave do tipo (str/int/float/bool/data) ou None se não entendeu."""
    t = sem_acento(str(texto or "")).strip().lower().strip(".")
    if not t:
        return None
    if t.isdigit() and 1 <= int(t) <= len(ORDEM_TIPOS):
        return ORDEM_TIPOS[int(t) - 1]
    for tipo, respostas in _RESPOSTAS.items():
        if t == tipo or t in respostas:
            return tipo
    for tipo, respostas in _RESPOSTAS.items():           # "texto (String)", "inteiro (INT)" — o rótulo inteiro
        if any(len(r) > 2 and re.search(rf"(?<![a-z]){re.escape(r)}(?![a-z])", t) for r in respostas):
            return tipo
    return None


def regra_padrao(nome, tipo):
    """Regra de validação padrão para o tipo: (regra, min, max)."""
    if tipo == "str":
        return ("livre" if nome in TEXTO_LIVRE else "obrigatorio"), None, None
    if tipo in ("int", "float"):
        base = nome.split("_")[0]
        faixa = FAIXAS.get(nome) or FAIXAS.get(base)
        if faixa:
            minimo, maximo = faixa
            return "faixa", (float(minimo) if tipo == "float" else minimo), (float(maximo) if tipo == "float" else maximo)
        return "minimo", (0.0 if tipo == "float" else 0), None
    return "obrigatorio", None, None                       # bool e data: o próprio tipo é a regra


def _deduzir(nome):
    """(tipo, certeza, motivo) só pelo nome."""
    partes = nome.split("_")
    primeira, ultima = partes[0], partes[-1]
    if nome in TEXTO_LIVRE:
        return "str", "obvio", "texto livre (sem regra)"
    for conjunto, tipo in ((STR, "str"), (BOOL, "bool"), (DATA, "data"), (INT, "int"), (FLOAT, "float")):
        if nome in conjunto:
            return tipo, "obvio", f"“{nome}” é {rotulo(tipo)}"
    if nome in DUVIDA:
        return DUVIDA[nome], "duvida", f"“{nome}” pode ser mais de um tipo"
    if nome.startswith(PREFIXO_DATA) or ultima == "data" or nome.endswith(SUFIXO_DATA):
        return "data", "obvio", "nome de data (data_…/…_em)"
    if nome.startswith(PREFIXO_BOOL):
        return "bool", "obvio", "pergunta de sim/não (tem_…/e_…)"
    if nome.endswith(SUFIXO_INT):
        return "int", "obvio", "contagem (…_dias, …_anos)"
    if nome.endswith(SUFIXO_FLOAT):
        return "float", "obvio", "medida/valor (…_kg, …_reais)"
    for conjunto, tipo in ((STR, "str"), (FLOAT, "float"), (INT, "int"), (BOOL, "bool"), (DATA, "data")):
        if primeira in conjunto and len(partes) > 1:
            return tipo, "obvio", f"começa com “{primeira}” → {rotulo(tipo)}"
    if primeira in DUVIDA and len(partes) > 1:
        return DUVIDA[primeira], "duvida", f"começa com “{primeira}”, que pode ser mais de um tipo"
    if primeira in TEXTO_LIVRE:
        return "str", "obvio", "texto livre (sem regra)"
    return "str", "duvida", "nome sem regra conhecida"


def identificar(nome, tipo=None):
    """Tipo de um campo. `tipo` (escrito no pedido ou respondido) vence a dedução.

    Devolve {"nome", "tipo", "regra", "min", "max", "certeza" (obvio | duvida | informado), "motivo", "sugestao"}.
    """
    nome = nome_campo(nome)
    sugestao, certeza, motivo = _deduzir(nome)
    if tipo:
        if tipo not in TIPOS:
            raise ValueError(f"tipo desconhecido: {tipo!r} (use {', '.join(TIPOS)})")
        certeza, motivo = "informado", f"tipo informado: {rotulo(tipo)}"
    final = tipo or sugestao
    regra, minimo, maximo = regra_padrao(nome, final)
    return {"nome": nome, "tipo": final, "regra": regra, "min": minimo, "max": maximo,
            "certeza": certeza, "motivo": motivo, "sugestao": sugestao}


def _item(pedaco):
    """"idade:int", "peso (decimal)", "data de nascimento" → (texto do nome, tipo informado ou None)."""
    pedaco = pedaco.strip(" -")
    m = _TIPO_JUNTO.match(pedaco)
    if not m:
        return pedaco, None
    return m.group("nome"), tipo_da_resposta(m.group("t1") or m.group("t2") or m.group("t3"))


def _palavras(texto):
    return [p for p in re.findall(r"[a-z0-9]+", texto) if p not in _LIGACOES]


def extrair_campos(texto):
    """Campos que o pedido LISTOU, na ordem: [{"nome", "texto", "tipo" (ou None)}].

    Só lê depois de um gatilho ("campos", "com os campos", "atributos", "contendo", "dados:", "informações:").
    Sem ":" depois do gatilho, a lista precisa de 2+ itens (exceto "campo X"); a lista acaba no primeiro
    pedaço que parece frase (mais de 4 palavras), em pontuação ou em "que/onde/para/com…".
    """
    t = sem_acento(texto or "").lower()
    achados, vistos = [], set()
    for m in _GATILHO.finditer(t):
        gatilho, dois_pontos = m.group("gat"), bool(m.group("dois"))
        if gatilho in ("dados", "informacoes") and not dois_pontos:
            continue                                        # "os dados do cliente" não é lista de campos
        resto = t[m.end():]
        fim = _FIM_LISTA.search(resto)
        itens = []
        for pedaco in re.split(r"\s*,\s*|\s+e\s+", (resto[:fim.start()] if fim else resto).strip()):
            nome_txt, tipo = _item(pedaco)
            palavras = _palavras(nome_txt)
            if not palavras:
                continue
            if len(palavras) > 4:                           # frase, não nome de campo: a lista acabou
                break
            if nome_campo(nome_txt) not in NAO_CAMPO:
                itens.append((nome_txt, tipo))
        if not itens or (not dois_pontos and len(itens) < 2 and gatilho != "campo"):
            continue
        for nome_txt, tipo in itens:
            nome = nome_campo(nome_txt)
            if nome and nome not in vistos and not keyword.iskeyword(nome):
                vistos.add(nome)
                achados.append({"nome": nome, "texto": nome_txt.strip(), "tipo": tipo})
    return achados


def ler_lista(valor):
    """Lista digitada ou do --campos → [(nome, tipo ou None)].

    Aceita "nome, idade:int, peso (decimal), data de nascimento" (vírgulas ou " e "), a forma curta da linha
    de comando "nome:str idade:int" (cada pedaço com ":") e listas Python de textos ou de {"nome", "tipo"}.
    """
    if isinstance(valor, str):
        valor = [valor]
    saida = []
    for item in valor or []:
        if isinstance(item, dict):
            saida.append((nome_campo(str(item.get("nome", ""))), item.get("tipo") or None))
            continue
        t = sem_acento(str(item)).lower().replace(";", ",").strip()
        if "," in t or re.search(r"\s+e\s+", t):
            pedacos = re.split(r"\s*,\s*|\s+e\s+", t)
        elif len(t.split()) > 1 and all(":" in p for p in t.split()):
            pedacos = t.split()                             # "nome:str idade:int"
        else:
            pedacos = [t]
        for pedaco in pedacos:
            nome_txt, tipo = _item(pedaco)
            saida.append((nome_campo(nome_txt), tipo))
    return [(n, t) for n, t in saida if n]


def analisar(texto_ou_lista):
    """Pedido (texto) ou lista de campos → [identificar(...)] com o tipo informado valendo sobre a dedução.

    Texto com gatilho ("… com os campos nome, idade") usa extrair_campos; senão é lido como lista.
    """
    pares = None
    if isinstance(texto_ou_lista, str):
        achados = extrair_campos(texto_ou_lista)
        if achados:
            pares = [(c["nome"], c["tipo"]) for c in achados]
    if pares is None:
        pares = ler_lista(texto_ou_lista)
    vistos, saida = set(), []
    for nome, tipo in pares:
        if nome not in vistos:
            vistos.add(nome)
            saida.append(identificar(nome, tipo))
    return saida


def duvidosos(campos):
    """Só os campos cujo tipo NÃO é óbvio (os que o questionário pergunta)."""
    return [c for c in campos if c["certeza"] == "duvida"]


def como_texto(campos):
    """"nome:str idade:int" — forma curta que volta para o gerador (--campos) e para a especificação."""
    return " ".join(f"{c['nome']}:{c['tipo']}" for c in campos)

"""
LNNL — identificador interno legível por humanos (implementação de referência).

Formato canônico de 14 caracteres, exibido com a máscara LNNL-LNNL-LNL-LNL
(L = letra maiúscula A–Z; N = dígito 1–9; o 0 não existe para não ser confundido com O):

    posição:  1  2  3  4  5  6  7  8  9 10 11 12 13 14
    classe:   L  N  N  L  L  N  N  L  L  N  L  L  N  L
    papel:    .  T  T  .  .  V  V  .  .  .  .  .  .  .

    T = código do tipo (2 dígitos, 11–99 sem zero; 93 reservado)
    V = 2 dígitos verificadores (resto módulo 79 da soma ponderada dos outros 12)

Sem dependências: somente a biblioteca padrão. Não depende de framework nem de banco.
Especificação completa: ../../RFC-LNNL.md
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from typing import Final

__all__ = [
    'LETRAS', 'DIGITOS', 'MASCARA', 'PESOS', 'MODULO', 'TIPO_RESERVADO', 'REGEX_CANONICA',
    'ResultadoValidacao', 'normalizar', 'formatar', 'valor_caractere', 'calcular_verificadores',
    'montar', 'extrair_dados', 'extrair_tipo', 'validar', 'gerar', 'candidatos_correcao',
    'codigos_tipo_disponiveis',
]

LETRAS: Final[str] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITOS: Final[str] = '123456789'
MASCARA: Final[str] = 'LNNL-LNNL-LNL-LNL'
CLASSES: Final[str] = 'LNNLLNNLLNLLNL'  # máscara sem separadores (14 posições)

# Pesos normativos dos 12 caracteres de dados, na ordem: posições 1–5 e 8–14.
# São distintos e não nulos módulo 79 (condição das garantias de detecção). NUNCA mudam:
# alterar um peso invalida todos os identificadores já emitidos.
PESOS: Final[tuple[int, ...]] = (71, 63, 76, 57, 31, 1, 11, 15, 37, 13, 58, 2)
MODULO: Final[int] = 79

# Código de tipo reservado como escape para uma futura extensão do espaço de tipos.
TIPO_RESERVADO: Final[str] = '93'

REGEX_CANONICA: Final[re.Pattern[str]] = re.compile(
    r'^[A-Z][1-9]{2}[A-Z]{2}[1-9]{2}[A-Z]{2}[1-9][A-Z]{2}[1-9][A-Z]$'
)

TAMANHO_INVALIDO: Final[str] = 'TAMANHO_INVALIDO'
FORMATO_INVALIDO: Final[str] = 'FORMATO_INVALIDO'
TIPO_RESERVADO_ERRO: Final[str] = 'TIPO_RESERVADO'
TIPO_INCOMPATIVEL: Final[str] = 'TIPO_INCOMPATIVEL'
VERIFICADOR_INVALIDO: Final[str] = 'VERIFICADOR_INVALIDO'

_NAO_ALFANUMERICO = re.compile(r'[^A-Z0-9]')


@dataclass(frozen=True)
class ResultadoValidacao:
    valido: bool
    erro: str | None = None
    canonico: str = ''

    def __bool__(self) -> bool:  # permite `if validar(x): ...`
        return self.valido


def normalizar(valor: str | None) -> str:
    """Maiúsculas e somente A–Z/0–9 (remove hífens, espaços e qualquer separador)."""
    if not valor:
        return ''
    return _NAO_ALFANUMERICO.sub('', str(valor).strip().upper())


def formatar(valor: str | None) -> str:
    """Aplica a máscara de exibição LNNL-LNNL-LNL-LNL (4-4-3-3) ao identificador."""
    c = normalizar(valor)
    if len(c) != 14:
        return c
    return f'{c[:4]}-{c[4:8]}-{c[8:11]}-{c[11:]}'


def valor_caractere(c: str) -> int:
    """A=1 … Z=26; dígitos 1–9 valem o próprio número."""
    if 'A' <= c <= 'Z':
        return ord(c) - 64
    if '1' <= c <= '9':
        return ord(c) - 48
    raise ValueError(f'Caractere fora do alfabeto LNNL: {c!r}')


def calcular_verificadores(dados_12: str) -> tuple[int, int]:
    """
    Verificadores dos 12 caracteres de dados (posições 1–5 e 8–14, nessa ordem):
        r  = (Σ PESOS[i] · valor(dados[i])) mod 79      → 0 … 78
        d1 = r div 9 + 1 ;  d2 = r mod 9 + 1             → dois dígitos de 1 a 9
    """
    if len(dados_12) != 12:
        raise ValueError(f'São necessários 12 caracteres de dados; recebidos {len(dados_12)}.')
    resto = sum(p * valor_caractere(c) for p, c in zip(PESOS, dados_12)) % MODULO
    return resto // 9 + 1, resto % 9 + 1


def montar(dados_12: str) -> str:
    """Intercala os verificadores nas posições 6 e 7 e devolve o identificador canônico."""
    d1, d2 = calcular_verificadores(dados_12)
    return f'{dados_12[:5]}{d1}{d2}{dados_12[5:]}'


def extrair_dados(canonico: str) -> str:
    """Os 12 caracteres de dados (o identificador sem as posições 6 e 7)."""
    c = normalizar(canonico)
    if len(c) != 14:
        raise ValueError('O identificador canônico tem 14 caracteres.')
    return c[:5] + c[7:]


def extrair_tipo(valor: str) -> str:
    """Código de tipo (posições 2 e 3)."""
    c = normalizar(valor)
    return c[1:3] if len(c) >= 3 else ''


def _tipo_str(tipo: str | int) -> str:
    t = f'{int(tipo):02d}' if isinstance(tipo, int) else str(tipo)
    if len(t) != 2 or any(ch not in DIGITOS for ch in t):
        raise ValueError(f'Tipo inválido: {tipo!r}. Use dois dígitos de 1 a 9 (11–99, sem zero).')
    return t


def validar(valor: str | None, tipo_esperado: str | int | None = None) -> ResultadoValidacao:
    """
    Valida na ordem normativa (o primeiro erro encontrado é o reportado):
    1. TAMANHO_INVALIDO  2. FORMATO_INVALIDO  3. TIPO_RESERVADO
    4. TIPO_INCOMPATIVEL (se tipo_esperado for informado)  5. VERIFICADOR_INVALIDO
    """
    c = normalizar(valor)
    if len(c) != 14:
        return ResultadoValidacao(False, TAMANHO_INVALIDO)
    if not REGEX_CANONICA.match(c):
        return ResultadoValidacao(False, FORMATO_INVALIDO)
    tipo = c[1:3]
    if tipo == TIPO_RESERVADO:
        return ResultadoValidacao(False, TIPO_RESERVADO_ERRO)
    if tipo_esperado is not None and tipo != _tipo_str(tipo_esperado):
        return ResultadoValidacao(False, TIPO_INCOMPATIVEL)
    d1, d2 = calcular_verificadores(c[:5] + c[7:])
    if c[5:7] != f'{d1}{d2}':
        return ResultadoValidacao(False, VERIFICADOR_INVALIDO)
    return ResultadoValidacao(True, None, c)


def gerar(tipo: str | int, aleatorio=None) -> str:
    """
    Gera um identificador válido para o tipo. Usa um gerador criptograficamente seguro
    (secrets) por padrão. A unicidade NÃO é garantida aqui: o armazenamento deve ter uma
    restrição de unicidade e o gravador deve tentar de novo em caso de colisão.
    """
    t = _tipo_str(tipo)
    if t == TIPO_RESERVADO:
        raise ValueError(f'O tipo {TIPO_RESERVADO} é reservado e não pode ser atribuído.')
    escolha = (aleatorio or secrets.SystemRandom()).choice
    letra = lambda: escolha(LETRAS)  # noqa: E731
    digito = lambda: escolha(DIGITOS)  # noqa: E731
    dados = (
        letra() + t + letra() + letra()          # posições 1–5
        + letra() + letra() + digito()           # posições 8–10
        + letra() + letra() + digito() + letra()  # posições 11–14
    )
    return montar(dados)


def candidatos_correcao(valor: str) -> list[str]:
    """
    Para atendimento humano: identificadores válidos que diferem do informado em exatamente
    um caractere (mesma classe L/N). Como toda troca de um caractere é detectada, um ID com um
    único erro de digitação sempre aparece nesta lista — mas pode não ser o único candidato.
    Os candidatos devem ser confirmados no armazenamento; nunca corrija automaticamente.
    """
    c = normalizar(valor)
    if len(c) != 14 or not REGEX_CANONICA.match(c) or validar(c):
        return []
    saida = []
    for i, classe in enumerate(CLASSES):
        alfabeto = LETRAS if classe == 'L' else DIGITOS
        for ch in alfabeto:
            if ch == c[i]:
                continue
            candidato = c[:i] + ch + c[i + 1:]
            if validar(candidato):
                saida.append(candidato)
    return saida


def codigos_tipo_disponiveis() -> list[str]:
    """Os 80 códigos de tipo atribuíveis: 11–99 sem o dígito 0 e sem o 93 reservado."""
    return [a + b for a in DIGITOS for b in DIGITOS if a + b != TIPO_RESERVADO]

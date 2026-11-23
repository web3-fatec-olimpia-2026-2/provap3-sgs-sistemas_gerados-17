"""
ViagemCerta — PROTOTYPE (GoF · criação): criar COPIANDO um modelo pronto (clone).

ANTES (nucleo/antes_prototipos.py): copiar_na_mao(original) lista campo por campo — se a Destino
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
            raise AttributeError(f"a Destino não tem o campo {campo!r}")
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

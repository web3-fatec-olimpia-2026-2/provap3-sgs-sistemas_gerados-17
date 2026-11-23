"""
PETShop — SRP + OCP (Aula 06): uma classe, um motivo para mudar.

Petshop (nucleo/entidades.py) → dados + total      (muda se a REGRA mudar)
ReciboFormatter               → texto do recibo    (muda se o LAYOUT mudar)
ReciboCsvFormatter            → formato novo       (EXTENSÃO: nada foi reaberto → OCP)
ArquivoRepository             → grava o texto      (muda se o DESTINO mudar)
Cuidado: SRP não é "uma classe por método" — a unidade é a responsabilidade.
"""


class ReciboFormatter:
    """APRESENTAÇÃO: recebe a Petshop por parâmetro e só LÊ os dados dela."""

    def formatar(self, item):
        # Texto idêntico ao da versão "faz-tudo" → prova de refatoração segura.
        return (f"RECIBO - PETShop\n{item.cliente}\n"
                f"{item.quantidade} unidade(s)\nTotal: R$ {item.total:.2f}")


class ReciboCsvFormatter:
    """Formato NOVO por extensão (OCP): mesma interface formatar(item)."""

    def formatar(self, item):
        return "cliente;quantidade;total\n" + f"{item.cliente};{item.quantidade};{item.total:.2f}"


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

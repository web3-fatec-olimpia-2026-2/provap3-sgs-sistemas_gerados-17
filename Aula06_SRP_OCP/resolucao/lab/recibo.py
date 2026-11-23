# LAB Aula 06 — SRP: uma classe, uma responsabilidade (RESOLVIDO)
#
# ANTES: a Reserva calculava o total, formatava o recibo E salvava em arquivo
#        → três motivos para mudar na mesma classe (viola o SRP).
# DEPOIS: três classes, cada uma com UM motivo para mudar.
#
#   Reserva            → regra de negócio   (muda se a regra do total mudar)
#   ReciboFormatter    → apresentação       (muda se o LAYOUT do recibo mudar)
#   ArquivoRepository  → infraestrutura     (muda se o DESTINO mudar: arquivo → banco)


class Reserva:
    """Só os dados da reserva e a regra de negócio (total)."""

    def __init__(self, hospede, diarias, valor_diaria):
        self.hospede = hospede
        self.diarias = diarias
        self.valor_diaria = valor_diaria

    def total(self):
        return self.diarias * self.valor_diaria


class ReciboFormatter:
    """Só a APRESENTAÇÃO: transforma uma reserva em texto.

    Recebe a reserva por parâmetro e só LÊ os dados dela — não precisa ser parte da Reserva.
    """

    def formatar(self, reserva):
        # Texto IDÊNTICO ao do antigo Reserva.formatar_recibo() → prova de refatoração segura.
        return (f"RECIBO\n{reserva.hospede}\n"
                f"{reserva.diarias} diarias\nTotal: R$ {reserva.total()}")


class ArquivoRepository:
    """Só a INFRAESTRUTURA: grava um texto em algum lugar (aqui, arquivo em disco)."""

    def salvar(self, texto, caminho):
        # encoding explícito: evita surpresa com acentos (ex.: "Conceição") no Windows.
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)


# ---------------------------------------------------------------------------
# Mostrando o ganho do SRP + OCP juntos (extra):
# o layout mudou? Crio OUTRO formatter, sem tocar em Reserva nem no repository.
# ---------------------------------------------------------------------------
class ReciboHtmlFormatter:
    def formatar(self, reserva):
        return (f"<h1>RECIBO</h1><p>{reserva.hospede}</p>"
                f"<p>{reserva.diarias} diarias</p><p>Total: R$ {reserva.total()}</p>")


def emitir_recibo(reserva, formatter, repositorio, caminho):
    """Junta as peças: cada uma faz a sua parte e não sabe dos detalhes da outra."""
    texto = formatter.formatar(reserva)
    repositorio.salvar(texto, caminho)
    return texto


# Duas linhas pedidas no HW 06a:
# Reserva guarda os dados e calcula o total (negócio); ReciboFormatter só monta o texto (apresentação);
# ArquivoRepository só grava o texto no disco (infraestrutura) — cada uma tem um único motivo para mudar.

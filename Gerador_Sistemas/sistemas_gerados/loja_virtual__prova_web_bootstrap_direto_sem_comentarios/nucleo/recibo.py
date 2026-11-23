class ReciboFormatter:
    def formatar(self, item):
        return (f"RECIBO - Loja Virtual\n{item.cliente}\n"
                f"{item.quantidade} unidade(s)\nTotal: R$ {item.total:.2f}")


class ReciboCsvFormatter:
    def formatar(self, item):
        return "cliente;quantidade;total\n" + f"{item.cliente};{item.quantidade};{item.total:.2f}"


class ArquivoRepository:
    def salvar(self, texto, caminho):
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)


def emitir_recibo(item, formatter, repositorio, caminho):
    texto = formatter.formatar(item)
    repositorio.salvar(texto, caminho)
    return texto

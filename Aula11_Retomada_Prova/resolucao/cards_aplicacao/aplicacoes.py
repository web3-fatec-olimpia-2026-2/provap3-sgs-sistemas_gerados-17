"""
Aula 11 — as 6 "Aplicações orientadas" do Material de Retomada, resolvidas em código.
Cada bloco responde à pergunta do card ("faça X e EXPLIQUE por quê") nos comentários.
"""
import json

# ===========================================================================
# CARD 1 — Strategy: "Crie a TarifaParceiro (20% off) SEM tocar na Reserva."
# ===========================================================================
class TarifaFidelidade:
    def calcular(self, diaria):
        return diaria * 0.9


class Reserva:
    def __init__(self, diaria, tarifa):
        self.diaria = diaria
        self.tarifa = tarifa

    def total(self):
        return self.tarifa.calcular(self.diaria)


class TarifaParceiro:            # ← NOVA. A classe Reserva acima não foi tocada.
    def calcular(self, diaria):
        return diaria * 0.8
# EXPLICAÇÃO: não precisei mexer na Reserva porque ela depende da INTERFACE `calcular`,
# não de um tipo concreto. Qualquer objeto com calcular(diaria) serve → OCP.


# ===========================================================================
# CARD 2 — SRP/OCP: "Precisa de um recibo em JSON além do texto. Onde mexe?"
# ===========================================================================
class ReciboTextoFormatter:
    def formatar(self, hospede, total):
        return f"RECIBO\n{hospede}\nTotal: R$ {total:.2f}"


class ReciboJsonFormatter:       # ← NOVA classe; nenhuma existente foi reaberta.
    def formatar(self, hospede, total):
        return json.dumps({"hospede": hospede, "total": round(total, 2)}, ensure_ascii=False)
# EXPLICAÇÃO: formatar é responsabilidade do formatter (SRP), não da Reserva. Um formato novo
# é uma EXTENSÃO (classe nova com o mesmo `formatar`) — a Reserva e o formatter de texto
# continuam fechados para modificação (OCP).


# ===========================================================================
# CARD 3 — Service × ViewModel: "Regra 'menor de 18 não reserva suíte': Service ou VM?"
# ===========================================================================
class ReservaService:
    """REGRA DE NEGÓCIO (o que é verdade no domínio). Não sabe de tela."""

    IDADE_MINIMA_SUITE = 18

    def pode_reservar(self, idade, categoria):
        if categoria == "suite" and idade < self.IDADE_MINIMA_SUITE:
            return False
        return True


class OpcaoQuartoViewModel:
    """LÓGICA DE EXIBIÇÃO: traduz a decisão do Service em rótulos para a tela."""

    def __init__(self, idade, categoria, servico=None):
        servico = servico or ReservaService()
        self.permitido = servico.pode_reservar(idade, categoria)   # pergunta ao Service
        self.botao_label = "Reservar" if self.permitido else "Indisponível para menores"
        self.css = "btn-ativo" if self.permitido else "btn-desabilitado"
# EXPLICAÇÃO: a regra dos 18 anos vale com ou sem tela (API, admin, relatório) → é regra de
# negócio → Service. O ViewModel só decide COMO mostrar o resultado (texto/cor do botão).


# ===========================================================================
# CARD 4 — Adapter: "API de pagamento com cobrar(json) mas o sistema espera processar(valor)."
# ===========================================================================
class ApiPagamentoTerceiro:
    """Código de TERCEIRO (não controlamos): recebe um JSON em texto, valor em centavos."""

    def __init__(self):
        self.recebidos = []

    def cobrar(self, payload_json: str) -> str:
        dados = json.loads(payload_json)
        self.recebidos.append(dados)
        status = "OK" if dados["amount_cents"] > 0 else "ERRO"
        return json.dumps({"status": status, "id": f"PG{len(self.recebidos):04d}"})


class PagamentoAdapter:
    """Interface que o NOSSO sistema espera: processar(valor_em_reais) -> id da transação."""

    def __init__(self, api):
        self._api = api

    def processar(self, valor):
        # traduz a CHAMADA e os FORMATOS: reais(float) → centavos(int) dentro de um JSON
        payload = json.dumps({"amount_cents": round(valor * 100), "currency": "BRL"})
        resposta = json.loads(self._api.cobrar(payload))
        if resposta["status"] != "OK":
            raise ValueError("pagamento recusado")
        return resposta["id"]
# EXPLICAÇÃO: é UMA peça de terceiro que faz a coisa certa mas fala outra língua
# (nome do método, JSON, centavos). O Adapter traduz por dentro; o sistema continua chamando
# processar(valor). Se a lib fosse nossa e já parecida, duck typing dispensaria a classe.


# ===========================================================================
# CARD 5 — Facade: "Checkout: fechar conta + liberar quarto + enviar nota."
# ===========================================================================
class Conta:
    def fechar(self, reserva_id):
        return 750.0                      # valor fixo só para o exemplo


class Quartos:
    def __init__(self):
        self.liberados = []

    def liberar(self, numero):
        self.liberados.append(numero)


class NotaFiscal:
    def __init__(self):
        self.emitidas = []

    def emitir(self, reserva_id, valor):
        self.emitidas.append((reserva_id, valor))
        return f"NF-{reserva_id}"


class CheckoutFacade:
    def __init__(self, conta, quartos, nota):
        self._conta, self._quartos, self._nota = conta, quartos, nota

    def finalizar(self, reserva_id, quarto):
        valor = self._conta.fechar(reserva_id)          # 1. fecha a conta
        self._quartos.liberar(quarto)                   # 2. libera o quarto
        nf = self._nota.emitir(reserva_id, valor)       # 3. emite a nota
        return {"valor": valor, "nota": nf}
# EXPLICAÇÃO: ajuda porque são TRÊS subsistemas numa ordem fixa, e várias telas (recepção,
# app, totem) fariam checkout — a ordem fica num lugar só e quem chama conhece só a fachada.
# Seria CERIMÔNIA se o checkout fosse 1 ou 2 chamadas simples num único lugar (uma função basta).


# ===========================================================================
# CARD 6 — Decorator: "Some um ComBercoExtra (+25) sem alterar os outros."
# ===========================================================================
class ReservaBase:
    def __init__(self, diaria, noites):
        self.diaria, self.noites = diaria, noites

    def preco(self):
        return self.diaria * self.noites


class ServicoExtra:
    def __init__(self, reserva):
        self._reserva = reserva

    def preco(self):
        return self._reserva.preco()


class ComCafeDaManha(ServicoExtra):
    def preco(self):
        return self._reserva.preco() + 40.0


class ComBercoExtra(ServicoExtra):        # ← NOVO; nenhum outro decorador foi alterado.
    def preco(self):
        return self._reserva.preco() + 25.0
# EXPLICAÇÃO: a ordem não muda o total porque cada camada SÓ SOMA um valor fixo ao que vem de
# dentro (soma é comutativa). Se uma camada multiplicasse (desconto %), a ordem passaria a importar.

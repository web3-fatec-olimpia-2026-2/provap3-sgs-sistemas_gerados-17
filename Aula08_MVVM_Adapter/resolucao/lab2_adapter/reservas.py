"""
Aula 08 — Lab 2 — Adapter (RESOLVIDO).

O projeto migrou de SQLite para PostgreSQL/Neon. O driver novo resolve a MESMA coisa
(gravar e buscar reserva), mas fala outra língua:

    a app espera (ALVO)              o ClienteNeon oferece (ADAPTADO)
    repo.salvar(reserva) -> int      cliente.execute("INSERT_RESERVA", d) -> {"ticket": n}
    repo.buscar(id) -> dict|None     cliente.fetch_one(chave) -> {"found": True, "row": {...}} | None

ADAPTER = NeonReservaAdapter: por FORA fala a língua da app (salvar/buscar);
por DENTRO traduz para a língua do Neon. Ninguém troca o aparelho, ninguém quebra a parede.
"""


# ---------------------------------------------------------------------------
# ALVO (Target): a interface que o resto do sistema já usa. Não mexer.
# ---------------------------------------------------------------------------
class ReservaRepository:
    def salvar(self, reserva: dict) -> int:
        raise NotImplementedError

    def buscar(self, reserva_id: int) -> dict | None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Implementação antiga (SQLite simulado) — já falava a língua certa.
# ---------------------------------------------------------------------------
class ArmazenamentoLocal(ReservaRepository):
    def __init__(self):
        self._dados = {}
        self._proximo_id = 1

    def salvar(self, reserva: dict) -> int:
        novo_id = self._proximo_id
        self._dados[novo_id] = dict(reserva)
        self._proximo_id += 1
        return novo_id

    def buscar(self, reserva_id: int) -> dict | None:
        return self._dados.get(reserva_id)


# ---------------------------------------------------------------------------
# ADAPTADO (Adaptee): código de TERCEIRO — não controlamos a assinatura. Não mexer.
# ---------------------------------------------------------------------------
class ClienteNeon:
    def __init__(self):
        self._tabela = {}
        self._seq = 1

    def execute(self, comando: str, dados: dict) -> dict:
        if comando != "INSERT_RESERVA":
            raise ValueError(f"comando desconhecido: {comando}")
        chave = self._seq
        self._tabela[chave] = dict(dados)
        self._seq += 1
        return {"ticket": chave}

    def fetch_one(self, chave: int) -> dict | None:
        registro = self._tabela.get(chave)
        if registro is None:
            return None
        return {"found": True, "row": dict(registro)}


# ---------------------------------------------------------------------------
# ADAPTER — o que eu construí
# ---------------------------------------------------------------------------
class NeonReservaAdapter(ReservaRepository):
    """Veste o ClienteNeon com a interface ReservaRepository.

    Herda de ReservaRepository → É-UM repositório (o serviço aceita sem saber que é Neon).
    TEM-UM ClienteNeon (composição) → delega o trabalho de verdade a ele.
    """

    def __init__(self, cliente):
        # Guardo o objeto adaptado. O sublinhado diz: detalhe interno do adapter.
        self._cliente = cliente

    def salvar(self, reserva: dict) -> int:
        # 1) traduz a CHAMADA: salvar(...) → execute("INSERT_RESERVA", ...)
        resposta = self._cliente.execute("INSERT_RESERVA", reserva)
        # 2) traduz o FORMATO da resposta: {"ticket": n} → n (int, como a app espera)
        return int(resposta["ticket"])

    def buscar(self, reserva_id: int) -> dict | None:
        resposta = self._cliente.fetch_one(reserva_id)
        if resposta is None:          # "não achou" continua sendo None para a app
            return None
        return resposta["row"]        # desembrulha {"found": True, "row": {...}} → {...}


# ---------------------------------------------------------------------------
# O SMELL original — mantido INALTERADO porque um teste do lab o usa
# (o HW 08a pede para não mexer nos testes).
# ---------------------------------------------------------------------------
class ReservaService:
    """Versão com cheiro: conhece DOIS bancos e decide com 'if usa_neon'."""

    def __init__(self, repo_local, cliente_neon, usa_neon=False):
        self.repo_local = repo_local
        self.cliente_neon = cliente_neon
        self.usa_neon = usa_neon

    def confirmar(self, reserva: dict) -> int:
        if self.usa_neon:
            resposta = self.cliente_neon.execute("INSERT_RESERVA", reserva)
            return resposta["ticket"]
        else:
            return self.repo_local.salvar(reserva)


# ---------------------------------------------------------------------------
# DEPOIS do Adapter: o serviço conhece UMA interface. Zero "if de banco".
# Trocar de banco = trocar o objeto injetado no construtor (OCP).
# ---------------------------------------------------------------------------
class ReservaServiceLimpo:
    def __init__(self, repo: ReservaRepository):
        self._repo = repo            # injeção de dependência: quem cria escolhe o banco

    def confirmar(self, reserva: dict) -> int:
        # regra de negócio mínima de exemplo (pode crescer sem saber de banco)
        if reserva.get("noites", 0) < 1:
            raise ValueError("reserva precisa de ao menos 1 noite")
        return self._repo.salvar(reserva)

    def consultar(self, reserva_id: int) -> dict | None:
        return self._repo.buscar(reserva_id)

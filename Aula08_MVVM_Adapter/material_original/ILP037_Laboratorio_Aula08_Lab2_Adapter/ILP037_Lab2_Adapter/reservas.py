"""
Armazenamento de reservas do Resort de Olimpia.

CONTEXTO (vem da segunda-feira de Web III): o projeto migrou o banco de
SQLite para PostgreSQL na nuvem (Neon). O driver novo NAO fala a mesma
lingua do antigo. O codigo da aplicacao esperava chamar:

    repo.salvar(reserva)        -> grava e devolve um id
    repo.buscar(id)            -> devolve a reserva ou None

Mas o cliente novo (ClienteNeon, que simula o driver do Postgres/Neon)
so entende:

    cliente.execute(comando, dados)   -> executa e devolve um "ticket"
    cliente.fetch_one(chave)          -> devolve um registro cru (dict) ou None

As duas interfaces resolvem a MESMA coisa, mas com nomes e formatos
DIFERENTES. Sao incompativeis.

>>> O SMELL <<<
Veja a classe ReservaService la embaixo: para nao quebrar, alguem comecou a
encher o servico de 'if usa_neon:'. Agora o servico conhece DOIS dialetos de
banco. Cada metodo novo vai ter que repetir o if. Isso vaza o detalhe do
banco para dentro da regra de negocio.

>>> SEU TRABALHO <<<
Construir um ADAPTER: NeonReservaAdapter. Ele VESTE o ClienteNeon com a
interface que a aplicacao ja espera (salvar/buscar), traduzindo as chamadas.
Assim o ReservaService volta a conhecer UMA interface so, sem nenhum 'if'.

A classe NeonReservaAdapter abaixo esta vazia de proposito: os testes batem
nela e ficam VERMELHOS.
"""


# ---------------------------------------------------------------------------
# A INTERFACE QUE A APLICACAO ESPERA (o "alvo" do Adapter)
# ---------------------------------------------------------------------------
class ReservaRepository:
    """Contrato que o resto do sistema ja usa. Nao mexa nele."""

    def salvar(self, reserva: dict) -> int:
        raise NotImplementedError

    def buscar(self, reserva_id: int) -> dict | None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# O ARMAZENAMENTO ANTIGO (SQLite), que ja implementava a interface certa
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
# O CLIENTE NOVO (Neon/Postgres) -- interface INCOMPATIVEL. Nao mexa nele:
# e codigo de terceiro, voce nao controla a assinatura dos metodos.
# ---------------------------------------------------------------------------
class ClienteNeon:
    """Simula o driver do Postgres/Neon. Fala 'execute' e 'fetch_one'."""

    def __init__(self):
        self._tabela = {}
        self._seq = 1

    def execute(self, comando: str, dados: dict) -> dict:
        # So entende o comando "INSERT_RESERVA".
        if comando != "INSERT_RESERVA":
            raise ValueError(f"comando desconhecido: {comando}")
        chave = self._seq
        self._tabela[chave] = dict(dados)
        self._seq += 1
        return {"ticket": chave}      # devolve um dict com 'ticket', nao um int

    def fetch_one(self, chave: int) -> dict | None:
        registro = self._tabela.get(chave)
        if registro is None:
            return None
        # devolve o registro embrulhado em metadados do driver
        return {"found": True, "row": dict(registro)}


# ---------------------------------------------------------------------------
# O ADAPTER QUE VOCE VAI CONSTRUIR -- hoje vazio (VERMELHO)
# ---------------------------------------------------------------------------
class NeonReservaAdapter(ReservaRepository):
    """
    Deve VESTIR um ClienteNeon com a interface ReservaRepository.

    TODO (voce):
      - __init__ recebe e guarda o cliente Neon
      - salvar(reserva): chamar cliente.execute("INSERT_RESERVA", reserva)
        e devolver o 'ticket' como inteiro
      - buscar(id): chamar cliente.fetch_one(id) e devolver o 'row'
        (ou None se nao achou)
    """

    def __init__(self, cliente):
        pass  # TODO

    def salvar(self, reserva: dict) -> int:
        pass  # TODO

    def buscar(self, reserva_id: int) -> dict | None:
        pass  # TODO


# ---------------------------------------------------------------------------
# O SMELL: o servico conhece os DOIS bancos e decide no 'if'
# ---------------------------------------------------------------------------
class ReservaService:
    """
    Versao com cheiro: recebe um repo local E um cliente neon, e um flag.
    Toda operacao repete o 'if usa_neon'. A regra de negocio (confirmar
    reserva) fica contaminada pelo detalhe de qual banco esta em uso.

    Depois do Adapter, este servico deve receber UM ReservaRepository so
    (local OU adapter) e NUNCA mais ter um 'if de banco'.
    """

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

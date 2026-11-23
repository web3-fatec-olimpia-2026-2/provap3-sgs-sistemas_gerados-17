# Laboratório 2 — Adapter: o banco mudou, o código de reserva não pode mudar
### ILP-037 · Aula 08 · Resort de Olímpia

## Contexto (vem da segunda-feira de Web III)
O projeto migrou o banco de **SQLite** para **PostgreSQL na nuvem (Neon)**. O
driver novo **não fala a mesma língua** do antigo. O resto do sistema esperava
`repo.salvar(reserva)` e `repo.buscar(id)`; o cliente novo só entende
`execute(...)` e `fetch_one(...)`. Interfaces incompatíveis para o mesmo fim.

## O que tem aqui
- `reservas.py` — a interface esperada (`ReservaRepository`), o armazenamento
  antigo (`ArmazenamentoLocal`), o cliente novo incompatível (`ClienteNeon`),
  o `ReservaService` com o **cheiro** (`if usa_neon`) e a classe
  `NeonReservaAdapter` **vazia**, que você vai preencher.
- `tests/test_adapter.py` — os testes.
- `pytest.ini` — já configurado.

## Como rodar
```
python3 -m pytest -v
```
Você verá **alguns testes passando e outros falhando** — o Adapter ainda não
existe de verdade.

## Sua missão
Construir o `NeonReservaAdapter`: ele **veste** o `ClienteNeon` com a interface
que o sistema já espera (`salvar`/`buscar`), **traduzindo** as chamadas por
dentro. Quando ele funcionar, o mesmo teste que vale para o armazenamento
antigo passa a valer para o Neon — e o `ReservaService` não precisa mais do
`if de banco`.

Prazo e entrega: veja o `HOMEWORK_08`.

# Laboratório — Decorator: serviços extras na reserva
### ILP-037 · Aula 10 · Resort de Olímpia · Python puro · ~40 min

## O problema
Uma reserva tem preço e descrição. O hóspede pode somar **extras** em qualquer
combinação: café da manhã, transfer, late checkout. Hoje isso é resolvido com uma
**pilha de flags e ifs** (`preco_com_extras(..., cafe=True, transfer=True, ...)`).
Cada extra novo obriga a mexer na função e em todo mundo que chama. E não dá para
combinar extras dinamicamente.

## O que tem aqui
- `reserva.py` — a `ReservaBase`, a base `ServicoExtra` (que delega), os três
  decoradores **a completar** (`ComCafeDaManha`, `ComTransfer`, `ComLateCheckout`) e o
  **smell** (`preco_com_extras`).
- `tests/test_reserva.py` — os testes.
- `pytest.ini` e `requirements.txt` — já configurados.

## Como rodar
No laboratório da FATEC (WSL), crie o ambiente e instale a dependência (só o pytest):
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v
```
Começa com a maioria **vermelha** — os decoradores ainda só delegam, sem somar nada.

## Sua missão
Implementar `preco()` e `descricao()` em cada decorador: chamar o de dentro
(`self._reserva.preco()` / `.descricao()`) e **acrescentar** a sua parte. Quando os três
estiverem prontos, os 6 testes passam — e você consegue **empilhar** extras em qualquer
ordem: `ComTransfer(ComCafeDaManha(ReservaBase(...)))`.

> O decorador **embrulha** e **soma** — ele não reescreve a reserva. Cada um só acrescenta o seu.

Prazo e entrega: veja o `HOMEWORK_10`.

# Laboratório — Facade na recepção
### ILP-037 · Aula 09 · Resort de Olímpia · Python puro · ~35 min

## O problema
Fazer uma reserva envolve **quatro subsistemas** na ordem certa: Disponibilidade →
Tarifa → Reservas → Notificador. Hoje o código cliente (`fazer_reserva_na_mao`)
conhece os quatro, a ordem e a regra. Cada tela que reserva repete tudo isso.

## O que tem aqui
- `recepcao.py` — os 4 subsistemas prontos, o cliente com o **cheiro**
  (`fazer_reserva_na_mao`) e a classe `RecepcaoFacade` **vazia**, que você vai preencher.
- `tests/test_recepcao.py` — os testes.
- `pytest.ini` — já configurado.

## Como rodar
No laboratório da FATEC (WSL), crie o ambiente e instale a dependência (só o pytest):
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v
```
Começa com a maioria **vermelha** — a `RecepcaoFacade` ainda não orquestra nada.

## Sua missão
Construir `RecepcaoFacade.reservar(quarto, hospede, noites)`: ela **esconde** a
orquestração dos quatro subsistemas atrás de um método só. O cliente passa a chamar
**a facade**, não os quatro. Quando ela funcionar, os 5 testes passam.

> A Facade **não reescreve** a regra — ela **orquestra** o que já existe. Compare com
> `fazer_reserva_na_mao`: é a mesma sequência, agora num lugar único.

Prazo e entrega: veja o `HOMEWORK_09`.

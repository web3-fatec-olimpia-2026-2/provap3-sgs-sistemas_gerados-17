# Coding Dojo — MVVM no check-in (Randori)
### ILP-037 · Aula 09 · Resort de Olímpia · ~30 min

## O que é
Um **Randori**: a turma resolve junto, revezando no teclado. É o **mesmo movimento**
do MVVM da Aula 08 (quartos), agora num cenário novo — o painel de **check-in do dia**.
Se o movimento já está no dedo, sai rápido.

## Como rodar
No laboratório da FATEC (WSL), crie o ambiente e instale a dependência (só o pytest):
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v
```
Começa com **4 testes vermelhos** — o `CheckinViewModel` está vazio.

## O movimento
Mover a decisão de exibição (selo VERDE/AMARELO/CINZA, rótulo do botão) e a regra
(só `confirmada` + `pago` faz check-in) de dentro da tela `painel_checkin()` para o
**CheckinViewModel**. Quando ele preparar os dados, os 4 testes passam — e nenhum
lê o texto da tela.

## Critério de "pronto" (Dojo)
- [ ] 4 verdes em `python3 -m pytest`
- [ ] nenhum teste lê a string da tela
- [ ] quem estava no teclado consegue explicar por que o `selo` está no ViewModel

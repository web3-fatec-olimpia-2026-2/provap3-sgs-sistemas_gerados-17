# Homework 10A — Terminar o laboratório do Decorator
### Individual · ILP-037 · Prazo: quarta 12/11, 23h59 · IA nível 2 (apoio, declarando)

> Este laboratório é começado **em aula**. Em casa, você só o termina se não fechou no presencial.

## O que entregar
O `reserva.py` com os três decoradores completos. Alvo: `python3 -m pytest` → **6 passed**.
Envie o `.py` no seu canal individual do Teams.

## Passo a passo (se você não terminou na aula)
```
unzip ILP037_Laboratorio_Aula10_Decorator.zip
cd ILP037_Lab_Decorator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v        # maioria vermelha: normal
```
Em cada decorador (`ComCafeDaManha`, `ComTransfer`, `ComLateCheckout`), implemente `preco()` e
`descricao()`: chame o de dentro (`self._reserva.preco()` / `.descricao()`) e **some** a sua parte.
Rode até **6 verdes**. Roteiro completo em `ILP037_Aula10_LAB_ROTEIRO_Decorator.md`.

## Critério de aceitação
- [ ] `6 passed`
- [ ] cada decorador chama o de dentro e **soma** — não reescreve a reserva
- [ ] nenhum teste foi alterado

## Sobre IA (nível 2)
Pode usar como apoio, mas **declare** numa linha o que perguntou. Você pode ser arguido sobre o
próprio código — inclusive na **P3 (prova prática, 27/11)**.

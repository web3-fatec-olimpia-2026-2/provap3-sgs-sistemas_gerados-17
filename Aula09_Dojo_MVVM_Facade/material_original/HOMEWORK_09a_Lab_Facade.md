# Homework 09A — Terminar o laboratório do Facade
### Individual · ILP-037 · Prazo: quarta 22/10, 23h59 · IA nível 2 (apoio, declarando)

> Este laboratório é começado **em aula**. Em casa, você só o termina se não fechou no presencial.

## O que entregar
O `recepcao.py` com a `RecepcaoFacade` preenchida. Alvo: `python3 -m pytest` → **5 passed**.
Envie o `.py` no seu canal individual do Teams.

## Passo a passo (se você não terminou na aula)
```
unzip ILP037_Laboratorio_Aula09_Facade.zip
cd ILP037_Lab_Facade
python3 -m pytest -v        # maioria vermelha: normal, a facade esta vazia
```
Preencha o `__init__` (guardar os 4 subsistemas) e o `reservar` (checar disponibilidade →
calcular → gravar → notificar; se ocupado, devolver `{"ok": False, "motivo": "indisponivel"}`).
Rode até **5 verdes**. O roteiro completo está em `ILP037_Aula09_LAB_ROTEIRO_Facade.md`.

## Critério de aceitação
- [ ] `5 passed`
- [ ] a fachada **orquestra** os subsistemas; não reescreve a regra de nenhum
- [ ] nenhum teste foi alterado

## Sobre IA (nível 2)
Pode usar como apoio, mas **declare** numa linha o que perguntou. Você pode ser arguido sobre o
próprio código (P3).

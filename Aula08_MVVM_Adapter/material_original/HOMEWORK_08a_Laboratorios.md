# Homework 08A — Entregar os dois laboratórios
### Individual · ILP-037 · Prazo: quarta 15/10, 23h59 · IA nível 2 (apoio, declarando)

> **Estes labs são feitos em aula.** Este arquivo é a referência de entrega e o guia para
> **terminar em casa caso você não tenha fechado no presencial**.

## O que entregar
Os dois laboratórios da aula, com os testes **verdes**:

1. **Lab 1 — MVVM:** o `quartos.py` com `QuartoViewModel` e `PainelQuartosVM` preenchidos.
   Alvo: `python3 -m pytest` → **8 passed**.
2. **Lab 2 — Adapter:** o `reservas.py` com `NeonReservaAdapter` preenchido.
   Alvo: `python3 -m pytest` → **7 passed**.

Envie os **dois arquivos `.py`** no seu canal individual do Teams.

## Passo a passo (se você não terminou na aula)

### Lab 1 — MVVM
```
unzip ILP037_Laboratorio_Aula08_Lab1_MVVM.zip
cd ILP037_Lab1_MVVM
python3 -m pytest -v        # 8 vermelhos: normal, as classes estao vazias
```
Preencha `QuartoViewModel.__init__` (disponivel, status_label, botao_label, preco_formatado) e
`PainelQuartosVM.__init__` (itens, livres, rodape). Rode de novo até **8 verdes**. O roteiro
completo está em `ILP037_Aula08_LAB1_ROTEIRO_MVVM.md`.

### Lab 2 — Adapter
```
unzip ILP037_Laboratorio_Aula08_Lab2_Adapter.zip
cd ILP037_Lab2_Adapter
python3 -m pytest -v        # alguns verdes, alguns vermelhos
```
Preencha `NeonReservaAdapter`: guarde o cliente no `__init__`; traduza `salvar` (chama
`execute`, devolve o `ticket` como int) e `buscar` (chama `fetch_one`, desembrulha o `row`).
Rode até **7 verdes**. Roteiro completo em `ILP037_Aula08_LAB2_ROTEIRO_Adapter.md`.

## Critério de aceitação
- [ ] Lab 1: `8 passed`
- [ ] Lab 2: `7 passed`
- [ ] nenhum teste foi alterado (você mexe só no código de produção, não nos testes)

## Sobre IA (nível 2)
Pode usar IA como **apoio** (tirar dúvida, explicar um erro), mas **declare** no final da
entrega: uma linha dizendo o que perguntou. O objetivo é você conseguir **ler e explicar** o
próprio código — isso pode ser arguido (P3).

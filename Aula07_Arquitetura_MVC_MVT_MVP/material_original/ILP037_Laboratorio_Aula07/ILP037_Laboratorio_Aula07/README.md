# ILP-037 — Laboratório da Aula 07 · Arquitetura

Você vai extrair um Service testável sem HTTP de uma "view" que faz coisas demais — o começo da separação em camadas (MVC/MVT/MVP).

## Comece por aqui
1. Abra o **ROTEIRO.md** e siga.
2. Rode os testes com `python3 -m pytest tests/ -v`.
3. Início: 1 verde, 1 vermelho. Fim: 2 verdes.

## O que é diferente
O código já funciona no começo. Você melhora a arquitetura sem mudar a saída — e ganha testabilidade: a regra passa a ser testável sem subir servidor.

## Python puro — imita uma view Django
A função imita uma view (recebe dados, devolve texto), mas roda em qualquer máquina. A aplicação no projeto Django vem pelo homework.

## Se der ModuleNotFoundError
Use `python3 -m pytest` (com o -m). O `pytest.ini` já resolve.

## Uso de IA
Nível 2 — pode usar para destravar, declare trechos acima de 5 linhas, saiba explicar.

---
*ILP-037 · FATEC Olímpia · 2026/2*

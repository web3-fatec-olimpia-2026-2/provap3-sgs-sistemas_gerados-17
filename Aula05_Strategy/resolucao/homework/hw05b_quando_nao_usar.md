# Homework 05b — Quando Strategy NÃO cabe

> ⚠️ **Nível 3 (IA vedada)** — modelo de estudo para conferência. Escreva o seu antes.

**Modelo (4 linhas):**
O Strategy ataca o `if/elif` que escolhe um cálculo pelo "tipo" de alguma coisa e que ganha um
ramo novo cada vez que o negócio inventa uma categoria, forçando a reabrir a mesma classe e
arriscar o que já funcionava. Ele só se paga quando existe de fato uma família de variações que
muda ou cresce. Se a regra é uma só e não tem perspectiva de variar (ex.: taxa de serviço fixa de
10% para todo mundo), criar interface + classes para ela é cerimônia: uma linha ou uma função resolve.

**Checklist (10 pts):** identifica o smell — `if/elif` que cresce (4) · explica quando é exagero —
comportamento único, sem variação (4) · autoral, 3–5 linhas (2).

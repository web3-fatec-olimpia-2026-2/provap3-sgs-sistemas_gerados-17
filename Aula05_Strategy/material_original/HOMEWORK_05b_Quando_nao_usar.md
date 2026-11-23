# 📝 Homework 05b — Quando Strategy NÃO cabe

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Individual · Prazo: quarta-feira, 10/09, 23h59 · 10 pontos**

---

## A tarefa

Em **três a cinco linhas**, responda com as suas palavras:

> **Que problema (code smell) o padrão Strategy resolve? E em que situação usar Strategy seria exagero — uma "fachada" que não se justifica?**

---

## Por que esta pergunta importa

A competência que esta disciplina avalia **não é escrever o padrão** — é **decidir se ele cabe**. Saber aplicar Strategy é fácil; saber quando **não** aplicar é o que separa quem entende de quem decora. Um padrão usado onde não precisa deixa o código mais complicado sem ganho nenhum — é o oposto do objetivo.

## Para você se situar

- **O *smell* que Strategy resolve:** um `if/elif` (ou `switch`) que escolhe comportamento por tipo e **cresce a cada tipo novo**, obrigando a mexer na mesma classe repetidamente.
- **Quando é exagero:** quando há um comportamento só, que não varia. Aí criar classes de estratégia é cerimônia — uma função simples resolve. Strategy só se paga quando a **família de comportamentos varia**.

A partir daí, a resposta tem que ser **sua**.

---

## A regra

**Com as suas palavras.** Não copie de slide, do material ou de IA. O valor está em você conectar as duas pontas — o problema e o limite — na sua cabeça.

---

## Como entregar

- Texto direto na tarefa do **Teams** (Módulo da Aula 05), ou um arquivo simples.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| Identifica o *smell* que Strategy resolve (o `if/elif` que cresce) | 4 |
| Explica quando é exagero (comportamento único, sem variação) | 4 |
| Texto autoral, dentro do limite de linhas | 2 |

---

## Uso de IA

**Nível 3 — VEDADO.**
Esta pergunta é exatamente o tipo de julgamento que a IA faz por você sem que você aprenda. O valor está inteiro em **você** decidir. Usar IA aqui é jogar o exercício fora — e é justamente esse julgamento que será cobrado na arguição do Marco 1.

---

*Homework 05b — ILP-037 — FATEC Olímpia — 2026/2*

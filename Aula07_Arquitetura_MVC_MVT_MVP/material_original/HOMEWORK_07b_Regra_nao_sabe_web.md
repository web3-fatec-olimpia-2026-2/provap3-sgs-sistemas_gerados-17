# 📝 Homework 07b — A regra não sabe o que é web

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Individual · Prazo: quarta-feira, 24/09, 23h59 · 10 pontos**

---

## A tarefa

Em **três a cinco linhas**, responda com as suas palavras:

> **Por que uma regra de negócio "não deve saber o que é web"? O que você ganha, na prática, ao separá-la da view (num Service ou Presenter)?**

---

## Para você se situar

Quando a regra de negócio está **dentro** da view, ela fica presa à camada web: para testá-la, você precisa de um `request`, de subir o servidor, de ler a resposta. Testar fica caro — e o que é caro, ninguém faz. A regra acaba **sem teste**.

Quando você **separa** a regra num Service que só recebe e devolve dados, ela deixa de depender da web. Você a testa direto, num piscar. Testar fica barato — e o que é barato, todo mundo faz. A regra fica **protegida por testes**.

Esse é o ganho concreto: **testabilidade**. E testabilidade não é um luxo — é o que permite mudar o código sem medo.

A partir daí, a resposta tem que ser **sua**.

---

## A regra

**Com as suas palavras.** Não copie de slide, do material ou de IA. O valor está em você conectar a separação de camadas ao ganho de testabilidade — na sua cabeça, com o seu jeito de dizer.

---

## Como entregar

- Texto direto na tarefa do **Teams** (Módulo da Aula 07), ou um arquivo simples.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| Explica que a regra presa à web só se testa subindo a web | 4 |
| Conecta a separação ao ganho de **testabilidade** | 4 |
| Texto autoral, dentro do limite de linhas | 2 |

---

## Uso de IA

**Nível 3 — VEDADO.**
Esta é uma pergunta de compreensão — o tipo que a IA responde perfeito, sem que você construa o entendimento. O valor está em **você** formular. E é esse raciocínio que sustenta as decisões de arquitetura que o Marco 2 vai cobrar.

---

*Homework 07b — ILP-037 — FATEC Olímpia — 2026/2*

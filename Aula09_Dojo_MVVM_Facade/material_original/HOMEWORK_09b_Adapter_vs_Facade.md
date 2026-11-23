# Homework 09B — Adapter × Facade: qual a diferença?
### Individual · ILP-037 · Prazo: quarta 22/10, 23h59 · **IA vedada (nível 3)**

## A tarefa
Em **3 a 5 linhas**, com **as suas palavras**, responda:

> **Qual a diferença entre o padrão _Adapter_ (Aula 08) e o padrão _Facade_ (Aula 09)?**

## Por que esta pergunta
Os dois "escondem" algo e é fácil confundir. Se você sabe diferenciar, você entendeu os dois —
não decorou nenhum. É a tabela de contraste que vimos em aula.

## O que uma boa resposta toca (guia — não precisa citar)
- **Adapter:** mexe em **uma** peça (um driver/biblioteca de terceiro) e **traduz** a interface
  dela para outra que o sistema já espera. Intenção: fazer a peça **caber**.
- **Facade:** mexe em **vários** subsistemas e **cria** uma interface **nova e simples** na frente
  deles. Intenção: **esconder** a complexidade da orquestração.
- Um bom fechamento: dar um exemplo de cada no Resort (o `NeonReservaAdapter` × a `RecepcaoFacade`).

## Critério de aceitação
- [ ] 3 a 5 linhas, texto seu
- [ ] deixa claro **um × vários** e **traduzir × esconder/criar interface nova**
- [ ] pelo menos um exemplo concreto

## Sobre IA (nível 3 — vedada)
Questão de compreensão própria. Não use IA para redigir. Respostas "de manual" podem ser
arguidas em aula (P3).

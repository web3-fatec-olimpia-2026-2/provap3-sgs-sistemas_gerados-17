# Homework 10B — Decorator × Adapter: manter ou mudar a interface?
### Individual · ILP-037 · Prazo: quarta 12/11, 23h59 · **IA vedada (nível 3)**

## A tarefa
Em **3 a 5 linhas**, com **as suas palavras**, responda:

> **Os dois embrulham um objeto. Por que o _Decorator_ MANTÉM a interface e o _Adapter_ a MUDA — e
> por que isso é o que permite empilhar decoradores?**

## Por que esta pergunta
É a confusão clássica: Adapter e Decorator parecem iguais (ambos envolvem um objeto). A diferença
está no que fazem com a **interface** — e é ela que decide se você pode empilhar.

## O que uma boa resposta toca (guia — não precisa citar)
- **Adapter:** embrulha para **traduzir** a interface de uma peça para **outra** que o sistema já
  espera. A peça de fora fala uma língua diferente da de dentro.
- **Decorator:** embrulha **mantendo a mesma** interface (`preco`/`descricao`) e só **somando**
  comportamento. Como a interface é a mesma por dentro e por fora, um decorador pode embrulhar
  outro — e por isso **empilha** (`ComTransfer(ComCafeDaManha(...))`).
- Fechamento: o Adapter quer **caber**; o Decorator quer **acrescentar**.

## Critério de aceitação
- [ ] 3 a 5 linhas, texto seu
- [ ] deixa claro **mudar × manter** a interface
- [ ] conecta "manter a interface" com "poder empilhar"

## Sobre IA (nível 3 — vedada)
Questão de compreensão própria. Não use IA para redigir. Isso pode voltar na **P3 (prova prática,
27/11)**: se você escreveu, você sabe explicar.

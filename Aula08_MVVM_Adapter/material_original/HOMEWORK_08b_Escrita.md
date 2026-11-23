# Homework 08B — Service × ViewModel: o que cada um separa
### Individual · ILP-037 · Prazo: quarta 15/10, 23h59 · **IA vedada (nível 3)**

## A tarefa
Em **3 a 5 linhas**, com **as suas palavras**, responda:

> **Qual a diferença entre o que o _Service_ separa (Aula 07) e o que o _ViewModel_ separa (Aula 08)?**

## Por que esta pergunta
Os dois tiram lógica de dentro da tela — mas lógicas **diferentes**. Se você entende a diferença,
você entende por que o MVVM não substitui o Service: eles convivem. Esta é exatamente a confusão
que a aula quis desfazer.

## O que uma boa resposta toca (não precisa citar, é para você se guiar)
- O **Service** separa a **regra de negócio** — cálculo, decisão, o que o sistema *faz*
  (ex.: calcular a diária com desconto, decidir se pode reservar).
- O **ViewModel** separa a **lógica de exibição** — como o dado *aparece* na tela
  (ex.: o texto "livre/INDISPONIVEL", o rótulo do botão, o "R$").
- Um cuida do que é **verdade no domínio**; o outro, do que é **mostrado ao usuário**.

## Critério de aceitação
- [ ] 3 a 5 linhas, texto seu
- [ ] deixa claro **regra de negócio** (Service) × **lógica de exibição** (ViewModel)
- [ ] dá pelo menos um exemplo concreto (pode ser do Resort)

## Sobre IA (nível 3 — vedada)
Esta é uma questão de **compreensão própria**. Não use IA para redigir. Respostas que soam
genéricas ou "de manual" podem ser arguidas em aula (P3): se você escreveu, você sabe explicar.

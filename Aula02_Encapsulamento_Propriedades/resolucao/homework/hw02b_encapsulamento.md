# Homework 02b — O que é encapsulamento

> ⚠️ Esta tarefa é **Nível 3 (IA vedada)** e exige texto autoral. O texto abaixo é um
> **modelo de estudo** para conferir se a sua resposta cobre os critérios — escreva a sua
> com as suas palavras e a sua própria analogia antes de comparar.

**Modelo (4 linhas):**
Encapsulamento é deixar o próprio objeto decidir como seus dados podem ser lidos e alterados,
em vez de qualquer parte do programa mexer neles diretamente. Um atributo público aceita
qualquer valor que alguém escreva — inclusive um impossível, como uma idade negativa —, então
o objeto passa a carregar um estado que não faz sentido e o erro só aparece longe dali, quando
outro código confia nesse dado. É como uma planilha compartilhada sem validação de célula:
qualquer pessoa digita "abc" na coluna de preço e a soma do fim do mês quebra sem ninguém saber onde.

**Checklist dos critérios (10 pts):**
- [ ] Distingue dado público (qualquer um altera) de dado protegido (o objeto valida) — 4 pts
- [ ] Explica **por que** é risco: o objeto entra em estado inválido — 3 pts
- [ ] Autoral e com 3 a 5 linhas — 2 pts
- [ ] Analogia própria (não usar cofre/fechadura/porta da aula) — 1 pt

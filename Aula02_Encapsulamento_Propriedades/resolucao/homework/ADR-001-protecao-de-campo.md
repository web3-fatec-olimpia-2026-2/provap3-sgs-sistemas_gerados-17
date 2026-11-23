# ADR 001 — Proteção do campo `valor_diaria`

> Homework 02c (da equipe). Exemplo usando a classe `Reserva` dos exercícios, como o próprio
> enunciado permite quando a equipe ainda não tem código. Troque pelo campo real do projeto.

## Contexto
O campo `valor_diaria` da `Reserva` aceitava qualquer número, inclusive negativo: era possível
criar uma reserva de 3 diárias a -50 reais, e o `total` virava -150 sem nenhum erro. O mesmo
acontecia com `diarias = 0`. A regra existia só na cabeça da equipe.

## Decisão
Proteger `valor_diaria` (≥ 0) e `diarias` (≥ 1) com `@property` + setter que levanta
`ValueError`. O `__init__` atribui por `self.valor_diaria = ...`, então a validação roda também
na criação. O `total` passou a ser uma property calculada (sem setter), para nunca ficar
desatualizado.

## Alternativa descartada
**Validar só no formulário da tela (Django Form).** Descartada porque não protege quem cria a
reserva por outros caminhos: shell, admin, importação, testes ou outra view. A regra precisa
morar no objeto, num lugar só.
Também descartamos colocar `@property` em `hospede` e `quarto`: não têm regra hoje, seria
cerimônia.

## Consequência
- Melhor: o objeto se protege sozinho; um valor inválido falha cedo, perto da causa.
- Custo: a classe ficou um pouco maior e todo código que cria `Reserva` precisa tratar
  `ValueError`.
- Teste de limite (`diarias = 1` é válido) adicionado para não regredir.

## Commit
`<hash do commit em que a proteção entrou>`

# ADR 003 — Onde mora a validação dos dados

> Homework 03c (da equipe) — modelo preenchido. Adapte os nomes de campos ao projeto real.

## Contexto
Nosso projeto usa Django (o mesmo de Web III). Precisamos decidir como e onde validar os dados
para que um valor inválido (diária negativa, capacidade zero, preço negativo) não entre no
sistema — vindo da tela, do admin, do shell ou de uma importação.

## Decisão
- **Campos do model** → validadores do Django (`MinValueValidator(0)` em `diaria`,
  `MinValueValidator(1)` em `capacidade`) e, para regras que envolvem mais de um campo,
  o método `clean()` do model. Motivo: o model alimenta formulário, admin e ORM, e esses três
  conhecem e executam validadores.
- **Dados calculados no model** (ex.: `receita_maxima`, `total`) → `@property` sem setter.
- **Regras em classes Python fora do model** (ex.: uma calculadora de tarifa) →
  `@property` com setter.

## Alternativa descartada
`@property` com setter **direto nos campos do model**. Descartada porque o campo deixaria de
ser um `Field`: some do ModelForm e do admin, e o ORM não consegue filtrar/ordenar por ele
(`Quarto.objects.filter(diaria__gte=100)` deixa de funcionar).
Também descartamos validar **só no formulário**, porque não protege quem grava pelo shell/admin.

## Consequência
- A regra de cada campo fica declarada no próprio model, visível e testável.
- Custo: `save()` **não valida sozinho** — é preciso garantir que a gravação passe por
  ModelForm ou chame `full_clean()` antes (em service/view). Teste cobrindo isso.

## Commit
`<hash do commit em que a primeira validação entrou no projeto>`

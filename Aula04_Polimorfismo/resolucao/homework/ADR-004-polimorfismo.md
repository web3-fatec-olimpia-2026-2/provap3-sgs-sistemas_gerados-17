# ADR 004 — Onde polimorfismo caberia no nosso projeto

> Homework 04c (da equipe) — modelo. Trocar pelo ponto real do projeto da equipe.

## Contexto
O sistema aceita três formas de pagamento (cartão, pix, boleto). Hoje a view de checkout decide
o que fazer com um `if/elif` por forma: cartão cobra taxa de 3%, pix dá 5% de desconto, boleto
soma R$ 2,50 de tarifa e vence em 3 dias. Cada forma nova (ex.: "carteira digital") obriga a
editar esse bloco.

## Decisão
**Vale** aplicar polimorfismo: cada forma vira uma classe com a mesma interface
(`calcular_valor_final(valor)` e `descricao()`), e o checkout chama o método sem perguntar o tipo.

```python
class Pagamento:                         # interface comum
    def calcular_valor_final(self, valor): raise NotImplementedError
class Pix(Pagamento):
    def calcular_valor_final(self, valor): return valor * 0.95
class Cartao(Pagamento):
    def calcular_valor_final(self, valor): return valor * 1.03
```

## Alternativa considerada
Manter o `if/elif`. Funciona e é mais curto com 3 formas, mas cada forma nova mexe numa função
já testada (risco de quebrar as outras) e a regra de cada forma fica espalhada.
Também consideramos um dicionário `{forma: percentual}` — descartado porque o boleto tem regra
diferente (tarifa fixa + vencimento), que não cabe num número só.

## Consequência
Adicionar uma forma nova = uma classe nova, checkout intacto. Custo: mais arquivos/classes;
para 2 formas fixas que nunca mudam, não valeria (critério antifachada).

## Status
Proposto — ainda não implementado.

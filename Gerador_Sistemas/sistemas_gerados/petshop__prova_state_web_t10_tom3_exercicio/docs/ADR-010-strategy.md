# ADR 010 — Strategy em PETShop

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — Aula 05

## Contexto
`CobrancaAntiga.valor()` tem um `if/elif` por tipo de cliente que cresce a cada regra nova — cada uma obriga a reabrir a classe.

## Decisão
APLICAMOS **Strategy**. Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`.

## Alternativa descartada
Dicionário `{tipo: percentual}` — resolve percentuais, mas não comporta uma regra com comportamento próprio (prazo, limite, cálculo diferente).

## Consequências
Regra nova = classe nova; `Cobranca` intacta (OCP). Custo: uma classe por regra.
Quando NÃO usar: Uma regra só, que nunca varia → uma função ou constante basta (Strategy seria cerimônia). Em Python a estratégia pode ser uma função.

## Onde está no código
`nucleo/politicas.py` (antes: `nucleo/antes_politicas.py`) · testes: `tests/test_politicas.py`

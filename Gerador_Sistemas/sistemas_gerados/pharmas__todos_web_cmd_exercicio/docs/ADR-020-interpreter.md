# ADR 020 — Interpreter em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`regra_antiga(item)` traz a condição fixa no código — mudar "a partir de 3" para "a partir de 4" exige programar e publicar de novo.

## Decisão
APLICAMOS **Interpreter**. Cada pedaço da gramática é uma classe com `interpretar(item)`: `Comparacao` (terminal), `E` e `Ou` (não terminais). `ler_regra(texto)` monta a árvore a partir do texto — a regra vira DADO.

## Alternativa descartada
`eval()` do texto — perigoso (executa qualquer código) e sem mensagens de erro úteis.

## Consequências
Regras guardáveis como texto e combináveis. Custo: cada operador novo é uma classe.
Quando NÃO usar: Linguagem grande (vira compilador — use uma biblioteca de parsing) ou regra que nunca muda.

## Onde está no código
`nucleo/regras.py` (antes: `nucleo/antes_regras.py`) · testes: `tests/test_regras.py`

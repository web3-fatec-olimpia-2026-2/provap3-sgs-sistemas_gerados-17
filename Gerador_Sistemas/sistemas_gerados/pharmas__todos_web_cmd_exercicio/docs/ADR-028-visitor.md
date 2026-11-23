# ADR 028 — Visitor em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`total_antigo` e `texto_antigo` percorrem as linhas perguntando o tipo — cada operação nova repete a escada; cada tipo novo mexe em todas.

## Decisão
APLICAMOS **Visitor**. Cada linha tem `aceitar(visitante)` e chama o método certo do visitante (despacho duplo); cada OPERAÇÃO é um visitante (`CalculoDoTotal`, `TextoDoOrcamento`) com um `visitar_*` por tipo.

## Alternativa descartada
`isinstance`/`if` por tipo em cada operação — repetido.

## Consequências
Operação nova sem tocar nos elementos. Custo: tipo novo de elemento = método novo em todos os visitantes.
Quando NÃO usar: Tipos de elemento que mudam muito (cada tipo novo mexe em TODOS os visitantes) — prefira polimorfismo comum.

## Onde está no código
`nucleo/orcamento.py` (antes: `nucleo/antes_orcamento.py`) · testes: `tests/test_orcamento.py`

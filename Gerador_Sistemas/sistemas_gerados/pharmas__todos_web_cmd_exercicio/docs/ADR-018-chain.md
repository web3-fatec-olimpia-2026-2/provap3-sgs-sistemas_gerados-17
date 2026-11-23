# ADR 018 — Chain of Responsibility em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`quem_aprova_antigo(item)` tem todas as alçadas num `if/elif`; incluir um nível (ex.: supervisor) obriga a reescrever a função.

## Decisão
APLICAMOS **Chain of Responsibility**. Cada `Aprovador` conhece só a SUA alçada e o PRÓXIMO elo: se pode, aprova; senão, repassa. A cadeia é montada de fora (`encadear`) — incluir ou tirar um nível não mexe nos outros.

## Alternativa descartada
`if/elif` central — simples, mas concentra todas as alçadas.

## Consequências
Níveis entram e saem sem mexer nos demais. Custo: seguir o pedido exige percorrer a cadeia.
Quando NÃO usar: Poucas regras fixas — um `if/elif` curto é mais legível. O pedido pode chegar ao fim da cadeia sem ninguém tratar.

## Onde está no código
`nucleo/aprovacao.py` (antes: `nucleo/antes_aprovacao.py`) · testes: `tests/test_aprovacao.py`

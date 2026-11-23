# ADR 009 — State em PETShop

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`SituacaoAntiga` repete a mesma escada de `if/elif` sobre `self.status` em `confirmar`, `concluir` e `cancelar`.

## Decisão
APLICAMOS **State**. Cada estado é uma classe (`Aberto`, `Confirmado`, `Concluido`, `Cancelado`) que sabe as SUAS transições; `SituacaoPetshop` (contexto) guarda o estado atual e delega. Transição proibida levanta `TransicaoInvalida`.

## Alternativa descartada
`if/elif` por status em cada método — repetido e fácil de esquecer uma transição.

## Consequências
Cada estado num lugar; estado novo = classe nova. Custo: uma classe por estado.
Quando NÃO usar: Dois estados e uma regra (um booleano basta). State × Strategy: no State o próprio estado troca o objeto do contexto; no Strategy quem escolhe é o cliente.

## Onde está no código
`nucleo/situacao.py` (antes: `nucleo/antes_situacao.py`) · testes: `tests/test_situacao.py`

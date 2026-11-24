# ADR 007 — Decorator em Cooperativa Citrícola

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão estrutural (GoF) — Aula 10

## Contexto
`preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

## Decisão
APLICAMOS **Decorator**. Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComClassificacao(ComFrete(LoteCitrosBase(item)))`.

## Alternativa descartada
Flags booleanas — cada extra novo vira parâmetro + `if` + mudança em quem chama; subclasse por combinação explodiria.

## Consequências
Extra novo = classe nova, combinável em tempo de execução. Custo: cadeias longas são difíceis de depurar.
Quando NÃO usar: Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

## Onde está no código
`nucleo/extras.py` (antes: `nucleo/antes_extras.py`) · testes: `tests/test_extras.py`

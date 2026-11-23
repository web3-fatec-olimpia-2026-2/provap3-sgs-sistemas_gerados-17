# ADR 007 — Factory Method em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`avisar_antigo(item, canal)` tem um `if/elif` para CRIAR o canal certo no meio do algoritmo — canal novo reabre a função.

## Decisão
APLICAMOS **Factory Method**. `Avisador.avisar(item)` é o algoritmo comum; o passo que varia — QUAL canal criar — é o método fábrica `criar_canal()`, sobrescrito por `AvisadorEmail`, `AvisadorSms`… O criador não conhece as classes concretas dos produtos.

## Alternativa descartada
`if/elif` (ou dicionário) na criação — simples, mas a escolha fica longe de quem sabe o que precisa.

## Consequências
Canal novo = produto + criador novos; `Avisador` intacto. Custo: uma subclasse de criador por produto.
Quando NÃO usar: Um tipo só de produto, ou escolha resolvida por um dicionário `{nome: Classe}` — em Python dá para passar a própria classe como parâmetro.

## Onde está no código
`nucleo/avisos.py` (antes: `nucleo/antes_avisos.py`) · testes: `tests/test_avisos.py`

# ADR 021 — Iterator em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`totais_antigo(colecao)` lê `colecao._itens[i]` por índice — depende da lista interna; trocar a estrutura quebra todos os laços.

## Decisão
APLICAMOS **Iterator**. `ColecaoReserva` esconde como guarda (dicionário por hospede) e entrega um ITERADOR (`IteradorDeItens`, com `__next__`) em `__iter__`. Percursos especiais (`acima_de`, `ordenados_por_total`) não expõem o interior.

## Alternativa descartada
Expor a lista interna — rápido, mas acopla todo mundo à estrutura.

## Consequências
Estrutura interna livre para mudar; percursos independentes. Custo: mais uma classe.
Quando NÃO usar: Lista e dicionário já são iteráveis em Python; classe de iterador só para percurso especial — um gerador (`yield`) é o atalho.

## Onde está no código
`nucleo/colecao.py` (antes: `nucleo/antes_colecao.py`) · testes: `tests/test_colecao.py`

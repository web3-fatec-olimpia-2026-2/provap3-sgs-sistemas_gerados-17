# ADR 016 — Flyweight em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
Cada registro cria o SEU objeto de tipo de cliente (nome + fator); 10 000 registros = 10 000 objetos iguais na memória.

## Decisão
APLICAMOS **Flyweight**. `TipoCompartilhado` guarda só o estado INTRÍNSECO (nome, fator), igual para todos e imutável; `FabricaDeTipos.obter(chave)` devolve sempre o mesmo objeto; o estado EXTRÍNSECO (a Pharm) chega por parâmetro: `tipo.valor(item)`.

## Alternativa descartada
Um objeto por registro — simples, porém multiplica a memória.

## Consequências
Milhares de registros apontam para poucos objetos. Custo: imutabilidade e contexto por parâmetro.
Quando NÃO usar: Poucos objetos, ou objetos que mudam — o ganho de memória não paga a complexidade.

## Onde está no código
`nucleo/tipos_compartilhados.py` (antes: `nucleo/antes_tipos_compartilhados.py`) · testes: `tests/test_tipos_compartilhados.py`

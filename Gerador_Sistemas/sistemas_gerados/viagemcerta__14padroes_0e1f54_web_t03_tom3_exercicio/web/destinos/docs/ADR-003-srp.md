# ADR 003 — SRP + OCP (separar responsabilidades) em ViagemCerta

- Status: aceito (exemplo de estudo gerado)
- Família: Princípios SOLID — Aula 06

## Contexto
`DestinoFazTudo` calcula, formata o recibo e grava em arquivo: três motivos para mudar na mesma classe.

## Decisão
APLICAMOS **SRP + OCP (separar responsabilidades)**. `Destino` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); `ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova (`ReciboCsvFormatter`) → OCP.

## Alternativa descartada
Manter tudo na entidade — layout, destino e regra mudariam a mesma classe.

## Consequências
Cada mudança mexe num lugar só; formato novo não reabre nada. Custo: mais classes pequenas.
Quando NÃO usar: SRP não é uma classe por método: separar "calcula", "soma", "arredonda" em classes é tão ruim quanto juntar tudo. A unidade é a responsabilidade (motivo para mudar).

## Onde está no código
`nucleo/recibo.py` (antes: `nucleo/antes_recibo.py`) · testes: `tests/test_recibo.py`

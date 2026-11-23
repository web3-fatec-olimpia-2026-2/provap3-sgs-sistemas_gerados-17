# ADR 002 — Polimorfismo (herança + sobrescrita) em Sistema Exemplo

- Status: aceito (exemplo de estudo gerado)
- Família: Fundamento de OO — Aula 04

## Contexto
`imprimir_preco(tipo)` decide o texto com `if/elif` por categoria; cada categoria nova obriga a editar a função (e arriscar as que já funcionavam).

## Decisão
APLICAMOS **Polimorfismo (herança + sobrescrita)**. Cada categoria é uma subclasse de `Basico` que SOBRESCREVE `descricao()` e `preco_unidade()`. `imprimir_preco(categoria)` só chama os métodos — o Python escolhe a versão pelo tipo real do objeto, em tempo de execução.

## Alternativa descartada
Manter o `if/elif` por tipo — cada categoria nova reabriria a função.

## Consequências
Categoria nova = classe nova; a função não muda. Custo: uma classe por categoria.
Quando NÃO usar: Se as categorias só diferem num número (sem comportamento próprio), um atributo ou tabela basta. Herança só para relação É-UM; TEM-UM é composição.

## Onde está no código
`nucleo/categorias.py` (antes: `nucleo/antes_categorias.py`) · testes: `tests/test_categorias.py`

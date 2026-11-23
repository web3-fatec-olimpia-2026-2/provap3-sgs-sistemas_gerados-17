# ADR 024 — Observer em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`alterar_antigo(...)` chama painel e log um por um — conhece todos os interessados; um interessado novo obriga a editar a função.

## Decisão
APLICAMOS **Observer**. `ReservaObservavel` (sujeito) guarda a lista de observadores e, a cada mudança, chama `atualizar(evento)` em todos. Interessado novo = `inscrever(obj)`; o sujeito não muda.

## Alternativa descartada
Chamar cada interessado na mão — acoplamento a todos.

## Consequências
Sujeito e observadores independentes. Custo: ordem e efeitos ficam menos visíveis.
Quando NÃO usar: Um interessado único e fixo — chame-o direto. Cadeias de observadores escondem o fluxo.

## Onde está no código
`nucleo/eventos.py` (antes: `nucleo/antes_eventos.py`) · testes: `tests/test_eventos.py`

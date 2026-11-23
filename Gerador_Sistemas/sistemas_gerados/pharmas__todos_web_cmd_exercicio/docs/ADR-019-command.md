# ADR 019 — Command em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`alterar_antigo(item, campo, valor)` muda a Pharm direto e a ação some — sem registro do valor anterior, não dá para desfazer.

## Decisão
APLICAMOS **Command**. Cada ação vira um OBJETO (`AlterarCampo`) que sabe `executar()` e `desfazer()` (guarda o valor anterior). `Historico` (o invocador) empilha os comandos e faz desfazer/refazer em ordem.

## Alternativa descartada
Guardar cópias do objeto inteiro antes de cada ação — é o Memento (mais memória).

## Consequências
Desfazer/refazer, fila e histórico de ações. Custo: uma classe por tipo de ação.
Quando NÃO usar: Ação simples que nunca será desfeita, enfileirada ou registrada — chame o método direto.

## Onde está no código
`nucleo/comandos.py` (antes: `nucleo/antes_comandos.py`) · testes: `tests/test_comandos.py`

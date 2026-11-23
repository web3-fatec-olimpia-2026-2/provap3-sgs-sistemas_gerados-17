# ADR 022 — Mediator em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
O campo de quantidade conhece o seletor, o resumo e o botão e mexe neles direto — todos acoplados a todos; componente novo obriga a mexer nos outros.

## Decisão
APLICAMOS **Mediator**. Cada componente só conhece o MEDIADOR e avisa `notificar(self, evento)`; `FormularioMediador` decide quem reage (recalcula o resumo, liga/desliga o botão).

## Alternativa descartada
Componentes chamando uns aos outros — N × N ligações.

## Consequências
Componentes independentes e reaproveitáveis. Custo: a complexidade se concentra no mediador.
Quando NÃO usar: 2–3 objetos que conversam pouco. Cuidado para o mediador não virar um "objeto deus".

## Onde está no código
`nucleo/mediador.py` (antes: `nucleo/antes_mediador.py`) · testes: `tests/test_mediador.py`

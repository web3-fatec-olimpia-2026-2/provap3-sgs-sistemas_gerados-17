# ADR 011 — Adapter em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão estrutural (GoF) — Aula 08

## Contexto
O gateway `PagaJa` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.

## Decisão
APLICAMOS **Adapter**. `PagaJaAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`).

## Alternativa descartada
`if usa_gateway` dentro do serviço — o detalhe do terceiro vaza para a regra e se repete em cada método.

## Consequências
Trocar de gateway = injetar outro processador. Custo: uma classe de tradução.
Quando NÃO usar: Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).

## Onde está no código
`nucleo/integracao.py` (antes: `nucleo/antes_integracao.py`) · testes: `tests/test_integracao.py`

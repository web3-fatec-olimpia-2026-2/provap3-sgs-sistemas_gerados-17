# ex04 — Adapter: gateway de pagamento de terceiro

**Cenário.** O sistema da loja paga tudo pela interface `ProcessadorPagamento`:

```python
processar(valor: float, token_cartao: str) -> str      # devolve o id da transação
# se recusar: levanta PagamentoRecusado(motivo)
```

A loja contratou o **PagaFácil**, cuja biblioteca (de terceiro — não pode ser alterada) fala assim:

```python
GatewayPagaFacil().charge({"amount_cents": 1999, "card": "tok_123", "currency": "BRL"})
# -> {"result": "approved", "tx": "PF-0001"}
# -> {"result": "denied", "reason": "saldo insuficiente"}
```

Hoje o `CheckoutAntigo` tem um `if usa_pagafacil:` para conversar com os dois mundos.

## Tarefa (no `exercicio.py`)
1. `PagaFacilAdapter(gateway)` que **é um** `ProcessadorPagamento`:
   - reais → **centavos inteiros** (cuidado: `19.99 * 100` dá `1998.9999…` → use `round`);
   - `"approved"` → devolve o `tx`; `"denied"` → levanta `PagamentoRecusado(reason)`.
2. Os mesmos testes devem passar com o `ProcessadorFake` (já pronto) **e** com o adapter
   (substituibilidade). O `Checkout` limpo (pronto) não deve ter nenhum `if` de gateway.

## Para explicar depois (P3)
- Por que Adapter e não Facade aqui?
- Se o PagaFácil fosse código **nosso**, você criaria o adapter?

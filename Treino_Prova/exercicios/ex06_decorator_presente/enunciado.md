# ex06 — Decorator: opcionais do pedido

**Cenário.** `preco_com_flags(valor, embrulho=False, cartao=False, expressa=False)` soma extras com
uma pilha de `if`. A loja quer também **cupom de 10%** e permitir **dois cartões** no mesmo pedido.

| Extra | Preço | Texto na descrição |
|---|---|---|
| `ComEmbrulho` | +15 | `" + embrulho"` |
| `ComCartao` | +5 | `" + cartao"` |
| `ComEntregaExpressa` | +25 | `" + entrega expressa"` |
| `ComCupom10` | **× 0,9 sobre tudo o que está dentro** (arredonde a 2 casas) | `" (-10% cupom)"` |

Base: `PedidoBase(valor)` com `preco()` e `descricao()` = `"Pedido R$ 100.00"` (pronta).

## Tarefa (no `exercicio.py`)
1. `Opcional` — decorador base: guarda o embrulhado e **delega** `preco()`/`descricao()`.
2. Os 4 decoradores acima, cada um chamando o de dentro e somando/alterando a sua parte.
3. As 8 combinações de embrulho/cartão/expressa devem dar o **mesmo preço** que `preco_com_flags`.

## Para explicar depois (P3)
- Por que a ordem de embrulho/cartão/expressa não muda o preço, mas a do cupom muda?
- Por que dá para ter dois cartões aqui e não com flags?
- Se todos os extras fossem só "+ valor fixo", Decorator ainda valeria a pena?

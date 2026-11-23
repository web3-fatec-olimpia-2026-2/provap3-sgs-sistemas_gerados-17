# ex05 — Facade: o checkout da loja

**Cenário.** Finalizar um pedido toca **quatro subsistemas** (prontos em `subsistemas.py`):
`Estoque`, `Pagamentos`, `NotaFiscal`, `Email`. Hoje a view, a API e o app repetem
`finalizar_na_mao(...)`, que conhece a ordem e as regras de aborto.

**Ordem correta:** 1) estoque tem os itens? → 2) cobra → 3) baixa o estoque → 4) emite a nota → 5) envia e-mail.

| Situação | Resultado | Efeitos |
|---|---|---|
| falta estoque | `{"ok": False, "motivo": "sem estoque"}` | **não** cobra, nada mais acontece |
| pagamento recusado | `{"ok": False, "motivo": "pagamento recusado"}` | **não** baixa estoque, sem nota, sem e-mail |
| tudo certo | `{"ok": True, "tx": ..., "nota": ...}` | baixa, emite, envia — nessa ordem |

## Tarefa (no `exercicio.py`)
`CheckoutFacade(estoque, pagamentos, nota, email)` com `finalizar(cliente, itens, valor)`.
A fachada **orquestra e delega** — não pode reimplementar regra de nenhum subsistema.

## Para explicar depois (P3)
- O que o cliente (view/API) deixou de conhecer?
- Onde entra um 6º passo ("pontos de fidelidade")? Quem precisa mudar?
- Quando esta fachada viraria um God object?

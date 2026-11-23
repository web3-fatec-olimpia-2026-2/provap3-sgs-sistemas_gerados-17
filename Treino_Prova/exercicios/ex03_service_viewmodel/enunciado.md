# ex03 — Service × ViewModel: painel de pedidos

**Cenário.** `tela_pedidos(pedidos, hoje)` faz tudo no mesmo laço:
- **regra de negócio**: cupom dá 10% de desconto **se** os itens somam R$ 100 ou mais; um pedido está
  **atrasado** se não foi entregue e `hoje > prazo`;
- **exibição**: rótulo `ENTREGUE`/`ATRASADO`/`A CAMINHO`, cor `verde`/`vermelho`/`amarelo`,
  preço `R$ 90.00`, rodapé `"N pedido(s) atrasado(s)"` ou `"Tudo em dia"`.

## Tarefa (no `exercicio.py`)
1. `PedidoService` — **só regra**: `total(pedido)` e `esta_atrasado(pedido, hoje)`. Nada de texto/cor.
2. `PedidoViewModel(pedido, hoje, servico=None)` — **só exibição**: `id`, `cliente`, `total_formatado`,
   `status_label`, `cor`. Ele **pergunta ao Service**; não recalcula a regra.
3. `PainelPedidosVM(pedidos, hoje)` — `itens` (lista de `PedidoViewModel`), `atrasados`, `rodape`.
4. `tela_pedidos_mvvm(pedidos, hoje)` — View burra; a saída tem que ser **idêntica** à de `tela_pedidos`.

## Para explicar depois (P3)
- "Cupom só vale acima de R$ 100" mora onde? E a cor vermelha?
- Se amanhã a API mobile precisar do total, ela usa o Service ou o ViewModel?

# ex02 — SRP + OCP: a nota do pedido

**Cenário.** `PedidoFazTudo` guarda os itens, calcula o total, **monta o texto da nota** e **grava em
arquivo**. Três motivos para mudar na mesma classe. O financeiro agora quer a nota também em **CSV**.

## Tarefa (no `exercicio.py`)
1. `Pedido(cliente, itens)` — só dados + `total()`. Itens são tuplas `(nome, preco_unitario, quantidade)`.
2. `NotaTextoFormatter.formatar(pedido)` — devolve **exatamente** o mesmo texto de `PedidoFazTudo.gerar_nota()`.
3. `NotaCsvFormatter.formatar(pedido)` — formato novo, **sem reabrir** `Pedido` nem o formatter de texto:
   ```
   item;qtd;subtotal
   Café;2;31.80
   Pão;1;7.50
   TOTAL;;39.30
   ```
4. `ArquivoRepository.salvar(texto, caminho)` — só grava (use `encoding="utf-8"`).

## Para explicar depois (P3)
- Quantos motivos para mudar `PedidoFazTudo` tinha? Quais?
- Onde entra um formato PDF amanhã? O que você **não** precisa tocar?
- Por que não criar uma classe por método?

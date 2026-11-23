# ex07 — Simulado da P3 (desafio integrador)

Leia [`loja.py`](loja.py) como se fosse o código da **sua** equipe. Sem IA, sem rodar (nas partes A–C).
Tempo sugerido: 60 min. Gabarito em [`gabarito_simulado.md`](gabarito_simulado.md).

## Parte A — Reconhecer (para cada bloco: padrão/princípio + 1 frase de justificativa)
- A1. `FretePAC`, `FreteRetirada` e o parâmetro `frete` de `PedidoService.total`
- A2. `Opcional`, `ComEmbrulho`, `ComCupom10`
- A3. `PagaFacilAdapter`
- A4. `PedidoService`
- A5. `CheckoutFacade`
- A6. `ResumoPedidoVM`
- A7. Por que `PagaFacilAdapter` não herda de nenhuma classe-interface e mesmo assim funciona?

## Parte B — Prever (escreva o resultado exato)
Considere `c = montar_checkout()` novo para cada item.
- B1. `c.finalizar("ana", ComEmbrulho(Carrinho([("cafe", 30), ("caneca", 45)])), FretePAC(), 2, "tok_ok")`
- B2. `c.finalizar("ana", ComCupom10(ComEmbrulho(Carrinho([("cafeteira", 200)]))), FretePAC(), 3, "tok_ok")["total"]`
- B3. `c.finalizar("ana", ComEmbrulho(ComCupom10(Carrinho([("cafeteira", 200)]))), FretePAC(), 3, "tok_ok")["total"]`
- B4. `c.finalizar("ana", Carrinho([("cafeteira", 200)]), FretePAC(), 30, "tok_ok")["frete"]`
- B5. `vm = ResumoPedidoVM(<resultado do B1>)` → `vm.valor_formatado`, `vm.frete_label`
- B6. `c.finalizar("ana", Carrinho([("x", 10)]), FreteRetirada(), 1, "tok_recusado")` — e quantos e-mails foram enviados?

## Parte C — "O que muda se…" (2–3 linhas cada)
- C1. …`PedidoService.total` passasse a fazer `if isinstance(frete, FretePAC): ... elif ...`?
- C2. …`PagaFacilAdapter.processar` devolvesse o dict `resp` cru?
- C3. …a regra "frete grátis a partir de R$ 200" fosse movida para `ResumoPedidoVM`?
- C4. …`CheckoutFacade.finalizar` passasse a calcular o frete e o cupom ela mesma?
- C5. …`ComCupom10.preco` fosse `return round(self.preco() * 0.9, 2)`?
- C6. Sem cupom, `ComEmbrulho(Carrinho([("cafeteira", 200)]))` com PAC 3 kg sai por **R$ 215** (frete grátis).
  Explique a um colega por que, **com** o cupom (B2), o desconto efetivo foi só de R$ 5,50 — e por que B3 sai mais caro que B2.

## Parte D — Estender SEM editar `loja.py` (código em `extensoes.py`)
- D1. `FreteMotoboy`: R$ 12 fixo; acima de 5 kg levanta `ValueError`.
- D2. `ComSeguro`: +3% sobre o que está dentro (arredonde a 2 casas); descrição `" + seguro"`.
- D3. `ProcessadorPix`: pagamento **nosso** com `processar(valor, token)` que devolve `"PIX-0001"`, `"PIX-0002"`…
  Responda: precisa de Adapter? Por quê?

Teste suas extensões: `ALVO=extensoes ../../../.venv/bin/python -m pytest -v`

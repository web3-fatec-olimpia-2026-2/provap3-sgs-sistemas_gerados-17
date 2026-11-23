# ex07 — Gabarito do simulado

## Parte A — Reconhecer
- **A1. Strategy** — família de cálculos de frete intercambiáveis com a mesma interface `calcular(peso_kg)`; o `PedidoService` recebe a estratégia e delega, sem `if` por tipo.
- **A2. Decorator** — `Opcional` embrulha um carrinho (ou outro opcional), mantém `preco()/descricao()` e cada subclasse soma/altera a sua parte; por manter a interface, empilha.
- **A3. Adapter** — o `GatewayPagaFacil` é de terceiro e fala `charge({...})`; o adapter expõe `processar(valor, token)`, traduz reais→centavos e `denied`→`PagamentoRecusado`.
- **A4. Service (camada de serviço / regra de negócio)** — concentra a regra "frete grátis a partir de R$ 200" e o cálculo do total; não sabe de tela nem de web, testável direto.
- **A5. Facade** — `finalizar()` é o ponto único que orquestra Service → pagamento → e-mail, na ordem, e decide abortar; delega a cada peça.
- **A6. ViewModel (MVVM)** — traduz o resultado cru em título, selo, valor formatado e rótulo do frete; a tela só exibe.
- **A7.** Duck typing: a `CheckoutFacade` só chama `self._processador.processar(...)`; qualquer objeto com esse método serve (foi o que permitiu o `ProcessadorPix` na Parte D). A classe-interface formal (como `ReservaRepository` no lab) é opcional em Python — documenta o contrato, mas não é exigida.

## Parte B — Prever
- **B1.** `{'ok': True, 'tx': 'PF-0001', 'total': 104, 'frete': 14}` — subtotal 75 + 15 (embrulho) = 90 < 200 → frete PAC 10 + 2×2 = 14 → 104.
- **B2.** `209.5` — (200 + 15) × 0,9 = 193,5 < 200 → perde o frete grátis → + PAC 10 + 2×3 = 16 → 209,5.
- **B3.** `211.0` — 200 × 0,9 = 180 + 15 = 195 < 200 → + 16 → 211,0.
- **B4.** `0` — subtotal 200 ≥ 200 → frete grátis, o peso (30 kg) nem é consultado.
- **B5.** `'R$ 104.00'` e `'Frete R$ 14.00'`.
- **B6.** `{'ok': False, 'motivo': 'cartão recusado'}` e **0** e-mails — a fachada retorna antes de notificar.

## Parte C — "O que muda se…"
- **C1.** Volta o smell do Strategy: o Service passa a conhecer cada frete; frete novo (motoboy) obriga a editar o Service (perde OCP) e o teste de todos os fretes passa pela mesma função.
- **C2.** O formato do terceiro vaza: a fachada receberia `{"result": ..., "tx": ...}` como `tx`, e a recusa não viraria exceção — o `try/except` nunca dispararia e um pagamento recusado seria tratado como sucesso.
- **C3.** Regra de negócio presa na tela: a cobrança real (Service) e o que é mostrado poderiam divergir; a API/relatório não teriam a regra; e testar "frete grátis" exigiria montar o ViewModel. O VM deve só **traduzir** `frete == 0` em "Frete grátis".
- **C4.** A fachada vira **God object**: passa a executar regra em vez de delegar, duplica a lógica do Service e ganha vários motivos para mudar.
- **C5.** `self.preco()` chama o próprio método → **recursão infinita** (`RecursionError`). O decorador tem que chamar o **de dentro** (`self._pedido.preco()`); essa é a essência do padrão.
- **C6.** O cupom por fora reduziu o subtotal de 215 para 193,50 — **abaixo de R$ 200** — e o pedido perdeu o frete grátis (+16): 215 − 21,50 + 16 = 209,50 (desconto efetivo de só 5,50). No B3 o cupom está por dentro: desconta só a cafeteira (180), o embrulho entra cheio (195), e também paga frete → 211. Lição: decorador que **multiplica** torna a **ordem** relevante, e regras de negócio (frete grátis) interagem com ela — isso deve ser decidido e testado.

## Parte D — Estender
Ver [`extensoes_gabarito.py`](extensoes_gabarito.py). Sobre D3: **não precisa de Adapter** — o
`ProcessadorPix` é código nosso e já nasce com `processar(valor, token)`; duck typing resolve.
Adapter só quando a peça é de terceiro e a interface não bate.

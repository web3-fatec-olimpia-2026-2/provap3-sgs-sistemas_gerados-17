# ex01 — Strategy: frete da loja

**Cenário.** A loja calcula o frete com um `if/elif` dentro de `PedidoAntigo.frete()`:

| tipo | regra |
|---|---|
| `"pac"` | R$ 10 + R$ 2 por kg |
| `"sedex"` | R$ 20 + R$ 4 por kg |
| `"retirada"` | grátis |

O marketing já avisou: vem "motoboy" no mês que vem e "drone" no outro. Cada novo tipo reabre a classe.

## Tarefa (no `exercicio.py`)
1. Crie as estratégias `FretePAC`, `FreteSedex`, `RetiradaNaLoja`, todas com `calcular(peso_kg)`.
2. Crie a classe `Pedido(peso_kg, frete)` que **recebe** a estratégia e **delega** em `frete()` — sem `if`.
3. Sem tocar em `Pedido`, crie `FreteMotoboy`: R$ 15 fixo até 5 kg; acima de 5 kg levanta `ValueError("motoboy até 5 kg")`.
4. Os valores têm que ser **idênticos** aos do `PedidoAntigo` (os testes comparam).

## Para explicar depois (P3)
- Por que `Pedido.frete()` não precisa mudar para o motoboy?
- Quando o Strategy seria exagero aqui?

Rodar contra a sua resolução: `ALVO=exercicio ../../../.venv/bin/python -m pytest -v`

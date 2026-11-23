# Homework 05a — Refatore para Strategy

O 05a pede exatamente o laboratório terminado. A resolução completa está em
[`../lab/tarifa.py`](../lab/tarifa.py) e os testes em [`../lab/tests/test_tarifa.py`](../lab/tests/test_tarifa.py):

| Critério | Onde |
|---|---|
| `if/elif` sumiu; a `Reserva` delega (4) | `Reserva.total()` → `self.tarifa.aplicar(base)` |
| Comportamento idêntico (3) | `test_refatoracao_preserva_o_comportamento` compara **antes × depois** em 9 combinações |
| Política nova sem alterar a `Reserva` (2) | `TarifaVIP` e `test_aberto_ao_novo` |
| Roda sem erro (1) | `python3 -m pytest tests/ -v` dentro de `resolucao/lab` |

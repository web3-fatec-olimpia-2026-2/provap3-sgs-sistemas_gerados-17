# 📝 Homework 05a — Refatore para Strategy

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Individual · Prazo: quarta-feira, 10/09, 23h59 · 10 pontos**

---

## O que você precisa saber

Este homework termina o laboratório da aula. Se você fez o laboratório, já sabe o caminho. Se faltou, este arquivo tem tudo.

**O problema (o *smell*).** Uma classe que decide comportamento com um `if/elif` por tipo cresce sem controle: cada tipo novo obriga a abrir a classe e mexer nela.

```python
class Reserva:
    def total(self):
        base = self.diarias * self.valor_diaria
        if self.tipo_hospede == "comum":
            return base
        elif self.tipo_hospede == "fidelidade":
            return base * 0.90
        elif self.tipo_hospede == "parceiro":
            return base * 0.80
```

**A solução: Strategy.** Cada política vira uma classe com um método comum (`aplicar`), e a `Reserva` recebe uma estratégia e delega:

```python
class TarifaComum:
    def aplicar(self, base):
        return base

class TarifaFidelidade:
    def aplicar(self, base):
        return base * 0.90

class Reserva:
    def __init__(self, diarias, valor_diaria, tarifa):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        self.tarifa = tarifa

    def total(self):
        base = self.diarias * self.valor_diaria
        return self.tarifa.aplicar(base)     # delega, sem if
```

---

## A tarefa

1. Refatore o `if/elif` da `Reserva` para **Strategy**: crie uma classe para cada política de tarifa (comum, fidelidade, parceiro) e faça a `Reserva` delegar.

2. Escreva um teste (ou um trecho que rode) mostrando que o resultado é o **mesmo de antes**: comum = base, fidelidade = 10% off, parceiro = 20% off.

3. Acrescente **uma política nova** (uma `TarifaVIP`, por exemplo) **sem tocar na classe `Reserva`**. Mostre que funciona.

---

## Como entregar

- Um arquivo **`.py`** com as classes de estratégia, a `Reserva` refatorada e a demonstração da política nova.
- Entregue no **Teams**, no Módulo da Aula 05.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| O `if/elif` sumiu; a `Reserva` delega para a estratégia | 4 |
| O comportamento é idêntico ao original (mesmos resultados) | 3 |
| A política nova funciona sem alterar a `Reserva` | 2 |
| O código roda sem erro | 1 |

---

## Uso de IA

**Nível 2 — permitido com declaração.** Pode usar para destravar; declare trechos acima de 5 linhas; saiba explicar cada um.

---

*Homework 05a — ILP-037 — FATEC Olímpia — 2026/2*

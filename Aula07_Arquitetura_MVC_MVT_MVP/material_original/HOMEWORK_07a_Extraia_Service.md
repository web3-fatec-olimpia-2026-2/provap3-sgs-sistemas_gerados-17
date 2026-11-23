# 📝 Homework 07a — Extraia o Service

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Individual · Prazo: quarta-feira, 24/09, 23h59 · 10 pontos**

---

## O que você precisa saber

Este homework termina o laboratório da aula. Se você fez o laboratório, já sabe o caminho.

**O problema.** Uma "view" que mistura regra de negócio (calcular) com apresentação (montar o texto) deixa a regra presa: para testá-la, você precisa chamar a view inteira.

**A solução: extrair um Service.** A regra vai para uma classe própria, que devolve **dados** (não texto) e **não sabe o que é web** — testável sozinha. A view fica fina: só orquestra.

```python
class RelatorioService:              # só a regra de negócio
    def __init__(self, reservas):
        self.reservas = reservas
    def _total_reserva(self, r):
        base = r["diarias"] * r["valor"]
        descontos = {"fidelidade": 0.90, "parceiro": 0.80}
        return base * descontos.get(r["tipo"], 1.0)
    def calcular(self):
        linhas = [(r["hospede"], self._total_reserva(r)) for r in self.reservas]
        return linhas, sum(t for _, t in linhas)   # devolve DADOS


def relatorio_reservas_view(reservas, request=None):   # a view fica fina
    linhas, total = RelatorioService(reservas).calcular()
    corpo = "\n".join(f"{nome}: R$ {t:.2f}" for nome, t in linhas)
    return f"RELATORIO\n{corpo}\nTOTAL: R$ {total:.2f}"
```

---

## A tarefa

1. Extraia o `RelatorioService` da view "faz-tudo", como acima: a regra devolve dados, a view só formata.

2. Escreva um teste que exercite o **Service sozinho**, sem chamar a view — provando que a regra é testável sem HTTP. Ex.: uma fidelidade de 2×100 deve dar 180.

3. Escreva um teste (ou verifique) que a **saída final da view continua idêntica** à de antes — a prova de que a refatoração foi segura.

---

## Como entregar

- Um arquivo **`.py`** com o Service, a view fina e os dois testes.
- Entregue no **Teams**, no Módulo da Aula 07.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| O Service contém a regra e **não tem nada de "web"** dentro | 4 |
| O teste do Service roda **sem chamar a view** (sem HTTP) | 3 |
| A saída final da view continua idêntica | 2 |
| O código roda sem erro | 1 |

---

## Uso de IA

**Nível 2 — permitido com declaração.** Pode usar para destravar; declare trechos acima de 5 linhas; saiba explicar.

---

*Homework 07a — ILP-037 — FATEC Olímpia — 2026/2*

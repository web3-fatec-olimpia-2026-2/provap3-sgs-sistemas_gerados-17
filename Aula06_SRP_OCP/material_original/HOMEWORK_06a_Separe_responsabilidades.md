# 📝 Homework 06a — Separe as responsabilidades

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Individual · Prazo: quarta-feira, 17/09, 23h59 · 10 pontos**

---

## O que você precisa saber

Este homework termina o laboratório da aula. Se você fez o laboratório, já sabe o caminho.

**O problema (o *smell*).** Uma classe que faz coisas demais tem vários motivos para mudar. Uma `Reserva` que calcula o total, formata o recibo e salva em arquivo mistura três responsabilidades: regra de negócio, apresentação e infraestrutura.

**A solução (SRP — Princípio da Responsabilidade Única).** Cada responsabilidade fica na sua própria classe:

```python
class Reserva:                      # só os dados e a regra de negócio
    def __init__(self, hospede, diarias, valor_diaria):
        self.hospede = hospede
        self.diarias = diarias
        self.valor_diaria = valor_diaria
    def total(self):
        return self.diarias * self.valor_diaria


class ReciboFormatter:              # só a apresentação
    def formatar(self, reserva):
        return (f"RECIBO\n{reserva.hospede}\n"
                f"{reserva.diarias} diarias\nTotal: R$ {reserva.total()}")


class ArquivoRepository:            # só a persistência
    def salvar(self, texto, caminho):
        with open(caminho, "w") as f:
            f.write(texto)
```

Cada classe agora tem **um só motivo para mudar**.

---

## A tarefa

1. Separe a `Reserva` "faz-tudo" em três classes, como acima: `Reserva`, `ReciboFormatter`, `ArquivoRepository`.

2. Escreva um teste (ou um trecho que rode) mostrando que o recibo formatado é **idêntico** ao da versão original — a prova de que a refatoração foi segura.

3. Escreva **duas linhas** de comentário dizendo qual responsabilidade é de cada classe.

---

## Como entregar

- Um arquivo **`.py`** com as três classes e a demonstração do recibo idêntico.
- Entregue no **Teams**, no Módulo da Aula 06.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| As três responsabilidades estão separadas em três classes | 4 |
| O recibo formatado é idêntico ao da versão original | 3 |
| Cada classe tem de fato **um só motivo para mudar** (sem sobre-separar) | 2 |
| O código roda sem erro | 1 |

> ⚠️ **Cuidado com o exagero.** SRP não é "uma classe por método". Se você criar dez classes minúsculas, errou o critério tanto quanto quem deixa tudo junto. A unidade é a **responsabilidade**, não o método.

---

## Uso de IA

**Nível 2 — permitido com declaração.** Pode usar para destravar; declare trechos acima de 5 linhas; saiba explicar.

---

*Homework 06a — ILP-037 — FATEC Olímpia — 2026/2*

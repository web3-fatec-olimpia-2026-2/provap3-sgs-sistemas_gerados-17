# 📝 Homework 04a — Sobrescreva os métodos

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Individual · Prazo: quarta-feira, 03/09, 23h59 · 10 pontos**

---

## O que você precisa saber

Este homework termina o laboratório da aula. Se você fez o laboratório, já sabe o caminho. Se faltou, este arquivo tem tudo.

**A ideia: polimorfismo.** Um subtipo pode **herdar** de uma classe e, ao mesmo tempo, **reescrever** um método herdado para se comportar do seu jeito. Reescrever um método herdado chama-se **sobrescrever** (override).

Veja: um `Quarto` tem um preço padrão. A `Suite` é-um `Quarto`, mas responde um preço diferente:

```python
class Quarto:
    def __init__(self, numero):
        self.numero = numero
    def descricao(self):
        return "Quarto comum"
    def preco_noite(self):
        return 200

class Suite(Quarto):          # herda de Quarto
    def descricao(self):       # SOBRESCREVE: mesmo nome, outra resposta
        return "Suite"
    def preco_noite(self):
        return 500
```

E então uma função consegue tratar qualquer quarto sem saber o tipo:

```python
def imprimir_diaria(quarto):
    return f"{quarto.descricao()}: R$ {quarto.preco_noite()}"
```

`imprimir_diaria` funciona com `Quarto`, com `Suite`, com qualquer categoria — cada uma responde a seu modo. **Isso é polimorfismo.**

---

## A tarefa

Partindo da classe `Quarto` acima (ou de uma estrutura sua parecida), crie **dois subtipos que sobrescrevem os métodos**:

1. **`Presidencial`** — é-um `Quarto`, mas `descricao()` devolve `"Quarto presidencial"` e `preco_noite()` devolve `1200`.
2. **Um terceiro tipo à sua escolha** — um `Chale`, um `Bangalo`, o que quiser — com a própria descrição e o próprio preço.

Depois, escreva um trecho que crie uma **lista** com os vários tipos e passe todos pela função `imprimir_diaria`, num laço. Mostre que a mesma função trata todos.

---

## Como entregar

- Um arquivo **`.py`** com as classes e o laço que prova o polimorfismo.
- Se você tem os testes do laboratório passando, mande junto.
- Entregue no **Teams**, no Módulo da Aula 04.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| Os subtipos herdam de `Quarto` e **sobrescrevem** os dois métodos | 4 |
| A função `imprimir_diaria` trata todos os tipos sem `if` de tipo | 3 |
| O laço demonstra os vários tipos passando pela mesma função | 2 |
| O código roda sem erro | 1 |

---

## Uso de IA

**Nível 2 — permitido com declaração.** Pode usar para destravar; declare trechos acima de 5 linhas; saiba explicar cada um.

---

*Homework 04a — ILP-037 — FATEC Olímpia — 2026/2*

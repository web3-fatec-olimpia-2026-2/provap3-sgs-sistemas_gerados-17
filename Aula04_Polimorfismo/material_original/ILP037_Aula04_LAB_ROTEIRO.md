# 🔬 Laboratório — Aula 04 · Polimorfismo

**ILP-037 · Muitos quartos, uma função · ~30 min**

> Você vai criar dois tipos de quarto — Suíte e Presidencial — que **herdam** de Quarto mas **respondem de forma diferente** aos mesmos métodos. Depois vai ver uma única função tratar os três. Isso é **polimorfismo**.
>
> **Importante:** este laboratório é em **Python puro**, com os exemplos do professor. **Não** é no projeto Django da sua equipe — o Python de ILP e o Python de Web III são mundos separados. Aqui a gente aprende o conceito; no homework, você aplica no seu projeto.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Ambiente *(3 min)*

🖥️ Na pasta do laboratório:
```bash
ls
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```
✅ Você vê `quartos.py`, `tests/`, `pytest.ini`, e o `(.venv)` na linha.

---

## PASSO 1 — Veja o que já existe e o alvo *(5 min)*

🖥️ Rode os testes:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: erro de importação** — as classes `Suite` e `Presidencial` ainda não existem. É a sua tarefa criá-las.

📝 Abra `quartos.py`. Repare em duas coisas que **já estão prontas**:
- a classe **`Quarto`**, com `descricao()` e `preco_noite()`
- a função **`imprimir_diaria(quarto)`** no fim — ela é o coração da aula, e você **não vai alterá-la**

📝 Abra `tests/test_quartos.py`. Ele é a sua especificação:
- `Suite` deve devolver `"Suite"` e `500`
- `Presidencial` deve devolver `"Quarto presidencial"` e `1200`
- as duas devem **ser-um** Quarto (herança)
- a função `imprimir_diaria` deve tratar os três

---

## PASSO 2 — Entenda o conceito *(4 min)*

**Herança** você já viu: `Suite(Quarto)` faz a Suíte ser-um Quarto.

**Polimorfismo** é o passo seguinte: a Suíte não só herda — ela **reescreve** um método herdado para se comportar do seu jeito. Isso se chama **sobrescrever** (override).

O ganho aparece na função `imprimir_diaria`: ela recebe *qualquer* Quarto e chama `.descricao()` e `.preco_noite()`. Ela **não sabe nem se importa** se é um Quarto comum, uma Suíte ou um Presidencial — cada um responde a seu modo. Uma função, muitos comportamentos.

*Analogia:* na recepção do Resort, o pedido é sempre o mesmo — "qual a diária deste quarto?". Cada categoria de quarto responde com o seu preço. Quem pergunta usa uma frase só; cada quarto responde a sua verdade.

---

## PASSO 3 — Crie a Suíte e a Presidencial *(12 min)*

📝 No `quartos.py`, no lugar indicado, escreva as duas classes:

```python
class Suite(Quarto):
    def descricao(self):
        return "Suite"
    def preco_noite(self):
        return 500


class Presidencial(Quarto):
    def descricao(self):
        return "Quarto presidencial"
    def preco_noite(self):
        return 1200
```

> 💭 Repare: as duas **herdam** de `Quarto` (o `(Quarto)`), então ganham o `__init__` de graça — você não reescreve o construtor. Mas **sobrescrevem** `descricao()` e `preco_noite()`, dando a própria resposta. Herança traz o que é igual; sobrescrever muda o que é diferente.

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: os 5 verdes.**

---

## PASSO 4 — Veja o polimorfismo acontecer *(4 min)*

🖥️ No Python, veja a mesma função tratar os três:
```bash
python3
```
```python
>>> from quartos import Quarto, Suite, Presidencial, imprimir_diaria
>>> quartos = [Quarto(101), Suite(201), Presidencial(301)]
>>> for q in quartos:
...     print(imprimir_diaria(q))
...
Quarto comum: R$ 200
Suite: R$ 500
Quarto presidencial: R$ 1200
```
✅ **Uma lista com três tipos diferentes. Um `for` só. Uma função só.** Cada quarto respondeu a sua diária. Isso é polimorfismo — e é o que deixa o código aberto para crescer: amanhã você cria uma nova categoria de quarto, e a `imprimir_diaria` funciona com ela sem mudar uma linha. Saia com `exit()`.

---

## ✅ Você firmou este lab quando

- [ ] Os 5 testes estão verdes
- [ ] Você entende que `imprimir_diaria` **não muda** para tratar um tipo novo
- [ ] Você sabe a diferença entre **herdar** (ganhar o que é igual) e **sobrescrever** (mudar o que é diferente)

**Travou?** Assista ao vídeo de resolução deste lab no Teams.

---

## ⭐ Desafio (se sobrar tempo)

📝 Crie uma quarta categoria — `Chale(Quarto)` — com a descrição e o preço que você quiser. Depois, adicione um `Chale` à lista do Passo 4 e rode de novo. **Repare que a `imprimir_diaria` funciona com ele sem você ter mudado a função.** Esse é o poder do polimorfismo: código aberto para o novo.

---

*Laboratório — Aula 04 — ILP-037 — FATEC Olímpia — 2026/2*

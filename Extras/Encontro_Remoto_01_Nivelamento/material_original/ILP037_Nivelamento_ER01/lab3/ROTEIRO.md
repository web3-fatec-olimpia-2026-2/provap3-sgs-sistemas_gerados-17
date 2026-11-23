# 🔬 Laboratório 3 — Herança: o Hóspede VIP

**ILP-037 · Nivelamento (ER01) · ~25 min · sem nota, sem prazo**

> Terceiro e último laboratório. Você vai criar um **HospedeVIP** que **é-um** Hóspede, com um benefício a mais. É a introdução a herança — o tema que a próxima sexta aprofunda.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Ambiente *(2 min)*

🖥️ Na pasta `lab3`:
```bash
ls
python3 -m venv .venv && source .venv/bin/activate && pip install pytest
```
✅ `(.venv)` na linha.

---

## PASSO 1 — Veja o alvo *(5 min)*

🖥️ Rode os testes:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: erro de importação** — a classe `HospedeVIP` ainda não existe. É a sua tarefa.

📝 Abra `hospede.py`. O `Hospede` está pronto e protegido (Labs 1 e 2). Abra `tests/test_hospede.py` e veja o que o `HospedeVIP` precisa:
- **ser um** Hospede (`isinstance(v, Hospede)` é `True`)
- **herdar** nome, documento e o método `fazer_check_in`
- ter um atributo **novo**: `pontos`
- **herdar** também a proteção da idade

---

## PASSO 2 — Entenda o conceito *(5 min)*

Um `HospedeVIP` é um Hóspede com mais coisas. Em vez de **copiar** toda a classe `Hospede` e acrescentar os pontos (o que duplicaria o código), você usa **herança**:

```python
class HospedeVIP(Hospede):     # o (Hospede) diz: "VIP é-um Hospede"
```

Isso faz o VIP **herdar** tudo que o Hóspede tem — nome, documento, idade protegida, `fazer_check_in` — de graça. Você só acrescenta o que é dele: os pontos.

O **`super()`** é a peça que reaproveita o construtor do Hóspede:
```python
super().__init__(nome, documento, idade)   # monta a parte "Hospede"
```

*Analogia:* a suíte é uma categoria de quarto — é um quarto, com mais. Não se reescreve o quarto; herda-se.

---

## PASSO 3 — Crie o HospedeVIP *(10 min)*

📝 No fim do `hospede.py`, no lugar indicado, escreva:

```python
class HospedeVIP(Hospede):
    def __init__(self, nome, documento, idade, pontos):
        super().__init__(nome, documento, idade)
        self.pontos = pontos
```

**Entenda:**
- `class HospedeVIP(Hospede):` — o `(Hospede)` estabelece a herança: VIP **é-um** Hóspede.
- `super().__init__(...)` — chama o construtor do Hóspede, que monta nome, documento e idade (com a proteção).
- `self.pontos = pontos` — a única coisa **nova** do VIP.

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: os 5 verdes.**

---

## PASSO 4 — Prove no terminal *(3 min)*

🖥️
```bash
python3
```
```python
>>> from hospede import HospedeVIP, Hospede
>>> v = HospedeVIP("Ana", "123", 30, 500)
>>> v.nome              # herdado
'Ana'
>>> v.pontos            # proprio do VIP
500
>>> v.fazer_check_in()  # metodo herdado
>>> v.hospedado
True
>>> isinstance(v, Hospede)   # o VIP E-UM Hospede
True
```
✅ Repare: o VIP usa `fazer_check_in`, que você **nunca escreveu de novo** — ele herdou. Saia com `exit()`.

---

## ✅ Você firmou este lab quando

- [ ] Os 5 testes estão verdes
- [ ] Você entende por que `isinstance(v, Hospede)` é `True` (o VIP **é-um** Hóspede)
- [ ] Você sabe dizer o que o `super()` fez

**Travou?** Vídeo de resolução do Lab 3 no Teams.

---

## 🎉 Você concluiu o nivelamento

Nos três laboratórios você firmou:
1. **OO base** — classe, objeto, atributo, método, `self`
2. **Encapsulamento** — proteger um dado com `@property` e `setter`
3. **Herança** — criar um tipo mais específico com `class Filho(Pai)` e `super()`

É a base inteira da disciplina até aqui. Na próxima sexta (28/08), a gente aprofunda herança e polimorfismo — e você chega pronto.

---

*Laboratório 3 — Nivelamento ER01 — ILP-037 — FATEC Olímpia — 2026/2*

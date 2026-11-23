# 🔬 Laboratório 1 — Orientação a Objetos do zero

**ILP-037 · Nivelamento (ER01) · ~25 min · sem nota, sem prazo**

> Este é o primeiro dos três laboratórios do nivelamento. Aqui você **constrói uma classe do zero** e firma o que é objeto, atributo, método e `self`. Se você travou em OO nas aulas, comece por aqui, com calma.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Prepare o ambiente *(3 min)*

🖥️ Na pasta `lab1`:
```bash
ls
```
✅ Você vê `hospede.py`, `tests/`, `pytest.ini`.

🖥️ Ambiente e pytest:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
```
✅ Confirme o `(.venv)` na linha.

---

## PASSO 1 — Veja o alvo *(4 min)*

🖥️ Rode os testes antes de escrever nada:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: erro de importação** (`ModuleNotFoundError` ou similar). É o certo — a classe `Hospede` ainda não existe. Você vai criá-la.

📝 Abra `tests/test_hospede.py`. **Ele é a sua especificação** — diz o que o `Hospede` precisa fazer:
- criar um hóspede com **nome** e **documento**
- começar **sem check-in** (`hospedado == False`)
- ter um método **`fazer_check_in()`** que muda isso para `True`
- dois hóspedes são **independentes** (check-in de um não afeta o outro)

---

## PASSO 2 — Escreva a classe *(12 min)*

📝 No `hospede.py`, apague o comentário e escreva:

```python
class Hospede:
    def __init__(self, nome, documento):
        self.nome = nome
        self.documento = documento
        self.hospedado = False

    def fazer_check_in(self):
        self.hospedado = True
```

**Entenda cada linha** (é o coração de OO):
- `class Hospede:` — a **classe**, o molde. Existe uma vez, no código.
- `def __init__(self, ...)` — o **construtor**: roda quando um hóspede nasce.
- `self` — é **o próprio objeto**. `self.nome = nome` guarda o nome *naquele* hóspede.
- `self.hospedado = False` — todo hóspede **começa** sem check-in.
- `def fazer_check_in(self):` — um **método**: uma ação que o hóspede sabe fazer.

---

## PASSO 3 — Veja passar *(4 min)*

🖥️ Rode de novo:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 4 verdes.**

🖥️ Prove no Python que dois hóspedes são independentes:
```bash
python3
```
```python
>>> from hospede import Hospede
>>> ana = Hospede("Ana", "123")
>>> bruno = Hospede("Bruno", "456")
>>> ana.fazer_check_in()
>>> ana.hospedado
True
>>> bruno.hospedado
False
```
✅ A Ana fez check-in, o Bruno não. **Cada objeto tem o próprio estado.** Esse é o ponto mais importante de OO. Saia com `exit()`.

---

## ✅ Você firmou este lab quando

- [ ] Os 4 testes estão verdes
- [ ] Você sabe dizer, com suas palavras, a diferença entre a **classe** `Hospede` e o **objeto** `ana`
- [ ] Você entende por que o check-in da Ana não mexeu no Bruno

**Travou?** Assista ao vídeo de resolução do Lab 1 no Teams. Ele constrói tudo isto passo a passo.

Quando terminar, siga para o **Lab 2**.

---

*Laboratório 1 — Nivelamento ER01 — ILP-037 — FATEC Olímpia — 2026/2*

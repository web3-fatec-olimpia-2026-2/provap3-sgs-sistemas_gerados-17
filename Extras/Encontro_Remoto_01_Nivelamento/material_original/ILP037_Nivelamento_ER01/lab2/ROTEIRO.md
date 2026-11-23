# 🔬 Laboratório 2 — Encapsulamento: proteja a idade

**ILP-037 · Nivelamento (ER01) · ~25 min · sem nota, sem prazo**

> Segundo laboratório. Agora que o `Hospede` existe, você vai **protegê-lo** — impedir que a idade receba um valor absurdo. É a "mão na massa" de encapsulamento, com `@property` e `setter`.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Ambiente *(2 min)*

🖥️ Na pasta `lab2`:
```bash
ls
python3 -m venv .venv && source .venv/bin/activate && pip install pytest
```
✅ `(.venv)` na linha, e você vê `hospede.py`, `tests/`, `pytest.ini`.

---

## PASSO 1 — Veja o ponto de partida *(5 min)*

🖥️ Rode os testes:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 3 passam, 1 falha.**
- ✅ cria hóspede com idade — passa
- ✅ check-in continua funcionando — passa
- ✅ idade zero é válida (um bebê de colo) — passa
- ❌ **idade negativa levanta erro — falha** (`DID NOT RAISE`)

Esse **um vermelho é a sua tarefa**: hoje a idade aceita `-5` sem reclamar. Você vai barrar isso.

📝 Abra `hospede.py`. O `Hospede` está pronto, mas a **idade é guardada direto**, sem proteção. Repare que **não há** `@property` para ela ainda.

---

## PASSO 2 — Entenda o conceito *(4 min)*

Um atributo comum é **público**: qualquer código escreve qualquer coisa nele. `h.idade = -5` passa.

**Encapsulamento** faz o objeto **proteger o próprio dado**. Em Python, a ferramenta é a `@property` com `setter`:
- `@property` → o jeito de **ler** `h.idade`
- `@idade.setter` → o jeito de **escrever**, que **valida antes** de guardar

*Analogia:* é o cofre do quarto — o hóspede usa, mas não mexe na fechadura. Um atributo público é um cofre com a porta encostada.

---

## PASSO 3 — Proteja a idade *(10 min)*

📝 No `hospede.py`, no lugar indicado pelo comentário, acrescente:

```python
    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, valor):
        if valor < 0:
            raise ValueError("idade nao pode ser negativa")
        self._idade = valor
```

> 💭 Repare no `self._idade` com **sublinhado** — é o dado interno, guardado de verdade. O `@property` lê ele; o `setter` valida antes de escrever nele.

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: os 4 verdes.**

---

## PASSO 4 — Prove no terminal *(2 min)*

🖥️
```bash
python3
```
```python
>>> from hospede import Hospede
>>> h = Hospede("Ana", "123", 30)
>>> h.idade
30
>>> h.idade = -5      # deve dar erro
```
✅ A última linha levanta `ValueError: idade nao pode ser negativa`. Saia com `exit()`.

---

## ✅ Você firmou este lab quando

- [ ] Os 4 testes estão verdes
- [ ] Você entende por que **zero é válido** (bebê) mas **negativo não é**
- [ ] Você sabe explicar o que o `setter` faz que um atributo comum não faz

**Travou?** Vídeo de resolução do Lab 2 no Teams.

Quando terminar, siga para o **Lab 3**.

---

*Laboratório 2 — Nivelamento ER01 — ILP-037 — FATEC Olímpia — 2026/2*

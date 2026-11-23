# 🔬 Laboratório — Aula 03 · Proteja a capacidade

**ILP-037 · Encapsulamento na sua máquina · ~30 min**

> Você vai pegar a classe `Quarto`, que **já protege a diária**, e **proteger também a capacidade**, com as suas próprias mãos. No fim, quatro testes verdes.
>
> **Marcações:** 🖥️ = terminal · 📝 = editor (VS Code) · ✅ = resultado esperado.
> **Regra do Interlocutor:** travou? Leia o erro **em voz alta** para o grupo. Se não resolver, o Interlocutor chama o professor.

---

## PASSO 0 — Confira que está no lugar certo *(3 min)*

🖥️ **No terminal**, dentro da pasta do laboratório:
```bash
ls
```
✅ Você tem que ver: `quarto.py`, `tests/`, `pytest.ini`, `requirements.txt`.
*(Se não vê, use `cd` até a pasta certa. A pasta importa tanto quanto o comando.)*

🖥️ Prepare o ambiente (primeira vez) e instale o pytest:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
✅ Confirme o `(.venv)` no começo da linha. Sem ele, o `pytest` não é encontrado.

---

## PASSO 1 — Veja o ponto de partida *(5 min)*

🖥️ Rode os testes agora, antes de mexer em nada:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 3 passam, 1 falha.**
- ✅ `test_cria_quarto_com_diaria` — passa
- ✅ `test_diaria_negativa_levanta_erro` — passa
- ✅ `test_cria_quarto_com_capacidade` — passa
- ❌ `test_capacidade_zero_levanta_erro` — **falha** (`DID NOT RAISE`)

Esse **um vermelho é a sua tarefa**. Ele diz: "a capacidade aceita zero, e não deveria". Você vai fechar essa porta.

> ⚠️ Se der `ModuleNotFoundError: No module named 'quarto'`, use `python3 -m pytest` (com o `-m`). O arquivo `pytest.ini` já está na pasta e resolve isso.

📝 **No VS Code**, abra `quarto.py` e leia. Repare que a **diária já está protegida** com `@property` e `setter` — ela é o seu modelo. A **capacidade** hoje é guardada direto, sem proteção. É ela que você vai proteger.

📝 Abra `tests/test_quarto.py` e leia o teste que falha. Ele é a sua **especificação**: capacidade 0 tem que levantar `ValueError`.

---

## PASSO 2 — Entenda o que já existe *(3 min)*

Olhe, no `quarto.py`, como a **diária** foi protegida:

```python
@property
def diaria(self):
    return self._diaria

@diaria.setter
def diaria(self, valor):
    if valor < 0:
        raise ValueError("diaria nao pode ser negativa")
    self._diaria = valor
```

Três peças:
- `self._diaria` — o dado guardado, com **sublinhado** (interno)
- `@property` — o jeito de **ler** `q.diaria`
- `@diaria.setter` — o jeito de **escrever**, que **valida antes**

Você vai fazer o **mesmo** para a capacidade — mudando só a regra.

---

## PASSO 3 — Proteja a capacidade *(12 min)*

📝 No `quarto.py`, no lugar indicado pelo comentário, acrescente a `@property` e o `setter` da capacidade. A regra é: **capacidade mínima é 1**.

```python
    @property
    def capacidade(self):
        return self._capacidade

    @capacidade.setter
    def capacidade(self, valor):
        if valor < 1:
            raise ValueError("capacidade minima e 1")
        self._capacidade = valor
```

> 💭 **Compare com a diária.** A estrutura é idêntica. O que muda é a **regra**: a diária barra o negativo (`< 0`); a capacidade barra qualquer coisa menor que 1 (`< 1`), porque zero também é inválido aqui. A regra vem do negócio, não de um molde.

🖥️ Rode de novo:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado agora: os 4 verdes.** `4 passed`.

> ⚠️ Deu erro? Confira: você escreveu `@capacidade.setter` (e não `@diaria.setter` de novo)? A indentação está com 4 espaços, igual ao resto? Leia a mensagem em voz alta antes de chamar.

---

## PASSO 4 — Prove no terminal *(2 min)*

🖥️ Veja a fechadura funcionando:
```bash
python3
```
```python
>>> from quarto import Quarto
>>> q = Quarto(101, 250, 2)
>>> q.capacidade
2
>>> q.capacidade = 0      # deve dar erro
```
✅ A última linha levanta `ValueError: capacidade minima e 1`. Saia com `exit()`.

---

## ✅ Você terminou quando

- [ ] Os 4 testes estão verdes
- [ ] Você consegue **explicar** por que a capacidade usa `< 1` e a diária usa `< 0`
- [ ] Todos da sua equipe chegaram aos 4 verdes *(a equipe só sinaliza quando todos terminam — quem acabou ajuda quem travou)*

---

## ⭐ Desafio (se sobrar tempo) — o dado calculado

📝 Acrescente uma `@property` chamada `receita_maxima`, que devolve `diaria * capacidade` — o máximo que o quarto rende por noite. Ela é **só-leitura**: **não tem setter**, calcula na hora.

```python
    @property
    def receita_maxima(self):
        return self.diaria * self.capacidade
```

🖥️ No Python: `q = Quarto(101, 250, 2)` → `q.receita_maxima` deve dar `500`.

> É a "conta do check-out" da Aula 02: nunca guardada, sempre somada na hora. Se a diária ou a capacidade mudarem, a receita acompanha sozinha.

---

*Laboratório — Aula 03 — ILP-037 — FATEC Olímpia — 2026/2*

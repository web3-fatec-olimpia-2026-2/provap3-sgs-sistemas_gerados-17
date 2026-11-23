# 🔬 Laboratório 3 — Como ler uma mensagem de erro

**ILP-037 · Nivelamento 2 (19/09) · ~25 min · sem nota, sem prazo**

> O erro do Python **não é seu inimigo** — é a coisa mais útil na tela. Ele diz onde o problema está, em que linha, e o que é. Muita gente entra em pânico e nem lê. Neste lab você aprende a ler qualquer erro em **três passos**, com erros reais do Resort.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## Os três passos para ler qualquer erro

Todo erro do Python, por mais assustador que pareça, se lê assim:

```
PASSO 1 — Vá para a ÚLTIMA linha. É ela que diz O QUE deu errado.
PASSO 2 — Ache o ARQUIVO e a LINHA (o "line N"). É ONDE deu errado.
PASSO 3 — Leia o tipo do erro (NameError, TypeError...). É a PISTA do porquê.
```

O meio da mensagem (o "traceback") é o caminho que o Python percorreu. Você lê **de baixo para cima**: a última linha primeiro.

---

## ERRO 1 — NameError *(8 min)*

🖥️ Rode:
```bash
python3 erro1.py
```
Você vê algo como:
```
  File "erro1.py", line 2, in total_diaria
    return noites * vlaor
                    ^^^^^
NameError: name 'vlaor' is not defined. Did you mean: 'valor'?
```

**Leia nos três passos:**
1. **Última linha:** `NameError: name 'vlaor' is not defined` → o Python não conhece `vlaor`.
2. **Onde:** `line 2` → o problema está na linha 2.
3. **A pista:** `NameError` quer dizer "nome não encontrado" — quase sempre é **erro de digitação** numa variável. E o Python até sugere: `Did you mean: 'valor'?`

📝 Abra `erro1.py`, conserte a linha 2 (`vlaor` → `valor`), salve e rode de novo.
✅ Agora imprime `600`.

---

## ERRO 2 — ValueError *(8 min)*

🖥️ Rode:
```bash
python3 erro2.py
```
```
  File "erro2.py", line 3, in <module>
    total = int(noites) * valor
            ^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'tres'
```

**Nos três passos:**
1. **Última linha:** `ValueError: invalid literal for int()... 'tres'` → o Python tentou virar o texto `"tres"` em número e não conseguiu.
2. **Onde:** `line 3`.
3. **A pista:** `ValueError` = "o valor não serve para esta operação". Aqui, `int("tres")` não dá — "tres" não é um número escrito em dígitos.

📝 Abra `erro2.py`. O problema é que `noites` recebeu o texto `"tres"` em vez de `"3"`. Troque para `"3"`, salve e rode.
✅ Agora imprime `total: 600`.

---

## ERRO 3 — IndexError *(6 min)*

🖥️ Rode:
```bash
python3 erro3.py
```
```
  File "erro3.py", line 2, in <module>
    print("quarto 4:", quartos[3])
                       ~~~~~~~^^^
IndexError: list index out of range
```

**Nos três passos:**
1. **Última linha:** `IndexError: list index out of range` → você pediu uma posição que não existe na lista.
2. **Onde:** `line 2`.
3. **A pista:** `IndexError` = "índice fora do alcance". A lista tem 3 itens (posições **0, 1, 2**), e você pediu a posição **3**, que não existe. Listas começam no zero.

📝 Abra `erro3.py`. Troque `quartos[3]` por `quartos[2]` (o último item), salve e rode.
✅ Agora imprime o quarto `201`.

---

## ✅ Você firmou este lab quando

- [ ] Você consertou os três erros
- [ ] Você sabe que a **última linha** diz o que deu errado
- [ ] Você sabe achar o **arquivo e a linha** no meio da mensagem
- [ ] Você reconhece: `NameError` (digitação), `ValueError` (valor não serve), `IndexError` (posição não existe)

---

## 🧠 A tabela de bolso dos erros mais comuns

| Erro | O que quase sempre é |
|---|---|
| `NameError` | digitou errado o nome de uma variável |
| `TypeError` | misturou tipos (ex.: somar texto com número) |
| `ValueError` | o valor não serve para a operação (ex.: `int("tres")`) |
| `IndexError` | pediu uma posição que a lista não tem |
| `KeyError` | pediu uma chave que o dicionário não tem |
| `IndentationError` | espaços/tabs inconsistentes |
| `ModuleNotFoundError` | import errado, ou rodou da pasta errada |

**Travou?** O vídeo de resolução do Lab 3 está no Teams.

---

## 🎉 Você concluiu o Nivelamento 2

Você firmou:
1. **SQL na mão** — o que o ORM faz por baixo
2. **Git além do commit** — branch e resolução de conflito
3. **Ler um erro** — em três passos, sem pânico

São as três bases que a Unidade 3 (arquitetura, ORM) vai pedir. Bom trabalho.

---

*Laboratório 3 — Nivelamento 2 — ILP-037 — FATEC Olímpia — 2026/2*

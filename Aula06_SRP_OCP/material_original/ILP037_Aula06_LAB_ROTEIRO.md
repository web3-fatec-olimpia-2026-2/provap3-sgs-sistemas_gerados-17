# 🔬 Laboratório — Aula 06 · Uma classe, uma responsabilidade (SRP)

**ILP-037 · Separar responsabilidades · ~30 min**

> Você vai pegar uma classe `Reserva` que **faz coisas demais** — calcula o total, formata o recibo e salva em arquivo — e separar cada responsabilidade na sua própria classe. Isso é o **SRP** (Princípio da Responsabilidade Única). No fim, o recibo continua idêntico, mas o design fica limpo.
>
> **O que torna este lab importante:** o código **já funciona** no começo. Você não conserta um bug — melhora o design sem mudar o comportamento. Os testes provam que você não quebrou nada. É a mesma refatoração segura da Aula 05, agora guiada por um princípio.
>
> **Python puro, não Django.** Exemplos do professor.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Ambiente *(3 min)*

🖥️ Na pasta do laboratório:
```bash
ls
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```
✅ Você vê `recibo.py`, `tests/`, `pytest.ini`, e o `(.venv)` na linha.

---

## PASSO 1 — Veja o *smell* *(6 min)*

🖥️ Rode os testes:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 1 verde, 1 vermelho.**
- ✅ `test_total` — passa (a regra de negócio já está certa)
- ❌ `test_recibo_formatado` — falha (`ReciboFormatter` ainda não existe)

📝 Abra `recibo.py`. Olhe a classe `Reserva`. Ela faz **três coisas diferentes**:
1. `total()` — calcula o valor (**regra de negócio**)
2. `formatar_recibo()` — monta o texto (**apresentação**)
3. `salvar_em_arquivo()` — grava no disco (**infraestrutura**)

**O *smell*:** essa classe tem **três motivos para mudar**. Se o layout do recibo mudar, você mexe nela. Se a forma de salvar mudar (banco em vez de arquivo), você mexe nela. Se a regra do total mudar, você mexe nela. Três responsabilidades misturadas num lugar só.

> 💭 O SRP diz: **uma classe, uma responsabilidade — um só motivo para mudar.** A `Reserva` deveria cuidar só da reserva; formatar e salvar são trabalho de outras classes.

---

## PASSO 2 — Entenda o alvo *(4 min)*

📝 Leia o teste `test_recibo_formatado` em `tests/test_recibo.py`. Ele espera uma classe `ReciboFormatter` com um método `formatar(reserva)` que devolve o **mesmo texto** de antes. Essa é a sua especificação para a parte da apresentação.

Você vai separar a `Reserva` em três classes:
- **`Reserva`** — só os dados e o `total()`
- **`ReciboFormatter`** — só o `formatar(reserva)`
- **`ArquivoRepository`** — só o `salvar(texto, caminho)`

---

## PASSO 3 — Separe as responsabilidades *(12 min)*

📝 Reescreva `recibo.py` com as três classes:

```python
class Reserva:
    def __init__(self, hospede, diarias, valor_diaria):
        self.hospede = hospede
        self.diarias = diarias
        self.valor_diaria = valor_diaria

    def total(self):
        return self.diarias * self.valor_diaria


class ReciboFormatter:
    def formatar(self, reserva):
        return (f"RECIBO\n{reserva.hospede}\n"
                f"{reserva.diarias} diarias\nTotal: R$ {reserva.total()}")


class ArquivoRepository:
    def salvar(self, texto, caminho):
        with open(caminho, "w") as f:
            f.write(texto)
```

> 💭 Repare no que mudou: o `ReciboFormatter` **recebe** a reserva e lê os dados dela — não precisa ser parte da `Reserva`. Cada classe agora tem um só motivo para mudar. Mudou o layout? Mexe só no formatter. Mudou o destino? Mexe só no repository. A `Reserva` fica em paz.

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: os 2 verdes.** O recibo é idêntico ao de antes — você mudou a **estrutura**, não o **comportamento**.

---

## PASSO 4 — Junte as peças no terminal *(5 min)*

🖥️ Veja as três classes colaborando:
```bash
python3
```
```python
>>> from recibo import Reserva, ReciboFormatter, ArquivoRepository
>>> r = Reserva("Ana Souza", 3, 200)
>>> texto = ReciboFormatter().formatar(r)
>>> print(texto)
RECIBO
Ana Souza
3 diarias
Total: R$ 600
>>> ArquivoRepository().salvar(texto, "recibo_ana.txt")
```
✅ Cada classe fez a sua parte: a `Reserva` sabe o total, o formatter monta o texto, o repository salva. Três responsabilidades, três classes, colaborando. Saia com `exit()`.

---

## ✅ Você firmou este lab quando

- [ ] Os 2 testes estão verdes
- [ ] Cada classe tem **um só motivo para mudar**
- [ ] Você sabe dizer qual responsabilidade é de cada classe
- [ ] Você entende por que o recibo idêntico prova que a refatoração foi segura

---

## 🔗 SRP e OCP — os dois princípios da noite

Você acabou de aplicar o **SRP**: separar responsabilidades. O outro princípio de hoje, o **OCP** (Aberto/Fechado), você já aplicou na **Aula 05**, sem saber o nome:

> Quando você criou uma `TarifaVIP` nova **sem tocar na classe `Reserva`**, isso foi OCP: o código ficou **aberto para estender** (novas tarifas) e **fechado para modificação** (a `Reserva` não muda). O padrão Strategy **é** o OCP na prática.

Os princípios não são teoria nova — eles **dão nome** ao que você já vem fazendo bem.

---

*Laboratório — Aula 06 — ILP-037 — FATEC Olímpia — 2026/2*

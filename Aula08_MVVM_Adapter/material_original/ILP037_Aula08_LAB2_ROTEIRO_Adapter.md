# 🧪 Roteiro de Laboratório 2 — Adapter
### ILP-037 · Aula 08 · Resort de Olímpia · Python puro · ~30 min

> **Objetivo:** fazer um driver de banco incompatível (`ClienteNeon`) caber na interface que o
> sistema já espera (`salvar`/`buscar`), sem mexer no cliente nem no serviço — construindo um
> **Adapter**.
>
> **Pacote do aluno:** `ILP037_Laboratorio_Aula08_Lab2_Adapter.zip`
> **Solução do professor (não distribuir):** `SOLUCAO_PROFESSOR_Aula08_Lab2_Adapter.py`

---

## Contexto (vem da segunda-feira de Web III)

O projeto migrou de **SQLite** para **PostgreSQL na nuvem (Neon)**. O driver novo resolve a
mesma coisa — gravar e buscar reserva — mas fala outra língua:

| O sistema espera (interface antiga) | O `ClienteNeon` oferece |
|---|---|
| `repo.salvar(reserva)` → devolve `int` (id) | `cliente.execute("INSERT_RESERVA", dados)` → devolve `{"ticket": n}` |
| `repo.buscar(id)` → devolve `dict` ou `None` | `cliente.fetch_one(chave)` → devolve `{"found": True, "row": {...}}` ou `None` |

A peça é a certa. O **encaixe** é o errado.

---

## Antes de começar

**🖥️ terminal:**
```
unzip ILP037_Laboratorio_Aula08_Lab2_Adapter.zip
cd ILP037_Lab2_Adapter
python3 -m pytest -v
```
**Resultado esperado:** **alguns verdes, alguns vermelhos**. O `NeonReservaAdapter` está vazio,
então os testes que dependem dele falham. (Um ou outro passa por acaso — por exemplo, "buscar
inexistente devolve None" passa porque um método vazio devolve `None`. Não se iluda: isso cai
no próximo passo.)

---

## O "antes" — o cheiro

**📝 VS Code** — abra `reservas.py` e desça até `ReservaService`. Olhe o `confirmar()`: um
`if self.usa_neon`. Se é Neon, chama `execute` e lê `["ticket"]`; senão, `salvar`. **Cada
método novo vai repetir esse if.** A regra de negócio passou a conhecer dois bancos. É isso que
o Adapter elimina.

---

## Passo 1 — Guardar o cliente no Adapter

**📝 VS Code** — complete o `__init__` do `NeonReservaAdapter`:

```python
    def __init__(self, cliente):
        self._cliente = cliente
```

**🖥️ terminal:**
```
python3 -m pytest -v -k "e_um_reserva_repository"
```
**Resultado esperado:** `test_adapter_e_um_reserva_repository` verde (ele já era, por herança —
confirma que o adaptador **é um** `ReservaRepository`).

---

## Passo 2 — Traduzir o `salvar`

**📝 VS Code** — o sistema chama `salvar`; por dentro, traduza para o `execute` do Neon e
**desembrulhe** o formato de resposta:

```python
    def salvar(self, reserva):
        resposta = self._cliente.execute("INSERT_RESERVA", reserva)
        return int(resposta["ticket"])     # {'ticket': n}  ->  n
```

**🖥️ terminal:**
```
python3 -m pytest -v -k "salvar"
```
**Resultado esperado:** `test_adapter_salvar_devolve_id_inteiro` verde.

> **Leia o que você fez:** quem chama `salvar` não faz ideia de que lá dentro virou `execute`.
> Essa é a tradução do Adapter.

---

## Passo 3 — Traduzir o `buscar`

**📝 VS Code:**

```python
    def buscar(self, reserva_id):
        resposta = self._cliente.fetch_one(reserva_id)
        if resposta is None:
            return None
        return resposta["row"]             # {'found':True,'row':{...}} -> {...}
```

**🖥️ terminal — rode tudo:**
```
python3 -m pytest -v
```
**Resultado esperado:** **7 verdes**.

---

## Passo 4 — A prova: substituibilidade

**🖥️ terminal** — rode o teste parametrizado:
```
python3 -m pytest -v -k "qualquer_repo"
```
Repare que ele roda **duas vezes**: uma com `local`, outra com `neon_adapter`. O **mesmo** teste,
o **mesmo** `assert`, para os dois bancos. Para o serviço, eles viraram o mesmo tipo de coisa.

> É por isso que o `if usa_neon` some: o serviço passa a receber **um** `ReservaRepository` e
> nunca mais pergunta qual banco é. Trocar de banco = trocar o objeto injetado.

---

## ✅ Pronto quando...
- [ ] `python3 -m pytest` mostra **7 passed**
- [ ] o `test_qualquer_repo_salva_e_busca_igual` passa nos **dois** ids (`local` e `neon_adapter`)
- [ ] você consegue apontar, no `salvar`, **onde** está a tradução de formato

---

## Delimitação em Python (o freio)

- **Duck typing dispensa o Adapter formal:** se você controla as duas pontas e as interfaces já
  são parecidas, qualquer objeto com os métodos certos serve — não precisa de classe Adapter.
- **O Adapter se justifica** quando o objeto adaptado é **código de terceiro** cuja assinatura
  você **não pode mudar**: um driver de banco (o Neon), uma biblioteca de pagamento, uma API
  externa. Foi o caso real de vocês.
- **Não envelope o que você mesmo escreveu** só para "ficar bonito". Adapte o que não controla.

*Fonte da delimitação: GIRIDHAR, Aprendendo Padrões de Projeto em Python. Ficha formal do
padrão (intenção, participantes, consequências): GAMMA et al., Padrões de Projetos.*

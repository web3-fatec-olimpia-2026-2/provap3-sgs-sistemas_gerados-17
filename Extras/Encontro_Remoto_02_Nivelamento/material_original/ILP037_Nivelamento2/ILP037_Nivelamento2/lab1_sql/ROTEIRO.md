# 🔬 Laboratório 1 — SQL na mão, antes do ORM

**ILP-037 · Nivelamento 2 (19/09) · ~30 min · sem nota, sem prazo**

> Antes do Django fazer as consultas por você (o ORM), vale entender o que ele faz por baixo: **SQL**. Aqui você escreve consultas na mão, num banco de verdade do Resort — sem instalar nada, porque o SQLite já vem dentro do Python.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Criar o banco *(3 min)*

O banco vem pronto para você criar com um comando. Na pasta `lab1_sql`:

🖥️ **No terminal:**
```bash
python3 criar_banco.py
```
✅ Aparece: `Banco resort.db criado: 4 quartos, 5 reservas.`

Isso criou um arquivo `resort.db` com duas tabelas:

```
quarto:  id · numero · categoria · diaria
reserva: id · hospede · quarto_id · noites
```

> 💡 A tabela `reserva` tem um `quarto_id` que aponta para o `id` de um `quarto`. Isso é uma **chave estrangeira** — o elo entre as duas tabelas. É esse elo que o JOIN usa.

---

## PASSO 1 — Ver o banco por dentro *(5 min)*

🖥️ Abra o banco no terminal:
```bash
python3 -c "import sqlite3; con=sqlite3.connect('resort.db'); [print(r) for r in con.execute('SELECT * FROM quarto')]"
```
✅ Você vê os 4 quartos. Repita trocando `quarto` por `reserva` para ver as reservas.

Agora entenda a estrutura de uma consulta SQL:
```sql
SELECT  quais colunas você quer
FROM    qual tabela
WHERE   qual condição (opcional)
```

---

## PASSO 2 — Escrever suas consultas *(15 min)*

📝 **Copie** o arquivo de exemplo:
```bash
cp exemplo_consultas.py minhas_consultas.py
```

📝 Abra `minhas_consultas.py`. Ele tem quatro consultas para você completar. Escreva cada uma como uma string SQL:

- **CONSULTA_1** — Todos os quartos: `numero` e `diaria`. *(já vem pronta de exemplo)*
- **CONSULTA_2** — Só os quartos com `diaria` acima de 300. *(dica: use `WHERE diaria > 300`)*
- **CONSULTA_3** — Quantas reservas existem no total. *(dica: `SELECT COUNT(*) FROM reserva`)*
- **CONSULTA_4** — O nome do hóspede e o número do quarto de cada reserva. *(dica: precisa de JOIN — veja o Passo 3)*

---

## PASSO 3 — O JOIN: juntar duas tabelas *(o alvo)*

A CONSULTA_4 precisa de dados de **duas** tabelas ao mesmo tempo: o `hospede` está em `reserva`, o `numero` está em `quarto`. O **JOIN** junta as duas pelo elo (`quarto_id` = `id`):

```sql
SELECT r.hospede, q.numero
FROM reserva r
JOIN quarto q ON r.quarto_id = q.id
```

Lê-se: "da reserva (apelidada `r`) e do quarto (apelidado `q`), traga o hóspede e o número, juntando onde o `quarto_id` da reserva bate com o `id` do quarto."

> 💡 É exatamente isto que o ORM do Django faz quando você escreve `reserva.quarto.numero`. Ele monta um JOIN por baixo. Entender o SQL é entender o que o ORM esconde.

---

## PASSO 4 — Conferir suas respostas *(5 min)*

🖥️ Rode o verificador:
```bash
python3 verificar.py
```
✅ Ele confere cada consulta e diz **verde** (acertou) ou mostra quantas linhas vieram vs. o esperado. Ajuste e rode de novo até as 4 ficarem verdes.

---

## ✅ Você firmou este lab quando

- [ ] As 4 consultas estão verdes
- [ ] Você entende o que `SELECT`, `FROM` e `WHERE` fazem
- [ ] Você sabe explicar o que um JOIN junta, e por qual elo

**Travou?** O vídeo de resolução do Lab 1 está no Teams.

Quando terminar, siga para o **Lab 2 (Git)**.

---

*Laboratório 1 — Nivelamento 2 — ILP-037 — FATEC Olímpia — 2026/2*

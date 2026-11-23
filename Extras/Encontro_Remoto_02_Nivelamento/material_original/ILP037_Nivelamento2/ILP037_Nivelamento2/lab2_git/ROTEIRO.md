# 🔬 Laboratório 2 — Git além do commit

**ILP-037 · Nivelamento 2 (19/09) · ~30 min · sem nota, sem prazo**

> Você já sabe `add`, `commit`, `push`. Mas quando duas pessoas mexem no mesmo arquivo, aparece um **conflito** — e é aí que muita gente trava e desiste. Neste lab você vai **criar um conflito de propósito** e aprender a resolvê-lo com calma. Depois disso, conflito deixa de assustar.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.
>
> **Este lab é auto-contido:** você cria um repositório local só para praticar. Não mexe no projeto da equipe.

---

## PASSO 0 — Criar um repositório de treino *(3 min)*

🖥️ Na pasta `lab2_git`, rode o preparador:
```bash
python3 preparar.py
```
✅ Ele cria uma pasta `treino/` com um repositório Git já iniciado e um arquivo `categorias.txt`. Entre nela:
```bash
cd treino
git log --oneline
```
✅ Você vê o primeiro commit.

---

## PASSO 1 — O que é uma branch *(5 min)*

Uma **branch** é uma linha de trabalho paralela. Você cria uma, faz mudanças nela, e o `main` continua intacto até você juntar (`merge`).

🖥️ Crie uma branch e entre nela:
```bash
git checkout -b nova-categoria
```
✅ `git status` mostra que você está na branch `nova-categoria`.

📝 Abra `categorias.txt`. Ele tem uma linha `- [A DEFINIR]`. Troque por `- suite`:
```
categorias do resort:
- comum
- suite
```
🖥️ Salve e commite:
```bash
git add categorias.txt
git commit -m "define suite"
```

---

## PASSO 2 — Provocar o conflito *(5 min)*

Agora volte para o `main` e altere a **mesma linha** de outro jeito — é isso que gera o conflito.

🖥️
```bash
git checkout main
```
📝 Abra `categorias.txt` (repare: aqui ainda está `- [A DEFINIR]`, porque a mudança da suite ficou na outra branch). Troque a mesma linha por `- presidencial`:
```
categorias do resort:
- comum
- presidencial
```
🖥️ Commite:
```bash
git add categorias.txt
git commit -m "define presidencial"
```

Agora as duas branches definiram a mesma linha de formas diferentes. Junte-as:
```bash
git merge nova-categoria
```
⚠️ **Esperado:** `CONFLICT (content): Merge conflict in categorias.txt`. **Isso é normal e esperado** — não é erro seu. O Git está dizendo: "vocês dois mudaram a mesma linha, eu não sei qual manter. Decidam vocês."

---

## PASSO 3 — Ler e resolver o conflito *(12 min)*

📝 Abra `categorias.txt`. O Git marcou o conflito assim:
```
categorias do resort:
- comum
<<<<<<< HEAD
- presidencial
=======
- suite
>>>>>>> nova-categoria
```

**Como ler isso:**
- Entre `<<<<<<< HEAD` e `=======` está o que **você tinha no main** (`- presidencial`).
- Entre `=======` e `>>>>>>>` está o que **vinha da outra branch** (`- suite`).

**Resolver = decidir o que fica, e apagar as marcas.** Neste caso, queremos as duas categorias. Deixe o arquivo assim, **sem nenhuma marca** `<<<`, `===`, `>>>`:
```
categorias do resort:
- comum
- presidencial
- suite
```

🖥️ Salve, marque como resolvido e finalize:
```bash
git add categorias.txt
git commit -m "resolve conflito: mantem presidencial e suite"
```
✅ `git status` mostra tudo limpo. `git log --oneline` mostra o histórico com o merge.

> 💡 Foi só isso. Conflito não é um bug — é o Git pedindo uma decisão humana. As três marcas dizem "isto de um lado, aquilo do outro"; você escolhe e apaga as marcas.

---

## ✅ Você firmou este lab quando

- [ ] Você criou uma branch, fez um commit nela, e voltou para o main
- [ ] Você provocou um conflito e **entende por que ele apareceu**
- [ ] Você sabe ler as marcas `<<<`, `===`, `>>>` e resolver
- [ ] O `git status` ficou limpo no fim

**Travou?** O vídeo de resolução do Lab 2 está no Teams.

Quando terminar, siga para o **Lab 3 (ler um erro)**.

---

*Laboratório 2 — Nivelamento 2 — ILP-037 — FATEC Olímpia — 2026/2*

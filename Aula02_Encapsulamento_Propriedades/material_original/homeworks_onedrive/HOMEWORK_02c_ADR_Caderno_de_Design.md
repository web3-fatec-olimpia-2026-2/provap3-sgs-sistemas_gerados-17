# 📓 Homework 02c — ADR 001 no Caderno de Design *(da equipe)*

**ILP-037 Técnicas de Programação II · FATEC Olímpia · CST em DSM · 2026/2**
**Da equipe · Uma entrega por equipe · Prazo: domingo, 17/08, 23h59 · 20 pontos**

---

## O que é isto, e por que importa

Ao longo do semestre, a sua equipe vai registrar as **decisões de design** do projeto num documento chamado **Caderno de Design**. Cada decisão importante vira um **ADR** — *Architecture Decision Record*, um "registro de decisão de arquitetura". É um arquivo curto que responde: **qual era o problema, o que decidimos, e por quê.**

Este é o **primeiro ADR** da sua equipe. Ele compõe o **Marco 1** da disciplina, que vale muito na nota final. Comecem leves, mas comecem certo — porque o Caderno cresce um ADR por vez, e este é o tijolo de baixo.

---

## O problema a registrar

No projeto da sua equipe (o mesmo que vocês desenvolvem nas outras disciplinas), procurem no código um **campo que aceita valor inválido hoje**. Exemplos comuns:

- um campo de **preço** que aceita número negativo;
- uma **quantidade** que aceita zero ou negativo onde não deveria;
- uma **data** sem validação;
- um campo de **status** que aceita qualquer texto.

Achem **um** desses. Ele é o assunto do ADR.

> Se vocês ainda não têm código de projeto, usem a classe `Reserva` dos exercícios desta aula como base: o campo `valor_diaria`, que aceitava valor negativo antes de vocês protegerem.

---

## Passo a passo — criar o ADR e enviar

Tudo no terminal, dentro do repositório da equipe.

**1. Abra uma branch para esta mudança:**
```bash
git checkout -b docs/adr-001
```
*(`checkout -b` cria uma branch nova e já entra nela — é o espaço isolado onde vocês fazem a mudança sem mexer no código principal.)*

**2. Crie a pasta e o arquivo:**
```bash
mkdir -p docs/design
```
Crie o arquivo **`docs/design/ADR-001-protecao-de-campo.md`** com esta estrutura (troquem o que está entre colchetes):

```markdown
# ADR 001 — Proteção do campo [nome do campo]

## Contexto
Que campo do nosso projeto aceita valor inválido hoje, e por que isso é um problema?
Exemplo: o campo `preco` aceita número negativo, o que permitiria cadastrar um
produto custando -10 reais.

## Decisão
Como vamos proteger esse campo.
Exemplo: validar com @property e setter, levantando ValueError para valor negativo.

## Alternativa descartada
O que vocês consideraram e NÃO escolheram, e por quê. (Esta seção é a que mais conta —
mostra que vocês pensaram em mais de uma opção.)
Exemplo: validar só no formulário da tela. Descartado porque não protege quem cria o
registro por outros caminhos (pelo shell, pelo admin, por importação).

## Consequência
O que muda por causa dessa decisão. O que fica melhor, e o que custa.
Exemplo: o objeto passa a se proteger sozinho; em troca, o código fica um pouco maior.

## Commit
[o código do commit em que a proteção entrou — vocês preenchem depois do passo 4]
```

**3. Salvem o arquivo. Depois, no terminal:**
```bash
git add docs/design/ADR-001-protecao-de-campo.md
git commit -m "docs: ADR 001 - protege campo contra valor invalido"
git push -u origin docs/adr-001
```

**4. Abram o Pull Request:**
Depois do `push`, o GitHub mostra um link para abrir o *pull request* (PR). Abram o PR. É assim que a mudança é proposta ao projeto principal.

**5. Entreguem:**
O **Relator** da equipe cola o **link do PR** na tarefa do Teams. Uma linha basta.

---

## Onde o ADR deve ficar

Se o repositório da sua equipe já tem um arquivo `docs/decisoes.md` para decisões, vocês podem usar **aquele arquivo** em vez da pasta `docs/design/` — desde que a decisão fique versionada, junto com o código, e rastreável por um commit. **Combinem entre a equipe e sejam consistentes o semestre inteiro:** escolham um lugar e mantenham.

---

## Como será avaliado *(20 pontos)*

| Critério | Pontos |
|---|---|
| A pasta/arquivo existe e está versionada no repositório (há commit e PR) | 5 |
| As **quatro seções** estão preenchidas — não só a primeira | 6 |
| A "alternativa descartada" mostra que a equipe pensou em mais de uma opção | 5 |
| O campo escolhido de fato tinha um problema real de validação | 4 |

---

## Uso de IA nesta tarefa

**Nível 2 — permitido com declaração.** A IA pode ajudar a redigir o texto do ADR ou a lembrar um comando de Git. Mas a **decisão** — qual campo, o que fazer, o que descartar — tem que ser da equipe, e vocês precisam saber defendê-la. A defesa oral do Marco 1 é sem consulta.

---

## Resumo

| | |
|---|---|
| **Quem** | A equipe, uma entrega só |
| **O quê** | Um ADR registrando a proteção de um campo do projeto |
| **Onde** | No repositório, por pull request |
| **Quem entrega** | O Relator cola o link do PR no Teams |
| **Prazo** | **Domingo, 17/08, 23h59** |

---

*Homework 02c — ILP-037 — FATEC Olímpia — 2026/2*

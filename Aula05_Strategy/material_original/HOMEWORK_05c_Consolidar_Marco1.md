# 📓 Homework 05c — Consolidar o Caderno para o Marco 1 *(da equipe)*

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Da equipe · Uma entrega por equipe · Prazo: quarta-feira, 10/09, 23h59 · 20 pontos**

> Este homework **é** a preparação da entrega do Marco 1 (11/09). Fazê-lo bem é entregar bem.

---

## O que é o Marco 1

O Marco 1 avalia a **decisão de design** da sua equipe — não se o código funciona (isso é Web III), mas **por que o código está assim**. O instrumento é o **Caderno de Design**: os ADRs que vocês vêm escrevendo, em `docs/design/`, versionados com o código.

**Fechar o Marco é consolidar o que já existe** — não começar do zero.

---

## A tarefa

**1. Revisar todos os ADRs que a equipe já tem.** Para cada um, confira as cinco seções:

```
Contexto              — qual era o problema
Decisão               — o que fizemos
Alternativa descartada — o que NÃO fizemos, e por quê   ← a que mais conta
Consequência          — o que mudou, o que custou
Commit                — o hash onde a decisão entrou no código
```

**2. Corrigir o erro mais comum: descrever em vez de justificar.**

- **Descrever** (fraco): "Usamos `@property` para proteger o preço."
- **Justificar** (forte): "Escolhemos `@property` em vez de validar só na tela, porque a validação de tela não protege quem cria o registro pelo shell ou pelo admin."

A diferença está na **alternativa descartada** e no **porquê**. Um ADR que só descreve perde nota, mesmo estando "certo".

**3. Acrescentar o ADR da decisão de hoje:** a equipe vai aplicar Strategy em algum ponto do projeto? Onde, ou por que não? Registrem essa decisão como um ADR novo.

**4. Garantir que está tudo no GitHub** — não só na máquina de um integrante. Um `git push`, e conferir no navegador que os arquivos aparecem.

---

## Checklist de fechamento *(o que a banca vai olhar)*

```
[ ] A pasta docs/design/ está no repositório e versionada
[ ] Cada decisão importante virou um ADR
[ ] Cada ADR tem as CINCO seções preenchidas
[ ] A "alternativa descartada" existe em cada ADR
[ ] Os ADRs JUSTIFICAM, não só descrevem
[ ] Cada ADR tem o commit (rastreável)
[ ] Está tudo no GitHub (push feito, conferido)
[ ] Cada integrante sabe defender oralmente cada decisão (arguição sem consulta)
```

---

## Como entregar

1. Commit e push do Caderno consolidado no repositório da equipe.
2. O **Relator** cola no Teams o link da pasta `docs/design/` (ou do commit). Uma linha basta.

---

## Como será avaliado *(20 pontos — compõe o Marco 1)*

| Critério | Pontos |
|---|---|
| Os ADRs existentes estão com as cinco seções preenchidas | 6 |
| As decisões justificam, não só descrevem (a alternativa descartada é real) | 6 |
| O ADR da decisão sobre Strategy foi acrescentado | 4 |
| Está tudo versionado no GitHub, com commits rastreáveis | 4 |

---

## Material de apoio

No Teams: o vídeo **"Como fechar o Marco 1"** e o **checklist em PDF**. Se algum ponto acima ficou confuso, o vídeo mostra num Caderno real.

---

## Uso de IA

**Nível 2 — permitido com declaração.** A IA pode ajudar a redigir o texto dos ADRs, mas a **decisão** é da equipe, e a **defesa oral do Marco 1 é sem consulta**. Um ADR que vocês não sabem defender não vale.

---

*Homework 05c — ILP-037 — FATEC Olímpia — 2026/2*

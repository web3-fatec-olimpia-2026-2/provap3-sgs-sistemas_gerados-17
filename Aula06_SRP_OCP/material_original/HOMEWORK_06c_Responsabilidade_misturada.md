# 📓 Homework 06c — Responsabilidade misturada no projeto *(da equipe · opcional)*

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Da equipe · Opcional (sem nota) · Prazo: quarta-feira, 17/09, 23h59**

> Opcional e sem nota — mas é o tipo de exercício que faz o projeto de vocês melhorar de verdade, e alimenta o próximo marco.

---

## A ideia

Na aula você viu o SRP: uma classe deve ter um só motivo para mudar. Quase todo projeto tem, em algum lugar, uma classe que **faz coisas demais** — uma view que também valida e formata, um model que também envia e-mail, uma função que calcula e salva.

A tarefa é **enxergar** um desses pontos no projeto da equipe e **registrar** a observação. Não precisa separar agora — só reconhecer e anotar.

---

## O que fazer

1. Procurem no projeto da equipe uma classe ou função que acumula **mais de uma responsabilidade**. Exemplos:
   - uma view que busca dados, aplica regra de negócio **e** monta o HTML
   - um model que, além dos dados, também envia notificação
   - uma função que calcula algo **e** grava no banco

2. Registrem no Caderno de Design um ADR curto:

```markdown
# ADR 00X — Responsabilidade misturada em [nome da classe/função]

## Contexto
Qual classe/função acumula responsabilidades demais, e quais são elas?
Ex.: a view lista_reservas busca do banco, calcula o total com desconto e
monta o texto do relatório — três responsabilidades.

## Decisão
Vamos separar agora, ou deixar registrado para depois? E por quê?
Ex.: registrado para o Marco 2 — hoje funciona, e separar agora atrasaria a
Sprint. Mas fica anotado como dívida de design.

## Consequência
O que ganhamos ao separar (quando separarmos), e o custo de deixar como está.
```

---

## Por que vale a pena (mesmo sem nota)

- Alimenta o **Marco 2**: dívidas de design registradas agora viram refatorações justificadas depois.
- Treina o olho para *smells* — a competência central da disciplina.
- Um Caderno que registra o que **ainda não está bom** é mais honesto (e mais valioso) que um que só mostra acertos.

---

## Como entregar

- Commit no repositório da equipe. O Relator cola o link no Teams, se quiser registrar a entrega.

---

## Uso de IA

**Nível 2.** A IA pode ajudar a redigir, mas a observação — qual ponto do projeto — é de vocês.

---

*Homework 06c — ILP-037 — FATEC Olímpia — 2026/2*

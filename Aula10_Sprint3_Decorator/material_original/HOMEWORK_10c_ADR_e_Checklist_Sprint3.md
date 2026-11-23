# Homework 10C — ADR do Decorator + Checklist do Sprint 3
### Da equipe · ILP-037 · Prazo: quarta 12/11, 23h59 · IA nível 1 (livre p/ pesquisa)

Duas entregas da equipe, que já fazem parte do **Sprint 3** e alimentam o **P1** (Caderno de
Design).

---

## Parte 1 — ADR do Decorator (fecha o catálogo de padrões)

Escrevam **um ADR** no Caderno de Design (`/docs/design/`) decidindo se cabe um **Decorator** em
algum ponto do projeto — **com justificativa**.

Procurem um ponto que ganharia com **somar responsabilidades opcionais** a algo: extras de um
pedido/reserva, descontos aplicáveis, formatações encadeadas, um log/auditoria em volta de uma
ação. Um Decorator ajudaria a empilhar essas opções? Ou é só uma lista simples e seria cerimônia?

> **"Não aplicamos" é tão válido quanto "aplicamos"**, desde que justificado. Cuidado com os erros
> típicos: Decorator onde bastaria somar uma lista; e confundir com o `@` de função do Python.

### Modelo de ADR (copie e preencha)
```markdown
# ADR 00X — Decorator em [nome do ponto]

- Data: 2026-11-__
- Status: aceito
- Decisores: [nomes da equipe]

## Contexto
[Onde há variações OPCIONAIS a somar. Cole o caminho do arquivo e 2-3 linhas.]

## Decisão
[APLICAMOS um Decorator / NÃO APLICAMOS — frase clara.]

## Justificativa
[Por quê. Se aplicaram: o que cada decorador acrescenta mantendo a interface, e
 por que empilhar ajuda. Se não: por que não cabia — soma fixa? lista bastaria?
 Amarrem na delimitação em Python (o @ de função é outra coisa).]

## Consequências
[O que muda. Como ficou combinar opcionais; ou o que deixaram como está e por quê.]
```

---

## Parte 2 — Checklist do Sprint 3 preenchido

Preencham o **checklist do Sprint 3** (postado no Teams / `ABERTURA_Sprint3_ILP-037.md`) com o
estado atual da equipe, marcando o que já está feito e o que falta até **04/12**. Ele cobre:
produto, Caderno de Design (todos os ADRs — de Strategy a Decorator), preparação para a **P3
(27/11)** e portfólio (P4).

---

## Critério de aceitação
- [ ] ADR do Decorator commitado em `/docs/design/` (decide e **justifica**)
- [ ] o ADR cita a delimitação (soma fixa → lista; `@` de função ≠ padrão)
- [ ] checklist do Sprint 3 preenchido com o estado real da equipe
- [ ] relator enviou os links no canal da equipe

> Este é o **fecho do catálogo de padrões** do Caderno — a peça central do **P1**. É o que mais
> pesa na média. Caprichem na justificativa, como foi dito desde o Marco 1.

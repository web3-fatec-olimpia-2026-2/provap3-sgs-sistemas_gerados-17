# ADR 005 — Aplicar Strategy na política de cancelamento?

> Homework 05c (da equipe) — modelo do ADR "da decisão de hoje" + checklist do Marco 1.

## Contexto
O sistema tem três políticas de cancelamento de reserva — **flexível** (reembolso total até 24h
antes), **moderada** (50%) e **não reembolsável** (0%) — decididas hoje num `if/elif` dentro de
`Reserva.cancelar()`. O comercial já pediu uma quarta ("feriado": 30% e só até 7 dias antes).

## Decisão
Aplicar **Strategy**: cada política vira uma classe com `calcular_reembolso(reserva, data)`;
a `Reserva` recebe a política e delega. A política nova entra como classe nova.

## Alternativa descartada
- **Manter o `if/elif`**: com a 4ª política, a função passa de 20 linhas e cada mudança reabre
  `Reserva.cancelar()`, já testada. Descartado.
- **Tabela `{politica: percentual}`**: descartada porque as políticas diferem em *prazo* e
  *percentual* (e a de feriado tem regra de data), não cabem em um número.

## Consequência
Política nova = classe nova, `Reserva` intacta; cada política testável isoladamente.
Custo: +4 classes pequenas. **Onde NÃO aplicamos:** taxa de serviço (10% fixo para todos) — sem
variação, Strategy seria cerimônia.

## Commit
`<hash>`

---

## Checklist de fechamento do Marco 1 (o que a banca olha)
- [ ] `docs/design/` no repositório e versionada
- [ ] Cada decisão importante virou um ADR
- [ ] Cada ADR com as **cinco seções**: Contexto · Decisão · Alternativa descartada · Consequência · Commit
- [ ] A alternativa descartada existe e é real
- [ ] Os ADRs **justificam** ("escolhemos X em vez de Y porque…"), não só **descrevem** ("usamos X")
- [ ] Cada ADR aponta o commit
- [ ] Tudo no GitHub (push conferido no navegador)
- [ ] Cada integrante sabe defender cada decisão **sem consulta**

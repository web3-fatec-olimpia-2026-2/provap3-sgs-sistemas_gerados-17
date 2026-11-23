# Homeworks da Aula 08

## 08A — Entregar os dois laboratórios
- Lab 1 MVVM: [`../lab1_mvvm/quartos.py`](../lab1_mvvm/quartos.py) → 8 testes originais + 3 meus.
- Lab 2 Adapter: [`../lab2_adapter/reservas.py`](../lab2_adapter/reservas.py) → 7 testes originais + 5 meus.
- Nenhum teste original foi alterado (só o código de produção).

## 08B — Service × ViewModel (IA vedada — modelo de estudo)

**Modelo (4 linhas):**
O Service tira da tela a regra de negócio, aquilo que é verdade no domínio independente de quem
olha: por exemplo, calcular a diária com desconto de fidelidade ou decidir se o quarto pode ser
reservado. O ViewModel tira da tela a lógica de exibição, como essa verdade aparece para o usuário:
transformar `ocupado=True` em "INDISPONIVEL", trocar o botão por "(ocupado)" ou mostrar 200.0 como
"R$ 200.00". Um responde "o que o sistema faz", o outro "como mostrar" — por isso convivem e o MVVM
não substitui o Service.

**Checklist:** 3–5 linhas · regra de negócio (Service) × lógica de exibição (ViewModel) · exemplo concreto.

## 08C — Dois ADRs (equipe) — modelos

```markdown
# ADR 008 — MVVM na tela de painel de quartos

- Status: aceito

## Contexto
`templates/quartos/painel.html` tem `{% if quarto.ocupado %}INDISPONIVEL{% else %}livre{% endif %}`,
outro `if` para o rótulo do botão e o cálculo de "LOTADO" com `{% with %}`. A decisão de exibição
está espalhada no template e não tem teste.

## Decisão
APLICAMOS um ViewModel de preparação (`PainelQuartosVM`) chamado na view antes do `render`.

## Justificativa
Há decisão de exibição real (rótulo condicional, estado derivado "LOTADO", formatação de preço).
No servidor não há binding, então o ViewModel é só uma classe de preparação — sem "observables"
(delimitação em Python, GIRIDHAR). Ganho: testamos "quando aparece LOTADO" sem renderizar.

## Consequências
Template fica só com `{{ item.status_label }}`. Custo: uma classe a mais. A tela de "contato",
que só mostra dados como estão, continua sem ViewModel (seria cerimônia).
```

```markdown
# ADR 009 — Adapter no acesso ao banco pós-migração Neon

- Status: aceito

## Contexto
Na migração SQLite → PostgreSQL/Neon usamos o próprio ORM do Django: só mudou `DATABASES` em
`settings.py`. Nenhum código nosso chama o driver `psycopg` diretamente.

## Decisão
NÃO APLICAMOS Adapter.

## Justificativa
O ORM já é a camada que esconde o banco — trocar o banco foi trocar configuração, sem `if` de
banco no código. Criar um Adapter envolvendo o que já é uma abstração (e que nós não chamamos
diretamente) seria cerimônia. O Adapter se justificaria se chamássemos um driver/API de terceiro
com interface diferente (ex.: um gateway de pagamento) — fica anotado como candidato.

## Consequências
Nada muda agora. Se surgir integração com serviço externo de interface diferente, reabrimos este ADR.
```

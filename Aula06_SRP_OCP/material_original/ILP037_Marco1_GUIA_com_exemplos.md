# 📐 O que eu quero no Marco 1 — guia com exemplos do Resort
### ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2 · Prof. José Ceron Neto

> **Módulo de apoio à entrega do Marco 1.** Este guia explica, com exemplos do
> projeto do Resort, exatamente o que faz um Caderno de Design tirar nota máxima —
> e o que faz perder nota. Leia antes de entregar. Se depois disto o seu Caderno
> ainda parecer com os exemplos de "nota baixa", é sinal de que falta trabalho.

---

## 1. O que o Marco 1 avalia (e o que NÃO avalia)

O Marco 1 avalia **a decisão de design** da sua equipe — o *porquê* do código,
registrado no Caderno de Design (a pasta `docs/design/` com os ADRs).

| O Marco 1 avalia | O Marco 1 NÃO avalia |
|---|---|
| Se as decisões estão **registradas e justificadas** | Se o código roda (isso é Web III) |
| Se vocês **pensaram em alternativas** | A quantidade de linhas de código |
| Se sabem **defender** cada decisão oralmente | Se o design é "perfeito" |
| Se o Caderno está **versionado no GitHub** | Se vocês usaram muitos padrões |

> A frase que resume tudo: **o Marco não pergunta o que você fez, pergunta por que.**

---

## 2. A estrutura de um ADR — as cinco seções

Vocês já conhecem desde o ADR 001. Todo ADR tem cinco seções:

```
Contexto              — qual era o problema, e por que era um problema
Decisão               — o que vocês decidiram fazer
Alternativa descartada — o que consideraram e NÃO escolheram, e por quê
Consequência          — o que mudou, o que melhorou, o que custou
Commit                — o hash do commit onde a decisão entrou no código
```

**A seção que mais vale:** *Alternativa descartada*. É ela que prova que houve
uma **decisão** — uma escolha entre caminhos — e não só a primeira ideia que
apareceu. Um ADR sem alternativa descartada parece que ninguém decidiu nada.

---

## 3. A rúbrica — como eu vou dar a nota

Cada ADR vale por estes critérios. A nota do Marco 1 é a leitura do conjunto do
Caderno mais a defesa oral.

| Critério | Peso | O que preciso ver |
|---|---|---|
| **Cinco seções preenchidas** | 25% | Nenhum ADR com seção vazia ou "a preencher" |
| **Justifica, não só descreve** | 30% | A Decisão diz *por quê*, não só *o quê* |
| **Alternativa descartada real** | 20% | Uma opção concreta considerada e recusada, com motivo |
| **Rastreabilidade (commit)** | 10% | Cada ADR aponta o commit da mudança |
| **Defesa oral** | 15% | Cada integrante explica uma decisão sem consulta |

### O que ZERA a entrega *(não é sobre qualidade — é sobre existência)*

- Caderno **não versionado no GitHub** (ficou só numa máquina, ou no OneDrive).
- ADRs **todos vazios ou só com Contexto** — começou e não terminou.
- Uso de **IA não declarado** no texto dos ADRs (a política L.D.P.A. vale aqui).
- Ninguém da equipe **sabe defender** o que está escrito (sinal de texto copiado).

---

## 4. Os exemplos — o mesmo ADR, nota máxima vs. nota baixa

Abaixo, a **mesma decisão** do Resort escrita de dois jeitos. Compare e veja em
qual dos dois o seu Caderno se parece.

---

### 📄 Exemplo A — Proteção do campo `valor_diaria`

#### ❌ VERSÃO NOTA BAIXA

```markdown
# ADR 001 — Proteção do valor da diária

## Contexto
O valor da diária precisava ser protegido.

## Decisão
Usamos @property com setter.

## Alternativa descartada
(vazio)

## Consequência
Ficou mais seguro.

## Commit
(a preencher)
```

**Por que perde nota:**
- *Contexto* não diz qual era o risco concreto (uma diária negativa entrando no sistema).
- *Decisão* **descreve** ("usamos @property") sem dizer **por quê** o `@property` e não outra coisa.
- *Alternativa descartada* **vazia** — a seção que mais conta. Parece que não houve decisão.
- *Consequência* vaga: "mais seguro" não diz o que mudou nem o que custou.
- Sem *commit* — não dá para rastrear.

#### ✅ VERSÃO NOTA MÁXIMA

```markdown
# ADR 001 — Proteção do campo valor_diaria

## Contexto
O campo valor_diaria era um atributo público comum: qualquer parte do código
podia gravar qualquer número, inclusive negativo. Numa reserva de teste, um valor
de -50 foi gravado sem o objeto reclamar, o que permitiria uma diária negativa
bagunçar o cálculo do total. A regra "diária nunca é negativa" existia só na
cabeça da equipe, não no código.

## Decisão
Transformamos valor_diaria numa @property com setter que valida antes de gravar:
se o valor for negativo, levanta ValueError. Assim o próprio objeto Reserva
protege o próprio estado — nenhum caminho consegue gravar um valor inválido.

## Alternativa descartada
Consideramos validar apenas na tela de cadastro, deixando o atributo livre.
Descartamos porque a validação de tela só protege quem passa pelo formulário —
quem cria uma reserva pelo shell, por importação ou por um teste escaparia da
regra. A proteção no próprio objeto vale para todos os caminhos.

## Consequência
O objeto Reserva ficou responsável pela própria integridade. Em troca, a classe
ficou um pouco maior (getter + setter em vez de atributo simples) e quem lê
precisa entender @property. Achamos a troca válida: custo pequeno, proteção total.

## Commit
a3f9c21 — "protege valor_diaria com @property e setter"
```

**Por que tira nota máxima:**
- *Contexto* conta o caso real e o risco concreto (o -50 gravado).
- *Decisão* diz o quê **e por quê** (o objeto protege todos os caminhos).
- *Alternativa descartada* mostra uma opção real recusada, com o motivo exato.
- *Consequência* é honesta sobre o ganho **e** o custo.
- *Commit* presente — rastreável.

---

### 📄 Exemplo B — Política de tarifa (Strategy)

#### ❌ VERSÃO NOTA BAIXA

```markdown
# ADR 004 — Tarifas

## Contexto
Tínhamos vários descontos.

## Decisão
Usamos o padrão Strategy porque é o certo.

## Alternativa descartada
Não usar padrão nenhum.

## Consequência
Ficou mais organizado e profissional.

## Commit
d5b2e83
```

**Por que perde nota:**
- *Contexto* raso — não explica o problema do if/elif que crescia.
- *Decisão* apela para autoridade ("porque é o certo") em vez de razão. **Cuidado
  com isto:** dizer que usou um padrão "porque é boa prática" é o oposto do que a
  disciplina cobra — soa a padrão aplicado por status, não por necessidade.
- *Alternativa descartada* genérica ("não usar padrão") — não é uma alternativa
  pensada, é a ausência de uma.
- *Consequência* vazia de conteúdo: "profissional" não diz nada técnico.

#### ✅ VERSÃO NOTA MÁXIMA

```markdown
# ADR 004 — Política de tarifa com Strategy

## Contexto
O total de uma reserva depende de um desconto que varia por tipo de hóspede:
comum (0%), fidelidade (10%), parceiro (20%). O cálculo estava num total() com
if/elif por tipo. A pousada vai lançar novos convênios na temporada, e cada um
obrigaria a abrir a classe Reserva e acrescentar mais um elif — mexendo em código
que já funciona e arriscando quebrá-lo.

## Decisão
Aplicamos o padrão Strategy. Cada política de tarifa virou uma classe com um
método aplicar(base). A Reserva recebe uma estratégia e delega, sem if. Uma
política nova é uma classe nova; a Reserva não muda.

## Alternativa descartada
Consideramos duas opções. (1) Manter o if/elif: rejeitada porque cresce a cada
convênio e concentra o risco num ponto só. (2) Criar subclasses de Reserva por
tipo de hóspede (herança): rejeitada porque o tipo de desconto não define um tipo
de reserva — uma mesma reserva poderia trocar de política, e herança amarraria
isso rígido. Strategy, por composição, deixa a política trocável.

## Consequência
Adicionar um convênio novo não toca na Reserva nem nas outras políticas — aberto
para estender, fechado para modificar. Em troca, há mais classes pequenas.
Observação: em Python isso poderia ser uma função; usamos classes porque algumas
políticas futuras podem guardar estado (ex.: desconto com teto de valor).

## Commit
d5b2e83 — "refatora calculo de tarifa para o padrao Strategy"
```

**Por que tira nota máxima:**
- *Contexto* explica o *smell* concreto (o if/elif que cresce) e a pressão real
  (os convênios que vêm).
- *Decisão* diz o mecanismo e o ganho, sem apelar para "é o certo".
- *Alternativa descartada* mostra **duas** opções pensadas e recusadas, com motivo
  técnico — inclusive por que herança seria pior que composição aqui.
- *Consequência* é honesta (o custo das classes) e mostra maturidade (a nota sobre
  função vs. classe em Python).

---

## 5. O teste rápido antes de entregar

Para cada ADR do seu Caderno, pergunte:

1. **A Decisão diz "por quê", ou só "o quê"?** Se só diz o quê, reescreva.
2. **A Alternativa descartada tem uma opção real, com motivo?** Se está vazia ou
   genérica, pense no que vocês de fato consideraram e recusaram.
3. **Alguém de fora entenderia a decisão só lendo o ADR?** Se precisa de vocês
   explicando junto, falta no texto.
4. **Tem o commit?** Se não, rode `git log`, pegue o hash, cole.
5. **Cada integrante sabe defender este ADR sem olhar o papel?** Se não, estudem —
   a defesa é sem consulta.

Se os cinco derem "sim", o ADR está pronto.

---

## 6. Uso de IA neste marco

**Nível 2 (declaração) para redigir; nível 3 (proibido) na defesa.**
A IA pode ajudar a *escrever* o texto de um ADR — mas a **decisão** é da equipe, e
a **defesa oral é sem consulta**. Um ADR que vocês não sabem defender não vale,
por mais bem escrito que esteja. E uso de IA não declarado no texto zera a entrega.

---

*Guia do Marco 1 — ILP-037 — FATEC Olímpia — Prof. José Ceron Neto — 2026/2*

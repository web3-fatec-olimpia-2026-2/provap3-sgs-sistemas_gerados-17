# Homework 08C — Dois ADRs: aplicar-ou-não MVVM e Adapter no projeto
### Da equipe · ILP-037 · Prazo: quarta 15/10, 23h59 · IA nível 1 (livre p/ pesquisa, não p/ decidir por vocês)

## A tarefa
Escrever **dois ADRs** no Caderno de Design da equipe (`/docs/design/`), um para cada padrão da
aula. Em cada um, a equipe **decide aplicar ou não** o padrão no projeto — **com justificativa**.

1. **ADR — MVVM:** há na tela do projeto alguma **decisão de exibição** (rótulo condicional,
   formatação, estado derivado) que valha extrair para um ViewModel? Ou a exibição é trivial e
   não compensa?
2. **ADR — Adapter:** vocês migraram para PostgreSQL/Neon na segunda. Há um ponto onde o código
   conhece o banco **diretamente** (ou conheceu, durante a migração)? Um Adapter cabe ali — ou o
   duck typing já resolveu e um Adapter formal seria cerimônia?

## ⚖️ O mote: decidir é o trabalho
**"Não aplicamos" é uma resposta tão válida quanto "aplicamos"** — desde que justificada pelo
problema real do projeto, não por "é boa prática". A competência avaliada é **decidir se cabe**.

## Modelo de ADR (copie e preencha — um por padrão)

```markdown
# ADR 00X — [MVVM | Adapter] no [nome do módulo/tela]

- Data: 2026-10-__
- Status: aceito
- Decisores: [nomes da equipe]

## Contexto
[Qual trecho do projeto está em jogo. Cole o caminho do arquivo e 2-3 linhas do código
 que motivaram a discussão. Ex.: "A tela X monta o rótulo de status dentro do template" /
 "O módulo Y chama o driver do Neon direto em três lugares".]

## Decisão
[APLICAMOS o padrão / NÃO APLICAMOS o padrão — frase clara.]

## Justificativa
[Por quê. Se aplicaram: qual smell o padrão resolveu, o que ficou testável/trocável.
 Se não aplicaram: por que não cabia — exibição trivial? duck typing já bastava?
 sobre-engenharia? Amarrem na delimitação em Python vista na aula.]

## Consequências
[O que muda daqui pra frente. O que passou a ser testável/substituível, ou o que vocês
 conscientemente deixaram como está e por quê.]
```

## Exemplo preenchido (de referência — não copiem, é do Resort fictício)

```markdown
# ADR 007 — Adapter para o acesso ao banco pós-migração Neon

- Data: 2026-10-14
- Status: aceito
- Decisores: equipe Mirante

## Contexto
Após migrar de SQLite para PostgreSQL/Neon, o ReservaService passou a ter um
`if driver == "neon"` em dois metodos, lendo `resp["ticket"]` do driver novo.

## Decisão
APLICAMOS o padrão Adapter: criamos NeonReservaAdapter implementando nossa
interface ReservaRepository (salvar/buscar).

## Justificativa
O driver do Neon é código de terceiro — não podemos mudar a assinatura dele.
É exatamente o caso em que o Adapter se justifica (GIRIDHAR). O `if de banco`
vazava detalhe de infraestrutura para dentro da regra. Com o Adapter, o
serviço voltou a depender de uma interface só (OCP).

## Consequências
Trocar de banco agora é trocar o objeto injetado. O serviço ficou testável com
um repositório em memória, sem subir o Neon.
```

## Critério de aceitação
- [ ] **dois** ADRs commitados em `/docs/design/`
- [ ] cada um decide **explicitamente** aplicar ou não — e **justifica** pelo problema real
- [ ] pelo menos um cita a **delimitação em Python** vista na aula (quando o padrão encolhe/dispensa)
- [ ] relator enviou o link do commit no canal da equipe

> Estes dois ADRs são **insumo direto do Marco 2**. Caprichem: no Marco 1, o que separou os
> Cadernos fortes dos fracos foi **justificar** em vez de descrever.

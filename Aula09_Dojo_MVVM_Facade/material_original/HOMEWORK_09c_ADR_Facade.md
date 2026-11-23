# Homework 09C — ADR: aplicar-ou-não um Facade no projeto
### Da equipe · ILP-037 · Prazo: quarta 22/10, 23h59 · IA nível 1 (livre p/ pesquisa, não p/ decidir por vocês)

## A tarefa
Escrever **um ADR** no Caderno de Design da equipe (`/docs/design/`) decidindo se cabe um
**Facade** em algum ponto do projeto — **com justificativa**.

Procurem um ponto onde **uma** ação do sistema chama **vários** passos na ordem (ex.: uma view
que busca dados + calcula + grava + responde; um fluxo de cadastro que toca vários módulos). Uma
Facade simplificaria quem chama? Ou já está simples o bastante e seria cerimônia?

> **Sem requisito novo.** Esta semana não teve segunda de Web III — vocês decidem **sobre o
> código que já têm**, não sobre algo a construir.

## ⚖️ O mote: decidir é o trabalho
**"Não aplicamos" é tão válido quanto "aplicamos"** — desde que justificado pelo problema real.
Cuidado com os dois erros típicos: criar Facade onde a orquestração é trivial (cerimônia); e
deixar a Facade inchar e virar um *God object* (ela deve **delegar**, não reimplementar).

## Modelo de ADR (copie e preencha)

```markdown
# ADR 00X — Facade em [nome do fluxo/módulo]

- Data: 2026-10-__
- Status: aceito
- Decisores: [nomes da equipe]

## Contexto
[Qual fluxo está em jogo. Cole o caminho do arquivo e 2-3 linhas do código onde uma
 ação chama vários passos na ordem.]

## Decisão
[APLICAMOS um Facade / NÃO APLICAMOS — frase clara.]

## Justificativa
[Por quê. Se aplicaram: qual acoplamento a vários subsistemas o Facade escondeu, o que
 o cliente deixou de conhecer. Se não: por que não cabia — orquestração trivial? uma
 função já bastaria? risco de God object? Amarrem na delimitação em Python vista em aula.]

## Consequências
[O que muda. O que o cliente passou a chamar; ou o que vocês conscientemente deixaram
 como está e por quê.]
```

## Exemplo preenchido (de referência — do Resort fictício, não copiem)

```markdown
# ADR 008 — Facade para o fluxo de reserva

- Data: 2026-10-21
- Status: aceito
- Decisores: equipe Mirante

## Contexto
A view de reserva chamava, na ordem: checar disponibilidade, calcular tarifa, gravar
e notificar. A mesma sequencia aparecia tambem no fluxo do balcao presencial.

## Decisao
APLICAMOS um Facade: RecepcaoFacade.reservar() concentra a orquestracao.

## Justificativa
Havia acoplamento real a quatro subsistemas, repetido em dois lugares. O Facade
removeu a duplicacao e isolou a ordem num ponto so. Nao e God object: ele delega a
cada subsistema, nao reimplementa regra.

## Consequencias
A view e o balcao agora chamam recepcao.reservar(...). Um 5o passo (emitir nota) sera
adicionado so na facade, sem tocar em quem chama.
```

## Critério de aceitação
- [ ] ADR commitado em `/docs/design/`
- [ ] decide **explicitamente** aplicar ou não — e **justifica** pelo problema real
- [ ] cita a **delimitação** (quando o Facade é cerimônia / risco de God object)
- [ ] relator enviou o link do commit no canal da equipe

> Insumo direto do **Marco 2**. Caprichem na justificativa — é o que separou os Cadernos fortes
> dos fracos no Marco 1.

# Aula 11 — Retomada para a Prova Prática (P3)

> ILP-037 · 13/11/2026 · **sem conteúdo novo**
> Fontes: `ILP037_Aula11_Slides_1.pdf`, `ILP037_Aula11_KIT_REVISAO_ALUNO.md`,
> `ILP037_Aula11_MATERIAL_RETOMADA.md`, `guia-12-perguntas-p3-ilp037.pdf`, `study-guide-p3-ilp037.pdf`,
> áudio "Padrões de projeto da Gangue dos Quatro", descrição do módulo no Teams.
> No Teams também: "Diagnóstico pré-P3" (Forms) e "Padrões Mapa Mental"/"FlashCards" (NotebookLM).

## 1. A P3 — como funciona (leia com atenção)

| | |
|---|---|
| **Data** | **27/11/2026** (sexta) · 20/11 sem aula · 04/12 Caderno · 11/12 encerramento |
| **Formato** | Individual na defesa (slides falam "em grupo"; descrição do módulo diz "individual") — **cada um defende o PRÓPRIO código** |
| **IA** | **Vedada** |
| **Regra "explique uma função"** | O professor sorteia uma função/bloco **do seu código** e pergunta: **(1) o que faz · (2) por que foi escrita assim · (3) o que muda se alterar** |
| **Atenção** | "Código funcionando **sem explicação** não pontua integralmente." |
| **Tipos de pergunta** (Kit) | reconhecer o padrão · prever o resultado · achar o erro · explicar a sua decisão |

## 2. O que cai — a tabela da revisão ⭐

| Conceito | Pergunta que você precisa saber responder |
|---|---|
| **Strategy** | que smell indica que ele cabe? (`if/elif` por tipo que cresce) |
| **SRP / OCP** | um motivo para mudar · estender sem modificar o que já funciona |
| **Service × ViewModel** | regra de negócio × lógica de exibição |
| **Adapter** | traduzir **uma** interface para **caber** |
| **Facade** | **esconder vários** subsistemas atrás de um balcão |
| **Decorator** | **somar** e **empilhar**, **mantendo** a interface |
| **Decidir & justificar** | quando **NÃO** aplicar — e por quê |

## 3. O trio que mais confunde

| Padrão | Mexe em | Interface | Intenção |
|---|---|---|---|
| Adapter | **uma** peça incompatível | **muda** (traduz p/ outra que já existe) | fazer **caber** |
| Facade | **vários** subsistemas | **cria** uma nova, simples | **esconder** a complexidade |
| Decorator | **um** objeto, empilhável | **mantém** a mesma | **somar** sem trocar o de baixo |

> **"Adapter faz caber. Facade esconde a bagunça atrás de um balcão. Decorator soma camadas sem
> trocar o que está embaixo."**

## 4. Os 6 cards da retomada (ciclo Problema → Conceito → Demonstração → Aplicação)

| Card | Problema | Conceito em 1 linha | Delimitação (quando NÃO) |
|---|---|---|---|
| 1 Strategy | `if/elif` de tarifa cresce a cada tipo | cada cálculo numa classe com `calcular`; contexto recebe e delega | fórmula única → função basta |
| 2 SRP/OCP | `Reserva` calcula + formata + grava | 1 classe, 1 razão p/ mudar; formato novo = classe nova | não é "1 classe por método" |
| 3 Service × VM | tela decide rótulo **e** regra | Service = verdade do negócio; VM = como mostrar | CRUD trivial não precisa de VM |
| 4 Adapter | driver Neon fala `execute`; app espera `salvar` | veste a peça de terceiro com a interface esperada | você controla as 2 pontas → duck typing |
| 5 Facade | reservar chama 4 subsistemas em ordem | 1 ponto de entrada que orquestra e **delega** | 1–2 passos → função; cuidado God object |
| 6 Decorator | extras com flags/ifs | embrulha, mantém interface, soma; empilha | soma fixa → lista + `sum()`; `@` do Python é outra coisa |

## 5. Como responder "explique esta função" (Q10 do guia)
1. **O que faz** — o papel dela no sistema (não leia a sintaxe linha a linha).
2. **Por que assim** — qual problema/smell, qual padrão/princípio, qual alternativa foi descartada.
3. **O que muda se alterar** — impacto em acoplamento, testabilidade, extensão, testes existentes.

> Ex.: "Esta é a `RelatorioService.calcular`. Ela aplica o desconto por tipo e devolve dados, sem
> saber de web. Tirei da view para testar sem HTTP e reaproveitar na API. Se eu voltar a regra para a
> view, o teste passa a precisar de request e a API teria que duplicar a conta."

## 6. Resolução e treino

| O quê | Onde |
|---|---|
| Kit de Revisão resolvido e explicado (Partes 1–4) | `resolucao/kit_revisao_resolvido.md` |
| Previsões do kit **conferidas rodando** | `resolucao/verificacao_kit/` (pytest) |
| As 6 "Aplicações orientadas" dos cards, em código | `resolucao/cards_aplicacao/` (pytest) |
| **Treino para a prova** (exercícios novos + gabarito) | `../Treino_Prova/` |

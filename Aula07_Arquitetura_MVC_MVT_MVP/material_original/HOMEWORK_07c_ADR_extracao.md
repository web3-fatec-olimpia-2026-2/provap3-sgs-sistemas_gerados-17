# 📓 Homework 07c — ADR: planejar a extração de um Service *(da equipe)*

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Da equipe · Uma entrega por equipe · Prazo: quarta-feira, 24/09, 23h59 · 20 pontos**

> Este homework alimenta diretamente o **Marco 2** (entrega 09/10, que pede arquitetura declarada + um Presenter/Service extraído). Fazê-lo bem adianta o Marco.

---

## A ideia

Na aula você viu como extrair um Service testável de uma view que faz coisas demais. Agora o alvo é o **projeto real da equipe**: encontrar uma view assim no `views.py`, e **planejar** a extração — sem precisar implementar ainda.

Registrar o plano antes de codar é o que a disciplina valoriza: decidir com clareza, depois executar.

---

## O que fazer

**1. Achem, no `views.py` do projeto, uma view que mistura responsabilidades.** Procure uma que faça mais de uma destas coisas: buscar dados, aplicar regra de negócio (cálculo, decisão), e montar a resposta. Quanto mais ela faz, melhor candidata.

**2. Registrem no Caderno de Design um ADR** planejando a extração:

```markdown
# ADR 00X — Extrair um Service da view [nome da view]

## Contexto
Qual view faz coisas demais, e quais responsabilidades ela mistura?
Ex.: a view lista_reservas busca as reservas, calcula o total com desconto por
tipo de hóspede, E monta o contexto do template. A regra do desconto está presa
na view — não conseguimos testá-la sem simular uma requisição.

## Decisão
O que vamos extrair, e para onde.
Ex.: extrair um ReservaService com um método calcular_totais(), que recebe as
reservas e devolve os dados calculados. A view passa a só chamar o service e
montar o contexto.

## Alternativa descartada
O que consideramos e não escolhemos.
Ex.: deixar a regra na view e testar com o test client do Django. Descartado
porque o teste ficaria lento e acoplado à camada web — e a regra continuaria sem
poder ser reaproveitada em outro lugar (ex.: um relatório, uma API).

## Consequência
O que muda quando extrairmos.
Ex.: a regra do desconto fica testável sem subir servidor e reaproveitável.
Custo: mais um arquivo (services.py) e uma camada a entender.

## Status
Planejado — a extração será feita na sprint. (Registrando a decisão de design.)
```

---

## Cuidado com o exagero *(vale nota)*

**Não escolham uma view trivial.** Se a view só lista objetos e renderiza, ela **não precisa** de Service — e propor extração ali mostra que a equipe não entendeu o critério. Escolham uma view que tem **regra de verdade**. Reconhecer que uma view simples deve continuar simples é tão importante quanto saber extrair.

---

## Como entregar

1. Commit do ADR no repositório da equipe.
2. O **Relator** cola o link no Teams.

---

## Como será avaliado *(20 pontos)*

| Critério | Pontos |
|---|---|
| A view escolhida de fato mistura regra e apresentação (não é trivial) | 6 |
| O plano de extração é concreto (o que vira Service, o que a view mantém) | 6 |
| A alternativa descartada mostra que pensaram no trade-off | 5 |
| A equipe consegue defender a decisão (será perguntado no Marco 2) | 3 |

---

## Uso de IA

**Nível 2 — permitido com declaração.** A IA pode ajudar a redigir, mas a **escolha da view** e a **decisão** são da equipe, e a defesa é sem consulta.

---

*Homework 07c — ILP-037 — FATEC Olímpia — 2026/2*

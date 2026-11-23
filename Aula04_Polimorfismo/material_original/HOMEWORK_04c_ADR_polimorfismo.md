# 📓 Homework 04c — ADR: onde polimorfismo caberia *(da equipe)*

**ILP-037 Técnicas de Programação II · FATEC Olímpia · 2026/2**
**Da equipe · Uma entrega por equipe · Prazo: quarta-feira, 03/09, 23h59 · 20 pontos**

---

## O que é isto

O **Caderno de Design** é onde a equipe registra as **decisões de design** do projeto — o *porquê* do código. Cada decisão vira um **ADR** (*Architecture Decision Record*).

Neste homework, vocês **não vão implementar** nada. Vão **enxergar** um lugar no projeto onde polimorfismo caberia, e **registrar** essa observação. Enxergar antes de codar é metade do trabalho de design.

---

## O que procurar

Polimorfismo cabe quando você tem **vários tipos que fazem a mesma coisa de formas diferentes**. No projeto da sua equipe, procure algo assim. Exemplos comuns:

- **Tipos de usuário** que têm permissões ou telas diferentes (aluno, professor, admin)
- **Tipos de item** que calculam algo de forma diferente (produto físico × digital; quarto comum × suíte)
- **Formas de pagamento** que processam diferente (cartão, pix, boleto)
- **Tipos de notificação** que enviam diferente (e-mail, SMS, push)

Achem **um** ponto desses no projeto de vocês. É o assunto do ADR.

---

## O que escrever — ADR

Criem, no repositório, um arquivo como `docs/design/ADR-004-polimorfismo.md`:

```markdown
# ADR 004 — Onde polimorfismo caberia no nosso projeto

## Contexto
Que ponto do nosso projeto tem vários tipos que fazem a mesma coisa de
formas diferentes?
Ex.: temos três formas de pagamento (cartão, pix, boleto), e hoje o código
decide o que fazer com um if para cada uma.

## Decisão
Se vale (ou não) aplicar polimorfismo ali, e por quê.
Ex.: vale — cada forma de pagamento vira uma classe com um método processar(),
e uma função trata todas igual, sem if.

## Alternativa considerada
O que existe hoje ou o que mais consideramos.
Ex.: manter o if/elif atual. Funciona, mas cada forma nova obriga a mexer na
função e arriscar quebrar as existentes.

## Consequência
O que muda se aplicarmos (mesmo que só no futuro).
Ex.: adicionar uma forma de pagamento nova passa a não exigir mexer no código
que já existe.

## Status
Proposto — ainda não implementado. (Só registrando a decisão de design.)
```

---

## Como entregar

1. Façam commit do arquivo no repositório da equipe.
2. O **Relator** cola no Teams o link do arquivo (ou do commit). Uma linha basta.

---

## Como será avaliado *(20 pontos)*

| Critério | Pontos |
|---|---|
| O ADR existe e está versionado no repositório | 5 |
| O ponto escolhido de fato tem "vários tipos que fazem o mesmo de formas diferentes" | 6 |
| A "alternativa considerada" mostra que a equipe pensou no trade-off | 5 |
| A equipe consegue defender a decisão (será perguntado no Marco 1) | 4 |

---

## Uso de IA

**Nível 2 — permitido com declaração.** A IA pode ajudar a redigir, mas a **observação** — qual ponto do projeto — tem que ser da equipe, e vocês precisam saber defendê-la sem consulta.

---

## Se a equipe ainda não tem Caderno de Design

Criem a pasta `docs/design/` no repositório (ou usem o `docs/decisoes.md`, se já existir). O Caderno é um conjunto de arquivos markdown, um por decisão, versionado com o código. É o artefato que mais pesa na nota do Marco 1 — comecem agora.

---

*Homework 04c — ILP-037 — FATEC Olímpia — 2026/2*

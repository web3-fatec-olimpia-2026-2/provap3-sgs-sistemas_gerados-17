# Homeworks da Aula 09

## 09A — Lab Facade
[`../lab_facade/recepcao.py`](../lab_facade/recepcao.py) → 5 testes originais + 6 meus (inclui a
prova de equivalência com `fazer_reserva_na_mao`).

## 09B — Adapter × Facade (IA vedada — modelo de estudo)

**Modelo (4 linhas):**
O Adapter trabalha com **uma** peça que já faz o serviço certo mas fala outra língua: ele traduz
as chamadas e o formato dela para a interface que o sistema **já usa**, como o `NeonReservaAdapter`
transformando `execute(...)`/`{"ticket": n}` em `salvar(...)`/`n`. O Facade trabalha com **vários**
subsistemas que funcionam bem mas exigem saber a ordem certa de chamá-los: ele **cria uma interface
nova e mais simples** na frente deles, como a `RecepcaoFacade.reservar()` escondendo disponibilidade,
tarifa, gravação e notificação. Um faz caber, o outro esconde a bagunça.

**Checklist:** um × vários · traduzir para interface existente × criar interface nova · exemplo concreto.

## 09C — ADR Facade (equipe) — modelo

```markdown
# ADR 010 — Facade no fluxo de check-out

- Status: aceito

## Contexto
`reservas/views.py::checkout` chama, na ordem: calcular consumo do frigobar, aplicar tarifa,
registrar pagamento, liberar o quarto e enviar e-mail. A mesma sequência foi copiada para o
endpoint da API `api/checkout`.

## Decisão
APLICAMOS um Facade: `CheckoutFacade.finalizar(reserva)` em `reservas/services.py`.

## Justificativa
Acoplamento real a cinco subsistemas, duplicado em dois clientes (view e API). A fachada
concentra a ordem e delega a cada subsistema — não reimplementa nenhuma regra (evita God object).
Não aplicamos no fluxo "editar perfil": ele só valida e salva um model; uma fachada ali seria cerimônia.

## Consequências
View e API passam a chamar `CheckoutFacade.finalizar(...)`. Um passo novo (emitir NF) entra só
na fachada. A fachada não impede uso direto dos subsistemas (não é prisão).
```

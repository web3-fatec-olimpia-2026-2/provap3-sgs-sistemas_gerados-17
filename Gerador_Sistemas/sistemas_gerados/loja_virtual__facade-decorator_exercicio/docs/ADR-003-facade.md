# ADR 003 — Facade em Loja Virtual

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão estrutural (GoF) — Aula 09

## Contexto
`atender_na_mao` conhece 5 subsistemas, a ordem e as regras de aborto; cada tela que conclui um atendimento repetiria tudo isso.

## Decisão
APLICAMOS **Facade**. `AtendimentoFacade.concluir(recurso, item)` é o balcão único: disponibilidade → cálculo → cobrança → registro → notificação, DELEGANDO a cada subsistema.

## Alternativa descartada
Cada tela orquestrar os subsistemas — duplicação e acoplamento a cinco objetos.

## Consequências
Passo novo entra só na fachada; clientes conhecem um objeto. Custo: mais uma classe.
Quando NÃO usar: 1–2 passos num lugar só → uma função basta. Se a fachada passar a executar regra (em vez de delegar) vira God object. Ela não proíbe usar os subsistemas direto.

## Onde está no código
`nucleo/atendimento.py` (antes: `nucleo/antes_atendimento.py`) · testes: `tests/test_atendimento.py`

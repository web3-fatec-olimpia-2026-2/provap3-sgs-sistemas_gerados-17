# ADR 004 — Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web) em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Arquitetura — Aula 07

## Contexto
`relatorio_view` mistura a regra (desconto por tipo de hóspede) com a apresentação (texto); para testar a conta é preciso chamar a view e ler texto.

## Decisão
APLICAMOS **Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web)**. `RelatorioService.calcular()` faz só a regra e devolve DADOS; a view fica fina (chama e formata); a mesma regra serve a API (`relatorio_api`). No Django: models = dado, views = regra/orquestração, template = apresentação, services.py = a regra complexa.

## Alternativa descartada
Deixar a regra na view e testar com o client HTTP — teste lento e acoplado; a API teria que duplicar a conta.

## Consequências
Regra testável sem HTTP e reaproveitável. Custo: uma camada a mais.
Quando NÃO usar: View que só lista e renderiza não precisa de Service — só há Service quando há cálculo, decisão ou orquestração de vários passos.

## Onde está no código
`nucleo/relatorio.py` (antes: `nucleo/antes_relatorio.py`) · testes: `tests/test_relatorio.py`

# ADR 006 — Singleton em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
Cada parte do sistema cria a sua `ConfiguracaoAntiga()`; mudar a taxa no caixa não muda no relatório — dois lugares cobrando valores diferentes.

## Decisão
APLICAMOS **Singleton**. `Configuracao.__new__` devolve SEMPRE o mesmo objeto (guardado em `_instancia`); quem precisa chama `Configuracao()` e recebe a única que existe. `reiniciar()` existe só para os testes.

## Alternativa descartada
Passar a configuração por parâmetro (injeção) — mais explícito, mas todo construtor a recebe.

## Consequências
Um ponto só de verdade para a configuração. Custo: estado global (testes precisam reiniciar).
Quando NÃO usar: Em Python um módulo já é único: uma variável no módulo resolve sem cerimônia. Singleton é estado global escondido — dificulta testes; prefira injetar a dependência quando der.

## Onde está no código
`nucleo/configuracao.py` (antes: `nucleo/antes_configuracao.py`) · testes: `tests/test_configuracao.py`

# ADR 008 — Builder em ViagemCerta

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`nova_destino_antiga(...)` recebe os campos na ORDEM certa; trocar dois números de lugar cria uma Destino válida porém errada, e não há valores padrão.

## Decisão
APLICAMOS **Builder**. `DestinoBuilder` tem um `com_<campo>()` por atributo, cada um devolvendo o próprio builder (interface fluente); `construir()` confere o que falta e só então cria a Destino. `DiretorDeDestino` guarda receitas prontas.

## Alternativa descartada
Argumentos nomeados com padrão — resolve a ordem, mas não monta em etapas nem guarda receitas.

## Consequências
Montagem legível e em etapas, com erro claro do que falta. Custo: uma classe espelhando os campos.
Quando NÃO usar: Objeto com poucos campos: em Python, argumentos NOMEADOS já resolvem a ordem.

## Onde está no código
`nucleo/construtor.py` (antes: `nucleo/antes_construtor.py`) · testes: `tests/test_construtor.py`

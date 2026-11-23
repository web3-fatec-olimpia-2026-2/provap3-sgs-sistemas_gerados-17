# ADR 009 — Builder em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`nova_reserva_antiga(...)` recebe os campos na ORDEM certa; trocar dois números de lugar cria uma Reserva válida porém errada, e não há valores padrão.

## Decisão
APLICAMOS **Builder**. `ReservaBuilder` tem um `com_<campo>()` por atributo, cada um devolvendo o próprio builder (interface fluente); `construir()` confere o que falta e só então cria a Reserva. `DiretorDeReserva` guarda receitas prontas.

## Alternativa descartada
Argumentos nomeados com padrão — resolve a ordem, mas não monta em etapas nem guarda receitas.

## Consequências
Montagem legível e em etapas, com erro claro do que falta. Custo: uma classe espelhando os campos.
Quando NÃO usar: Objeto com poucos campos: em Python, argumentos NOMEADOS já resolvem a ordem.

## Onde está no código
`nucleo/construtor.py` (antes: `nucleo/antes_construtor.py`) · testes: `tests/test_construtor.py`

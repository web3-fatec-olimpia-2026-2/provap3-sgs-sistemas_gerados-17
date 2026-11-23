# ADR 010 — Prototype em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`copiar_na_mao(original)` repete campo por campo; quando a Reserva ganha um dado novo, a cópia esquece dele sem avisar.

## Decisão
APLICAMOS **Prototype**. `clonar(original, **mudancas)` copia o objeto inteiro com `copy.deepcopy` (inclusive listas internas) e aplica as mudanças pelos setters. `RegistroDePrototipos` guarda modelos e entrega clones.

## Alternativa descartada
Construir do zero repetindo os valores — espalha a receita e esquece dados novos.

## Consequências
Criar a partir de modelos prontos sem conhecer cada campo. Custo: deepcopy de objeto grande é caro.
Quando NÃO usar: Objeto simples, criado em uma linha — copiar não economiza nada. Cuidado: cópia RASA (`copy.copy`) compartilha as listas internas com o original.

## Onde está no código
`nucleo/prototipos.py` (antes: `nucleo/antes_prototipos.py`) · testes: `tests/test_prototipos.py`

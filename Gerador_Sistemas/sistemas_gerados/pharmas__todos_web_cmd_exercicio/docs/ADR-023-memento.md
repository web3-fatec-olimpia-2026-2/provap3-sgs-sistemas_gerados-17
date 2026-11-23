# ADR 023 — Memento em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
Para "voltar atrás", quem usa copia os campos internos (`_campo`) da Pharm num dicionário — depende do interior dela e esquece campos novos.

## Decisão
APLICAMOS **Memento**. `EditorPharm` (originador) cria um `Memento` com a cópia do próprio estado e sabe restaurá-lo; `HistoricoDeVersoes` (zelador) só empilha mementos, sem olhar dentro.

## Alternativa descartada
Copiar os campos na mão — quebra o encapsulamento e esquece o que for novo.

## Consequências
Desfazer sem expor o interior. Custo: cada versão ocupa memória.
Quando NÃO usar: Estado grande e muitas versões (memória). Memento × Command: o Command desfaz UMA ação; o Memento volta o estado inteiro.

## Onde está no código
`nucleo/versoes.py` (antes: `nucleo/antes_versoes.py`) · testes: `tests/test_versoes.py`

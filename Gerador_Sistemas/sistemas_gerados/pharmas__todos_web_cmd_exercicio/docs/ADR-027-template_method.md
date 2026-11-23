# ADR 027 — Template Method em Pharmas

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`fechar_padrao_antigo` e `fechar_com_taxa_antigo` são cópias do mesmo roteiro (validar → calcular → ajustar → formatar); corrigir um passo exige lembrar de todas as cópias.

## Decisão
APLICAMOS **Template Method**. `Fechamento.fechar(item)` é o método TEMPLATE: fixa a ordem dos passos; as subclasses sobrescrevem só o passo que muda (`ajustar`), e o gancho tem padrão vazio.

## Alternativa descartada
Copiar o roteiro em cada variação — duplicação.

## Consequências
Roteiro num lugar só; subclasses mínimas. Custo: a herança amarra as subclasses à base.
Quando NÃO usar: Só um passo varia — passe uma função (Strategy). Template Method usa HERANÇA; Strategy, COMPOSIÇÃO.

## Onde está no código
`nucleo/fechamento.py` (antes: `nucleo/antes_fechamento.py`) · testes: `tests/test_fechamento.py`

# ADR 012 — Bridge em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
Uma classe por COMBINAÇÃO: `SimplesTexto`, `SimplesHtml`, `DetalhadoTexto`, `DetalhadoHtml` — 2 tipos × 2 formatos = 4 classes repetidas; formato novo exigiria uma classe por tipo.

## Decisão
APLICAMOS **Bridge**. Duas hierarquias separadas: a ABSTRAÇÃO `Comprovante` (Simples, Detalhado) decide O QUE mostrar; a IMPLEMENTAÇÃO `Formato` (Texto, Html) decide COMO escrever. A ponte é `self.formato` (composição).

## Alternativa descartada
Herança por combinação — N × M classes com código duplicado.

## Consequências
N + M classes em vez de N × M; formato trocado em tempo de execução. Custo: mais indireção.
Quando NÃO usar: Só uma dimensão varia — herança simples ou Strategy basta. Bridge se planeja no início; encaixar duas classes prontas é Adapter.

## Onde está no código
`nucleo/comprovantes.py` (antes: `nucleo/antes_comprovantes.py`) · testes: `tests/test_comprovantes.py`

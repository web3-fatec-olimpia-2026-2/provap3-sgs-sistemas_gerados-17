# ADR 008 — Abstract Factory em ViagemCerta

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
`montar_relatorio_antigo(itens, formato)` decide o formato em CADA peça (cabeçalho, linha, rodapé); esquecer um `if` mistura texto com HTML no mesmo relatório.

## Decisão
APLICAMOS **Abstract Factory**. `KitRelatorio` (fábrica abstrata) declara `criar_cabecalho`, `criar_linha` e `criar_rodape`; cada kit concreto (`KitTexto`, `KitHtml`) cria TODAS as peças da mesma família. `montar_relatorio(kit, itens)` só conhece a interface.

## Alternativa descartada
Um `if formato` por peça — funciona, mas nada garante que as peças combinem.

## Consequências
Família nova = kit novo, e as peças sempre combinam. Custo: peça nova = método novo em todos os kits.
Quando NÃO usar: Uma família só, ou uma peça só — Factory Method (ou a classe direta) resolve. Um TIPO de peça novo obriga a mexer em todos os kits.

## Onde está no código
`nucleo/kits.py` (antes: `nucleo/antes_kits.py`) · testes: `tests/test_kits.py`

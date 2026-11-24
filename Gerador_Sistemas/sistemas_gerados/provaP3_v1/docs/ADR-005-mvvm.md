# ADR 005 — MVVM (ViewModel) em Cooperativa Citrícola

- Status: aceito (exemplo de estudo gerado)
- Família: Arquitetura — Aulas 08 e 09

## Contexto
`tela_painel` decide no meio do desenho o status, o rótulo do botão, o "R$" e o rodapé "ENTRESSAFRA - nenhum talhão pronto" — só dá para testar lendo a tela.

## Decisão
APLICAMOS **MVVM (ViewModel)**. `ItemViewModel` / `PainelVM` traduzem o dado cru em dado pronto (`status_label`, `acao_label`, `preco_formatado`, `rodape`); a View só costura. No Django não há binding: o ViewModel é preparação chamada antes do `render`.

## Alternativa descartada
Manter os `if` de exibição no template — só se testaria lendo HTML.

## Consequências
Rótulo/estado novo muda só o ViewModel; testes sem renderizar. Custo: uma camada a mais.
Quando NÃO usar: Tela que mostra o dado como está não precisa de ViewModel. Service × ViewModel: regra de negócio (o que é verdade) × lógica de exibição (como aparece).

## Onde está no código
`nucleo/painel.py` (antes: `nucleo/antes_painel.py`) · testes: `tests/test_painel.py`

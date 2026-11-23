# ADR 017 — Proxy em Hotel Resort

- Status: aceito (exemplo de estudo gerado)
- Família: Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia

## Contexto
Quem consulta faz o cache e confere a permissão na mão, misturado com a chamada — cada ponto de uso repete (ou esquece) essas regras.

## Decisão
APLICAMOS **Proxy**. `ConsultaComCache` e `ConsultaProtegida` têm o MESMO `calcular(item)` do objeto real (`ConsultaDePreco`); por dentro guardam respostas ou barram perfis e só então repassam. Quem usa nem percebe — e os proxies empilham.

## Alternativa descartada
Cache e permissão no código de quem chama — repetido em cada ponto de uso.

## Consequências
Regras de acesso num lugar só, transparentes. Custo: uma indireção e, no cache, dado velho.
Quando NÃO usar: Acesso simples, sem custo nem regra. Proxy × Decorator: o Decorator ACRESCENTA comportamento; o Proxy CONTROLA o acesso ao objeto real.

## Onde está no código
`nucleo/acesso.py` (antes: `nucleo/antes_acesso.py`) · testes: `tests/test_acesso.py`

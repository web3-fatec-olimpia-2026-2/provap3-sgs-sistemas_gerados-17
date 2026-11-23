# Motor de ID interno — LNNL

Identificador interno **legível por humanos**, com 14 caracteres exibidos como
`LNNL-LNNL-LNL-LNL` (ex.: `K12W-F22M-T5R-Q7L`), código de **tipo** embutido e **2 dígitos
verificadores módulo 79**. Ele detecta 100% dos erros de um caractere e das transposições, e
98,75% dos erros duplos.

> **Não substitui o UUID.** O UUID continua sendo a chave primária e a identidade técnica. O
> LNNL é a identidade usada por pessoas (atendimento, comprovantes, vouchers, endpoints de
> consulta) e entra onde o desenvolvedor decidir.

Esta pasta é **independente de projeto e de framework**: não importa nada do sistema em que
está guardada.

| Leia | Para |
| :-- | :-- |
| [`RFC-LNNL.md`](RFC-LNNL.md) | A especificação completa (formato, módulo 79, provas, comparação com UUID, Snowflake, ULID…). |
| [`vetores-teste.json`](vetores-teste.json) | Casos que toda implementação deve reproduzir. |

```
motor-id-interno/
├── RFC-LNNL.md                  especificação (rascunho de RFC)
├── vetores-teste.json           43 válidos + 11 inválidos com o erro esperado
├── imagens/                     figuras da especificação (SVG gerado)
├── analise/resultados.json      números usados no texto e nas figuras
├── ferramentas/
│   ├── analise_deteccao.py      taxas de detecção: cálculo exato + Monte Carlo
│   └── gerar_figuras.py         gera imagens/*.svg a partir da análise
└── referencia/
    ├── python/lnnl.py           implementação (só biblioteca padrão) + test_lnnl.py
    ├── javascript/lnnl.mjs      implementação ES2020 (Node e navegador) + lnnl.test.mjs
    └── sql/lnnl.sql             CHECK para PostgreSQL, MySQL/MariaDB e SQLite
```

## Uso rápido

Python:

```python
import lnnl

novo = lnnl.gerar('22')            # 'K22WF92MT5RQ7L' (exemplo; o sorteio é seguro)
lnnl.formatar(novo)                # 'K22W-F92M-T5R-Q7L'
lnnl.validar('k22w f92m t5r q7l', tipo_esperado='22')   # válido, canonico='K22WF92MT5RQ7L'
lnnl.validar('K22W-F92M-T5R-Q7M').erro                   # 'VERIFICADOR_INVALIDO'
```

JavaScript:

```js
import { gerar, formatar, validar } from './referencia/javascript/lnnl.mjs';
const id = gerar('22');
validar(formatar(id), '22').valido; // true
```

Regras que valem em qualquer stack:

1. Guarde **só a forma canônica** (14 caracteres, sem hífen) com restrição `UNIQUE` e `CHECK`.
2. Gere com sorteio seguro. Em caso de colisão, **insira e tente de novo**; nunca consulte
   antes e insira depois.
3. Valide antes de consultar e consulte **sempre** com autorização e filtro de *tenant*: o ID
   não é segredo.
4. Registre os tipos num arquivo só de acréscimos. **Nunca** use o tipo `93`.

## Reproduzir os testes, a análise e as figuras

```bash
cd motor-id-interno/referencia/python && python3 -m unittest test_lnnl.py
```

```bash
cd motor-id-interno/referencia/javascript && node --test lnnl.test.mjs
```

```bash
cd motor-id-interno && python3 ferramentas/analise_deteccao.py && python3 ferramentas/gerar_figuras.py
```

A análise leva cerca de 15 segundos e regrava `analise/resultados.json`. As figuras são
desenhadas a partir desse arquivo, então os números das imagens e do texto saem da mesma
fonte.

## Estado da verificação

| Item | Situação |
| :-- | :-- |
| Python (`test_lnnl.py`) | passa, incluindo as verificações exaustivas de troca e de transposição |
| JavaScript (`lnnl.test.mjs`) | passa (Node 24) |
| SQLite (`GLOB` + tipo) | testado |
| PostgreSQL (`lnnl_valido`) e MySQL | escritos, **ainda não executados num banco real** |

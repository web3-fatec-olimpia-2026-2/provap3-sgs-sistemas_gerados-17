# Treino para a P3 — ILP-037 (prova prática de 27/11/2026)

> Base: resumo/kit da **Aula 11** (`../Aula11_Retomada_Prova/RESUMO.md`).
> Regra da P3: o professor sorteia **uma função do seu código** e pergunta
> **(1) o que faz · (2) por que foi escrita assim · (3) o que muda se alterar**. Sem IA.

## Como usar (ordem sugerida — ~5 h no total, dá para dividir em 3 noites)

| # | Arquivo / pasta | O que treina | Tempo |
|---|---|---|---|
| 1 | [`01_reconhecer_o_padrao.md`](01_reconhecer_o_padrao.md) | olhar um cenário e nomear o padrão **pelo smell** | 20 min |
| 2 | [`02_prever_o_resultado.md`](02_prever_o_resultado.md) | ler código e prever a saída **sem rodar** | 30 min |
| 3 | [`03_achar_o_erro.md`](03_achar_o_erro.md) | erros conceituais típicos (padrão mal aplicado) | 30 min |
| 4 | [`exercicios/`](exercicios/) | **fazer**: 6 refatorações curtas + 1 desafio integrador | 2–3 h |
| 5 | [`04_explique_a_funcao.md`](04_explique_a_funcao.md) | **simulado oral**: o tripé o-que / por-quê / o-que-muda | 40 min |
| 6 | [`05_checklist_vespera.md`](05_checklist_vespera.md) | revisão final de 1 página | 15 min |

**Regras de treino (iguais às da prova):** sem IA, sem olhar o gabarito antes de tentar, e
**fale em voz alta** as explicações (a P3 é oral). Gabaritos ficam no fim de cada folha.

## Exercícios de código

Cada pasta em `exercicios/` tem:

```
exNN_nome/
├── enunciado.md      ← o que fazer (leia primeiro)
├── exercicio.py      ← SEU arquivo: tem o código com smell + os TODOs
├── gabarito.py       ← resolução comentada (só abra depois)
├── tests/            ← os mesmos testes servem para os dois
└── pytest.ini
```

Os testes rodam contra o `gabarito.py` por padrão. Para testar **a sua** resolução:

```bash
cd "Treino_Prova/exercicios/ex01_strategy_frete"
ALVO=exercicio ../../../.venv/bin/python -m pytest -v
```

Ver o gabarito passando (ou rodar tudo do projeto):

```bash
bash rodar_testes.sh Treino_Prova
```

| Exercício | Padrão/princípio | Domínio |
|---|---|---|
| ex01 | Strategy | frete de uma loja |
| ex02 | SRP + OCP | nota do pedido (texto/CSV/arquivo) |
| ex03 | Service × ViewModel | painel de pedidos (atrasado, cupom) |
| ex04 | Adapter | gateway de pagamento de terceiro |
| ex05 | Facade | checkout (estoque, pagamento, nota, e-mail) |
| ex06 | Decorator | embrulho, cartão, entrega expressa, cupom |
| ex07 | **Desafio integrador** (simulado da P3) | tudo junto: identificar, prever, explicar e estender |

> **Quer mais perguntas, em qualquer assunto?** Use o gerador determinístico:
> `python Gerador_Sistemas/gerar_sistema.py --assunto "..." --exercicio --testar`,
> ou pelo SGS: `python Gerador_Sistemas/tela_prompt.py` (abre em http://127.0.0.1:6100) e digite
> `sgs gerar <pedido>` com a caixa "Modo exercício" marcada. O sistema sai completo e correto (nada para
> corrigir) e vem com um **questionário** no formato da P3 (`exercicios.html` e, com Django, `/exercicios/`),
> cada resposta oculta atrás do botão **Ver resposta**
> (ver [`../Gerador_Sistemas/README.md`](../Gerador_Sistemas/README.md)).
>
> Por que um domínio **diferente** do Resort? Porque a P3 pergunta sobre o **seu** código, não o do
> professor. Treinar o mesmo movimento num cenário novo prova que você entendeu o padrão — não
> decorou o exemplo.

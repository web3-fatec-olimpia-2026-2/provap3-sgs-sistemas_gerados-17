# Academia Fit — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: para **estudo** (smell `antes_*.py`, ADRs, tripé) · código **comentado**.
> Padrões (3): Encapsulamento com @property, Adapter, Strategy.

## 1. Como o gerador decidiu

Assunto informado: _"academia em que o preço muda conforme o plano do aluno e o pagamento passa por uma API de terceiro"_

- Domínio escolhido: `academia` (palavras: academia, aluno)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| Adapter | terceiro, api de |
| Strategy | conforme o, plano, muda conforme |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Matricula com @property (base de tudo)
  integracao.py
  integracao_base.py
  antes_integracao.py
  politicas.py
  antes_politicas.py
tests/
  fabrica.py                ← cria Matricula válidas para os testes
  test_entidades.py
  test_integracao.py
  test_politicas.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Matricula` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/integracao.py` → `CobraJaAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Matricula`

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

### 4.1 Encapsulamento com @property

_Fundamento de OO — Aulas 02 e 03_ · `nucleo/entidades.py` · testes: `tests/test_entidades.py`

**Problema (smell):** Um atributo público aceita qualquer valor: `obj.meses = 0` ou `obj.mensalidade = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

**Conceito:** O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

| Peça | No código |
|---|---|
| Atributo interno | `self._meses`, `self._mensalidade`… |
| Getter | `@property` |
| Setter (a fechadura) | `@meses.setter` → `ValueError` se inválido |
| Dado calculado | `total` (só leitura) |

**Quando NÃO usar:** Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Matricula.meses` (setter) | Intercepta toda escrita em `meses` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.meses = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_meses`, o objeto pode nascer inválido. |
| `Matricula.total` | Calcula `meses × mensalidade` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `meses` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Adapter

_Padrão estrutural (GoF) — Aula 08_ · `nucleo/integracao.py` · antes: `nucleo/antes_integracao.py` · testes: `tests/test_integracao.py`

**Problema (smell):** O gateway `CobraJa` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.

**Conceito:** `CobraJaAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`).

| Peça | No código |
|---|---|
| Alvo (interface esperada) | `ProcessadorPagamento.processar(valor, token)` |
| Adaptado (terceiro) | `GatewayCobraJa.charge(payload)` |
| Adapter | `CobraJaAdapter` |
| Cliente limpo | `CheckoutService` |

**Quando NÃO usar:** Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `CobraJaAdapter.processar(valor, token)` | Converte o pedido de pagamento do sistema numa chamada `charge` e devolve o id ou levanta `PagamentoRecusado`. | Adapter: o gateway é de terceiro (não controlamos a assinatura); o adapter faz a peça caber e o `CheckoutService` perde o `if`. | Devolvendo o dict cru, o formato do terceiro vaza e a recusa passaria como sucesso; sem `round`, 19.99 viraria 1998 centavos. |


### 4.3 Strategy

_Padrão comportamental (GoF) — Aula 05_ · `nucleo/politicas.py` · antes: `nucleo/antes_politicas.py` · testes: `tests/test_politicas.py`

**Problema (smell):** `CobrancaAntiga.valor()` tem um `if/elif` por tipo de plano que cresce a cada regra nova — cada uma obriga a reabrir a classe.

**Conceito:** Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`.

| Peça | No código |
|---|---|
| Contexto | `Cobranca` |
| Interface da estratégia | `aplicar(base)` |
| Estratégias | `PoliticaMensal`, `PoliticaUniversitario`, `PoliticaCorporativo` |
| Estratégia nova (OCP) | `PoliticaFamilia` |
| Versão pythônica | `CobrancaComFuncao` (estratégia = função) |

**Quando NÃO usar:** Uma regra só, que nunca varia → uma função ou constante basta (Strategy seria cerimônia). Em Python a estratégia pode ser uma função.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Cobranca.valor()` | Pega o `total` da Matricula e devolve o valor depois da política aplicada. | Strategy: a família de regras de tipo de plano varia; cada uma é uma classe e o contexto delega, sem `if`. | Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/academia_fit__adapter-strategy/especificacao.json --exercicio --nome academia_fit__adapter-strategy_treino`

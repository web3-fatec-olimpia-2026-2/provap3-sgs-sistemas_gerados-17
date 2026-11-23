# Hotel Resort — sistema de estudo gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v1.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Padrões: Encapsulamento com @property, Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), Adapter, Decorator.

## 1. Como o gerador decidiu

Assunto informado: _"Hotel com a exposição de uma API de consulta sobre a reserva. Padrão de projeto deve ser MVT, e a URL com as Migrations. Faça um exemplo com a soma do Decorator para as hospedagens"_

- Domínio escolhido: `hotel` (palavras: hotel)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web) | mvt |
| Adapter | api de |
| Decorator | decorator |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Reserva com @property (base de tudo)
  relatorio.py
  antes_relatorio.py
  integracao.py
  integracao_base.py
  antes_integracao.py
  extras.py
  antes_extras.py
tests/
  fabrica.py                ← cria Reserva válidas para os testes
  test_entidades.py
  test_relatorio.py
  test_integracao.py
  test_extras.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Reserva` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)
- `nucleo/integracao.py` → `PagaFacilAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/extras.py` → `ReservaBase` embrulha a `Reserva`; os `Com…` embrulham o componente

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

### 4.1 Encapsulamento com @property

_Fundamento de OO — Aulas 02 e 03_ · `nucleo/entidades.py` · testes: `tests/test_entidades.py`

**Problema (smell):** Um atributo público aceita qualquer valor: `obj.diarias = 0` ou `obj.valor_diaria = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

**Conceito:** O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

| Peça | No código |
|---|---|
| Atributo interno | `self._diarias`, `self._valor_diaria`… |
| Getter | `@property` |
| Setter (a fechadura) | `@diarias.setter` → `ValueError` se inválido |
| Dado calculado | `total` (só leitura) |

**Quando NÃO usar:** Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Reserva.diarias` (setter) | Intercepta toda escrita em `diarias` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.diarias = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_diarias`, o objeto pode nascer inválido. |
| `Reserva.total` | Calcula `diarias × valor_diaria` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `diarias` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web)

_Arquitetura — Aula 07_ · `nucleo/relatorio.py` · antes: `nucleo/antes_relatorio.py` · testes: `tests/test_relatorio.py`

**Problema (smell):** `relatorio_view` mistura a regra (desconto por tipo de hóspede) com a apresentação (texto); para testar a conta é preciso chamar a view e ler texto.

**Conceito:** `RelatorioService.calcular()` faz só a regra e devolve DADOS; a view fica fina (chama e formata); a mesma regra serve a API (`relatorio_api`). No Django: models = dado, views = regra/orquestração, template = apresentação, services.py = a regra complexa.

| Peça | No código |
|---|---|
| Regra (sem web) | `RelatorioService` |
| View fina | `relatorio_view` |
| Outra apresentação | `relatorio_api` |

**Quando NÃO usar:** View que só lista e renderiza não precisa de Service — só há Service quando há cálculo, decisão ou orquestração de vários passos.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `RelatorioService.calcular()` | Aplica o fator de cada tipo de hóspede e devolve `(linhas, total_geral)`. | A regra fica fora da web: testável sem request/servidor e reaproveitável pela API. | Se passar a receber `request` ou devolver texto, volta a exigir a web para testar e a API teria que duplicar a conta. |


### 4.3 Adapter

_Padrão estrutural (GoF) — Aula 08_ · `nucleo/integracao.py` · antes: `nucleo/antes_integracao.py` · testes: `tests/test_integracao.py`

**Problema (smell):** O gateway `PagaFacil` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.

**Conceito:** `PagaFacilAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`).

| Peça | No código |
|---|---|
| Alvo (interface esperada) | `ProcessadorPagamento.processar(valor, token)` |
| Adaptado (terceiro) | `GatewayPagaFacil.charge(payload)` |
| Adapter | `PagaFacilAdapter` |
| Cliente limpo | `CheckoutService` |

**Quando NÃO usar:** Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `PagaFacilAdapter.processar(valor, token)` | Converte o pedido de pagamento do sistema numa chamada `charge` e devolve o id ou levanta `PagamentoRecusado`. | Adapter: o gateway é de terceiro (não controlamos a assinatura); o adapter faz a peça caber e o `CheckoutService` perde o `if`. | Devolvendo o dict cru, o formato do terceiro vaza e a recusa passaria como sucesso; sem `round`, 19.99 viraria 1998 centavos. |


### 4.4 Decorator

_Padrão estrutural (GoF) — Aula 10_ · `nucleo/extras.py` · antes: `nucleo/antes_extras.py` · testes: `tests/test_extras.py`

**Problema (smell):** `preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

**Conceito:** Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComTransfer(ComCafeDaManha(ReservaBase(item)))`.

| Peça | No código |
|---|---|
| Componente | `ReservaBase(item)` |
| Decorador base (delega) | `Adicional` |
| Decoradores que somam | `ComCafeDaManha`, `ComTransfer`, `ComLateCheckout` |
| Decorador que multiplica | `ComDescontoFidelidade` |

**Quando NÃO usar:** Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComCafeDaManha.preco()` | Pergunta o preço ao componente de dentro e soma R$ 40.00. | Decorator: o extra é opcional e combinável; mantendo a interface, empilha. | Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/hotel_resort__service-adapter-decorator/especificacao.json --exercicio --nome hotel_resort__service-adapter-decorator_treino`

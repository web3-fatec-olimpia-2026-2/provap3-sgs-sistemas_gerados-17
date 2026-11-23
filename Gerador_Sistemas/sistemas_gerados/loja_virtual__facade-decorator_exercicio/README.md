# Loja Virtual — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: para **estudo** (smell `antes_*.py`, ADRs, tripé) · código **comentado**.
> Padrões (3): Encapsulamento com @property, Decorator, Facade.

## 1. Como o gerador decidiu

Escolha explícita: domínio **loja**, padrões: encapsulamento, decorator, facade.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Pedido com @property (base de tudo)
  extras.py
  antes_extras.py
  atendimento.py
  atendimento_base.py
  antes_atendimento.py
tests/
  fabrica.py                ← cria Pedido válidas para os testes
  test_entidades.py
  test_extras.py
  test_atendimento.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
gabarito/nucleo/            ← resolução completa (em nucleo/ ficam assinaturas com TODO)
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Pedido` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/extras.py` → `PedidoBase` embrulha a `Pedido`; os `Com…` embrulham o componente
- `nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

### 4.1 Encapsulamento com @property

_Fundamento de OO — Aulas 02 e 03_ · `nucleo/entidades.py` · testes: `tests/test_entidades.py`

**Problema (smell):** Um atributo público aceita qualquer valor: `obj.quantidade = 0` ou `obj.preco_unitario = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

**Conceito:** O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

| Peça | No código |
|---|---|
| Atributo interno | `self._quantidade`, `self._preco_unitario`… |
| Getter | `@property` |
| Setter (a fechadura) | `@quantidade.setter` → `ValueError` se inválido |
| Dado calculado | `total` (só leitura) |

**Quando NÃO usar:** Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Pedido.quantidade` (setter) | Intercepta toda escrita em `quantidade` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.quantidade = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_quantidade`, o objeto pode nascer inválido. |
| `Pedido.total` | Calcula `quantidade × preco_unitario` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `quantidade` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Decorator

_Padrão estrutural (GoF) — Aula 10_ · `nucleo/extras.py` · antes: `nucleo/antes_extras.py` · testes: `tests/test_extras.py`

**Problema (smell):** `preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

**Conceito:** Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComCartao(ComEmbrulho(PedidoBase(item)))`.

| Peça | No código |
|---|---|
| Componente | `PedidoBase(item)` |
| Decorador base (delega) | `Adicional` |
| Decoradores que somam | `ComEmbrulho`, `ComCartao`, `ComEntregaExpressa` |
| Decorador que multiplica | `ComCupom10` |

**Quando NÃO usar:** Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComEmbrulho.preco()` | Pergunta o preço ao componente de dentro e soma R$ 15.00. | Decorator: o extra é opcional e combinável; mantendo a interface, empilha. | Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda. |


### 4.3 Facade

_Padrão estrutural (GoF) — Aula 09_ · `nucleo/atendimento.py` · antes: `nucleo/antes_atendimento.py` · testes: `tests/test_atendimento.py`

**Problema (smell):** `atender_na_mao` conhece 5 subsistemas, a ordem e as regras de aborto; cada tela que conclui um atendimento repetiria tudo isso.

**Conceito:** `AtendimentoFacade.concluir(recurso, item)` é o balcão único: disponibilidade → cálculo → cobrança → registro → notificação, DELEGANDO a cada subsistema.

| Peça | No código |
|---|---|
| Subsistemas | `Disponibilidade`, `Calculadora`, `Pagamentos`, `Registro`, `Notificador` |
| Fachada | `AtendimentoFacade.concluir(...)` |
| Antes | `atender_na_mao(...)` |

**Quando NÃO usar:** 1–2 passos num lugar só → uma função basta. Se a fachada passar a executar regra (em vez de delegar) vira God object. Ela não proíbe usar os subsistemas direto.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `AtendimentoFacade.concluir(recurso, item)` | Orquestra os 5 subsistemas na ordem e aborta se indisponível ou se o pagamento for recusado. | Facade: esconde a orquestração; o cliente conhece um objeto em vez de cinco; a fachada delega, não reimplementa. | Um passo novo entra só aqui; mover o cálculo para dentro dela a transforma em God object. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/loja_virtual__facade-decorator_exercicio/especificacao.json --exercicio --nome loja_virtual__facade-decorator_exercicio_treino`



## 7. Modo exercício

Em `nucleo/`, os módulos de **decorator, facade** estão só com as **assinaturas** e
`raise NotImplementedError("TODO ...")` (as docstrings ficaram como pista). Os arquivos
`antes_*.py` e as peças prontas (`*_base.py`) estão completos.

```bash
python -m pytest                 # a SUA resolução (começa vermelha)
ALVO=gabarito python -m pytest   # a resolução completa (verde)
```

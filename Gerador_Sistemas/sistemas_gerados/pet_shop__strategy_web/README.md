# Pet Shop — sistema de estudo gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v1.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Padrões: Encapsulamento com @property, Strategy.

## 1. Como o gerador decidiu

Assunto informado: _"sistema de pet shop com banho que varia conforme o porte"_

- Domínio escolhido: `generico` (nenhuma palavra de domínio reconhecida → domínio genérico)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| Strategy | varia, conforme o |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Atendimento com @property (base de tudo)
  politicas.py
  antes_politicas.py
tests/
  fabrica.py                ← cria Atendimento válidas para os testes
  test_entidades.py
  test_politicas.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
web/                        ← projeto Django (MVT) que usa o núcleo
  atendimentos/  models · forms · services · viewmodels · views · urls · templates/ · tests/
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Atendimento` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Atendimento`
- `web/atendimentos/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

### 4.1 Encapsulamento com @property

_Fundamento de OO — Aulas 02 e 03_ · `nucleo/entidades.py` · testes: `tests/test_entidades.py`

**Problema (smell):** Um atributo público aceita qualquer valor: `obj.quantidade = 0` ou `obj.valor_unitario = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

**Conceito:** O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

| Peça | No código |
|---|---|
| Atributo interno | `self._quantidade`, `self._valor_unitario`… |
| Getter | `@property` |
| Setter (a fechadura) | `@quantidade.setter` → `ValueError` se inválido |
| Dado calculado | `total` (só leitura) |

**Quando NÃO usar:** Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Atendimento.quantidade` (setter) | Intercepta toda escrita em `quantidade` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.quantidade = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_quantidade`, o objeto pode nascer inválido. |
| `Atendimento.total` | Calcula `quantidade × valor_unitario` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `quantidade` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Strategy

_Padrão comportamental (GoF) — Aula 05_ · `nucleo/politicas.py` · antes: `nucleo/antes_politicas.py` · testes: `tests/test_politicas.py`

**Problema (smell):** `CobrancaAntiga.valor()` tem um `if/elif` por tipo de cliente que cresce a cada regra nova — cada uma obriga a reabrir a classe.

**Conceito:** Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`.

| Peça | No código |
|---|---|
| Contexto | `Cobranca` |
| Interface da estratégia | `aplicar(base)` |
| Estratégias | `PoliticaComum`, `PoliticaEspecial`, `PoliticaParceiro` |
| Estratégia nova (OCP) | `PoliticaVip` |
| Versão pythônica | `CobrancaComFuncao` (estratégia = função) |

**Quando NÃO usar:** Uma regra só, que nunca varia → uma função ou constante basta (Strategy seria cerimônia). Em Python a estratégia pode ser uma função.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Cobranca.valor()` | Pega o `total` da Atendimento e devolve o valor depois da política aplicada. | Strategy: a família de regras de tipo de cliente varia; cada uma é uma classe e o contexto delega, sem `if`. | Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/pet_shop__strategy_web/especificacao.json --exercicio --nome pet_shop__strategy_web_treino`

## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/atendimentos/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/atendimentos/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/atendimentos/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/atendimentos/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/atendimentos/views.py` | **fina**: busca → Service/ViewModel → render |
| Template | `web/atendimentos/templates/atendimentos/` | só exibe |

Pegadinha testada em `tests/test_models.py`: `save()` sozinho **não** valida — quem valida é
`full_clean()` / o `ModelForm`.

```bash
cd web
python -m pytest -v
python manage.py makemigrations atendimentos
python manage.py migrate
python manage.py runserver
```

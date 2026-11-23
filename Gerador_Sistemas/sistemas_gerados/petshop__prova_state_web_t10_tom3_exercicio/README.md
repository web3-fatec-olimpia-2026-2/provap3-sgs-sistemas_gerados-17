# PETShop — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: para **estudo** (smell `antes_*.py`, ADRs, tripé) · código **comentado**.
> Padrões (10): Encapsulamento com @property, Polimorfismo (herança + sobrescrita), SRP + OCP (separar responsabilidades), Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), MVVM (ViewModel), Adapter, Decorator, Facade, State, Strategy.

## 1. Como o gerador decidiu

Escolha explícita: domínio **generico (personalizado por especificacao.json)**, padrões: encapsulamento, polimorfismo, srp, service, mvvm, adapter, decorator, facade, state, strategy.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Petshop com @property (base de tudo)
  categorias.py
  antes_categorias.py
  recibo.py
  antes_recibo.py
  relatorio.py
  antes_relatorio.py
  painel.py
  antes_painel.py
  integracao.py
  integracao_base.py
  antes_integracao.py
  extras.py
  antes_extras.py
  atendimento.py
  atendimento_base.py
  antes_atendimento.py
  situacao.py
  antes_situacao.py
  politicas.py
  antes_politicas.py
tests/
  fabrica.py                ← cria Petshop válidas para os testes
  test_entidades.py
  test_categorias.py
  test_recibo.py
  test_relatorio.py
  test_painel.py
  test_integracao.py
  test_extras.py
  test_atendimento.py
  test_situacao.py
  test_politicas.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
requirements.txt            ← TODAS as dependências (Django, pytest, pytest-django)
iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin
web/                        ← projeto Django (MVT) que usa o núcleo
  .env.example              ← modelo do .env (chave secreta, admin, porta)
  petshops/  models · forms · services · viewmodels · views · urls · templates/ · tests/
exercicios.html             ← questionário de revisão (resposta oculta em "Ver resposta")
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Petshop` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/categorias.py` é independente da entidade (só herança + sobrescrita)
- `nucleo/recibo.py` → `ReciboFormatter` lê a `Petshop`; `nucleo/antes_recibo.py` herda dela
- `nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)
- `nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict
- `nucleo/integracao.py` → `PagaJaAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/extras.py` → `PetshopBase` embrulha a `Petshop`; os `Com…` embrulham o componente
- `nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`
- `nucleo/situacao.py` → `SituacaoPetshop` TEM-UMA `Petshop` e um `Estado`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Petshop`
- `web/petshops/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

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
| `Petshop.quantidade` (setter) | Intercepta toda escrita em `quantidade` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.quantidade = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_quantidade`, o objeto pode nascer inválido. |
| `Petshop.total` | Calcula `quantidade × valor_unitario` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `quantidade` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Polimorfismo (herança + sobrescrita)

_Fundamento de OO — Aula 04_ · `nucleo/categorias.py` · antes: `nucleo/antes_categorias.py` · testes: `tests/test_categorias.py`

**Problema (smell):** `imprimir_preco(tipo)` decide o texto com `if/elif` por categoria; cada categoria nova obriga a editar a função (e arriscar as que já funcionavam).

**Conceito:** Cada categoria é uma subclasse de `Basico` que SOBRESCREVE `descricao()` e `preco_unidade()`. `imprimir_preco(categoria)` só chama os métodos — o Python escolhe a versão pelo tipo real do objeto, em tempo de execução.

| Peça | No código |
|---|---|
| Classe base | `Basico` |
| Subtipos que sobrescrevem | `Intermediario`, `Premium` |
| Subtipo que não sobrescreve (usa o da mãe) | `BasicoPadrao` |
| Função polimórfica | `imprimir_preco(categoria)` |
| Categoria nova | `Personalizado` |

**Quando NÃO usar:** Se as categorias só diferem num número (sem comportamento próprio), um atributo ou tabela basta. Herança só para relação É-UM; TEM-UM é composição.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `imprimir_preco(categoria)` | Monta "descrição: R$ preço por unidade" de qualquer categoria. | Polimorfismo: não pergunta o tipo (zero `if`); cada subclasse responde a seu modo. | Com `if/elif`, o `Personalizado` exigiria editar a função; hoje entra sem mudar uma linha. Se um subtipo não sobrescrever, usa o método da mãe. |


### 4.3 SRP + OCP (separar responsabilidades)

_Princípios SOLID — Aula 06_ · `nucleo/recibo.py` · antes: `nucleo/antes_recibo.py` · testes: `tests/test_recibo.py`

**Problema (smell):** `PetshopFazTudo` calcula, formata o recibo e grava em arquivo: três motivos para mudar na mesma classe.

**Conceito:** `Petshop` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); `ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova (`ReciboCsvFormatter`) → OCP.

| Peça | No código |
|---|---|
| Negócio | `Petshop` (nucleo/entidades.py) |
| Apresentação | `ReciboFormatter` |
| Extensão (OCP) | `ReciboCsvFormatter` |
| Infraestrutura | `ArquivoRepository` |
| Junta as peças | `emitir_recibo(...)` |

**Quando NÃO usar:** SRP não é uma classe por método: separar "calcula", "soma", "arredonda" em classes é tão ruim quanto juntar tudo. A unidade é a responsabilidade (motivo para mudar).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ReciboFormatter.formatar(item)` | Recebe a Petshop e devolve o texto do recibo. | SRP: layout tem motivo de mudança próprio; recebe a entidade por parâmetro e só lê. | Layout novo mexe só aqui; formato novo é outra classe; devolver isto para a Petshop recriaria os 3 motivos para mudar. |


### 4.4 Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web)

_Arquitetura — Aula 07_ · `nucleo/relatorio.py` · antes: `nucleo/antes_relatorio.py` · testes: `tests/test_relatorio.py`

**Problema (smell):** `relatorio_view` mistura a regra (desconto por tipo de cliente) com a apresentação (texto); para testar a conta é preciso chamar a view e ler texto.

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
| `RelatorioService.calcular()` | Aplica o fator de cada tipo de cliente e devolve `(linhas, total_geral)`. | A regra fica fora da web: testável sem request/servidor e reaproveitável pela API. | Se passar a receber `request` ou devolver texto, volta a exigir a web para testar e a API teria que duplicar a conta. |


### 4.5 MVVM (ViewModel)

_Arquitetura — Aulas 08 e 09_ · `nucleo/painel.py` · antes: `nucleo/antes_painel.py` · testes: `tests/test_painel.py`

**Problema (smell):** `tela_painel` decide no meio do desenho o status, o rótulo do botão, o "R$" e o rodapé "SEM DISPONIBILIDADE" — só dá para testar lendo a tela.

**Conceito:** `ItemViewModel` / `PainelVM` traduzem o dado cru em dado pronto (`status_label`, `acao_label`, `preco_formatado`, `rodape`); a View só costura. No Django não há binding: o ViewModel é preparação chamada antes do `render`.

| Peça | No código |
|---|---|
| Model (dado cru) | dicts em `ITENS` |
| ViewModel de um item | `ItemViewModel` |
| ViewModel do painel | `PainelVM` |
| View burra | `tela_painel_mvvm` |

**Quando NÃO usar:** Tela que mostra o dado como está não precisa de ViewModel. Service × ViewModel: regra de negócio (o que é verdade) × lógica de exibição (como aparece).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ItemViewModel.__init__` | Transforma o dict cru em textos prontos para a tela (status, ação, preço formatado). | MVVM: a decisão de como mostrar fica num lugar só e testável sem renderizar. | Status novo muda só o ViewModel; voltar os `if` para a tela obriga a ler HTML para testar. |


### 4.6 Adapter

_Padrão estrutural (GoF) — Aula 08_ · `nucleo/integracao.py` · antes: `nucleo/antes_integracao.py` · testes: `tests/test_integracao.py`

**Problema (smell):** O gateway `PagaJa` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.

**Conceito:** `PagaJaAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`).

| Peça | No código |
|---|---|
| Alvo (interface esperada) | `ProcessadorPagamento.processar(valor, token)` |
| Adaptado (terceiro) | `GatewayPagaJa.charge(payload)` |
| Adapter | `PagaJaAdapter` |
| Cliente limpo | `CheckoutService` |

**Quando NÃO usar:** Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `PagaJaAdapter.processar(valor, token)` | Converte o pedido de pagamento do sistema numa chamada `charge` e devolve o id ou levanta `PagamentoRecusado`. | Adapter: o gateway é de terceiro (não controlamos a assinatura); o adapter faz a peça caber e o `CheckoutService` perde o `if`. | Devolvendo o dict cru, o formato do terceiro vaza e a recusa passaria como sucesso; sem `round`, 19.99 viraria 1998 centavos. |


### 4.7 Decorator

_Padrão estrutural (GoF) — Aula 10_ · `nucleo/extras.py` · antes: `nucleo/antes_extras.py` · testes: `tests/test_extras.py`

**Problema (smell):** `preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

**Conceito:** Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComEmbalagem(ComUrgente(PetshopBase(item)))`.

| Peça | No código |
|---|---|
| Componente | `PetshopBase(item)` |
| Decorador base (delega) | `Adicional` |
| Decoradores que somam | `ComUrgente`, `ComEmbalagem`, `ComSeguro` |
| Decorador que multiplica | `ComDesconto10` |

**Quando NÃO usar:** Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComUrgente.preco()` | Pergunta o preço ao componente de dentro e soma R$ 30.00. | Decorator: o extra é opcional e combinável; mantendo a interface, empilha. | Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda. |


### 4.8 Facade

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


### 4.9 State

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/situacao.py` · antes: `nucleo/antes_situacao.py` · testes: `tests/test_situacao.py`

**Problema (smell):** `SituacaoAntiga` repete a mesma escada de `if/elif` sobre `self.status` em `confirmar`, `concluir` e `cancelar`.

**Conceito:** Cada estado é uma classe (`Aberto`, `Confirmado`, `Concluido`, `Cancelado`) que sabe as SUAS transições; `SituacaoPetshop` (contexto) guarda o estado atual e delega. Transição proibida levanta `TransicaoInvalida`.

| Peça | No código |
|---|---|
| Contexto | `SituacaoPetshop` |
| Estado base | `Estado` (tudo proibido por padrão) |
| Estados | `Aberto`, `Confirmado`, `Concluido`, `Cancelado` |

**Quando NÃO usar:** Dois estados e uma regra (um booleano basta). State × Strategy: no State o próprio estado troca o objeto do contexto; no Strategy quem escolhe é o cliente.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Aberto.confirmar(contexto)` | Troca o estado do contexto para `Confirmado`. | State: a transição pertence ao estado de origem; o contexto só delega. | Sem sobrescrever, valeria o padrão da base (TransicaoInvalida); trocando para `Concluido`, pularia a confirmação. |


### 4.10 Strategy

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
| `Cobranca.valor()` | Pega o `total` da Petshop e devolve o valor depois da política aplicada. | Strategy: a família de regras de tipo de cliente varia; cada uma é uma classe e o contexto delega, sem `if`. | Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/petshop__prova_state_web_t10_tom3_exercicio/especificacao.json --exercicio --nome petshop__prova_state_web_t10_tom3_exercicio_treino`

## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/petshops/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/petshops/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/petshops/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/petshops/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/petshops/views.py` | **fina**: busca → Service/ViewModel → render |
| Template | `web/petshops/templates/petshops/` | só exibe |

Pegadinha testada em `tests/test_models.py`: `save()` sozinho **não** valida — quem valida é
`full_clean()` / o `ModelForm`.

### Subir o site (no WSL, dentro desta pasta)

Tudo de uma vez — cria o `.venv`, instala o `requirements.txt`, copia `web/.env.example` para
`web/.env` (com uma chave secreta nova), roda as migrations, cria o superusuário e sobe o servidor:

```bash
bash iniciar.sh
```

O site abre sozinho em **modo PWA** — uma janela de app isolada das abas (Edge/Chrome `--app`); com
`PWA=0` no `web/.env` abre numa aba comum, e `ABRIR=0 bash iniciar.sh` não abre nada. Endereços:
http://127.0.0.1:8000/ (site) e http://127.0.0.1:8000/admin/ (usuário e senha do `web/.env`:
`DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD`). Outra porta: `bash iniciar.sh tudo 8001`.
O site é instalável (manifest em `/manifest.webmanifest`, service worker em `/sw.js`, ícones em `static/`).

Os mesmos passos, separados (cada um pode ser repetido sem estragar nada):

```bash
bash iniciar.sh venv        # cria .venv nesta pasta (se não existir)
bash iniciar.sh deps        # instala requirements.txt (se faltar algo)
bash iniciar.sh env         # web/.env a partir de web/.env.example (não sobrescreve)
bash iniciar.sh migrar      # makemigrations petshops + migrate
bash iniciar.sh admin       # cria/atualiza o superusuário com os dados do web/.env
bash iniciar.sh testar      # testes do núcleo e da web
bash iniciar.sh rodar 8000  # sobe o servidor (Ctrl+C para parar)
```

Sem o script (comandos puros do Django):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp web/.env.example web/.env
cd web
python manage.py makemigrations petshops && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o da raiz do projeto): `VENV=/caminho/.venv bash iniciar.sh`.

## 7. Modo exercício (questionário)

O código deste sistema está **completo e correto** — não há nada para corrigir. O exercício é um
**questionário de revisão** no formato da P3, com 51 perguntas sobre os padrões aplicados aqui
(o smell, como foi aplicado, o tripé de cada função, quando não usar, a alternativa descartada).
Cada resposta fica **oculta** até você clicar em **Ver resposta**.

- Abra `exercicios.html` (nesta pasta) direto no navegador — não precisa de servidor.
- Com o site no ar, o mesmo questionário está em `/exercicios/` (link **Exercícios** no topo ou na lista).

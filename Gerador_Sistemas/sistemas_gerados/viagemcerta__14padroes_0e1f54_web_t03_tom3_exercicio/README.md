# ViagemCerta — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: para **estudo** (smell `antes_*.py`, ADRs, tripé) · código **comentado**.
> Padrões (14): Encapsulamento com @property, Polimorfismo (herança + sobrescrita), SRP + OCP (separar responsabilidades), Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), MVVM (ViewModel), Singleton, Factory Method, Abstract Factory, Adapter, Composite, Decorator, Facade, State, Strategy.

## 1. Como o gerador decidiu

Assunto informado: _"agencia_viagem"_

- Domínio escolhido: `agencia_viagem` (palavras: viagem, agencia)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| (grupo prova) | — |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Viagcert com @property (base de tudo)
  categorias.py
  antes_categorias.py
  recibo.py
  antes_recibo.py
  relatorio.py
  antes_relatorio.py
  painel.py
  antes_painel.py
  configuracao.py
  antes_configuracao.py
  avisos.py
  antes_avisos.py
  kits.py
  antes_kits.py
  integracao.py
  integracao_base.py
  antes_integracao.py
  pacotes.py
  antes_pacotes.py
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
  fabrica.py                ← cria Viagcert válidas para os testes
  test_entidades.py
  test_categorias.py
  test_recibo.py
  test_relatorio.py
  test_painel.py
  test_configuracao.py
  test_avisos.py
  test_kits.py
  test_integracao.py
  test_pacotes.py
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
  viagcerts/  settings · models · forms · services · viewmodels · views · api (REST) · urls · templates/ · tests/
exercicios.html             ← questionário de revisão (resposta oculta em "Ver resposta")
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Viagcert` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/categorias.py` é independente da entidade (só herança + sobrescrita)
- `nucleo/recibo.py` → `ReciboFormatter` lê a `Viagcert`; `nucleo/antes_recibo.py` herda dela
- `nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)
- `nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict
- `nucleo/configuracao.py` → `Configuracao` única, lida por `total_com_taxa` (usa `item.total` da `Viagcert`) e `formatar`
- `nucleo/avisos.py` → cada `Avisador…` cria o seu `Canal…`; `avisar` lê `viajante` e `total` da `Viagcert`
- `nucleo/kits.py` → `montar_relatorio` pede as peças a um `Kit…` e lê as `Viagcert`s
- `nucleo/integracao.py` → `PagaTurAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/pacotes.py` → `Unitario` embrulha a `Viagcert`; `Pacote` guarda componentes
- `nucleo/extras.py` → `ViagcertBase` embrulha a `Viagcert`; os `Com…` embrulham o componente
- `nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`
- `nucleo/situacao.py` → `SituacaoViagcert` TEM-UMA `Viagcert` e um `Estado`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Viagcert`
- `web/viagcerts/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

### 4.1 Encapsulamento com @property

_Fundamento de OO — Aulas 02 e 03_ · `nucleo/entidades.py` · testes: `tests/test_entidades.py`

**Problema (smell):** Um atributo público aceita qualquer valor: `obj.noites = 0` ou `obj.valor_noite = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

**Conceito:** O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

| Peça | No código |
|---|---|
| Atributo interno | `self._noites`, `self._valor_noite`… |
| Getter | `@property` |
| Setter (a fechadura) | `@noites.setter` → `ValueError` se inválido |
| Dado calculado | `total` (só leitura) |

**Quando NÃO usar:** Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Viagcert.noites` (setter) | Intercepta toda escrita em `noites` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.noites = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_noites`, o objeto pode nascer inválido. |
| `Viagcert.total` | Calcula `noites × valor_noite` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `noites` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Polimorfismo (herança + sobrescrita)

_Fundamento de OO — Aula 04_ · `nucleo/categorias.py` · antes: `nucleo/antes_categorias.py` · testes: `tests/test_categorias.py`

**Problema (smell):** `imprimir_preco(tipo)` decide o texto com `if/elif` por categoria; cada categoria nova obriga a editar a função (e arriscar as que já funcionavam).

**Conceito:** Cada categoria é uma subclasse de `Economico` que SOBRESCREVE `descricao()` e `preco_unidade()`. `imprimir_preco(categoria)` só chama os métodos — o Python escolhe a versão pelo tipo real do objeto, em tempo de execução.

| Peça | No código |
|---|---|
| Classe base | `Economico` |
| Subtipos que sobrescrevem | `Executivo`, `Luxo` |
| Subtipo que não sobrescreve (usa o da mãe) | `EconomicoPadrao` |
| Função polimórfica | `imprimir_preco(categoria)` |
| Categoria nova | `Aventura` |

**Quando NÃO usar:** Se as categorias só diferem num número (sem comportamento próprio), um atributo ou tabela basta. Herança só para relação É-UM; TEM-UM é composição.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `imprimir_preco(categoria)` | Monta "descrição: R$ preço por noite" de qualquer categoria. | Polimorfismo: não pergunta o tipo (zero `if`); cada subclasse responde a seu modo. | Com `if/elif`, o `Aventura` exigiria editar a função; hoje entra sem mudar uma linha. Se um subtipo não sobrescrever, usa o método da mãe. |


### 4.3 SRP + OCP (separar responsabilidades)

_Princípios SOLID — Aula 06_ · `nucleo/recibo.py` · antes: `nucleo/antes_recibo.py` · testes: `tests/test_recibo.py`

**Problema (smell):** `ViagcertFazTudo` calcula, formata o recibo e grava em arquivo: três motivos para mudar na mesma classe.

**Conceito:** `Viagcert` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); `ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova (`ReciboCsvFormatter`) → OCP.

| Peça | No código |
|---|---|
| Negócio | `Viagcert` (nucleo/entidades.py) |
| Apresentação | `ReciboFormatter` |
| Extensão (OCP) | `ReciboCsvFormatter` |
| Infraestrutura | `ArquivoRepository` |
| Junta as peças | `emitir_recibo(...)` |

**Quando NÃO usar:** SRP não é uma classe por método: separar "calcula", "soma", "arredonda" em classes é tão ruim quanto juntar tudo. A unidade é a responsabilidade (motivo para mudar).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ReciboFormatter.formatar(item)` | Recebe a Viagcert e devolve o texto do recibo. | SRP: layout tem motivo de mudança próprio; recebe a entidade por parâmetro e só lê. | Layout novo mexe só aqui; formato novo é outra classe; devolver isto para a Viagcert recriaria os 3 motivos para mudar. |


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

**Problema (smell):** `tela_painel` decide no meio do desenho o status, o rótulo do botão, o "R$" e o rodapé "ESGOTADO - nenhum voo com assento" — só dá para testar lendo a tela.

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


### 4.6 Singleton

_Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/configuracao.py` · antes: `nucleo/antes_configuracao.py` · testes: `tests/test_configuracao.py`

**Problema (smell):** Cada parte do sistema cria a sua `ConfiguracaoAntiga()`; mudar a taxa no caixa não muda no relatório — dois lugares cobrando valores diferentes.

**Conceito:** `Configuracao.__new__` devolve SEMPRE o mesmo objeto (guardado em `_instancia`); quem precisa chama `Configuracao()` e recebe a única que existe. `reiniciar()` existe só para os testes.

| Peça | No código |
|---|---|
| Singleton | `Configuracao` (`__new__` + `_instancia`) |
| Clientes | `total_com_taxa(item)`, `formatar(valor)` |
| Antes | `CONFIG_DO_CAIXA` × `CONFIG_DO_RELATORIO` |

**Quando NÃO usar:** Em Python um módulo já é único: uma variável no módulo resolve sem cerimônia. Singleton é estado global escondido — dificulta testes; prefira injetar a dependência quando der.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Configuracao.__new__` | Cria o objeto na primeira chamada e devolve o mesmo nas seguintes. | Singleton: `__new__` decide qual objeto sai (antes do `__init__`); guardar na classe garante um só. | Sem o `if _instancia is None`, cada chamada criaria outro objeto e as partes divergiriam; com um `__init__` atribuindo valores, cada `Configuracao()` apagaria as mudanças. |


### 4.7 Factory Method

_Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/avisos.py` · antes: `nucleo/antes_avisos.py` · testes: `tests/test_avisos.py`

**Problema (smell):** `avisar_antigo(item, canal)` tem um `if/elif` para CRIAR o canal certo no meio do algoritmo — canal novo reabre a função.

**Conceito:** `Avisador.avisar(item)` é o algoritmo comum; o passo que varia — QUAL canal criar — é o método fábrica `criar_canal()`, sobrescrito por `AvisadorEmail`, `AvisadorSms`… O criador não conhece as classes concretas dos produtos.

| Peça | No código |
|---|---|
| Produto | `Canal` → `CanalEmail`, `CanalSms` |
| Criador | `Avisador` (com `avisar`) |
| Método fábrica | `criar_canal()` |
| Criadores concretos | `AvisadorEmail`, `AvisadorSms` |
| Extensão (OCP) | `CanalWhatsapp` + `AvisadorWhatsapp` |

**Quando NÃO usar:** Um tipo só de produto, ou escolha resolvida por um dicionário `{nome: Classe}` — em Python dá para passar a própria classe como parâmetro.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Avisador.avisar(item)` | Monta a mensagem da Viagcert e envia pelo canal que `criar_canal()` devolver. | Factory Method: o algoritmo é comum e só a criação do produto varia — fica num método que a subclasse sobrescreve. | Com `CanalEmail()` fixo aqui, todo avisador viraria e-mail; com `if` por canal, cada canal novo reabriria o método. |


### 4.8 Abstract Factory

_Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/kits.py` · antes: `nucleo/antes_kits.py` · testes: `tests/test_kits.py`

**Problema (smell):** `montar_relatorio_antigo(itens, formato)` decide o formato em CADA peça (cabeçalho, linha, rodapé); esquecer um `if` mistura texto com HTML no mesmo relatório.

**Conceito:** `KitRelatorio` (fábrica abstrata) declara `criar_cabecalho`, `criar_linha` e `criar_rodape`; cada kit concreto (`KitTexto`, `KitHtml`) cria TODAS as peças da mesma família. `montar_relatorio(kit, itens)` só conhece a interface.

| Peça | No código |
|---|---|
| Fábrica abstrata | `KitRelatorio` |
| Fábricas concretas | `KitTexto`, `KitHtml` |
| Família nova | `KitMarkdown` |
| Cliente | `montar_relatorio(kit, itens)` |

**Quando NÃO usar:** Uma família só, ou uma peça só — Factory Method (ou a classe direta) resolve. Um TIPO de peça novo obriga a mexer em todos os kits.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `montar_relatorio(kit, itens)` | Monta cabeçalho, uma linha por Viagcert e o rodapé com o total, pedindo cada peça ao kit. | Abstract Factory: o cliente recebe a família inteira e não sabe qual é — impossível misturar. | Criando uma peça direto (ex.: `<li>` fixo), um relatório em texto ganharia HTML; trocar o kit troca todas as peças de uma vez. |


### 4.9 Adapter

_Padrão estrutural (GoF) — Aula 08_ · `nucleo/integracao.py` · antes: `nucleo/antes_integracao.py` · testes: `tests/test_integracao.py`

**Problema (smell):** O gateway `PagaTur` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.

**Conceito:** `PagaTurAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`).

| Peça | No código |
|---|---|
| Alvo (interface esperada) | `ProcessadorPagamento.processar(valor, token)` |
| Adaptado (terceiro) | `GatewayPagaTur.charge(payload)` |
| Adapter | `PagaTurAdapter` |
| Cliente limpo | `CheckoutService` |

**Quando NÃO usar:** Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `PagaTurAdapter.processar(valor, token)` | Converte o pedido de pagamento do sistema numa chamada `charge` e devolve o id ou levanta `PagamentoRecusado`. | Adapter: o gateway é de terceiro (não controlamos a assinatura); o adapter faz a peça caber e o `CheckoutService` perde o `if`. | Devolvendo o dict cru, o formato do terceiro vaza e a recusa passaria como sucesso; sem `round`, 19.99 viraria 1998 centavos. |


### 4.10 Composite

_Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/pacotes.py` · antes: `nucleo/antes_pacotes.py` · testes: `tests/test_pacotes.py`

**Problema (smell):** `total_antigo(coisa)` pergunta com `isinstance` se é lista ou Viagcert e se chama de novo — cada operação nova (descrição, contagem) repete essa checagem.

**Conceito:** `Componente` define a interface comum (`preco`, `descricao`); `Unitario` (folha) embrulha uma Viagcert; `Pacote` (composto) guarda filhos — folhas ou pacotes — e repassa a pergunta a eles.

| Peça | No código |
|---|---|
| Componente | `Componente` |
| Folha | `Unitario(item)` |
| Composto | `Pacote(nome, desconto)` com `adicionar` |
| Recursão | `Pacote.preco()` soma `filho.preco()` |

**Quando NÃO usar:** Lista plana, sem pacotes dentro de pacotes — `sum()` resolve.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Pacote.preco()` | Soma o preço de cada filho (que pode ser outro pacote) e aplica o desconto do pacote. | Composite: folha e composto respondem `preco()`, então a soma não pergunta o tipo e a recursão acontece sozinha. | Com `isinstance` aqui o pacote voltaria a conhecer os tipos; sem `round`, centavos se acumulariam. |


### 4.11 Decorator

_Padrão estrutural (GoF) — Aula 10_ · `nucleo/extras.py` · antes: `nucleo/antes_extras.py` · testes: `tests/test_extras.py`

**Problema (smell):** `preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

**Conceito:** Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComTranslado(ComSeguroViagem(ViagcertBase(item)))`.

| Peça | No código |
|---|---|
| Componente | `ViagcertBase(item)` |
| Decorador base (delega) | `Adicional` |
| Decoradores que somam | `ComSeguroViagem`, `ComTranslado`, `ComPasseioGuiado` |
| Decorador que multiplica | `ComAltaTemporada` |

**Quando NÃO usar:** Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComSeguroViagem.preco()` | Pergunta o preço ao componente de dentro e soma R$ 90.00. | Decorator: o extra é opcional e combinável; mantendo a interface, empilha. | Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda. |


### 4.12 Facade

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


### 4.13 State

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/situacao.py` · antes: `nucleo/antes_situacao.py` · testes: `tests/test_situacao.py`

**Problema (smell):** `SituacaoAntiga` repete a mesma escada de `if/elif` sobre `self.status` em `confirmar`, `concluir` e `cancelar`.

**Conceito:** Cada estado é uma classe (`Aberto`, `Confirmado`, `Concluido`, `Cancelado`) que sabe as SUAS transições; `SituacaoViagcert` (contexto) guarda o estado atual e delega. Transição proibida levanta `TransicaoInvalida`.

| Peça | No código |
|---|---|
| Contexto | `SituacaoViagcert` |
| Estado base | `Estado` (tudo proibido por padrão) |
| Estados | `Aberto`, `Confirmado`, `Concluido`, `Cancelado` |

**Quando NÃO usar:** Dois estados e uma regra (um booleano basta). State × Strategy: no State o próprio estado troca o objeto do contexto; no Strategy quem escolhe é o cliente.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Aberto.confirmar(contexto)` | Troca o estado do contexto para `Confirmado`. | State: a transição pertence ao estado de origem; o contexto só delega. | Sem sobrescrever, valeria o padrão da base (TransicaoInvalida); trocando para `Concluido`, pularia a confirmação. |


### 4.14 Strategy

_Padrão comportamental (GoF) — Aula 05_ · `nucleo/politicas.py` · antes: `nucleo/antes_politicas.py` · testes: `tests/test_politicas.py`

**Problema (smell):** `CobrancaAntiga.valor()` tem um `if/elif` por tipo de cliente que cresce a cada regra nova — cada uma obriga a reabrir a classe.

**Conceito:** Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`.

| Peça | No código |
|---|---|
| Contexto | `Cobranca` |
| Interface da estratégia | `aplicar(base)` |
| Estratégias | `PoliticaComum`, `PoliticaFidelidade`, `PoliticaCorporativo` |
| Estratégia nova (OCP) | `PoliticaEstudante` |
| Versão pythônica | `CobrancaComFuncao` (estratégia = função) |

**Quando NÃO usar:** Uma regra só, que nunca varia → uma função ou constante basta (Strategy seria cerimônia). Em Python a estratégia pode ser uma função.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Cobranca.valor()` | Pega o `total` da Viagcert e devolve o valor depois da política aplicada. | Strategy: a família de regras de tipo de cliente varia; cada uma é uma classe e o contexto delega, sem `if`. | Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/viagemcerta__14padroes_0e1f54_web_t03_tom3_exercicio/especificacao.json --exercicio --nome viagemcerta__14padroes_0e1f54_web_t03_tom3_exercicio_treino`

## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/viagcerts/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/viagcerts/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/viagcerts/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/viagcerts/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/viagcerts/views.py` | **fina**: busca → Service/ViewModel → render |
| API REST | `web/viagcerts/api.py` | JSON em `api/v1/` (GET/POST) e `api/v1/<id>/` (GET/PUT/PATCH/DELETE), validado pelo **mesmo** Form |
| Settings da app | `web/viagcerts/settings.py` | `API_LIMITE` e `API_ESCRITA`, trocáveis no projeto com o prefixo `VIAGCERTS_` |
| Template | `web/viagcerts/templates/viagcerts/` | só exibe |

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
bash iniciar.sh migrar      # makemigrations viagcerts + migrate
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
python manage.py makemigrations viagcerts && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o da raiz do projeto): `VENV=/caminho/.venv bash iniciar.sh`.

## 7. Modo exercício (questionário)

O código deste sistema está **completo e correto** — não há nada para corrigir. O exercício é um
**questionário de revisão** no formato da P3, com 71 perguntas sobre os padrões aplicados aqui
(o smell, como foi aplicado, o tripé de cada função, quando não usar, a alternativa descartada).
Cada resposta fica **oculta** até você clicar em **Ver resposta**.

- Abra `exercicios.html` (nesta pasta) direto no navegador — não precisa de servidor.
- Com o site no ar, o mesmo questionário está em `/exercicios/` (link **Exercícios** no topo ou na lista).


## Módulo `destinos` (Destino)

App Django acrescentada por `sgs app` (pedido: _"destinos de viagem com os campos cidade e pais"_). Telas em `/destinos/`, API REST em `/destinos/api/v1/`, padrões: encapsulamento, polimorfismo, srp, service, singleton, factory_method, abstract_factory, builder, prototype, strategy. Detalhes: `web/destinos/README.md`.


## Ligação `Viagcert.destino` → `Destino`

Campo de referência (ForeignKey) opcional, acrescentado por `sgs ligar`: aparece no formulário e na API REST de `viagcerts` (o id do Destino); apagar o Destino só limpa o campo (SET_NULL). Teste: `web/viagcerts/tests/test_ligacao_destino.py`.

# Pharmas — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: para **estudo** (smell `antes_*.py`, ADRs, tripé) · código **comentado**.
> Padrões (28): Encapsulamento com @property, Polimorfismo (herança + sobrescrita), SRP + OCP (separar responsabilidades), Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), MVVM (ViewModel), Singleton, Factory Method, Abstract Factory, Builder, Prototype, Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy, Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor.

## 1. Como o gerador decidiu

Assunto informado: _"sds gerar sistema de Farmácia"_

- Domínio escolhido: `generico` (nenhuma palavra de domínio reconhecida → domínio genérico)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| (grupo prova) | — |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

> campo 'cliente' já existe na entidade (veio do domínio): mantido o original.
> campo 'codigo' já existe na entidade (veio do domínio): mantido o original.
> campo 'quantidade' já existe na entidade (veio do domínio): mantido o original.
> campo 'valor' ignorado: nome reservado pelo gerador — use outro nome.
> campo 'observacao' já existe na entidade (veio do domínio): mantido o original.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Pharm com @property (base de tudo)
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
  construtor.py
  antes_construtor.py
  prototipos.py
  antes_prototipos.py
  integracao.py
  integracao_base.py
  antes_integracao.py
  comprovantes.py
  antes_comprovantes.py
  pacotes.py
  antes_pacotes.py
  extras.py
  antes_extras.py
  atendimento.py
  atendimento_base.py
  antes_atendimento.py
  tipos_compartilhados.py
  antes_tipos_compartilhados.py
  acesso.py
  antes_acesso.py
  aprovacao.py
  antes_aprovacao.py
  comandos.py
  antes_comandos.py
  regras.py
  antes_regras.py
  colecao.py
  antes_colecao.py
  mediador.py
  antes_mediador.py
  versoes.py
  antes_versoes.py
  eventos.py
  antes_eventos.py
  situacao.py
  antes_situacao.py
  politicas.py
  antes_politicas.py
  fechamento.py
  antes_fechamento.py
  orcamento.py
  antes_orcamento.py
tests/
  fabrica.py                ← cria Pharm válidas para os testes
  test_entidades.py
  test_categorias.py
  test_recibo.py
  test_relatorio.py
  test_painel.py
  test_configuracao.py
  test_avisos.py
  test_kits.py
  test_construtor.py
  test_prototipos.py
  test_integracao.py
  test_comprovantes.py
  test_pacotes.py
  test_extras.py
  test_atendimento.py
  test_tipos_compartilhados.py
  test_acesso.py
  test_aprovacao.py
  test_comandos.py
  test_regras.py
  test_colecao.py
  test_mediador.py
  test_versoes.py
  test_eventos.py
  test_situacao.py
  test_politicas.py
  test_fechamento.py
  test_orcamento.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
requirements.txt            ← TODAS as dependências (Django, pytest, pytest-django)
iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin
web/                        ← projeto Django (MVT) que usa o núcleo
  .env.example              ← modelo do .env (chave secreta, admin, porta)
  pharns/  models · forms · services · viewmodels · views · urls · templates/ · tests/
exercicios.html             ← questionário de revisão (resposta oculta em "Ver resposta")
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Pharm` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/categorias.py` é independente da entidade (só herança + sobrescrita)
- `nucleo/recibo.py` → `ReciboFormatter` lê a `Pharm`; `nucleo/antes_recibo.py` herda dela
- `nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)
- `nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict
- `nucleo/configuracao.py` → `Configuracao` única, lida por `total_com_taxa` (usa `item.total` da `Pharm`) e `formatar`
- `nucleo/avisos.py` → cada `Avisador…` cria o seu `Canal…`; `avisar` lê `cliente` e `total` da `Pharm`
- `nucleo/kits.py` → `montar_relatorio` pede as peças a um `Kit…` e lê as `Pharm`s
- `nucleo/construtor.py` → `PharmBuilder` cria a `Pharm` de `nucleo/entidades.py`
- `nucleo/prototipos.py` → `clonar` copia qualquer `Pharm` (os setters validam as mudanças)
- `nucleo/integracao.py` → `PagaJaAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/comprovantes.py` → cada `Comprovante…` TEM-UM `Formato…` e lê a `Pharm`
- `nucleo/pacotes.py` → `Unitario` embrulha a `Pharm`; `Pacote` guarda componentes
- `nucleo/extras.py` → `PharmBase` embrulha a `Pharm`; os `Com…` embrulham o componente
- `nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`
- `nucleo/tipos_compartilhados.py` → `Registro` liga a `Pharm` a um `TipoCompartilhado` da `FabricaDeTipos`
- `nucleo/acesso.py` → os proxies embrulham `ConsultaDePreco`, que lê `item.total`
- `nucleo/aprovacao.py` → a cadeia de `Aprovador` lê `item.total`
- `nucleo/comandos.py` → `AlterarCampo` muda a `Pharm` pelos setters; `Historico` empilha
- `nucleo/regras.py` → `ler_regra` monta `Comparacao`/`E`/`Ou`, que leem campos da `Pharm`
- `nucleo/colecao.py` → `ColecaoPharm` guarda `Pharm`s e entrega `IteradorDeItens`
- `nucleo/mediador.py` → os componentes avisam o `FormularioMediador` (independente da entidade)
- `nucleo/versoes.py` → `EditorPharm` salva/restaura o estado da `Pharm` em `Memento`s
- `nucleo/eventos.py` → `PharmObservavel` embrulha a `Pharm` e avisa os observadores
- `nucleo/situacao.py` → `SituacaoPharm` TEM-UMA `Pharm` e um `Estado`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Pharm`
- `nucleo/fechamento.py` → `Fechamento.fechar` lê `item.total` da `Pharm`
- `nucleo/orcamento.py` → `LinhaPharm` embrulha a `Pharm`; os visitantes percorrem o `Orcamento`
- `web/pharns/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

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
| `Pharm.quantidade` (setter) | Intercepta toda escrita em `quantidade` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.quantidade = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_quantidade`, o objeto pode nascer inválido. |
| `Pharm.total` | Calcula `quantidade × valor_unitario` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `quantidade` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


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

**Problema (smell):** `PharmFazTudo` calcula, formata o recibo e grava em arquivo: três motivos para mudar na mesma classe.

**Conceito:** `Pharm` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); `ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova (`ReciboCsvFormatter`) → OCP.

| Peça | No código |
|---|---|
| Negócio | `Pharm` (nucleo/entidades.py) |
| Apresentação | `ReciboFormatter` |
| Extensão (OCP) | `ReciboCsvFormatter` |
| Infraestrutura | `ArquivoRepository` |
| Junta as peças | `emitir_recibo(...)` |

**Quando NÃO usar:** SRP não é uma classe por método: separar "calcula", "soma", "arredonda" em classes é tão ruim quanto juntar tudo. A unidade é a responsabilidade (motivo para mudar).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ReciboFormatter.formatar(item)` | Recebe a Pharm e devolve o texto do recibo. | SRP: layout tem motivo de mudança próprio; recebe a entidade por parâmetro e só lê. | Layout novo mexe só aqui; formato novo é outra classe; devolver isto para a Pharm recriaria os 3 motivos para mudar. |


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
| `Avisador.avisar(item)` | Monta a mensagem da Pharm e envia pelo canal que `criar_canal()` devolver. | Factory Method: o algoritmo é comum e só a criação do produto varia — fica num método que a subclasse sobrescreve. | Com `CanalEmail()` fixo aqui, todo avisador viraria e-mail; com `if` por canal, cada canal novo reabriria o método. |


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
| `montar_relatorio(kit, itens)` | Monta cabeçalho, uma linha por Pharm e o rodapé com o total, pedindo cada peça ao kit. | Abstract Factory: o cliente recebe a família inteira e não sabe qual é — impossível misturar. | Criando uma peça direto (ex.: `<li>` fixo), um relatório em texto ganharia HTML; trocar o kit troca todas as peças de uma vez. |


### 4.9 Builder

_Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/construtor.py` · antes: `nucleo/antes_construtor.py` · testes: `tests/test_construtor.py`

**Problema (smell):** `nova_pharm_antiga(...)` recebe os campos na ORDEM certa; trocar dois números de lugar cria uma Pharm válida porém errada, e não há valores padrão.

**Conceito:** `PharmBuilder` tem um `com_<campo>()` por atributo, cada um devolvendo o próprio builder (interface fluente); `construir()` confere o que falta e só então cria a Pharm. `DiretorDePharm` guarda receitas prontas.

| Peça | No código |
|---|---|
| Builder | `PharmBuilder` (`com_…`, `faltando`, `construir`) |
| Produto | `Pharm` |
| Diretor | `DiretorDePharm.basico(...)` |

**Quando NÃO usar:** Objeto com poucos campos: em Python, argumentos NOMEADOS já resolvem a ordem.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `PharmBuilder.construir()` | Confere os campos obrigatórios e cria a Pharm com os valores juntados. | Builder: separa o passo a passo da montagem da criação final; cada valor continua validado pelos setters. | Sem `faltando()`, o erro seria um TypeError confuso do construtor; se `com_…` não devolvesse `self`, não daria para encadear. |


### 4.10 Prototype

_Padrão de criação (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/prototipos.py` · antes: `nucleo/antes_prototipos.py` · testes: `tests/test_prototipos.py`

**Problema (smell):** `copiar_na_mao(original)` repete campo por campo; quando a Pharm ganha um dado novo, a cópia esquece dele sem avisar.

**Conceito:** `clonar(original, **mudancas)` copia o objeto inteiro com `copy.deepcopy` (inclusive listas internas) e aplica as mudanças pelos setters. `RegistroDePrototipos` guarda modelos e entrega clones.

| Peça | No código |
|---|---|
| Protótipo | a Pharm modelo |
| Clonagem | `clonar(original, **mudancas)` |
| Registro | `RegistroDePrototipos` (`registrar`, `criar`) |

**Quando NÃO usar:** Objeto simples, criado em uma linha — copiar não economiza nada. Cuidado: cópia RASA (`copy.copy`) compartilha as listas internas com o original.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `clonar(original, **mudancas)` | Faz uma cópia profunda e aplica as mudanças pedidas (validadas pelos setters). | Prototype: o próprio objeto é o molde; a cópia não precisa conhecer cada campo. | Com `copy.copy` (rasa) listas internas seriam compartilhadas; gravando em `__dict__`, as mudanças pulariam a validação. |


### 4.11 Adapter

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


### 4.12 Bridge

_Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/comprovantes.py` · antes: `nucleo/antes_comprovantes.py` · testes: `tests/test_comprovantes.py`

**Problema (smell):** Uma classe por COMBINAÇÃO: `SimplesTexto`, `SimplesHtml`, `DetalhadoTexto`, `DetalhadoHtml` — 2 tipos × 2 formatos = 4 classes repetidas; formato novo exigiria uma classe por tipo.

**Conceito:** Duas hierarquias separadas: a ABSTRAÇÃO `Comprovante` (Simples, Detalhado) decide O QUE mostrar; a IMPLEMENTAÇÃO `Formato` (Texto, Html) decide COMO escrever. A ponte é `self.formato` (composição).

| Peça | No código |
|---|---|
| Abstração | `Comprovante` → `ComprovanteSimples`, `ComprovanteDetalhado` |
| Implementação | `Formato` → `FormatoTexto`, `FormatoHtml` |
| A ponte | `self.formato` (TEM-UM) |
| Extensão | `FormatoMarkdown` serve a todos os tipos |

**Quando NÃO usar:** Só uma dimensão varia — herança simples ou Strategy basta. Bridge se planeja no início; encaixar duas classes prontas é Adapter.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComprovanteDetalhado.gerar(item)` | Escolhe as linhas do comprovante e pede ao formato para escrever cada uma. | Bridge: tipo de comprovante e formato variam separados; a ligação é um atributo, não uma subclasse. | Escrevendo `<p>` direto aqui, o tipo voltaria a depender do formato; trocar `self.formato` muda a saída sem criar classe. |


### 4.13 Composite

_Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/pacotes.py` · antes: `nucleo/antes_pacotes.py` · testes: `tests/test_pacotes.py`

**Problema (smell):** `total_antigo(coisa)` pergunta com `isinstance` se é lista ou Pharm e se chama de novo — cada operação nova (descrição, contagem) repete essa checagem.

**Conceito:** `Componente` define a interface comum (`preco`, `descricao`); `Unitario` (folha) embrulha uma Pharm; `Pacote` (composto) guarda filhos — folhas ou pacotes — e repassa a pergunta a eles.

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


### 4.14 Decorator

_Padrão estrutural (GoF) — Aula 10_ · `nucleo/extras.py` · antes: `nucleo/antes_extras.py` · testes: `tests/test_extras.py`

**Problema (smell):** `preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

**Conceito:** Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComEmbalagem(ComUrgente(PharmBase(item)))`.

| Peça | No código |
|---|---|
| Componente | `PharmBase(item)` |
| Decorador base (delega) | `Adicional` |
| Decoradores que somam | `ComUrgente`, `ComEmbalagem`, `ComSeguro` |
| Decorador que multiplica | `ComDesconto10` |

**Quando NÃO usar:** Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComUrgente.preco()` | Pergunta o preço ao componente de dentro e soma R$ 30.00. | Decorator: o extra é opcional e combinável; mantendo a interface, empilha. | Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda. |


### 4.15 Facade

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


### 4.16 Flyweight

_Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/tipos_compartilhados.py` · antes: `nucleo/antes_tipos_compartilhados.py` · testes: `tests/test_tipos_compartilhados.py`

**Problema (smell):** Cada registro cria o SEU objeto de tipo de cliente (nome + fator); 10 000 registros = 10 000 objetos iguais na memória.

**Conceito:** `TipoCompartilhado` guarda só o estado INTRÍNSECO (nome, fator), igual para todos e imutável; `FabricaDeTipos.obter(chave)` devolve sempre o mesmo objeto; o estado EXTRÍNSECO (a Pharm) chega por parâmetro: `tipo.valor(item)`.

| Peça | No código |
|---|---|
| Flyweight | `TipoCompartilhado` (`__slots__`, imutável) |
| Fábrica (cache) | `FabricaDeTipos.obter(chave)` |
| Estado extrínseco | `Registro(item, tipo)` |

**Quando NÃO usar:** Poucos objetos, ou objetos que mudam — o ganho de memória não paga a complexidade.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `FabricaDeTipos.obter(chave)` | Devolve o objeto do tipo pedido, criando só na primeira vez. | Flyweight: o que se repete é compartilhado; o cache garante um objeto por chave. | Sem o cache, cada chamada criaria outro objeto; se o tipo fosse mutável, mudar um mudaria todos os registros. |


### 4.17 Proxy

_Padrão estrutural (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/acesso.py` · antes: `nucleo/antes_acesso.py` · testes: `tests/test_acesso.py`

**Problema (smell):** Quem consulta faz o cache e confere a permissão na mão, misturado com a chamada — cada ponto de uso repete (ou esquece) essas regras.

**Conceito:** `ConsultaComCache` e `ConsultaProtegida` têm o MESMO `calcular(item)` do objeto real (`ConsultaDePreco`); por dentro guardam respostas ou barram perfis e só então repassam. Quem usa nem percebe — e os proxies empilham.

| Peça | No código |
|---|---|
| Sujeito real | `ConsultaDePreco` |
| Proxy de cache | `ConsultaComCache` |
| Proxy de proteção | `ConsultaProtegida` |

**Quando NÃO usar:** Acesso simples, sem custo nem regra. Proxy × Decorator: o Decorator ACRESCENTA comportamento; o Proxy CONTROLA o acesso ao objeto real.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ConsultaComCache.calcular(item)` | Devolve o valor guardado; se ainda não tem, pergunta ao objeto real e guarda. | Proxy: mesma interface do real, então substitui o original sem o cliente mudar. | Com a chave só pelo cliente, mudar a quantidade devolveria valor velho; sem guardar, todo pedido iria ao real. |


### 4.18 Chain of Responsibility

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/aprovacao.py` · antes: `nucleo/antes_aprovacao.py` · testes: `tests/test_aprovacao.py`

**Problema (smell):** `quem_aprova_antigo(item)` tem todas as alçadas num `if/elif`; incluir um nível (ex.: supervisor) obriga a reescrever a função.

**Conceito:** Cada `Aprovador` conhece só a SUA alçada e o PRÓXIMO elo: se pode, aprova; senão, repassa. A cadeia é montada de fora (`encadear`) — incluir ou tirar um nível não mexe nos outros.

| Peça | No código |
|---|---|
| Elo base | `Aprovador` (`encadear`, `aprovar`) |
| Elos | `Atendente`, `Gerente`, `Diretoria` |
| Nível novo | `Supervisor` |
| Montagem | `cadeia_padrao()` |

**Quando NÃO usar:** Poucas regras fixas — um `if/elif` curto é mais legível. O pedido pode chegar ao fim da cadeia sem ninguém tratar.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Aprovador.aprovar(item)` | Aprova se o total cabe na alçada; senão repassa ao próximo; no fim devolve "sem aprovador". | Chain of Responsibility: cada elo decide sozinho e não conhece a cadeia inteira. | Sem testar `proximo is None`, o último elo quebraria com AttributeError; trocando a ordem dos elos, muda quem aprova. |


### 4.19 Command

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/comandos.py` · antes: `nucleo/antes_comandos.py` · testes: `tests/test_comandos.py`

**Problema (smell):** `alterar_antigo(item, campo, valor)` muda a Pharm direto e a ação some — sem registro do valor anterior, não dá para desfazer.

**Conceito:** Cada ação vira um OBJETO (`AlterarCampo`) que sabe `executar()` e `desfazer()` (guarda o valor anterior). `Historico` (o invocador) empilha os comandos e faz desfazer/refazer em ordem.

| Peça | No código |
|---|---|
| Comando | `Comando` → `AlterarCampo` |
| Invocador | `Historico` (`executar`, `desfazer`, `refazer`) |
| Receptor | a `Pharm` (setters validam) |

**Quando NÃO usar:** Ação simples que nunca será desfeita, enfileirada ou registrada — chame o método direto.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Historico.executar(comando)` | Executa o comando e só então o empilha; limpa a pilha de refazer. | Command: a ação é um objeto, então pode ser guardada, desfeita e refeita. | Empilhando antes de executar, um comando inválido entraria no histórico; sem limpar `_desfeitos`, refazer misturaria linhas do tempo. |


### 4.20 Interpreter

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/regras.py` · antes: `nucleo/antes_regras.py` · testes: `tests/test_regras.py`

**Problema (smell):** `regra_antiga(item)` traz a condição fixa no código — mudar "a partir de 3" para "a partir de 4" exige programar e publicar de novo.

**Conceito:** Cada pedaço da gramática é uma classe com `interpretar(item)`: `Comparacao` (terminal), `E` e `Ou` (não terminais). `ler_regra(texto)` monta a árvore a partir do texto — a regra vira DADO.

| Peça | No código |
|---|---|
| Expressão terminal | `Comparacao(campo, operador, numero)` |
| Não terminais | `E`, `Ou` |
| Leitor (parser) | `ler_regra(texto)` |

**Quando NÃO usar:** Linguagem grande (vira compilador — use uma biblioteca de parsing) ou regra que nunca muda.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ler_regra(texto)` | Quebra o texto em "ou" e depois em "e" e monta a árvore de `Comparacao`. | Interpreter: cada regra da gramática vira uma classe; o texto vira objetos que se avaliam sozinhos. | Separando primeiro por " e ", o "e" valeria depois do "ou" (outra regra); com `eval`, qualquer código rodaria. |


### 4.21 Iterator

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/colecao.py` · antes: `nucleo/antes_colecao.py` · testes: `tests/test_colecao.py`

**Problema (smell):** `totais_antigo(colecao)` lê `colecao._itens[i]` por índice — depende da lista interna; trocar a estrutura quebra todos os laços.

**Conceito:** `ColecaoPharm` esconde como guarda (dicionário por cliente) e entrega um ITERADOR (`IteradorDeItens`, com `__next__`) em `__iter__`. Percursos especiais (`acima_de`, `ordenados_por_total`) não expõem o interior.

| Peça | No código |
|---|---|
| Agregado | `ColecaoPharm` |
| Iterador | `IteradorDeItens` (`__iter__`, `__next__`) |
| Percursos | `acima_de` (gerador), `ordenados_por_total` |

**Quando NÃO usar:** Lista e dicionário já são iteráveis em Python; classe de iterador só para percurso especial — um gerador (`yield`) é o atalho.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `IteradorDeItens.__next__()` | Devolve o próximo item e avança a posição; no fim levanta `StopIteration`. | Iterator: a posição fica no iterador, então dois `for` não se atrapalham. | Sem `StopIteration` o `for` não termina (ou dá IndexError); com a posição na coleção, dois percursos se misturariam. |


### 4.22 Mediator

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/mediador.py` · antes: `nucleo/antes_mediador.py` · testes: `tests/test_mediador.py`

**Problema (smell):** O campo de quantidade conhece o seletor, o resumo e o botão e mexe neles direto — todos acoplados a todos; componente novo obriga a mexer nos outros.

**Conceito:** Cada componente só conhece o MEDIADOR e avisa `notificar(self, evento)`; `FormularioMediador` decide quem reage (recalcula o resumo, liga/desliga o botão).

| Peça | No código |
|---|---|
| Mediador | `FormularioMediador` |
| Componentes | `CampoQuantidade`, `SeletorTipo`, `Resumo`, `BotaoConfirmar` |
| Aviso | `mediador.notificar(origem, evento)` |

**Quando NÃO usar:** 2–3 objetos que conversam pouco. Cuidado para o mediador não virar um "objeto deus".

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `FormularioMediador.notificar(origem, evento)` | Recalcula o resumo (quantidade × preço × fator do tipo) e só habilita o botão se a quantidade for válida. | Mediator: a coordenação fica num lugar; os componentes não se conhecem. | Se o campo voltasse a atualizar o resumo direto, perderia a reutilização; esquecendo o botão aqui, ele ficaria ligado com valor inválido. |


### 4.23 Memento

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/versoes.py` · antes: `nucleo/antes_versoes.py` · testes: `tests/test_versoes.py`

**Problema (smell):** Para "voltar atrás", quem usa copia os campos internos (`_campo`) da Pharm num dicionário — depende do interior dela e esquece campos novos.

**Conceito:** `EditorPharm` (originador) cria um `Memento` com a cópia do próprio estado e sabe restaurá-lo; `HistoricoDeVersoes` (zelador) só empilha mementos, sem olhar dentro.

| Peça | No código |
|---|---|
| Originador | `EditorPharm` (`salvar`, `restaurar`) |
| Memento | `Memento` (estado + rótulo) |
| Zelador | `HistoricoDeVersoes` |

**Quando NÃO usar:** Estado grande e muitas versões (memória). Memento × Command: o Command desfaz UMA ação; o Memento volta o estado inteiro.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `EditorPharm.salvar(rotulo)` | Cria um Memento com uma CÓPIA profunda do estado atual. | Memento: só o originador conhece o próprio estado; o zelador guarda sem abrir. | Sem `deepcopy`, o memento apontaria para o mesmo estado e mudaria junto; guardando os campos fora, o encapsulamento se perde. |


### 4.24 Observer

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/eventos.py` · antes: `nucleo/antes_eventos.py` · testes: `tests/test_eventos.py`

**Problema (smell):** `alterar_antigo(...)` chama painel e log um por um — conhece todos os interessados; um interessado novo obriga a editar a função.

**Conceito:** `PharmObservavel` (sujeito) guarda a lista de observadores e, a cada mudança, chama `atualizar(evento)` em todos. Interessado novo = `inscrever(obj)`; o sujeito não muda.

| Peça | No código |
|---|---|
| Sujeito | `PharmObservavel` (`inscrever`, `cancelar`, `notificar`) |
| Observadores | `PainelObservador`, `LogObservador`, `AlertaObservador` |
| Evento | dict com campo, valor, total anterior e total |

**Quando NÃO usar:** Um interessado único e fixo — chame-o direto. Cadeias de observadores escondem o fluxo.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `PharmObservavel.alterar(campo, valor)` | Altera a Pharm (validando) e avisa todos os inscritos com um evento. | Observer: o sujeito não sabe quem escuta; cada observador reage do seu jeito. | Notificando ANTES do setter, um valor inválido seria anunciado; sem copiar a lista, quem se cancelasse no meio faria pular um observador. |


### 4.25 State

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/situacao.py` · antes: `nucleo/antes_situacao.py` · testes: `tests/test_situacao.py`

**Problema (smell):** `SituacaoAntiga` repete a mesma escada de `if/elif` sobre `self.status` em `confirmar`, `concluir` e `cancelar`.

**Conceito:** Cada estado é uma classe (`Aberto`, `Confirmado`, `Concluido`, `Cancelado`) que sabe as SUAS transições; `SituacaoPharm` (contexto) guarda o estado atual e delega. Transição proibida levanta `TransicaoInvalida`.

| Peça | No código |
|---|---|
| Contexto | `SituacaoPharm` |
| Estado base | `Estado` (tudo proibido por padrão) |
| Estados | `Aberto`, `Confirmado`, `Concluido`, `Cancelado` |

**Quando NÃO usar:** Dois estados e uma regra (um booleano basta). State × Strategy: no State o próprio estado troca o objeto do contexto; no Strategy quem escolhe é o cliente.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Aberto.confirmar(contexto)` | Troca o estado do contexto para `Confirmado`. | State: a transição pertence ao estado de origem; o contexto só delega. | Sem sobrescrever, valeria o padrão da base (TransicaoInvalida); trocando para `Concluido`, pularia a confirmação. |


### 4.26 Strategy

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
| `Cobranca.valor()` | Pega o `total` da Pharm e devolve o valor depois da política aplicada. | Strategy: a família de regras de tipo de cliente varia; cada uma é uma classe e o contexto delega, sem `if`. | Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança. |


### 4.27 Template Method

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/fechamento.py` · antes: `nucleo/antes_fechamento.py` · testes: `tests/test_fechamento.py`

**Problema (smell):** `fechar_padrao_antigo` e `fechar_com_taxa_antigo` são cópias do mesmo roteiro (validar → calcular → ajustar → formatar); corrigir um passo exige lembrar de todas as cópias.

**Conceito:** `Fechamento.fechar(item)` é o método TEMPLATE: fixa a ordem dos passos; as subclasses sobrescrevem só o passo que muda (`ajustar`), e o gancho tem padrão vazio.

| Peça | No código |
|---|---|
| Classe abstrata | `Fechamento` |
| Método template | `fechar(item)` |
| Passos / gancho | `validar`, `calcular`, `ajustar` (gancho), `formatar` |
| Subclasses | `FechamentoPadrao`, `FechamentoComTaxa`, `FechamentoEspecial` |

**Quando NÃO usar:** Só um passo varia — passe uma função (Strategy). Template Method usa HERANÇA; Strategy, COMPOSIÇÃO.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Fechamento.fechar(item)` | Chama validar, calcular, ajustar e formatar, nessa ordem. | Template Method: o esqueleto é fixo e as subclasses preenchem só os passos variáveis. | Se uma subclasse sobrescrever `fechar`, perde-se a garantia da ordem; esquecendo `validar`, total inválido passaria. |


### 4.28 Visitor

_Padrão comportamental (GoF) — além das aulas; referência: lista GoF da Wikipédia_ · `nucleo/orcamento.py` · antes: `nucleo/antes_orcamento.py` · testes: `tests/test_orcamento.py`

**Problema (smell):** `total_antigo` e `texto_antigo` percorrem as linhas perguntando o tipo — cada operação nova repete a escada; cada tipo novo mexe em todas.

**Conceito:** Cada linha tem `aceitar(visitante)` e chama o método certo do visitante (despacho duplo); cada OPERAÇÃO é um visitante (`CalculoDoTotal`, `TextoDoOrcamento`) com um `visitar_*` por tipo.

| Peça | No código |
|---|---|
| Elementos | `LinhaPharm`, `LinhaExtra`, `LinhaDesconto` (`aceitar`) |
| Estrutura | `Orcamento` |
| Visitantes | `CalculoDoTotal`, `TextoDoOrcamento` |
| Operação nova | `ContagemPorTipo` |

**Quando NÃO usar:** Tipos de elemento que mudam muito (cada tipo novo mexe em TODOS os visitantes) — prefira polimorfismo comum.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `LinhaExtra.aceitar(visitante)` | Chama `visitante.visitar_extra(self)`. | Visitor: o despacho duplo escolhe o método pelo tipo da linha E pelo visitante, sem `if`. | Chamando outro `visitar_*`, a linha seria tratada como outro tipo; sem `aceitar`, voltaria o `isinstance` em cada operação. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/pharmas__todos_web_cmd_exercicio/especificacao.json --exercicio --nome pharmas__todos_web_cmd_exercicio_treino`

## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/pharns/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/pharns/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/pharns/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/pharns/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/pharns/views.py` | **fina**: busca → Service/ViewModel → render |
| Template | `web/pharns/templates/pharns/` | só exibe |

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
bash iniciar.sh migrar      # makemigrations pharns + migrate
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
python manage.py makemigrations pharns && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o da raiz do projeto): `VENV=/caminho/.venv bash iniciar.sh`.

## 7. Modo exercício (questionário)

O código deste sistema está **completo e correto** — não há nada para corrigir. O exercício é um
**questionário de revisão** no formato da P3, com 141 perguntas sobre os padrões aplicados aqui
(o smell, como foi aplicado, o tripé de cada função, quando não usar, a alternativa descartada).
Cada resposta fica **oculta** até você clicar em **Ver resposta**.

- Abra `exercicios.html` (nesta pasta) direto no navegador — não precisa de servidor.
- Com o site no ar, o mesmo questionário está em `/exercicios/` (link **Exercícios** no topo ou na lista).

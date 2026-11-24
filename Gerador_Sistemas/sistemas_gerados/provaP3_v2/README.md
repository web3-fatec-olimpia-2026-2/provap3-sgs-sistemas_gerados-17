# Cooperativa Citrícola — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: para **estudo** (smell `antes_*.py`, ADRs, tripé) · código **comentado**.
> Padrões (9): Encapsulamento com @property, Polimorfismo (herança + sobrescrita), SRP + OCP (separar responsabilidades), Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), MVVM (ViewModel), Adapter, Decorator, Facade, Strategy.

## 1. Como o gerador decidiu

Escolha explícita: domínio **citricultura**, padrões: encapsulamento, polimorfismo, srp, service, mvvm, adapter, decorator, facade, strategy.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← LoteCitros com @property (base de tudo)
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
  politicas.py
  antes_politicas.py
tests/
  fabrica.py                ← cria LoteCitros válidas para os testes
  test_entidades.py
  test_categorias.py
  test_recibo.py
  test_relatorio.py
  test_painel.py
  test_integracao.py
  test_extras.py
  test_atendimento.py
  test_politicas.py
docs/                       ← um ADR por padrão
especificacao.json          ← a entrada usada (dá para editar e regenerar)
requirements.txt            ← o Python exigido, o Django e o que ele usa, os testes e as deste sistema
iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin
web/                        ← projeto Django (MVT) que usa o núcleo
  .env.example              ← modelo do .env (chave secreta, admin, porta)
  citricultura/  settings · models · forms · services · viewmodels · views · api (REST) · urls · templates/ · tests/
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `LoteCitros` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/categorias.py` é independente da entidade (só herança + sobrescrita)
- `nucleo/recibo.py` → `ReciboFormatter` lê a `LoteCitros`; `nucleo/antes_recibo.py` herda dela
- `nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)
- `nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict
- `nucleo/integracao.py` → `PagaCoopAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/extras.py` → `LoteCitrosBase` embrulha a `LoteCitros`; os `Com…` embrulham o componente
- `nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `LoteCitros`
- `web/citricultura/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

### 4.1 Encapsulamento com @property

_Fundamento de OO — Aulas 02 e 03_ · `nucleo/entidades.py` · testes: `tests/test_entidades.py`

**Problema (smell):** Um atributo público aceita qualquer valor: `obj.caixas = 0` ou `obj.preco_caixa = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

**Conceito:** O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

| Peça | No código |
|---|---|
| Atributo interno | `self._caixas`, `self._preco_caixa`… |
| Getter | `@property` |
| Setter (a fechadura) | `@caixas.setter` → `ValueError` se inválido |
| Dado calculado | `total` (só leitura) |

**Quando NÃO usar:** Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `LoteCitros.caixas` (setter) | Intercepta toda escrita em `caixas` e só grava se a regra for respeitada; senão levanta `ValueError`. | Encapsulamento: a regra mora no objeto, num lugar só; como o `__init__` faz `self.caixas = ...`, vale também na criação. Descartado: validar só na tela. | Sem o setter, um valor inválido entra e o `total` sai errado; se o `__init__` gravar direto em `_caixas`, o objeto pode nascer inválido. |
| `LoteCitros.total` | Calcula `caixas × preco_caixa` na hora. | Dado derivado não se guarda: se fosse atributo, mudar `caixas` deixaria o total desatualizado. | Virando atributo comum, dois dados podem discordar; com setter, alguém gravaria um total que não bate com a conta. |


### 4.2 Polimorfismo (herança + sobrescrita)

_Fundamento de OO — Aula 04_ · `nucleo/categorias.py` · antes: `nucleo/antes_categorias.py` · testes: `tests/test_categorias.py`

**Problema (smell):** `imprimir_preco(tipo)` decide o texto com `if/elif` por categoria; cada categoria nova obriga a editar a função (e arriscar as que já funcionavam).

**Conceito:** Cada categoria é uma subclasse de `LaranjaPera` que SOBRESCREVE `descricao()` e `preco_unidade()`. `imprimir_preco(categoria)` só chama os métodos — o Python escolhe a versão pelo tipo real do objeto, em tempo de execução.

| Peça | No código |
|---|---|
| Classe base | `LaranjaPera` |
| Subtipos que sobrescrevem | `LaranjaValencia`, `LimaoTahiti` |
| Subtipo que não sobrescreve (usa o da mãe) | `LaranjaPeraPadrao` |
| Função polimórfica | `imprimir_preco(categoria)` |
| Categoria nova | `TangerinaPonkan` |

**Quando NÃO usar:** Se as categorias só diferem num número (sem comportamento próprio), um atributo ou tabela basta. Herança só para relação É-UM; TEM-UM é composição.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `imprimir_preco(categoria)` | Monta "descrição: R$ preço por caixa" de qualquer categoria. | Polimorfismo: não pergunta o tipo (zero `if`); cada subclasse responde a seu modo. | Com `if/elif`, o `TangerinaPonkan` exigiria editar a função; hoje entra sem mudar uma linha. Se um subtipo não sobrescrever, usa o método da mãe. |


### 4.3 SRP + OCP (separar responsabilidades)

_Princípios SOLID — Aula 06_ · `nucleo/recibo.py` · antes: `nucleo/antes_recibo.py` · testes: `tests/test_recibo.py`

**Problema (smell):** `LoteCitrosFazTudo` calcula, formata o recibo e grava em arquivo: três motivos para mudar na mesma classe.

**Conceito:** `LoteCitros` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); `ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova (`ReciboCsvFormatter`) → OCP.

| Peça | No código |
|---|---|
| Negócio | `LoteCitros` (nucleo/entidades.py) |
| Apresentação | `ReciboFormatter` |
| Extensão (OCP) | `ReciboCsvFormatter` |
| Infraestrutura | `ArquivoRepository` |
| Junta as peças | `emitir_recibo(...)` |

**Quando NÃO usar:** SRP não é uma classe por método: separar "calcula", "soma", "arredonda" em classes é tão ruim quanto juntar tudo. A unidade é a responsabilidade (motivo para mudar).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ReciboFormatter.formatar(item)` | Recebe a LoteCitros e devolve o texto do recibo. | SRP: layout tem motivo de mudança próprio; recebe a entidade por parâmetro e só lê. | Layout novo mexe só aqui; formato novo é outra classe; devolver isto para a LoteCitros recriaria os 3 motivos para mudar. |


### 4.4 Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web)

_Arquitetura — Aula 07_ · `nucleo/relatorio.py` · antes: `nucleo/antes_relatorio.py` · testes: `tests/test_relatorio.py`

**Problema (smell):** `relatorio_view` mistura a regra (desconto por destino da fruta) com a apresentação (texto); para testar a conta é preciso chamar a view e ler texto.

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
| `RelatorioService.calcular()` | Aplica o fator de cada destino da fruta e devolve `(linhas, total_geral)`. | A regra fica fora da web: testável sem request/servidor e reaproveitável pela API. | Se passar a receber `request` ou devolver texto, volta a exigir a web para testar e a API teria que duplicar a conta. |


### 4.5 MVVM (ViewModel)

_Arquitetura — Aulas 08 e 09_ · `nucleo/painel.py` · antes: `nucleo/antes_painel.py` · testes: `tests/test_painel.py`

**Problema (smell):** `tela_painel` decide no meio do desenho o status, o rótulo do botão, o "R$" e o rodapé "ENTRESSAFRA - nenhum talhão pronto" — só dá para testar lendo a tela.

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

**Problema (smell):** O gateway `PagaCoop` (de terceiro) fala `charge({... amount_cents ...})`, mas o sistema espera `processar(valor, token)`; o checkout antigo tem um `if usa_gateway`.

**Conceito:** `PagaCoopAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`).

| Peça | No código |
|---|---|
| Alvo (interface esperada) | `ProcessadorPagamento.processar(valor, token)` |
| Adaptado (terceiro) | `GatewayPagaCoop.charge(payload)` |
| Adapter | `PagaCoopAdapter` |
| Cliente limpo | `CheckoutService` |

**Quando NÃO usar:** Se você controla as duas pontas e as interfaces já batem, duck typing basta — Adapter só para peça de terceiro. Adapter ≠ Facade (uma peça × vários subsistemas).

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `PagaCoopAdapter.processar(valor, token)` | Converte o pedido de pagamento do sistema numa chamada `charge` e devolve o id ou levanta `PagamentoRecusado`. | Adapter: o gateway é de terceiro (não controlamos a assinatura); o adapter faz a peça caber e o `CheckoutService` perde o `if`. | Devolvendo o dict cru, o formato do terceiro vaza e a recusa passaria como sucesso; sem `round`, 19.99 viraria 1998 centavos. |


### 4.7 Decorator

_Padrão estrutural (GoF) — Aula 10_ · `nucleo/extras.py` · antes: `nucleo/antes_extras.py` · testes: `tests/test_extras.py`

**Problema (smell):** `preco_com_flags(item, ...=False, ...)` soma extras com uma pilha de flags e `if`; não dá para repetir extra nem combinar dinamicamente.

**Conceito:** Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComClassificacao(ComFrete(LoteCitrosBase(item)))`.

| Peça | No código |
|---|---|
| Componente | `LoteCitrosBase(item)` |
| Decorador base (delega) | `Adicional` |
| Decoradores que somam | `ComFrete`, `ComClassificacao`, `ComCamaraFria` |
| Decorador que multiplica | `ComBonusQualidade` |

**Quando NÃO usar:** Se todos os extras somam valor fixo, uma lista + `sum()` basta. O `@decorator` do Python decora funções; o padrão decora objetos. Camada que multiplica torna a ORDEM relevante.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `ComFrete.preco()` | Pergunta o preço ao componente de dentro e soma R$ 120.00. | Decorator: o extra é opcional e combinável; mantendo a interface, empilha. | Sem chamar o de dentro o extra some (ou vira recursão); com o percentual por fora × por dentro o total muda. |


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


### 4.9 Strategy

_Padrão comportamental (GoF) — Aula 05_ · `nucleo/politicas.py` · antes: `nucleo/antes_politicas.py` · testes: `tests/test_politicas.py`

**Problema (smell):** `CobrancaAntiga.valor()` tem um `if/elif` por destino da fruta que cresce a cada regra nova — cada uma obriga a reabrir a classe.

**Conceito:** Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`.

| Peça | No código |
|---|---|
| Contexto | `Cobranca` |
| Interface da estratégia | `aplicar(base)` |
| Estratégias | `PoliticaIndustria`, `PoliticaMesa`, `PoliticaExportacao` |
| Estratégia nova (OCP) | `PoliticaRefugo` |
| Versão pythônica | `CobrancaComFuncao` (estratégia = função) |

**Quando NÃO usar:** Uma regra só, que nunca varia → uma função ou constante basta (Strategy seria cerimônia). Em Python a estratégia pode ser uma função.

**Tripé da P3** (o professor sorteia a função e pergunta):

| Função | O que faz | Por que assim | O que muda se alterar |
|---|---|---|---|
| `Cobranca.valor()` | Pega o `total` da LoteCitros e devolve o valor depois da política aplicada. | Strategy: a família de regras de destino da fruta varia; cada uma é uma classe e o contexto delega, sem `if`. | Voltando ao `if/elif` os números seguem iguais, mas toda política nova reabre a classe (perde OCP). Trocar `cobranca.politica` muda o valor sem criar outra cobrança. |

## 5. Roteiro de estudo (30–40 min)

1. Abra cada `nucleo/antes_*.py` e diga **em voz alta** qual é o smell.
2. Abra a versão "depois" e aponte as **peças** do padrão (tabelas da seção 4).
3. **Preveja** o resultado de um teste antes de rodar; depois rode e confira.
4. Responda o **tripé** de cada função em voz alta (o que faz · por que assim · o que muda se).
5. Mude um número (um fator, um limite) e preveja **qual teste quebra**.
6. Gere de novo em modo exercício e refaça sem olhar:
   `python Gerador_Sistemas/gerar_sistema.py --spec <caminho>/provaP3/especificacao.json --exercicio --nome provaP3_treino`

## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/citricultura/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/citricultura/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/citricultura/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/citricultura/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/citricultura/views.py` | **fina**: busca → Service/ViewModel → render |
| API REST | `web/citricultura/api.py` | JSON em `api/v1/` (GET/POST) e `api/v1/<id>/` (GET/PUT/PATCH/DELETE), validado pelo **mesmo** Form |
| Settings da app | `web/citricultura/settings.py` | `API_LIMITE` e `API_ESCRITA`, trocáveis no projeto com o prefixo `CITRICULTURA_` |
| Template | `web/citricultura/templates/citricultura/` | só exibe |

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
bash iniciar.sh migrar      # makemigrations citricultura + migrate
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
python manage.py makemigrations citricultura && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o do SGS, `Gerador_Sistemas/.venv`):
`VENV=/caminho/.venv bash iniciar.sh`. As dependências estão explicadas no `requirements.txt` (o Python
exigido, o Django e o que ele usa, os testes e as pontuais deste sistema).

## Prova Prática P3 — ISW-030 Desenvolvimento Web III — o ambiente do guia, já montado

Gerado com o **perfil** do domínio (`dominios.PERFIS`), igual ao guia
`ProvaPraticaP3/GUIA_Ambiente_Django_Maquinas_FATEC*.pdf`. A pasta `web/` faz o papel da pasta de trabalho
do guia (lá, `~/provaP3`; aqui o caminho é **relativo**: `sistemas_gerados/provaP3/web`).

| No guia | Aqui |
|---|---|
| `pip install django djangorestframework pytest pytest-django` | `requirements.txt` (`bash iniciar.sh deps`) |
| `django-admin startproject cooperativa .` | `web/manage.py` + `web/cooperativa/` (settings, urls, wsgi) |
| `python manage.py startapp citricultura` | `web/citricultura/` (models, forms, views, api.py, serializers.py, api_drf.py, tests/) |
| `"rest_framework"` e `"citricultura"` em `INSTALLED_APPS` | `web/cooperativa/settings.py` |
| `pytest.ini`: `DJANGO_SETTINGS_MODULE = cooperativa.settings` · `python_files = tests.py test_*.py` | `web/pytest.ini` |

Rotas: `/` leva a `/citricultura/` (telas do CRUD) · `/citricultura/api/v1/` (API em Django puro, `JsonResponse`) ·
`/api/lote-citroses/` (API com o **DRF**: Serializer + ViewSet + router; `/api/` abre a Browsable API) ·
`/admin/` (Django Admin).

Na tela do SGS: `sgs provap3` gera e prepara tudo (.venv, dependências, .env, migrations, admin);
`sgs rodar NN` sobe o site. No terminal (com o .venv ativado):

```bash
cd sistemas_gerados/provaP3/web
python manage.py migrate
python manage.py runserver
python -m pytest
```


## Campo `LoteCitros.cidade` (novo)

Regra: cidade: texto obrigatório (não pode ser vazio) — `texto` (sgs incrementar). Vale no @property do núcleo, no model (validators/choices), no form e na API; os testes da classe foram refeitos.


## Versão 17.2

Cópia do sistema 17 feita pelo SGS (`sgs editar`): o original não mudou. Esta versão roda na porta 61172 (a do 17 é 6117).

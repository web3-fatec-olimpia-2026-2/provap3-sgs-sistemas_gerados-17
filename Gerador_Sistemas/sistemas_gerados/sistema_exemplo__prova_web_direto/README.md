# Sistema Exemplo — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: **só gerar** (sem material de estudo) · código **comentado**.
> Padrões (9): Encapsulamento com @property, Polimorfismo (herança + sobrescrita), SRP + OCP (separar responsabilidades), Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), MVVM (ViewModel), Adapter, Decorator, Facade, Strategy.

## 1. Como o gerador decidiu

Assunto informado: _"source "/home/oscar/projetos/django/Tecnicas de Programacao II/.venv/bin/activate"
python -m pytest -q
cd web && python -m pytest -q"_

- Domínio escolhido: `generico` (nenhuma palavra de domínio reconhecida → domínio genérico)
- Nenhuma palavra de padrão reconhecida → gerados os 9 padrões cobrados na P3 (grupo `prova`).

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| (grupo prova) | — |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Atendimento com @property (base de tudo)
  categorias.py
  recibo.py
  relatorio.py
  painel.py
  integracao.py
  integracao_base.py
  extras.py
  atendimento.py
  atendimento_base.py
  politicas.py
tests/
  fabrica.py                ← cria Atendimento válidas para os testes
  test_entidades.py
  test_categorias.py
  test_recibo.py
  test_relatorio.py
  test_painel.py
  test_integracao.py
  test_extras.py
  test_atendimento.py
  test_politicas.py
especificacao.json          ← a entrada usada (dá para editar e regenerar)
requirements.txt            ← TODAS as dependências (Django, pytest, pytest-django)
iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin
web/                        ← projeto Django (MVT) que usa o núcleo
  .env.example              ← modelo do .env (chave secreta, admin, porta)
  atendimentos/  models · forms · services · viewmodels · views · urls · templates/ · tests/
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Atendimento` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/categorias.py` é independente da entidade (só herança + sobrescrita)
- `nucleo/recibo.py` → `ReciboFormatter` lê a `Atendimento`
- `nucleo/relatorio.py` → `RelatorioService` trabalha com dicts (dados vindos do banco/ORM)
- `nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict
- `nucleo/integracao.py` → `PagaJaAdapter` implementa `ProcessadorPagamento` (`integracao_base.py`) e `CheckoutService` cobra `item.total`
- `nucleo/extras.py` → `AtendimentoBase` embrulha a `Atendimento`; os `Com…` embrulham o componente
- `nucleo/atendimento.py` → `AtendimentoFacade` delega aos 5 subsistemas de `atendimento_base.py`; a `Calculadora` usa `item.total`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Atendimento`
- `web/atendimentos/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

| Padrão | Arquivo | Ideia |
|---|---|---|
| Encapsulamento com @property | `nucleo/entidades.py` | O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter. |
| Polimorfismo (herança + sobrescrita) | `nucleo/categorias.py` | Cada categoria é uma subclasse de `Basico` que SOBRESCREVE `descricao()` e `preco_unidade()`. `imprimir_preco(categoria)` só chama os métodos — o Python escolhe a versão pelo tipo real do objeto, em tempo de execução. |
| SRP + OCP (separar responsabilidades) | `nucleo/recibo.py` | `Atendimento` fica com dados + `total` (negócio); `ReciboFormatter` só formata (apresentação); `ArquivoRepository` só grava (infraestrutura). Formato novo = classe nova (`ReciboCsvFormatter`) → OCP. |
| Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web) | `nucleo/relatorio.py` | `RelatorioService.calcular()` faz só a regra e devolve DADOS; a view fica fina (chama e formata); a mesma regra serve a API (`relatorio_api`). No Django: models = dado, views = regra/orquestração, template = apresentação, services.py = a regra complexa. |
| MVVM (ViewModel) | `nucleo/painel.py` | `ItemViewModel` / `PainelVM` traduzem o dado cru em dado pronto (`status_label`, `acao_label`, `preco_formatado`, `rodape`); a View só costura. No Django não há binding: o ViewModel é preparação chamada antes do `render`. |
| Adapter | `nucleo/integracao.py` | `PagaJaAdapter` É-UM `ProcessadorPagamento`: por fora fala `processar`, por dentro traduz a chamada, reais → centavos e a resposta (aprovado → id; negado → `PagamentoRecusado`). |
| Decorator | `nucleo/extras.py` | Cada extra EMBRULHA o componente, MANTÉM a interface (`preco`/`descricao`) e soma a sua parte; por isso empilha: `ComEmbalagem(ComUrgente(AtendimentoBase(item)))`. |
| Facade | `nucleo/atendimento.py` | `AtendimentoFacade.concluir(recurso, item)` é o balcão único: disponibilidade → cálculo → cobrança → registro → notificação, DELEGANDO a cada subsistema. |
| Strategy | `nucleo/politicas.py` | Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`. |



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
bash iniciar.sh migrar      # makemigrations atendimentos + migrate
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
python manage.py makemigrations atendimentos && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o da raiz do projeto): `VENV=/caminho/.venv bash iniciar.sh`.

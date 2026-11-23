# Biblioteca Municipal — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: **só gerar** (sem material de estudo) · código **comentado**.
> Padrões (3): Encapsulamento com @property, MVVM (ViewModel), Strategy.

## 1. Como o gerador decidiu

Assunto informado: _"biblioteca onde a multa varia conforme o tipo de leitor. Texto escrito sem “sgs gerar” só é ANOTADO na tela (nada é gerado por engano). As caixas embaixo (+ Django, exercício, testes, estudo, comentários) valem para a geração."_

- Domínio escolhido: `biblioteca` (palavras: biblioteca, leitor, multa)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| MVVM (ViewModel) | tela |
| Strategy | tipo de, varia, conforme o |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Emprestimo com @property (base de tudo)
  painel.py
  politicas.py
tests/
  fabrica.py                ← cria Emprestimo válidas para os testes
  test_entidades.py
  test_painel.py
  test_politicas.py
especificacao.json          ← a entrada usada (dá para editar e regenerar)
requirements.txt            ← TODAS as dependências (Django, pytest, pytest-django)
iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin
web/                        ← projeto Django (MVT) que usa o núcleo
  .env.example              ← modelo do .env (chave secreta, admin, porta)
  emprestimos/  models · forms · services · viewmodels · views · urls · templates/ · tests/
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Emprestimo` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/painel.py` → `PainelVM` monta um `ItemViewModel` por dict
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Emprestimo`
- `web/emprestimos/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

| Padrão | Arquivo | Ideia |
|---|---|---|
| Encapsulamento com @property | `nucleo/entidades.py` | O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter. |
| MVVM (ViewModel) | `nucleo/painel.py` | `ItemViewModel` / `PainelVM` traduzem o dado cru em dado pronto (`status_label`, `acao_label`, `preco_formatado`, `rodape`); a View só costura. No Django não há binding: o ViewModel é preparação chamada antes do `render`. |
| Strategy | `nucleo/politicas.py` | Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`. |



## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/emprestimos/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/emprestimos/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/emprestimos/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/emprestimos/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/emprestimos/views.py` | **fina**: busca → Service/ViewModel → render |
| Template | `web/emprestimos/templates/emprestimos/` | só exibe |

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
bash iniciar.sh migrar      # makemigrations emprestimos + migrate
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
python manage.py makemigrations emprestimos && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o da raiz do projeto): `VENV=/caminho/.venv bash iniciar.sh`.

# Academia Fit — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: **só gerar** (sem material de estudo) · código **comentado**.
> Padrões (2): Encapsulamento com @property, Strategy.

## 1. Como o gerador decidiu

Assunto informado: _"Sistema para cadastrar funcionários e alunos de uma faculdade. Validar CPF com dígitos numéricos apenas, não aceita letras. Ainda sim é tratado como string. Já os campos como Nome não aceita números nem símbolos."_

- Domínio escolhido: `academia` (palavras: alunos)

| Padrão | Palavras do assunto que o indicaram |
|---|---|
| Encapsulamento com @property | validar |

A entidade com `@property` (encapsulamento) entra sempre: é a base dos outros padrões.

> --django incluiu o Strategy: o Service da camada web reaproveita as políticas do núcleo.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Matricula com @property (base de tudo)
  politicas.py
tests/
  fabrica.py                ← cria Matricula válidas para os testes
  test_entidades.py
  test_politicas.py
especificacao.json          ← a entrada usada (dá para editar e regenerar)
requirements.txt            ← TODAS as dependências (Django, pytest, pytest-django)
iniciar.sh                  ← prepara e sobe o site: venv · deps · .env · migrations · admin
web/                        ← projeto Django (MVT) que usa o núcleo
  .env.example              ← modelo do .env (chave secreta, admin, porta)
  matriculas/  models · forms · services · viewmodels · views · urls · templates/ · tests/
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Matricula` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Matricula`
- `web/matriculas/services.py` importa as políticas de `nucleo/politicas.py` (Strategy) → `viewmodels.py` prepara a tela → `views.py` só orquestra → os templates exibem

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

| Padrão | Arquivo | Ideia |
|---|---|---|
| Encapsulamento com @property | `nucleo/entidades.py` | O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter. |
| Strategy | `nucleo/politicas.py` | Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`. |



## 6. Camada web (Django · MVT)

| Camada | Arquivo | Papel |
|---|---|---|
| Model | `web/matriculas/models.py` | campos com **validators** (encapsulamento no mundo Django) + `total` calculado |
| Form | `web/matriculas/forms.py` | `ModelForm` reaproveita os validators |
| Service | `web/matriculas/services.py` | regra sem web; reaproveita o **Strategy** do núcleo |
| ViewModel | `web/matriculas/viewmodels.py` | prepara título, valor formatado, selo e rodapé |
| View | `web/matriculas/views.py` | **fina**: busca → Service/ViewModel → render |
| Template | `web/matriculas/templates/matriculas/` | só exibe |

Pegadinha testada em `tests/test_models.py`: `save()` sozinho **não** valida — quem valida é
`full_clean()` / o `ModelForm`.

### Subir o site (no WSL, dentro desta pasta)

Tudo de uma vez — cria o `.venv`, instala o `requirements.txt`, copia `web/.env.example` para
`web/.env` (com uma chave secreta nova), roda as migrations, cria o superusuário e sobe o servidor:

```bash
bash iniciar.sh
```

Depois abra http://127.0.0.1:8000/ (site) e http://127.0.0.1:8000/admin/ (usuário e senha do
`web/.env`: `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD`). Outra porta: `bash iniciar.sh tudo 8001`.

Os mesmos passos, separados (cada um pode ser repetido sem estragar nada):

```bash
bash iniciar.sh venv        # cria .venv nesta pasta (se não existir)
bash iniciar.sh deps        # instala requirements.txt (se faltar algo)
bash iniciar.sh env         # web/.env a partir de web/.env.example (não sobrescreve)
bash iniciar.sh migrar      # makemigrations matriculas + migrate
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
python manage.py makemigrations matriculas && python manage.py migrate
python manage.py garantir_admin
python manage.py runserver 127.0.0.1:8000
```

Reaproveitar um `.venv` que já tem Django (ex.: o da raiz do projeto): `VENV=/caminho/.venv bash iniciar.sh`.

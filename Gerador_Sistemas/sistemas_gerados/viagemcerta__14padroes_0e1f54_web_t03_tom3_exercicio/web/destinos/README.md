# Módulo `destinos` — Destino (acrescentado por `sgs app`)

Pedido: _"destinos de viagem com os campos cidade e pais"_ · domínio: `generico`

| Item | Conteúdo |
|---|---|
| Pacote | `destinos` (registrado em `INSTALLED_APPS` de `web/config/settings.py`) |
| Entidade | `Destino` — campos: `cliente`, `codigo`, `quantidade`, `valor_unitario`, `cidade`, `pais`, `observacao`, `tipo` |
| Padrões | Encapsulamento com @property, Polimorfismo (herança + sobrescrita), SRP + OCP (separar responsabilidades), Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), Singleton, Factory Method, Abstract Factory, Builder, Prototype, Strategy — o núcleo deste módulo fica em `nucleo/` (dentro da app) |
| Form | `DestinoForm` (`forms.py`): o MESMO ModelForm valida as telas e a API |
| CRUD (telas) | `/destinos/` · `/destinos/novo/` · `/destinos/<id>/` · `/destinos/<id>/editar/` · `/destinos/<id>/excluir/` |
| API REST | `/destinos/api/v1/` (GET, POST) · `/destinos/api/v1/<id>/` (GET, PUT, PATCH, DELETE) |
| Settings | `settings.py` desta app: `API_LIMITE`, `API_ESCRITA` (no projeto: `DESTINOS_API_LIMITE`…) |
| Arquivos | `settings.py` · `models.py` · `forms.py` · `services.py` · `viewmodels.py` · `views.py` · `api.py` · `urls.py` · `templates/` · `static/` · `nucleo/` · `tests/` |
| Testes | `cd web && python -m pytest destinos` (telas, API e o núcleo em `tests/nucleo/`) |
| Banco | `bash iniciar.sh migrar` (o `makemigrations` já inclui `destinos`) |

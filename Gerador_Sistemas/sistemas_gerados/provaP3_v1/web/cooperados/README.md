# Módulo `cooperados` — Cooperado (acrescentado por `sgs app`)

Pedido: _"Criar uma classe"_ · domínio: `generico`

| Item | Conteúdo |
|---|---|
| Pacote | `cooperados` (registrado em `INSTALLED_APPS` de `web/config/settings.py`) |
| Entidade | `Cooperado` — campos: `cliente`, `codigo`, `quantidade`, `valor_unitario`, `observacao`, `tipo` |
| Padrões | Encapsulamento com @property, Camada de Service (MVC/MVT/MVP — a regra não sabe o que é web), Strategy — o núcleo deste módulo fica em `nucleo/` (dentro da app) |
| Form | `CooperadoForm` (`forms.py`): o MESMO ModelForm valida as telas e a API |
| CRUD (telas) | `/cooperados/` · `/cooperados/novo/` · `/cooperados/<id>/` · `/cooperados/<id>/editar/` · `/cooperados/<id>/excluir/` |
| API REST | `/cooperados/api/v1/` (GET, POST) · `/cooperados/api/v1/<id>/` (GET, PUT, PATCH, DELETE) |
| Settings | `settings.py` desta app: `API_LIMITE`, `API_ESCRITA` (no projeto: `COOPERADOS_API_LIMITE`…) |
| Arquivos | `settings.py` · `models.py` · `forms.py` · `services.py` · `viewmodels.py` · `views.py` · `api.py` · `urls.py` · `templates/` · `static/` · `nucleo/` · `tests/` |
| Testes | `cd web && python -m pytest cooperados` (telas, API e o núcleo em `tests/nucleo/`) |
| Banco | `bash iniciar.sh migrar` (o `makemigrations` já inclui `cooperados`) |

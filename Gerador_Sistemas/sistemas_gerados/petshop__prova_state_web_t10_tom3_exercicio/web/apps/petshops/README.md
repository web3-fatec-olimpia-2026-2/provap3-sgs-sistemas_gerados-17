# App `petshops` — PETShop

Documentação individual da app (Instruções de desenvolvimento DJANGO §9.3).

| Item | Conteúdo |
|---|---|
| Finalidade | Cadastro e listagem de `Petshop` com o valor calculado pela política de tipo de cliente (Strategy do núcleo). Não faz autenticação nem pagamento. |
| Dependências | `nucleo/` (Python puro, `nucleo.politicas`); Django; chaves do `web/.env`. |
| Modelos | `Petshop` (chave UUIDv4) com ID interno LNNL — sem escopo de tenant (modo `single`). |
| Serviços públicos | `PetshopService.valor_final(obj)` e `PetshopService.resumo(objetos)` (`services.py`). |
| URLs | `petshops:lista` (`/`), `petshops:criar` (`/novo/`), `petshops:api` (`/api/`). |
| Instalação em outro projeto | `INSTALLED_APPS += ["apps.petshops"]`, `path("", include("apps.petshops.urls"))`, `python manage.py migrate`. |
| Testes | `cd web && python -m pytest apps/petshops` |

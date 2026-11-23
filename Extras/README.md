# Extras — material fora das 11 aulas

Módulos de "Atividades de aula" que não são uma das 11 aulas, mais o repositório de referência.
Material original + texto extraído; **sem resolução** (não têm entrega nem caem como conteúdo novo
na P3, mas reforçam a base).

| Pasta | O que é | Conteúdo |
|---|---|---|
| `Encontro_Remoto_01_Nivelamento/` | Sábado 22/08, assíncrono | Slides "Nivelamento: firmando a base" + FAQ (Dropbox) + 3 labs com testes: **lab1** OO do zero (classe, objeto, `self`), **lab2** encapsulamento (`@property`), **lab3** herança (`super()`, é-um) |
| `Encontro_Remoto_02_Nivelamento/` | Sábado 19/09, assíncrono | Slides + guia de estudo + FAQ + 3 labs: **lab1_sql** (SELECT/WHERE/JOIN — o que o ORM faz por baixo), **lab2_git** (branch e conflito), **lab3_erro** (3 passos para ler erro do Python); 2 áudios em `midia/` |
| `Apresentacao_Marco1/` | 11/09 | Slides do professor sobre as apresentações do Marco 1 (Caderno de Design) |
| `repo_ilp_referencia/` | GitHub `web3-fatec-olimpia-2026-2/ilp-referencia` (público) | Branch `aula-02`: `Reserva` com `@property` construída em TDD. ⚠️ tem o bug `if value <= 1` em `diarias` (rejeita 1 diária) — ver `Aula02_.../RESUMO.md` |

Para rodar um lab de nivelamento (no WSL):

```bash
cd "Extras/Encontro_Remoto_01_Nivelamento/material_original/ILP037_Nivelamento_ER01/lab2"
../../../../../.venv/bin/python -m pytest tests/ -v
```

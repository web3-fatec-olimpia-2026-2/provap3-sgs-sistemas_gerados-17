# Referências estáticas

Cópias locais de páginas externas usadas como **origem e referência** do estudo. Cada cópia guarda de onde veio
e a data em que foi incorporada. Nenhuma delas é editada: só se acrescenta a identificação da origem.

| Página | Abrir | Fonte | Versão copiada | Incorporada em |
|---|---|---|---|---|
| Padrão de projeto de software (Wikipédia) | [`wikipedia_padrao_de_projeto_de_software.html`](wikipedia_padrao_de_projeto_de_software.html) | <https://pt.wikipedia.org/wiki/Padr%C3%A3o_de_projeto_de_software> | revisão `oldid=65925269` | 22/11/2026 (texto) · 23/11/2026 (layout) |
| Django Study Hub | [`django_study_hub.html`](django_study_hub.html) | <https://mrsautchuk.github.io/django-study-hub/> | commit `d5008d7` de 21/11/2026 ([repositório](https://github.com/MrSautchuk/django-study-hub)) | 23/11/2026 |

As duas abrem com **duplo clique** (sem servidor). Os links de dentro levam aos sites originais (precisam de rede).

## Wikipédia — Padrão de projeto de software

- Usada pelo gerador (`gerar_sistema.py`, constante `REFERENCIA_GOF`) como fonte da lista GoF: 23 padrões —
  5 de criação, 7 estruturais e 11 comportamentais.
- **Layout original:** o HTML da página e o CSS da própria Wikipédia (skin Vector 2022) ficam em
  `wikipedia_padrao_de_projeto_de_software_arquivos/`, junto com os ícones e as imagens da página.
  Os scripts foram removidos; a página usa o modo sem JavaScript do próprio Vector (menus só com CSS).
- No topo há uma faixa azul com a fonte, a revisão e as datas — é a única coisa acrescentada.
- Correção de 23/11/2026: a cópia de 22/11 tinha só o texto do artigo com um CSS genérico; caixas, infobox e
  tabelas ficavam desalinhadas e, no tema escuro do sistema, com texto ilegível. Agora usa o CSS da Wikipédia,
  com a **mesma revisão** do texto.
- Licença do texto: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br); autores no
  [histórico de edições](https://pt.wikipedia.org/w/index.php?title=Padr%C3%A3o_de_projeto_de_software&action=history).

## Django Study Hub

- Site estático em português para estudar Django (Desenvolvimento Web III / prova P3): visão geral, projeto guiado,
  modo prova P3, simulado e módulos (models, URLs, views, ORM, templates, forms, DRF, testes).
- **Layout original:** `index.html`, `src/style.css` e `src/app.js` do site entram **sem alteração**, embutidos num
  único `django_study_hub.html`. Os 14 arquivos `data/*.json` também vão embutidos: aberto por `file://`, o
  navegador bloquearia o `fetch('./data/...')` do site, então uma ponte mínima de `fetch` entrega os JSON embutidos.
- A origem e a data aparecem num comentário no topo do arquivo, em dois `<meta>` (`sgs-origem`,
  `sgs-incorporado-em`) e numa linha do rodapé do próprio site.
- `django_study_hub_arquivos/` guarda os arquivos **como vieram do site** (index.html, src/, data/, README.md),
  para comparar com versões futuras. Eles funcionam servidos por HTTP (ex.: `python3 -m http.server`), não por
  duplo clique.
- O repositório não declara licença: a cópia é só para estudo pessoal, com crédito ao autor — não redistribuir.
- Favoritos, histórico e tema ficam no `localStorage` do navegador (como no site); nada é enviado para fora.

## Atualizar uma cópia

Os scripts de `montagem/` refazem as cópias a partir dos arquivos baixados (rodar no WSL, fora da pasta baixada):

```bash
python3 -I montagem/montar_wikipedia.py <pasta com pagina.html e estilo1..3.css> <pasta de saída>
python3 -I montagem/montar_study_hub.py <pasta com index.html, src/, data/ e README.md> <pasta de saída>
```

Ao atualizar, troque a revisão/commit e a data de incorporação no script e nesta tabela.

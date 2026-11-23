# Plano de Estudo — Técnicas de Programação II (ILP-037)

> Equipe Teams: **Tecnicas de Programacao II-A1129-N-D.S.M.-312-20262** (Fatec Olímpia · DSM · 2026/2)
> Prof. José Ceron Neto · Objetivo final: **treinar para a Prova Prática (P3) de 27/11/2026**,
> usando o *Kit de Revisão* da **Aula 11** como guia.

---

## 1. O que esta tarefa fez

| Etapa | O que aconteceu | Resultado no disco |
|---|---|---|
| 1. Localizar | Teams (Chrome) → **Atividades de aula** (app Classwork). Os arquivos ficam na biblioteca **Classwork** do SharePoint da equipe; alguns módulos apontam para pastas no OneDrive do professor, Dropbox e GitHub. | — |
| 2. Extrair | Download da biblioteca Classwork inteira (111 arquivos, com vídeos/áudios) + links extras: Aula 02 (OneDrive: enunciados 02a/b/c e 2 guias PDF), Aula 03 (Dropbox: lab, enunciados 03a/b/c, soluções, complementar), Encontro Remoto 01 (Dropbox: labs + FAQ) e o repositório GitHub de referência. | `AulaXX_*/material_original/` |
| 3. Organizar | Uma pasta por aula (11) + `Extras/`. Zips de laboratório descompactados; vídeos/áudios em `material_original/midia/`. | `AulaXX_*/` |
| 4. Resumir | Todos os PDFs convertidos em texto; um `RESUMO.md` por aula. | `AulaXX_*/material_texto/`, `AulaXX_*/RESUMO.md` |
| 5. Resolver | Todos os laboratórios, dojos e homeworks, com código **comentado** e testes `pytest` (os testes originais do professor foram mantidos; acrescentei testes de limite e de "antes × depois"). | `AulaXX_*/resolucao/` |
| 6. Treinar | Treino no formato da P3, a partir da Aula 11: reconhecer, prever, achar o erro, explicar a função + 7 exercícios de código com gabarito. | `Treino_Prova/` |

**Não baixado (só citado):** links do Microsoft Forms (diagnósticos/quizzes), playlists do YouTube,
NotebookLM (mapas mentais/flashcards — exigem login Google) e as tarefas do app "Trabalhos".
A pasta *Documentos* do canal Geral tem envios de colegas — não é material de aula, não foi copiada.

---

## 2. Mapa das aulas

| Pasta | Tema | Labs/atividades resolvidos |
|---|---|---|
| [`Aula01_Kickoff`](Aula01_Kickoff/RESUMO.md) | Classe × objeto, `self`, oficina de modelagem | HW01, HW01b, oficina |
| [`Aula02_Encapsulamento_Propriedades`](Aula02_Encapsulamento_Propriedades/RESUMO.md) | Encapsulamento, `@property`, TDD, ADR | Reserva TDD, HW02a/b/c |
| [`Aula03_Encapsulamento_Dois_Mundos`](Aula03_Encapsulamento_Dois_Mundos/RESUMO.md) | `@property` × validador Django; herança × composição | Lab capacidade, HW03a/b/c |
| [`Aula04_Polimorfismo`](Aula04_Polimorfismo/RESUMO.md) | Herdar × sobrescrever, função polimórfica | Lab quartos, HW04a/b/c, extra `abc` |
| [`Aula05_Strategy`](Aula05_Strategy/RESUMO.md) | 1º padrão: Strategy; Marco 1 | Lab tarifa, HW05a/b/c |
| [`Aula06_SRP_OCP`](Aula06_SRP_OCP/RESUMO.md) | SRP, OCP, princípio × padrão | Lab recibo, HW06a/b/c |
| [`Aula07_Arquitetura_MVC_MVT_MVP`](Aula07_Arquitetura_MVC_MVT_MVP/RESUMO.md) | MVC/MVT/MVP, Service testável sem HTTP | Lab relatório, HW07a/b/c |
| [`Aula08_MVVM_Adapter`](Aula08_MVVM_Adapter/RESUMO.md) | MVVM (ViewModel) e Adapter | Lab1 MVVM, Lab2 Adapter, HW08a/b/c |
| [`Aula09_Dojo_MVVM_Facade`](Aula09_Dojo_MVVM_Facade/RESUMO.md) | Dojo MVVM e Facade | Dojo check-in, Lab Facade, HW09a/b/c |
| [`Aula10_Sprint3_Decorator`](Aula10_Sprint3_Decorator/RESUMO.md) | Decorator; trio estrutural; Sprint 3 | Lab extras, HW10a/b/c |
| [`Aula11_Retomada_Prova`](Aula11_Retomada_Prova/RESUMO.md) | Retomada pré-P3 (sem conteúdo novo) | Kit de revisão resolvido, 6 cards em código |
| [`Extras`](Extras/README.md) | Encontros Remotos 01/02, Marco 1, repositório de referência | (material de apoio) |
| [`Treino_Prova`](Treino_Prova/README.md) | **Treino para a P3** | 5 folhas + 7 exercícios com gabarito |
| [`Gerador_Sistemas`](Gerador_Sistemas/README.md) | **Gerador determinístico** (sem IA) de sistemas de estudo para qualquer assunto: os 23 padrões GoF por categoria + os 5 fundamentos das aulas, validação, testes, ADRs e site Django pronto para subir | `gerar_sistema.py` + tela estilo terminal com comandos `sgs` (`tela_prompt.py`) + cópia da Wikipédia (`referencias/`) + 4 exemplos |

---

## 3. Estrutura de cada pasta de aula

```
AulaXX_Tema/
├── RESUMO.md              ← conceitos da aula + tabela de onde está cada resolução
├── material_original/     ← arquivos como vieram do Teams (PDF, .md, .zip descompactado, .py, midia/)
├── material_texto/        ← texto extraído dos PDFs
└── resolucao/             ← labs e homeworks resolvidos (código comentado + testes)
```

Homeworks escritos com **IA vedada (nível 3)** estão como *modelo de estudo* — escreva o seu antes
de comparar. ADRs (tarefas de equipe) estão como *modelos* a adaptar ao projeto real da equipe.

---

## 4. Como rodar

Ambiente: `.venv` na raiz (Python 3 do WSL, com `pytest` e `pypdf`).

```bash
bash rodar_testes.sh            # todas as pastas (em 22/11/2026: 35 conjuntos, 1015 testes)
bash rodar_testes.sh Aula05     # só uma aula
```

Gerar um sistema de estudo novo para um assunto qualquer (ver `Gerador_Sistemas/README.md`):

```bash
.venv/bin/python Gerador_Sistemas/gerar_sistema.py --assunto "clínica em que a consulta varia conforme o convênio" --testar
```

Ou pela **tela estilo terminal** no navegador (escreva o pedido e tecle Enter; `sgs` mostra os comandos
de configuração, listagem, testes e para subir o site Django; gerar é `sgs gerar <pedido>`) — abre em http://127.0.0.1:6100:

```bash
.venv/bin/python Gerador_Sistemas/tela_prompt.py
```

Treinar um exercício contra a SUA resolução:

```bash
cd "Treino_Prova/exercicios/ex01_strategy_frete" && ALVO=exercicio ../../../.venv/bin/python -m pytest -v
```

---

## 5. Pontos de atenção encontrados no material

- **P3 = 27/11**, sem IA; o professor sorteia uma função **do seu código** e pergunta o quê / por quê / o que muda.
- O repositório de referência (branch `aula-02`) tem `if value <= 1` em `diarias` → rejeita reserva de 1 diária. A versão correta (`< 1`) está no guia de estudo e na minha resolução, com teste de limite.
- Datas finais: 04/12 entrega do Caderno de Design · 11/12 encerramento.

---

## 6. Andamento

- [x] Acessar o Teams e mapear o material (Classwork → SharePoint, OneDrive, Dropbox, GitHub)
- [x] Escrever este plano
- [x] Baixar e organizar o material nas 11 pastas (+ Extras)
- [x] Extrair texto dos PDFs e escrever os `RESUMO.md`
- [x] Resolver laboratórios e homeworks (código comentado + testes) — 232 testes passando
- [x] Montar `Treino_Prova/` a partir da Aula 11
- [x] Analisar o django-study-hub e criar o gerador determinístico `Gerador_Sistemas/gerar_sistema.py`
- [x] Tela estilo terminal com comandos `sgs`; os 23 padrões GoF por categoria (referência: cópia da Wikipédia de 22/11/2026);
      modos "só gerar" e "apenas o código"; Django pronto para subir (`iniciar.sh`, `.env`, migrations, superusuário)
- [x] SGS: numeração fixa e portas 8100+NN (hoje 6100+NN), terminal (cd, source, manage.py…), `sgs comand`, PWA
- [x] Estilos (simples · cmd · bootstrap · web com os temas de `temas/`), Bootstrap local, notas de apresentação,
      opções das Instruções Django (UUID, apps/, baseline de segurança) e do `motor-id-interno` (LNNL),
      perguntas antes de gerar (rodadas de 10, `sgs gerar -sp`)
- [x] CRUD completo no site gerado; modo exercício virou questionário com "Ver resposta" (o código sai sempre
      completo); identificador de tipos dos campos (`tipos_campos.py`: texto, inteiro, decimal, sim/não, data —
      só os tipos duvidosos viram pergunta)
- [x] 100 domínios em 10 setores (`Gerador_Sistemas/catalogo_100_dominios.txt` + `dominios.py`), escolha do domínio
      por pontos (+3 pelo nome), `sgs dominios <termo>` e `--listar <termo>`
- [x] `.gitignore` para subir a pasta inteira no GitHub (raiz, `Gerador_Sistemas/`, `sistemas_gerados/` e o de cada
      sistema gerado): mínimo das Instruções Django §4.7 + `db.sqlite3` + `Zone.Identifier` + estado local do SGS
- [x] SGS: portas na base 6100 e liberadas ao parar/fechar/reabrir (porta ocupada → pergunta "forçar? s/N"); prompt
      em duas linhas (`$>` embaixo); histórico global em arquivo (`history`, `history -c`, sobrevive ao F5); todo
      comando padrão também com `sgs` na frente; versões (`sgs editar NN` → 01.1 … 01.99, porta 61011…) e módulos
      (`sgs app NN <pedido>`: mais uma app Django com form, CRUD, API REST, padrões, settings e testes)
- [x] Incremento perguntado: `sgs app` pergunta o nome da funcionalidade (pelo contexto), versão ou edição sem
      versionar (`-sv`), a ligação com uma classe existente (`Viagcert.destino → Destino`), campos e padrões;
      `sgs ligar NN Classe.campo Alvo` (ForeignKey opcional no models, form, API e testes, com a migration)
- [x] `sgs incrementar NN Classe.campo <padrão>`: acrescenta ou modifica um campo com um padrão (inteiro>=0,
      faixa, decimal, lista fechada, texto, sim/não, data) — a classe é refeita (o @property do núcleo, o model,
      o form, a API e os testes); perguntado com "Perguntar"; versão ou `-sv`
- [x] Intellisense na tela (até 5 sugestões enquanto se digita, a sugestão em cinza na linha completa com TAB, clique
      escolhe) e verificação de todos os comandos listados, com e sem `sgs`
- [x] `sgs api config NN`: os campos de cada endpoint da API (v1 e resumo de cada app) expostos ou ocultos, campo a
      campo (gravado no `config/settings.py`); `?campos=` escolhe entre os expostos; `/api/v1/campos/` lista
- [x] `sgs tutorial` (classe nova, ligar, campos, padrão de um campo: tipo, @property, lista; padrões de projeto; API)
      lado a lado com a Wiki (formatação corrigida: servida da pasta `referencias/`, o CSS carrega) e o Django Study
      Hub (`sgs hub`); três linhas de comandos principais separados por `|`, a 1ª começando pela cor da janela
      (`sgs visual`: CMD/PowerShell, o padrão ao abrir, ou a do SGS)
- [x] Tela no estilo do Prompt de Comando: `sgs cmd` (o padrão ao abrir; também `cmd`) e `sgs cmd sgs` (as cores do
      SGS) no lugar do seletor do topo; topo sem o nome, com os comandos sem o `sgs` até o fim da tela; barra da
      janela só "SGS"; prompt `~\caminho>` numa linha; caixas do rodapé numa linha, sem cor
- [x] Janela de app num perfil só do SGS (sem ícone de extensão e sem ⋮), sempre com `pwa=true` ao abrir;
      Alt+Enter maximiza/volta; `sgs topo` (abre oculto) e `sgs foot` alternam o topo e as caixas; sem botão executar
- [x] A tela também pelo Django: `python manage.py runserver` da raiz do projeto (o `manage.py` da raiz repassa
      para o `Gerador_Sistemas/manage.py`, que também funciona de lá; sem o `.venv` ativado, os dois rodam de novo
      com o python do `.venv`) (porta 6100, mesmo início e
      janela); as rotas saíram do http.server para `tela_prompt.atender()`, usada pelos dois servidores; a tela abre
      sem topo e sem caixas; `sgs topo` e `sgs foot` são sempre as duas primeiras sugestões ao digitar `sgs`
- [x] O `.venv` mora em `Gerador_Sistemas/.venv` (recriado pelo `Gerador_Sistemas/requirements.txt`); na raiz, um
      atalho `.venv` para ele (ativar e runserver nas duas pastas)
- [x] requirements.txt dos sistemas gerados: o Python exigido (3.12+, conferido pelo iniciar.sh), o Django e o que
      ele usa, os testes e as dependências pontuais de cada sistema, cada linha com o porquê; o `iniciar.sh deps`
      confere TODAS (pip --no-index, sem internet) em vez de só Django/pytest

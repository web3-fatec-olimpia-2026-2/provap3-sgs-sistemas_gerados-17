# SGS - Sistema Gerador de Sistema (ILP-037 · P3)

Monta, **sem IA**, um sistema de exemplo completo para **qualquer assunto de prova**: código comentado,
testes, ADRs, README explicativo e, se você quiser, um site Django **pronto para subir** (Bootstrap e
temas, `.env`, migrations, superusuário, PWA). **A mesma entrada gera sempre a mesma saída, byte a byte**
(há teste que garante isso).

| Peça | Para quê |
|---|---|
| [`tela_prompt.py`](tela_prompt.py) | o **SGS**: tela estilo terminal no navegador (porta 6100); as rotas em `atender()` |
| [`manage.py`](manage.py) · [`sgs_web/`](sgs_web/) | a mesma tela pelo **Django**: `python manage.py runserver` (settings mínimo, uma view que chama `atender()`) |
| [`../iniciar.sh`](../iniciar.sh) · [`../iniciar.bat`](../iniciar.bat) · [`../requirements.txt`](../requirements.txt) | **um comando num PC novo** (Linux/WSL e Windows/FATEC): prepara `.venv`, `requirements.txt`, `.env`, migrations e sobe o SGS ou qualquer sistema gerado |
| [`requirements.txt`](requirements.txt) · `.venv/` | o ambiente do projeto (Python 3.12+, Django, DRF, pytest, pytest-django, argon2): o `.venv` mora aqui; na raiz há um atalho para ele |
| [`gerar_sistema.py`](gerar_sistema.py) | o gerador (também roda sozinho, pela linha de comando) |
| [`sgs_terminal.py`](sgs_terminal.py) · [`sgs_comand.py`](sgs_comand.py) · [`sgs_perguntas.py`](sgs_perguntas.py) | terminal da tela · help numerado · perguntas antes de gerar |
| [`temas_web.py`](temas_web.py) | cores dos 10 temas × 6 tons (pasta `temas/`) e das 20 paletas, com contraste WCAG |
| [`dominios.py`](dominios.py) · [`catalogo_100_dominios.txt`](catalogo_100_dominios.txt) | os **101 domínios** em 11 setores: a lista do usuário (001–100) + o **101** da Prova Prática P3 (`citricultura`) |
| [`tipos_campos.py`](tipos_campos.py) | **identificador de tipos**: acha os campos do pedido e deduz o tipo pelo nome (texto, inteiro, decimal, sim/não, data) |
| `recursos/bootstrap-5.3.3/` | Bootstrap copiado para dentro do projeto (ver [`recursos/README.md`](recursos/README.md)) |
| `temas/` · `Instruçõs de desenvolvimento DJANGO/` · `motor-id-interno/` | referências usadas nas opções da camada web |
| `referencias/` | cópia da Wikipédia (lista GoF) com fonte, revisão, data da consulta (22/11/2026) e licença |
| `tests/` | testes do gerador e do SGS (`python -m pytest -v` nesta pasta) |
| `sistemas_gerados/` | onde os sistemas são criados (e o registro dos números fixos) |

---

## 1. Rodar o SGS

### Como usar em um PC novo (um comando)

Depois de clonar o repositório em qualquer máquina com **Python 3.12+**, rode na **raiz do projeto** (ou `bash ../iniciar.sh` / `..\iniciar.bat` de dentro de `Gerador_Sistemas/`):

**Linux / WSL / macOS / Git Bash:**

```bash
bash iniciar.sh                       # prepara tudo e sobe o SGS (http://127.0.0.1:6100)
bash iniciar.sh provap3               # prepara ambiente, .env, migrations e admin e sobe o provaP3
bash iniciar.sh sistema <pasta> [p]   # prepara e sobe qualquer sistema em sistemas_gerados/<pasta>
source iniciar.sh ativar              # prepara (se precisar) e deixa o .venv ATIVO no terminal atual
bash iniciar.sh preparar              # prepara .venv, atalho na raiz, deps e .env sem subir servidor
bash iniciar.sh testar [filtro]       # garante o ambiente e roda rodar_testes.sh
```

**Windows (`cmd` ou PowerShell — ex.: máquinas da FATEC, sem alterar `ExecutionPolicy`):**

```bat
iniciar.bat                           REM prepara tudo e sobe o SGS (http://127.0.0.1:6100)
iniciar.bat provap3                   REM prepara .env, migrations e admin e sobe o provaP3
iniciar.bat sistema <pasta> [porta]   REM prepara e sobe qualquer sistema em sistemas_gerados\<pasta>
iniciar.bat ativar                    REM prepara (se precisar) e ativa o .venv no cmd atual
iniciar.bat preparar                  REM prepara .venv e deps sem subir servidor
iniciar.bat testar [nome]             REM roda pytest do SGS ou de um sistema específico
```

**O que os scripts fazem automaticamente (de forma idempotente — se já estiver pronto, pulam rápido):**
1. Limpam `DJANGO_SETTINGS_MODULE` antes de rodar (evita que `sgs_web.settings` contamine os sistemas gerados).
2. Localizam o Python ≥ 3.12 disponível (`python3`, `python3.14`, `python3.13`, `python3.12`, `python` ou `py -3` no Windows).
3. Criam `Gerador_Sistemas/.venv` (se não existir) e o atalho `.venv` na raiz; os sistemas gerados reaproveitam o `Gerador_Sistemas/.venv` automaticamente quando presente.
4. Instalam `requirements.txt` apenas se faltar alguma dependência (checagem offline `--no-index` antes).
5. Criam `.env` a partir de `.env.example` quando existir e ainda não houver `.env` (gerando uma `SECRET_KEY` nova, sem nunca sobrescrever um `.env` existente).
6. Aplicam `makemigrations` + `migrate` e `garantir_admin` quando o projeto/sistema usar banco de dados.
7. Verificam se a porta está livre antes de subir o `runserver`.

*(Também funciona dentro da pasta de qualquer sistema gerado: `cd Gerador_Sistemas/sistemas_gerados/provaP3 && bash iniciar.sh` ou `source iniciar.sh ativar`.)*

### Rodar manualmente (com o ambiente já pronto)

No WSL, na raiz do projeto, com o `.venv` ativado — pelo **Django**:

```bash
source .venv/bin/activate
python manage.py runserver              # http://127.0.0.1:6100 (o 00) e abre a janela de app
python manage.py runserver --sem-abrir  # só sobe o servidor · runserver 6150 = outra porta
```

(o `manage.py` da raiz só repassa para o `Gerador_Sistemas/manage.py`; de dentro de `Gerador_Sistemas/` o mesmo
comando também funciona) ou, sem Django (só a biblioteca padrão): `python Gerador_Sistemas/tela_prompt.py`.

O **`.venv` mora em `Gerador_Sistemas/.venv`** (tudo do projeto numa pasta só; fora dela ficam as aulas) e é
criado pelo [`requirements.txt`](requirements.txt) desta pasta:

```bash
cd Gerador_Sistemas && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

Na raiz do projeto há um **atalho** `.venv` → `Gerador_Sistemas/.venv` (link simbólico, fora do git), então
`source .venv/bin/activate` e `python manage.py runserver` valem nas duas pastas. Sem ativar (terminal novo: só
existe o `python3` do sistema, sem Django), `python3 manage.py runserver` também funciona — os dois `manage.py`
percebem e rodam de novo com o python do `.venv`.
Os dois servem **a mesma tela**: as rotas moram em `tela_prompt.atender()`, que o `http.server` e a view do Django
(`sgs_web/`: settings mínimo, sem banco nem sessão, uma rota só) chamam do mesmo jeito. No Django, o `runserver`
do SGS usa a porta 6100 quando nenhuma é dada, faz o mesmo início (estilo cmd, sites de uma tela anterior
encerrados) e reinicia sozinho quando um arquivo do SGS muda (derrubando os sites que subiu, como no Ctrl+C).

Abre em **http://127.0.0.1:6100**, numa janela de app (PWA). Ctrl+C no terminal para parar. A tela sempre abre em **janela de app** (`pwa=true`) do Chrome (ou Edge) num
**perfil só do SGS** (`%LOCALAPPDATA%\SGS\navegador`): sem extensões e sem app instalado, a janela fica limpa — só
o título **SGS** e os botões da janela, sem o ícone de extensão e sem o ⋮. (O atalho “SGS” instalado pelo Chrome
continua mostrando os dois: é o Chrome que põe esses botões nos apps instalados.) **Alt+Enter** maximiza a janela;
de novo, volta ao tamanho de antes.

A tela abre limpa como o Prompt de Comando: `sgs topo` mostra no topo os **comandos principais sem o `sgs` na
frente** (`ajuda|gerar|listar|…|cmd|topo|foot`, fonte menor, separados por `|`, até o fim da tela; o clique executa
ou escreve no prompt o comando inteiro) e, de novo, oculta. `sgs foot` mostra as caixas de seleção e, de novo,
oculta (a linha do comando sempre fica) — a tela abre sem as duas. Ao digitar `sgs`, as duas primeiras sugestões
do intellisense são sempre `sgs topo` e `sgs foot`. Não há botão executar: o Enter executa.

A tela **abre sempre no estilo do Prompt de Comando** do Windows (`sgs cmd`): fundo `#0c0c0c` e tudo em cinza
`#cccccc` — o prompt numa linha só, `~\caminho>comando`, e as caixas do rodapé numa linha, sem cor. Para as cores
do SGS: `sgs cmd sgs` (prompt verde em duas linhas: `sgs@ilp037:~/caminho` em cima, `$>` e o comando embaixo).
Sem o `sgs` na frente também vale: `cmd` · `cmd sgs`.

**Estudo lado a lado:** `sgs tutorial` (classe nova, ligar, campos, o padrão de um campo, padrões de projeto, API),
`sgs wiki` (cópia da Wikipédia, com o CSS dela) e `sgs hub` (cópia do Django Study Hub). As três páginas têm a mesma
barra no topo, `Tutorial|Wiki · padrões GoF|Django Study Hub|← SGS` — injetada só na resposta: as cópias em
`referencias/` ficam intactas.

| O que você digita | O que acontece |
|---|---|
| `sgs gerar <pedido>` | **gera** (ou começa as perguntas, se “Perguntar antes de gerar” estiver marcado) |
| `sgs gerar -sp <pedido>` | gera **sem perguntar**; sozinho, no meio das perguntas, encerra e gera |
| texto solto | só é **anotado** na tela (nada é gerado por engano) |
| `cd`, `ls`, `pwd`, `tree`, `cat`, `date`, `uname`, `history`, `clear`, `source .venv/bin/activate`, `python manage.py migrate/runserver…`, `pytest`, `bash iniciar.sh` | terminal — **todo comando padrão funciona com ou sem `sgs` na frente** (`sgs ls`, `sgs history -c`) — `sgs comand` explica cada um |
| `sgs …` | configura, lista, roda e explica (digite só `sgs`) |

**Intellisense:** enquanto você digita, uma caixa acima do prompt mostra até **5 sugestões**, que mudam a cada
tecla. Com a caixa aberta:

- **↑/↓ andam entre as opções**, e a lista dá a volta;
- **TAB** ou **→**, com o cursor no fim da linha, escolhem a marcada. Ela tem a etiqueta "TAB · →" e, se começar
  com o que já foi digitado, aparece também na própria linha, em cinza;
- **clique** numa opção também escolhe;
- Esc fecha a caixa.

Com a caixa fechada, ↑/↓ voltam a ser o histórico.

As sugestões vêm de `/sugestoes`:
- o histórico, do mais recente para o mais antigo;
- as pastas para o `cd`;
- os comandos de cada sistema, já com o número (`sgs rodar 16`, `sgs incrementar 16`…);
- os comandos `sgs`;
- os comandos padrão, com e sem `sgs`.

A ordem é: começa com o que foi digitado → uma palavra começa com ele → contém → as letras na ordem. Há teste
que varre todos os comandos listados (o `sgs`, o `sgs comand` e os do terminal), com e sem `sgs` na frente.

**Histórico:** cada comando vai para o arquivo `Gerador_Sistemas/.sgs_historico` (como o `~/.bash_history`):
↑/↓ continuam funcionando depois do F5 e ao reabrir a tela. `history` (ou `sgs history`) mostra numerado,
`history N` os últimos N, `history -c` limpa e `history -d N` apaga uma linha. Respostas de pergunta não
entram, e senha digitada num comando (`admin_senha=…`) entra mascarada.

Principais comandos `sgs`:

| Comando | O que faz |
|---|---|
| `sgs provap3` | **Prova Prática P3**: gera o domínio 101 (`citricultura`) em `sistemas_gerados/provaP3` (projeto `cooperativa`, app `citricultura`, `/citricultura/` + DRF em `/api/`) e prepara o ambiente; se a pasta já existe, pergunta (`s/N`) antes de apagar |
| `sgs listar` · `sgs info NN` · `sgs testar NN` | sistemas pelo **número fixo** (01, 02…, dado na geração) e as **versões** (01.1, 01.2…) |
| `sgs rodar NN [porta]` · `sgs parar NN` · `sgs servidores` | sobe/derruba o site; o SGS é o 00 (porta 6100), o 01 roda na 6101, a versão 01.3 na 61013 |
| `sgs editar NN` | **editar = copiar**: cria a versão NN.k (01.1 … 01.99); o original não muda |
| `sgs app NN <pedido> [entidade=Nome] [padroes=a,b] [ligar=Classe.campo] [-sv]` | **funcionalidade nova** (módulo): mais uma app Django (form, CRUD, API REST, padrões, settings, models, views, testes); com “Perguntar”, pergunta o nome dela, versão ou edição e a ligação |
| `sgs ligar NN Classe.campo Alvo [-sv]` | campo de **referência** opcional entre duas classes do sistema (ex.: `Viagcert.destino → Destino`) |
| `sgs incrementar NN Classe.campo <padrão> [-sv]` | **incrementar/modificar** um campo com um padrão (`inteiro>=0`, `inteiro:1..30`, `lista:a,b,c`…), no @property e no Django |
| `sgs api config NN [<endpoint> campo=sim\|nao …]` | os **campos de cada endpoint** da API (v1 e resumo de cada app): expor ou ocultar, campo a campo |
| `sgs comandos NN` | comandos de terminal para rodar o sistema fora da tela |
| `sgs comand [n]` · `sgs exit` | help numerado da esteira de desenvolvimento · volta à tela principal |
| `sgs estilo [simples\|cmd\|bootstrap\|web]` · `sgs tema [T01…T10] [tom] [P01…P20]` | formatação das páginas geradas |
| `sgs tipos <campos>` | mostra o tipo que cada campo recebe pelo nome e quais viram pergunta (ex.: `sgs tipos nome, idade, status`) |
| `sgs cancelar` | desiste das perguntas em andamento |
| `sgs dominios [termo]` | os 101 domínios por setor (101 = Prova P3: `citricultura`); com termo, só os que batem (`sgs dominios saude`, `sgs dominios pet`, `sgs dominios 101`) |
| `sgs padroes` · `sgs config` · `sgs pwa=false` · `clear` | catálogo, configuração, PWA, limpar |
| `sgs tutorial` · `sgs wiki` · `sgs hub` | tutorial prático · Wikipédia (padrões GoF) · Django Study Hub, lado a lado |
| `sgs cmd` · `sgs cmd sgs` (ou `cmd` · `cmd sgs`) | estilo da tela: Prompt de Comando (padrão ao abrir) · cores do SGS |
| `sgs topo` · `sgs foot` | mostra/oculta os comandos do topo · mostra/oculta as caixas de seleção (alternam; a tela abre sem os dois) |

As caixas embaixo valem para o `sgs gerar` e ficam salvas: **+ Django**, **Modo exercício**, **Rodar testes**,
**Para estudo** (desmarcada = só gerar), **Comentários no código**, **Notas na web** e **Perguntar antes de gerar**.

### Perguntas antes de gerar

Com a caixa marcada, `sgs gerar <pedido>` faz **rodadas de 10 perguntas** antes de gerar, numa fila única:
1. Django, estilo, tema, tom e padrões;
2. **campos e tipos**: se o pedido não listou campos, pergunta quais; depois, **só o tipo dos campos que não é óbvio pelo nome** (ver abaixo);
3. finalidade, comentários no código, notas na web, exercício e testes;
4. UUID, LNNL e tipo, `apps/`, segurança, paleta, máquina de estados, nomes e domínio;
5. padrões de projeto um a um.

O que está **marcado** nas caixas não é perguntado, e o que não se aplica também não (sem Django, nada de estilo).
Ao fim de cada rodada aparece **“Refinar mais?”**: `sim` traz mais 10 perguntas. Só gera com `sgs gerar -sp`, que também vale no meio de qualquer pergunta (gera com o que já foi decidido). Para responder, use o número, o nome da opção, sim/não, um texto ou Enter (padrão).

### Campos e tipos (identificador de tipos)

O pedido pode listar campos a mais para a entidade: `sgs gerar pet shop com os campos nome do pet, raça, idade, peso, vacinado e data de nascimento`. O [`tipos_campos.py`](tipos_campos.py) faz duas coisas, por regras fixas:

- **acha a lista** depois de um gatilho (`com os campos`, `campos:`, `atributos`, `contendo`, `dados:`). Frases soltas como “banho e tosa” ou “campos obrigatórios” não viram campo;
- **deduz o tipo pelo nome**:

| Tipo | Sigla | Nomes óbvios (não são perguntados) | No núcleo | No Django |
|---|---|---|---|---|
| texto | String | nome, raça, email, telefone, cpf, placa… | recusa vazio | `CharField` |
| inteiro | INT | idade, ano, dias, quantidade, andar… | recusa bool e float; mínimo/faixa | `IntegerField` |
| decimal | FLOAT | preço, valor_…, peso, altura, salário, taxa… | recusa bool e texto | `DecimalField` |
| sim/não | BOOL | ativo, vacinado, pago, tem_…, e_… | só `True`/`False` | `BooleanField` (caixa de marcar) |
| data | DATE | data_…, nascimento, vencimento, …_em | texto `AAAA-MM-DD` validado | `DateField` (`<input type="date">`) |

Nomes ambíguos (codigo, numero, tamanho, status, nota…) ou desconhecidos ficam em **dúvida**: no questionário,
cada um vira a pergunta “Qual o tipo do campo X?”, com uma sugestão. Sem perguntas (`-sp`), vale a sugestão e
o cartão mostra uma nota. O tipo também pode ir junto no pedido (`idade:int`, `peso (decimal)`) e vence a dedução.
Campos que o domínio já tem, ou com nome reservado (`total`, `tipo`, `id`…), são ignorados com nota.

---

## 2. A camada web (com `+ Django`)

### Estilos e temas

| Estilo | Como fica |
|---|---|
| `simples` | sem formatação (HTML puro) |
| `cmd` | tela preta, estilo terminal |
| `bootstrap` | Bootstrap 5.3.3 padrão (navbar, cartões, tabela, formulário) |
| `web` | Bootstrap + **tema**: 10 temas × 6 tons da pasta `temas/` (T01 Profissional … T10 Personalizado; Claro … Escuro) |

- **Origem das cores:** os fundos de cada tema × tom foram copiados das imagens da pasta `temas/`. Os destaques de T02–T08 foram lidos das imagens, então são aproximados.
- **Contraste:** todos passam pelos mínimos WCAG das Instruções §11.7, com teste. O T09 Escuro dá 7,54:1, como no documento.
- **T10 Personalizado:** usa uma das 20 paletas das Instruções §11.9 (P01–P20).
- **Eixos de estilo (§11.10):** raio, sombra, movimento e tipografia vão em atributos `data-*` no `<html>`.
- **Bootstrap local:** vai **dentro** de cada sistema (sem CDN). Assim funciona offline e a CSP fica só com `'self'`.
- **Base visual:** as páginas estendem uma `base.html` fina com blocos nomeados (§11.5). Não há estilo nem script inline: há teste para isso.

### Notas na web × comentários no código

- **Comentários no código** são `#` e docstrings nos `.py`; a caixa “Comentários no código” liga e desliga.
- **Notas na web** são notas de **apresentação visíveis nas páginas**. Exemplos: “esta view é fina, quem calcula é o Service com o Strategy do núcleo”, “o selo vem do ItemVM”, “o formulário reaproveita os validators”. Elas têm um botão para ocultar, lembrado pelo navegador.

### Opções das Instruções de desenvolvimento DJANGO e do motor-id-interno

| Opção | O que gera | Referência |
|---|---|---|
| `id_publico=uuid` | chave `UUIDField` (UUIDv4) | Instruções §10.4 |
| `id_interno` (LNNL) | campo `id_interno` legível (`K21W-F92M-T5R-Q7L`), gerado no `save()` com nova tentativa em colisão; `lnnl.py` copiado do motor sem alteração | `motor-id-interno/` |
| `estrutura=apps` | app em `web/apps/<nome>/` com `README.md` da app | Instruções §9.2 e §9.3 |
| `seguranca=baseline` | cookies/cabeçalhos seguros, limites de entrada, **CSP nativa do Django 6** (Report-Only; `CSP_IMPOR=1` impõe), `ADMIN_URL` fora do padrão, Argon2id se instalado | Instruções §12–14 e §16.1 |

O `requirements.txt` do modo baseline inclui `argon2-cffi`; sem o pacote instalado, fica o PBKDF2 do Django.
O `.env` é lido pelo leitor próprio do projeto, não pelo `django-environ` das Instruções, para rodar sem
instalar nada. A geração continua guiada pelo **pedido**: essas opções são escolhas (perguntas, caixas e
`sgs config`), nunca obrigatórias.

### Modo exercício = questionário

O gerador **nunca** entrega código para você corrigir: o sistema sai sempre completo e correto, com os testes
verdes. Com **Modo exercício** marcado, ele gera também um **questionário de revisão** no formato da P3, sobre os
padrões daquele sistema: o smell, como foi aplicado, o tripé de cada função (o que faz · por que assim · o que
muda se), quando não usar e a alternativa descartada. Cada resposta fica **oculta** atrás do botão
**Ver resposta** (um `<details>`, sem JavaScript):

- `exercicios.html` na pasta do sistema, para abrir direto no navegador;
- com Django, a mesma página em `/exercicios/`, com link no topo (ou na lista), view, rota e teste próprios.

### API REST e settings de cada app

Toda app Django gerada (a principal e os módulos) traz, além das telas do CRUD:

| Arquivo | O que tem |
|---|---|
| `api.py` | API REST em JSON, só com Django: `api/v1/` (GET lista com `?limite=N`, POST cria) e `api/v1/<id>/` (GET, PUT, PATCH, DELETE). Valida com o **mesmo** ModelForm das telas, devolve `total` e `valor_final` (Strategy do núcleo), responde 400 com os erros por campo, 404 em JSON e 405 nos outros métodos. O CSRF continua ligado (sem `csrf_exempt`). |
| `settings.py` | as configurações da app: `API_LIMITE` (100) e `API_ESCRITA` (True), trocáveis no `config/settings.py` do projeto com o prefixo da app (ex.: `RESERVAS_API_ESCRITA = False` deixa a API só de leitura). |
| `tests/test_api.py` | criar, listar, ler, PUT, PATCH, DELETE, 400, 404, 405, os settings, os campos de cada endpoint e o CSRF (403 sem o token). |

**Campos de cada endpoint (`sgs api config`).** Cada app tem dois endpoints de leitura:

| Endpoint | Rota | Campos que mostra por padrão |
|---|---|---|
| **v1** (REST) | `/api/v1/` e `/api/v1/<id>/` | id, todos os campos do model (inclusive ligações e `id_interno`), `total` e `valor_final` |
| **resumo** (o link “API” do site) | `/api/` | id, `codigo`, `titulo` e `valor` |

Nos módulos, as rotas têm o nome da app na frente (`/destinos/api/v1/`). O `sgs api config NN` mostra cada endpoint,
campo a campo, com um clique para **ocultar** ou **expor**. Também dá para escrever direto:

```
sgs api config 16 /api/v1/ observacao=nao titulo=sim
sgs api config 16 /api/ noites=sim codigo=nao
sgs api config 16 /destinos/api/v1/ todos=nao id=sim cidade=sim
sgs api config 16 /api/v1/ padrao                     ← volta ao padrão
sgs api config 16 todos=sim                           ← sem endpoint: vale para TODOS os endpoints do sistema
```

**O site no ar acompanha.** Se o site do sistema está no ar pela tela, o SGS o reinicia sozinho na mesma porta
depois de um `sgs api config` ou de uma edição sem versão (`app`, `ligar`, `incrementar` com `-sv`), já com as
migrations, porque o servidor não recarrega sozinho. Depois é só dar F5 no navegador. Se o site estiver no ar por
fora da tela, o SGS só avisa.

A escolha vai para o `config/settings.py` do sistema (`VIAGCERTS_API_CAMPOS = {…}`, só o que mudou do padrão).
Campo que entrar depois, por `incrementar` ou `ligar`, segue o padrão do endpoint.

Quem chama a API ainda pode pedir só alguns campos, entre os expostos: `/api/v1/?campos=viajante,valor_final`. Um
campo oculto não aparece nem pedindo, e `/api/v1/campos/` lista os disponíveis e os expostos de cada endpoint.

Os testes da app conferem sempre o padrão, por isso a sua escolha não os quebra. Uma app gerada antes deste
recurso é refeita na primeira mudança, com as mesmas regras e as ligações de volta.

### Módulos (`sgs app`) e versões (`sgs editar`)

**Editar um sistema gera uma cópia**: `sgs editar 01` cria a versão **01.1** (depois 01.2 … até 01.99) na pasta
`<pasta do 01>_v1`, com o banco e o `web/.env` (a `PORTA` já ajustada) e sem `.venv`, caches e log. O original não
muda. Editar uma versão cria a próxima do mesmo sistema (editar a 01.1 gera a 01.2). As versões ficam em
`sistemas_gerados/.sgs_registro.json` (`versoes`) e nunca ganham número de sistema novo.

`sgs app 01 <pedido>` acrescenta ao 01 **mais uma app Django** — a funcionalidade nova. O módulo é gerado pelo
mesmo gerador, com o estilo, o tema e as opções do sistema; o pedido escolhe o domínio, os campos e os padrões, como
no `sgs gerar`.

Com a caixa **Perguntar antes de gerar**, o SGS pergunta antes de mexer em qualquer arquivo:

1. **que funcionalidade é** — o nome da classe nova, que depende do contexto. O padrão vem do pedido: “destinos de
   viagem” → `Destino`, “cadastro de horários de voos” → `Horario`. Você pode trocar por `Voo`, por exemplo;
2. **versão ou edição** — versão nova 01.k (cópia) ou editar o próprio 01, **sem versionar**;
3. **ligação** — ligar a classe nova a uma que já existe, nos dois sentidos: `Viagcert.destino → Destino` (a classe
   que existe ganha a referência) ou `Destino.viagcert → Viagcert` (a nova aponta para ela);
4. o **nome do campo** de referência, os **campos a mais** (com os tipos duvidosos), os **padrões** (o Strategy entra
   sempre), a máquina de estados e o domínio base.

`sgs app -sp` encerra as perguntas e aplica. Sem perguntas, tudo vai no comando:
`sgs app 16 -sp destinos de viagem ligar=Viagcert.destino padroes=state -sv`. `ligar=Classe.campo` aponta para a classe
nova; `ligar=Classe.campo:Alvo` serve para qualquer par. Tudo é planejado e conferido **antes** de escrever: nome
repetido ou ligação errada não muda nada.

**Passo a passo — o `ligar` liga duas classes que JÁ existem.** No sistema 16, que só tem a `Viagcert`:

```
sgs app 16 destinos de viagem ligar=Viagcert.destino -sv   ← cria a Destino e já liga (Viagcert.destino → Destino)
sgs app 16 horarios de voos entidade=Voo -sv               ← cria a Voo
sgs ligar 16 Voo.destino Destino -sv                       ← liga duas classes que já existem
sgs incrementar 16 Viagcert.noites inteiro:1..15 -sv        ← muda o padrão de um campo que existe
sgs incrementar 16 Viagcert.assento lista:janela,meio,corredor -sv   ← cria um campo novo com o padrão
```

`sgs ligar NN` e `sgs incrementar NN` sozinhos mostram as classes e os campos, com este passo a passo. Se o Alvo
ainda não existe, o `ligar` diz o comando que cria e liga. Sem o padrão, `sgs incrementar NN Classe.campo` mostra
como o campo está hoje e comandos prontos para ele.

**Ligação** (`sgs ligar NN Classe.campo Alvo [-sv]`, ou `ligar=` no `sgs app`) é um `ForeignKey` **opcional**
(`null`/`blank`, `SET_NULL`: apagar o alvo só limpa o campo). Ela entra:

- no `models.py`, antes do `tipo`, e no `Meta.fields` do form, onde vira uma lista de escolha;
- na API REST (o id do alvo) e no detalhe (vazio aparece como “—”);
- num teste próprio (`tests/test_ligacao_<campo>.py`), em `ligacoes.json` e no README.

Se o site já subiu (o sistema tem migrations), o SGS roda o `makemigrations` na hora, para o banco e os testes
acompanharem. Depois é só `sgs parar NN` e `sgs rodar NN`, que aplicam o `migrate`.

**Incrementar/modificar um campo** (`sgs incrementar NN Classe.campo <padrão> [-sv]`): define o padrão (a regra)
de UM campo de uma classe — a principal ou a de um módulo. Se o campo já existe, a regra dele **muda**; se o nome
é novo, a classe **ganha** o campo.

| Padrão | O que o campo aceita |
|---|---|
| `inteiro>=0` | inteiro com mínimo — negativo e letras são recusados |
| `inteiro:1..30` · `decimal>=0` · `decimal:0..100` | inteiro numa faixa; decimal com mínimo ou numa faixa |
| `lista:janela,meio,corredor` (ou `lista:1,2,3`) | **lista fechada**: só esses valores (no Django vira `choices` e uma lista de escolha) |
| `texto` · `texto-livre` · `simnao` · `data` | texto obrigatório; texto opcional; sim/não; data AAAA-MM-DD |

A classe é **refeita pelo gerador** a partir da especificação atualizada (`especificacao.json` da principal, ou
`modulos.json` do módulo). Por isso:

- o padrão vale no **@property** do núcleo (o setter recusa o que não segue o padrão), no model (validators ou
  choices), no form e na API;
- os testes da classe são refeitos junto, e as ligações dela voltam no lugar;
- refazer com a mesma regra gera exatamente os mesmos arquivos (há teste que garante);
- o README, o `iniciar.sh` e o `config/` do sistema não são tocados;
- campo novo num banco que já tem linhas ganha um valor padrão (o primeiro da lista, o mínimo…), e a migration é
  criada na hora.

O SGS recusa, sem escrever nada, o que quebraria a classe — por exemplo, a quantidade passar a ser decimal — e
ligações, que mudam com `sgs ligar`. `sgs incrementar NN` sozinho lista os campos com o padrão de cada um. Com
“Perguntar”, ele pergunta a classe, o campo (um que existe ou um novo), o padrão, o valor dele (mínimo, faixa, os
valores da lista) e versão ou edição; `sgs incrementar -sp` aplica. Anotado em `incrementos.json`.

Cada módulo tem:

- **form** (ModelForm), **CRUD** completo (`/<app>/`, `novo/`, `<id>/`, `editar/`, `excluir/`) e **API REST** (`/<app>/api/v1/`);
- `settings.py`, `models.py`, `views.py`, `services.py`, `viewmodels.py`, `urls.py`, templates e estáticos;
- os **padrões** do pedido, com o núcleo **dentro da app** (`<app>/nucleo/`) e os testes dele em `<app>/tests/nucleo/`;
- `README.md` próprio.

O módulo entra no `INSTALLED_APPS`, ganha a rota `/<app>/` (antes da raiz), entra no `makemigrations` do
`iniciar.sh` e fica anotado em `modulos.json` e numa seção do README. Se o nome da app já existir (ou for
reservado), nada é copiado e a tela pede `entidade=Nome`. Pelo Python:
`gerar_sistema.gerar_modulo(pasta, "pedido", entidade="Nome")` e `gerar_sistema.ligar_classes(pasta, "Viagcert",
"destino", "Destino")` fazem o mesmo direto na pasta.

### Portas: 6100, versões e porta presa

O SGS é o 00 na **6100**, o sistema NN roda na **6100 + NN**, e a versão usa a porta do sistema **seguida do último
dígito da versão**: 01.1 → 61011, 01.3 → 61013. Com a 6100 tudo cabe nas 65.535 portas, e por isso a 01.9, a 01.19 …
a 01.99 dividem a 61019. Um `sgs_config.json` salvo com a base antiga (8100) passa sozinho para a 6100.

- **Porta ocupada** (outra versão no ar, ou um site esquecido): o `sgs rodar` e o `python manage.py runserver` da
  tela dizem quem está na porta e perguntam **“forçar? s/N”**. Com `s`, a tela encerra o dono da porta e sobe o
  atual; com `n` (ou Enter), nada muda. A tela nunca encerra a si mesma.
- **Já no ar**: rodar de novo o mesmo sistema só reabre a janela.
- **Portas liberadas**: o `sgs parar` encerra o grupo de processos do site. Fechar o terminal (SIGHUP) ou um
  `kill` (SIGTERM) derruba os sites como o Ctrl+C. Se a tela cair sem limpar, a próxima tela encerra os órfãos
  anotados em `sistemas_gerados/.sgs_servidores.json`. As conexões em TIME_WAIT (os ~60 s depois de derrubar um
  site) não contam mais como porta ocupada.

### Pronto para subir

Cada sistema com Django traz `iniciar.sh` (venv → dependências → `.env` → migrations → admin → servidor,
abrindo em PWA), `web/.env.example`, comando `garantir_admin`, manifest/service worker/ícones e testes de tudo isso.

---

## 3. Linha de comando (sem a tela)

```bash
python Gerador_Sistemas/gerar_sistema.py --listar
```

```bash
python Gerador_Sistemas/gerar_sistema.py --assunto "biblioteca onde a multa varia conforme o tipo de leitor" --django --estilo web --tema T07 --tom claro --notas-web --testar
```

```bash
python Gerador_Sistemas/gerar_sistema.py --dominio loja --padrao criacao --django --estilo bootstrap --uuid --lnnl 35 --apps --seguranca-baseline --testar
```

```bash
python Gerador_Sistemas/gerar_sistema.py --dominio hotel --padrao prova --campos andar tem_varanda checkin:data nota:float --django --exercicio --testar
```

| Opção | O que faz |
|---|---|
| `--dominio`, `--assunto`, `--padrao`, `--sistema`, `--entidade`, `--spec` | o que gerar (padrões e grupos: seção 4) |
| `--campos nome:tipo …` | campos a mais na entidade; sem `:tipo`, o identificador de tipos deduz pelo nome |
| `--django` · `--exercicio` · `--direto` · `--sem-comentarios` · `--testar` | camada web · questionário com “Ver resposta” · só gerar · apenas o código · rodar testes |
| `--estilo` · `--tema` · `--tom` · `--paleta` · `--notas-web` | formatação das páginas (seção 2) |
| `--uuid` · `--lnnl [TIPO]` · `--apps` · `--seguranca-baseline` | opções das Instruções Django e do motor de ID |
| `--saida`, `--nome`, `--forcar` | onde criar, nome da pasta, substituir (nunca apaga pasta que ele não criou) |

---

## 4. Os 101 domínios, por setor

A lista vem do usuário ([`catalogo_100_dominios.txt`](catalogo_100_dominios.txt), lida sem alteração): ID,
domínio, sistema, entidade e 30 palavras que ativam cada um (e o **101**, `citricultura`, de `ProvaPraticaP3/domínio 101.txt`, com 101 palavras e perfil próprio da Prova Prática P3). O resto (atributos com validação, variantes do
Strategy, categorias, extras do Decorator, gateway do Adapter, painel, nomes de exemplo) está escrito à mão em
[`dominios.py`](dominios.py), coerente com o setor. Os 8 domínios originais continuam iguais (só ganharam as
palavras novas) e foram renumerados: hotel 001, cinema 002, clinica 011, academia 012, loja 023, biblioteca 045,
estacionamento 055, generico 100.

| IDs | Setor |
|---|---|
| 001–010 | Hospedagem, Turismo e Lazer |
| 011–022 | Saúde e Bem-Estar |
| 023–034 | Comércio e Varejo |
| 035–044 | Alimentação e Gastronomia |
| 045–054 | Educação e Cultura |
| 055–064 | Mobilidade, Veículos e Logística |
| 065–072 | Imóveis, Condomínios e Serviços Urbanos |
| 073–080 | Serviços Pessoais, Pets e Estética |
| 081–090 | Finanças, Jurídico e Corporativo |
| 091–100 | Indústria, Agro, Mídia e Genérico |
| 101 | Prova Prática P3 (ISW-030) — `citricultura` (`sgs provap3`: pasta `provaP3`, projeto `cooperativa`, app `citricultura`, DRF em `/api/`) |

Ver ou procurar: `sgs dominios [termo]` na tela, `--listar [termo]` na linha de comando. Nomes com “&” (Casa & Obra)
saem escapados nas páginas; o nome da pasta continua só com `[a-z0-9_]`.

---

## 5. Os 28 padrões, por categoria

Os 23 do GoF seguem a lista da Wikipédia (cópia em `referencias/`): 5 de criação, 7 estruturais e 11
comportamentais. Os outros 5 são os fundamentos das aulas.

| Categoria | Padrões (chave para `--padrao`) |
|---|---|
| **Fundamentos** (aulas) | `encapsulamento` · `polimorfismo` · `srp` · `service` · `mvvm` |
| **GoF · Criação** | `singleton` · `factory_method` · `abstract_factory` · `builder` · `prototype` |
| **GoF · Estruturais** | `adapter` · `bridge` · `composite` · `decorator` · `facade` · `flyweight` · `proxy` |
| **GoF · Comportamentais** | `chain` · `command` · `interpreter` · `iterator` · `mediator` · `memento` · `observer` · `state` · `strategy` · `template_method` · `visitor` |

Grupos: `todos` (28) · `gof` (23) · `prova` (os 9 da P3 — o padrão quando o pedido não cita padrão) ·
`criacao` · `estrutural` · `comportamental` · `fundamentos`. Cada padrão gera o módulo aplicado, o
`antes_*.py` (o smell, no modo estudo) e os testes (antes × depois, extensão e regras do padrão).

---

## 6. Como o gerador decide (determinístico, sem IA)

1. Texto normalizado (minúsculas, sem acento; palavras com “_” do catálogo viram frase: `cafe_manha` → “cafe manha”).
2. Domínio por **pontos**: cada palavra do domínio que aparece vale 1, e o nome do domínio no texto vale +3.
   Empate: vence quem bateu palavras mais longas (mais específicas); depois, o ID menor. O `generico` não pontua
   (as palavras dele estão em quase todo pedido): só entra quando nenhum outro bate, com o nome tirado de "sistema de …".
3. Padrões: cada um tem sua lista de palavras (`sgs padroes`); frases de grupo trazem o grupo inteiro.
4. Encapsulamento entra sempre; modelos fixos recebem os nomes do domínio; todo `.py` passa por `ast.parse`.

> Limite honesto: a decisão é por **palavras**, não por compreensão. Para controlar tudo, use as perguntas,
> `sgs gerar <domínio> <padrões>` ou um `--spec`.

---

## 7. Exemplos e testes

Exemplos em `sistemas_gerados/` (gerados antes desta rodada; continuam passando).

Para os testes do gerador e do SGS, rode `cd Gerador_Sistemas && python -m pytest -v`. Eles cobrem:
- os 101 domínios × 28 padrões (núcleo), um domínio novo por setor com Django, o perfil da Prova Prática P3 (`citricultura` / `sgs provap3` + DRF em `/api/` + trava contra sobrescrever) e, com `SGS_TESTE_COMPLETO=1`, todos com Django;
- a pontuação do domínio, o desempate e o filtro `sgs dominios <termo>`;
- os 4 estilos;
- os temas, com contraste;
- UUID, LNNL, `apps/` e baseline;
- os campos a mais de cada tipo (texto, inteiro, decimal, sim/não, data) e o identificador de tipos;
- o modo exercício (questionário, código completo);
- a API REST (CRUD, 400/404/405, os settings da app e o CSRF) e os módulos (`sgs app`, nas estruturas plana e `apps/`);
- as versões (`sgs editar`), as portas 6100/61011… e a pergunta de forçar a porta ocupada;
- o determinismo, inclusive dos binários;
- as perguntas e o `-sp`;
- o terminal, o histórico em arquivo (`history`, `history -c`) e o `sgs comand`;
- subir e derrubar um site de verdade, liberar porta em TIME_WAIT e encerrar os sites órfãos.

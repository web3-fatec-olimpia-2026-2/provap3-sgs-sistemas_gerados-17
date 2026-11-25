"""
SGS · COMAND — o "help" numerado dos comandos da esteira de desenvolvimento.

Na tela:  sgs comand      → lista numerada (01, 02, …), por etapa da esteira
          sgs comand n    → explica o comando n: o que faz, como usar, exemplo, saída típica e dica
          sgs exit        → volta para a tela principal
Dentro do módulo, digitar só o número (ex.: 12) também abre o comando 12.

Os comandos de terminal daqui FUNCIONAM na tela (com ou sem "sgs" na frente) — alguns de verdade,
outros simulados (o retorno de cada um está descrito no campo "na tela").
"""

# (comando, etapa, o que faz, uso, exemplo, saída típica, dica, na tela)
CATALOGO = [
    # ---------------------------------------------------------------- 1. navegar
    ("pwd", "1 · Navegar", "Mostra em que pasta você está.", "pwd", "pwd",
     "/home/oscar/projetos/django/Tecnicas de Programacao II",
     "Na tela, ~ é a raiz do projeto (o .venv mora em Gerador_Sistemas/.venv; na raiz há um atalho para ele).",
     "de verdade"),
    ("ls", "1 · Navegar", "Lista os arquivos e pastas (pastas terminam com /).", "ls [-a] [-l] [pasta]",
     "ls -l Gerador_Sistemas", "README.md  gerar_sistema.py  sistemas_gerados/  tela_prompt.py",
     "-a mostra os ocultos (.env, .venv); -l mostra tamanho e tipo.", "de verdade"),
    ("cd <pasta>", "1 · Navegar", "Entra numa pasta.", "cd <pasta>", "cd Gerador_Sistemas/sistemas_gerados",
     "(nada — o prompt passa a mostrar a pasta nova)", "Tab não completa aqui; use ls para ver os nomes.",
     "de verdade (só dentro do projeto)"),
    ("cd ..", "1 · Navegar", "Volta uma pasta (para a pasta \"mãe\").", "cd ..", "cd ..", "(nada — o prompt muda)",
     "cd - volta para a pasta anterior.", "de verdade"),
    ("cd ~", "1 · Navegar", "Volta para a raiz do projeto.", "cd ~   ou só   cd", "cd", "(nada — o prompt mostra ~)",
     "Na tela, ~ é a raiz do projeto, não a sua home do Linux.", "de verdade"),
    ("cd NN", "1 · Navegar", "Atalho da tela: entra na pasta do sistema número NN.", "cd NN", "cd 01",
     "(o prompt passa a mostrar ~/Gerador_Sistemas/sistemas_gerados/<pasta do 01>)",
     "Funciona porque não existe pasta chamada 01; no WSL de verdade use o caminho.", "atalho da tela"),
    ("tree", "1 · Navegar", "Desenha a árvore de pastas.", "tree [-L n] [pasta]", "tree -L 2",
     "├── nucleo/\n│   ├── entidades.py\n└── tests/", "Ignora .venv, __pycache__ e caches.", "de verdade"),
    ("cat <arquivo>", "1 · Navegar", "Mostra o conteúdo de um arquivo.", "cat <arquivo>", "cat requirements.txt",
     "Django>=6.0,<7.0\npytest>=8.0\npytest-django>=4.9",
     "Segredos do .env (SECRET_KEY, senha) aparecem mascarados na tela.", "de verdade"),
    ("head / tail", "1 · Navegar", "Mostra o começo (head) ou o fim (tail) de um arquivo.", "head -n 20 <arquivo>",
     "tail -n 5 web/servidor.log", "(as últimas 5 linhas do log)", "Bom para ler logs.", "de verdade"),
    ("clear", "1 · Navegar", "Limpa a tela (ficam só as duas linhas do topo).", "clear   ou   sgs clear", "clear",
     "(tela limpa)", "Atalho: Ctrl+L.", "de verdade"),
    ("history", "1 · Navegar",
     "Histórico de comandos, numerado como no bash. Fica no ARQUIVO .sgs_historico: sobrevive ao F5 e ao reiniciar.",
     "history [N]   ou   sgs history [N]", "history 20", "   41  sgs listar\n   42  cd 01",
     "↑/↓ no prompt percorrem o mesmo histórico. Senhas digitadas entram mascaradas.", "de verdade"),
    ("history -c", "1 · Navegar", "Limpa o histórico (como no bash); history -d N apaga só a linha N.",
     "history -c   ou   sgs history -c", "history -c", "(histórico vazio)",
     "Todo comando padrão funciona também com sgs na frente.", "de verdade"),
    # ---------------------------------------------------------------- 2. ambiente python
    ("source .venv/bin/activate", "2 · Ambiente Python",
     "Ativa o ambiente virtual: python e pip passam a ser os do .venv (com Django e pytest).",
     "source <pasta>/.venv/bin/activate", "source .venv/bin/activate", "(o prompt ganha \"(.venv)\" na frente)",
     "O .venv do projeto fica na raiz (~). Ative ANTES de rodar python/pip.", "simulado (marca o prompt)"),
    ("deactivate", "2 · Ambiente Python", "Desativa o ambiente virtual.", "deactivate", "deactivate",
     "(o \"(.venv)\" some do prompt)", "Só existe depois de um source …/activate.", "simulado"),
    ("python --version", "2 · Ambiente Python", "Mostra a versão do Python em uso.", "python --version",
     "python --version", "Python 3.14.4", "Com o .venv ativo, é o Python do .venv.", "de verdade"),
    ("which python", "2 · Ambiente Python", "Mostra QUAL python vai rodar (o caminho).", "which python",
     "which python", "/home/oscar/projetos/django/Tecnicas de Programacao II/.venv/bin/python",
     "Se mostrar /usr/bin/python3, o .venv não está ativo.", "simulado"),
    ("pip install -r requirements.txt", "2 · Ambiente Python",
     "Instala TODAS as dependências listadas no requirements.txt.", "pip install -r requirements.txt",
     "pip install -r requirements.txt", "Requirement already satisfied: Django>=6.0,<7.0 (6.1.3)",
     "Na tela só confere o que já está instalado (instalar baixa da internet: rode no WSL).",
     "simulado (confere de verdade)"),
    ("pip list", "2 · Ambiente Python", "Lista os pacotes instalados no ambiente.", "pip list", "pip list",
     "Django        6.1.3\npytest        9.2.0\npytest-django 4.14.0", "pip freeze mostra no formato do requirements.",
     "de verdade"),
    # ---------------------------------------------------------------- 3. configurar
    ("cp -n web/.env.example web/.env", "3 · Configurar",
     "Cria o .env a partir do modelo, sem sobrescrever um que já exista (-n).", "cp -n <modelo> <destino>",
     "cp -n web/.env.example web/.env", "(nada se deu certo)",
     "bash iniciar.sh env faz o mesmo e ainda gera uma SECRET_KEY nova.", "de verdade (só .env.example → .env)"),
    ("python manage.py check", "3 · Configurar", "Confere se o projeto Django está bem configurado.",
     "python manage.py check", "python manage.py check", "System check identified no issues (0 silenced).",
     "Rode dentro de web/ (na tela, se você estiver na pasta do sistema, ela acha o web/manage.py sozinha).",
     "de verdade"),
    # ---------------------------------------------------------------- 4. banco
    ("python manage.py makemigrations", "4 · Banco (migrations)",
     "Lê os models e cria os arquivos de migration (o \"plano\" das tabelas).",
     "python manage.py makemigrations [app]", "python manage.py makemigrations reservas",
     "Migrations for 'reservas':\n  reservas/migrations/0001_initial.py\n    + Create model Reserva",
     "Mudou um model? makemigrations de novo, depois migrate.", "de verdade"),
    ("python manage.py migrate", "4 · Banco (migrations)", "Aplica as migrations no banco (cria/altera tabelas).",
     "python manage.py migrate", "python manage.py migrate", "Applying reservas.0001_initial... OK",
     "O banco é o web/db.sqlite3.", "de verdade"),
    ("python manage.py showmigrations", "4 · Banco (migrations)", "Mostra quais migrations já foram aplicadas [X].",
     "python manage.py showmigrations", "python manage.py showmigrations", "reservas\n [X] 0001_initial", "",
     "de verdade"),
    # ---------------------------------------------------------------- 5. admin
    ("python manage.py garantir_admin", "5 · Admin",
     "Cria (ou atualiza) o superusuário com usuário, e-mail e senha do web/.env.", "python manage.py garantir_admin",
     "python manage.py garantir_admin", "superusuário criado: admin",
     "Pode rodar várias vezes. Os dados vêm do sgs config (admin_usuario, admin_email, admin_senha).", "de verdade"),
    ("python manage.py createsuperuser", "5 · Admin", "Versão INTERATIVA do Django: pergunta usuário e senha.",
     "python manage.py createsuperuser", "python manage.py createsuperuser", "Username: …  Password: …",
     "A tela não responde perguntas: use garantir_admin (ou rode este no WSL).", "não roda na tela (interativo)"),
    # ---------------------------------------------------------------- 6. rodar
    ("python manage.py runserver", "6 · Rodar", "Sobe o servidor de desenvolvimento do Django.",
     "python manage.py runserver [porta]", "python manage.py runserver",
     "Starting development server at http://127.0.0.1:6101/\nQuit the server with CONTROL-C.",
     "Na tela roda em segundo plano, na porta 6100 + NN do sistema (versão 01.3 → 61013), e abre em PWA "
     "(sgs pwa=false: aba). Porta ocupada por outro site (ex.: a 01.9 na porta da 01.19) → a tela pergunta "
     "se encerra o anterior (s/N).", "de verdade (em segundo plano)"),
    ("bash iniciar.sh", "6 · Rodar", "Tudo de uma vez: venv → dependências → .env → migrations → admin → servidor.",
     "bash iniciar.sh [tudo [porta]]", "bash iniciar.sh",
     "==> migrations … ==> superusuário … ==> site em http://127.0.0.1:8000/",
     "Rode na pasta do sistema (onde está o iniciar.sh).", "de verdade"),
    ("bash iniciar.sh <passo>", "6 · Rodar", "Um passo só: venv, deps, env, migrar, admin, testar ou rodar.",
     "bash iniciar.sh <passo>", "bash iniciar.sh migrar", "==> migrations\nNo changes detected …",
     "Cada passo pode ser repetido sem estragar nada.", "de verdade"),
    ("sgs rodar NN", "6 · Rodar", "Prepara (.env, migrations, admin) e sobe o site do sistema NN na porta 6100 + NN.",
     "sgs rodar NN [porta]", "sgs rodar 01", "✓ no ar: o sistema 01 — http://127.0.0.1:6101/",
     "O SGS (esta tela) é o 00, na porta 6100. Versão: sgs rodar 01.3 → porta 61013. Já no ar → só reabre.",
     "comando sgs"),
    ("sgs parar NN", "6 · Rodar", "Derruba o site do sistema NN (ou pela porta, ou todos) e libera a porta.",
     "sgs parar NN | porta | todos", "sgs parar 01", "site do sistema 01 derrubado — porta liberada",
     "Se a tela cair sem derrubar os sites, a próxima tela libera as portas ao abrir.", "comando sgs"),
    ("sgs servidores", "6 · Rodar", "Mostra os sites que a tela subiu e estão no ar.", "sgs servidores",
     "sgs servidores", "01  hotel_resort__prova_web  http://127.0.0.1:6101/", "", "comando sgs"),
    # ---------------------------------------------------------------- 7. testar
    ("python -m pytest -q", "7 · Testar", "Roda os testes da pasta atual.", "python -m pytest [-q] [-v]",
     "python -m pytest -q", "125 passed in 1.2s", "Dentro de web/ roda os testes do Django.", "de verdade"),
    ("explorer.exe exercicios.html", "7 · Testar",
     "No modo exercício, abre o questionário de revisão (resposta oculta em “Ver resposta”) no navegador.",
     "explorer.exe exercicios.html", "explorer.exe exercicios.html", "(abre no navegador padrão do Windows)",
     "Com o site no ar, o mesmo questionário está em /exercicios/. O código do sistema sai completo.", "de verdade"),
    ("bash rodar_testes.sh", "7 · Testar", "Roda os testes de TODAS as pastas do projeto.",
     "bash rodar_testes.sh [filtro]", "bash rodar_testes.sh Aula05", "Pastas testadas: 3 · com falha: 0",
     "Rode na raiz (~).", "de verdade"),
    ("sgs testar NN", "7 · Testar", "Roda os testes do sistema NN (núcleo e web).", "sgs testar NN", "sgs testar 01",
     "✓ núcleo (Python puro)  125 passed", "", "comando sgs"),
    ("git status", "7 · Testar", "Mostra o que mudou no repositório git.", "git status", "git status",
     "fatal: not a git repository (or any of the parent directories): .git",
     "Este projeto ainda não é um repositório git (git init cria).", "de verdade (só leitura)"),
    # ---------------------------------------------------------------- 8. sgs
    ("sgs", "8 · SGS", "Ajuda: comandos, opções da caixa e configuração.", "sgs", "sgs", "(a ajuda)", "", "comando sgs"),
    ("sgs gerar <pedido>", "8 · SGS",
     "GERA um sistema a partir do pedido em linguagem natural (texto sem sgs gerar só é anotado).",
     "sgs gerar <pedido>", "sgs gerar biblioteca onde a multa varia conforme o tipo de leitor",
     "✔ Biblioteca Municipal · 01 · porta 6101", "As caixas (+ Django, exercício…) valem para a geração.",
     "comando sgs"),
    ("sgs gerar -sp", "8 · SGS",
     "Com “Perguntar antes de gerar” ligado, sgs gerar faz rodadas de 10 perguntas; -sp (sem perguntar) gera "
     "direto — e, digitado no meio das perguntas, encerra e gera com o que já foi decidido.",
     "sgs gerar -sp [pedido]", "sgs gerar -sp loja com extras opcionais",
     "✓ perguntas encerradas (7 resposta(s)) — gerando com as decisões tomadas",
     "Nas perguntas: número da opção, sim/não, texto, ou Enter = padrão. sgs cancelar desiste.", "comando sgs"),
    ("sgs tipos <campos>", "8 · SGS",
     "Identificador de tipos: mostra o tipo que cada campo recebe pelo nome e quais viram pergunta.",
     "sgs tipos <campo, campo…>", "sgs tipos nome, idade, peso, vacinado, status",
     "nome texto (String) · idade inteiro (INT) · peso decimal (FLOAT) · vacinado sim/não (BOOL) · status DÚVIDA",
     "No pedido: “… com os campos nome, idade:int”. O tipo junto (idade:int) vence a dedução.", "comando sgs"),
    ("sgs cancelar", "8 · SGS", "Desiste das perguntas em andamento (nada é gerado).", "sgs cancelar", "sgs cancelar",
     "perguntas canceladas — nada foi gerado", "", "comando sgs"),
    ("sgs estilo", "8 · SGS", "Formatação das páginas web geradas: simples, cmd (tela preta), bootstrap ou web "
     "(Bootstrap + temas).", "sgs estilo [simples|cmd|bootstrap|web]", "sgs estilo web", "✓ estilo: web",
     "O Bootstrap vem dentro do projeto (recursos/bootstrap-5.3.3), sem CDN.", "comando sgs"),
    ("sgs tema", "8 · SGS", "Tema do estilo web: 10 temas × 6 tons (pasta temas/) e a paleta do T10.",
     "sgs tema [T01…T10] [tom] [P01…P20]", "sgs tema T04 escuro",
     "tema atual: T04 Animado · Escuro", "Contraste WCAG conferido em todas as combinações.", "comando sgs"),
    ("sgs gerar <domínio> <padrões…>", "8 · SGS", "Gera escolhendo direto, sem análise de palavras.",
     "sgs gerar <domínio> <padrões ou grupos>", "sgs gerar hotel criacao observer", "✔ Hotel Resort · 02",
     "Grupos: todos, gof, prova, criacao, estrutural, comportamental.", "comando sgs"),
    ("sgs listar", "8 · SGS", "Lista os sistemas pelo NÚMERO fixo (dado na geração), com a porta de cada um.",
     "sgs listar [recentes]", "sgs listar",
     "00  SGS (esta tela)  porta 6100\n01  biblioteca_municipal__strategy  6101\n01.1  biblioteca_municipal__strategy_v1  61011",
     "O número não muda quando aparece outro sistema — por isso a porta também não. 01.1, 01.2… são versões.",
     "comando sgs"),
    ("sgs editar NN", "8 · SGS",
     "PAINEL GUIADO DE EDIÇÃO do próprio sistema NN: mostra classes/campos atuais e conduz para Incrementar Campos, "
     "Ligar Classes, Nova Funcionalidade (app) e API — nunca cria cópia.",
     "sgs editar NN [incrementar | ligar | app <pedido> | api]", "sgs editar 01",
     "Editar o sistema 01 — ações clicáveis no próprio 01",
     "Para criar uma cópia antes de experimentar mudanças, use sgs duplicar NN.", "comando sgs"),
    ("sgs duplicar NN", "8 · SGS",
     "DUPLICAR = COPIAR: cria uma cópia versionada NN.k do sistema (01.1 … 01.99); o original NN não muda. "
     "É o único comando que gera cópia.",
     "sgs duplicar NN", "sgs duplicar 01", "✓ cópia (versão 01.1) criada a partir do 01 — porta 61011",
     "A porta da cópia é a do sistema + o último dígito da versão (01.9, 01.19 … 01.99 → 61019).", "comando sgs"),
    ("sgs app NN <pedido>", "8 · SGS",
     "FUNCIONALIDADE NOVA diretamente no sistema NN: acrescenta mais uma app Django — form, CRUD, API REST, padrões, "
     "settings, models, views e testes. Com “Perguntar”, conduz nome, ligação, campos e padrões.",
     "sgs app NN <pedido> [entidade=Nome] [padroes=a,b] [ligar=Classe.campo] [-sp]",
     "sgs app 16 destinos de viagem com os campos cidade e pais",
     "✓ o módulo destinos (Destino): aplicado no sistema 16 · Viagcert.destino → Destino",
     "Altera diretamente o NN (para cópia antes, use sgs duplicar NN). sgs app -sp encerra as perguntas e aplica.",
     "comando sgs"),
    ("sgs ligar NN Classe.campo Alvo", "8 · SGS",
     "LIGAR CLASSES diretamente no sistema NN: cria campo de REFERÊNCIA (ForeignKey opcional) de uma classe para outra "
     "(entra no models, form como lista de escolha, API e teste). Sozinho conduz passo a passo.",
     "sgs ligar NN [Classe.campo Alvo] [-sp]",
     "sgs ligar 16 Viagcert.destino Destino", "✓ a ligação Viagcert.destino → Destino: aplicado no sistema 16",
     "Com “Perguntar” ligado e ≥ 2 classes, sgs ligar NN pergunta origem, alvo e nome do campo. Apagar o Alvo só limpa "
     "o campo (SET_NULL).", "comando sgs"),
    ("sgs api config NN", "8 · SGS",
     "CAMPOS DA API: que campos cada endpoint expõe — o v1 (REST, /api/v1/) e o resumo (/api/, o link “API” do "
     "site) de cada app; nos módulos, /destinos/api/v1/…", "sgs api config NN [<endpoint> campo=sim|nao … | todos=nao | "
     "padrao]", "sgs api config 16 /api/v1/ observacao=nao titulo=sim",
     "✓ /api/v1/: expostos agora — id, viajante, voo, noites, valor_noite, tipo, total, valor_final, titulo",
     "Grava em config/settings.py (<APP>_API_CAMPOS). Quem chama escolhe entre os expostos: /api/v1/?campos=id,total.",
     "comando sgs"),
    ("sgs incrementar NN Classe.campo <padrão>", "8 · SGS",
     "INCREMENTAR CAMPOS diretamente no sistema NN: cria um campo novo ou modifica a regra de um campo existente "
     "(inteiro>=0, inteiro:1..30, decimal>=0, lista:a,b,c, texto, texto-livre, simnao, data). A classe é refeita no "
     "@property do núcleo, no model/form/API do Django e nos testes.",
     "sgs incrementar NN [Classe.campo <padrão>] [-sp]",
     "sgs incrementar 16 Viagcert.voo inteiro>=1", "✓ o campo Viagcert.voo (modificado): aplicado no sistema 16",
     "sgs incrementar NN sozinho conduz passo a passo ou lista os campos e padrões. Para cópia antes: sgs duplicar NN.",
     "comando sgs"),
    ("sgs info NN", "8 · SGS", "Detalhes e arquivos do sistema NN.", "sgs info NN", "sgs info 01", "(o cartão do sistema)",
     "", "comando sgs"),
    ("sgs comandos NN", "8 · SGS", "Os comandos de terminal para rodar o sistema NN fora da tela.", "sgs comandos NN",
     "sgs comandos 01", "cd …\nbash iniciar.sh", "", "comando sgs"),
    ("sgs padroes", "8 · SGS", "Os 28 padrões por categoria e as palavras que os ativam.", "sgs padroes [categoria]",
     "sgs padroes criacao", "(tabela)", "sgs dominios mostra os domínios.", "comando sgs"),
    ("sgs dominios [termo]", "8 · SGS",
     "Os 101 domínios nativos (100 palavras cada nos 001–100; 101 na Prova P3) + domínios personalizados; com termo, "
     "filtra por nome, sistema, entidade, setor ou palavra.",
     "sgs dominios [termo]", "sgs dominios saude", "011 clinica · 013 hospital · 014 odontologia …",
     "Sem termo mostra só os setores. Para adicionar um domínio novo: sgs dominios novo.", "comando sgs"),
    ("sgs dominios novo", "8 · SGS",
     "Módulo para cadastrar um NOVO domínio personalizado (além dos 101 nativos), com dados básicos e palavras-chave. "
     "Salvo em dominios_extras.json (ID ≥ 102) e ativo na hora em sgs gerar e sgs dominios.",
     'sgs dominios novo [chave sistema="..." entidade=Classe palavras="a, b, c"]',
     'sgs dominios novo energia_eolica sistema="Eólica Sul" entidade=Turbina palavras="eolica, turbina, vento"',
     "✓ domínio 102 (energia_eolica · Eólica Sul · Turbina) cadastrado",
     "Sem argumentos, conduz passo a passo (termine com sgs dominios novo -sp). Para remover: sgs dominios remover <chave>.",
     "comando sgs"),
    ("sgs config", "8 · SGS", "Mostra ou altera a configuração (caixas, porta base, admin, PWA).",
     "sgs config [chave=valor …]", "sgs config admin_senha=minhaSenha1", "✓ alterado: admin_senha", "",
     "comando sgs"),
    ("sgs pwa=false", "8 · SGS",
     "Sites passam a abrir numa ABA do navegador. sgs pwa=true volta ao padrão: janela de app (PWA isolado).",
     "sgs pwa=true | sgs pwa=false | sgs pwa", "sgs pwa=false", "PWA desligado: os sites abrem numa aba comum",
     "O padrão é PWA: janela própria, sem abas nem barra de endereço.", "comando sgs"),
    ("sgs wiki", "8 · SGS", "Abre a cópia da Wikipédia com a lista dos padrões GoF (com o layout da Wikipédia).",
     "sgs wiki", "sgs wiki", "(abre a página)", "No topo: Tutorial | Wiki · padrões GoF | Django Study Hub.",
     "comando sgs"),
    ("sgs tutorial", "8 · SGS", "Tutorial prático: classe nova, ligar classes, campos, o padrão de um campo "
     "(tipo, @property, lista…), padrões de projeto e API.", "sgs tutorial", "sgs tutorial",
     "o resumo em 9 passos + a página /tutorial", "Abre ao lado da Wiki e do Django Study Hub.", "comando sgs"),
    ("sgs hub", "8 · SGS", "Abre a cópia do Django Study Hub (models, views, ORM, forms, DRF).", "sgs hub", "sgs hub",
     "(abre a página)", "", "comando sgs"),
    ("sgs provap3", "8 · SGS", "Prova Prática P3: gera o sistema do domínio 101 (citricultura) como no guia da prova "
     "(pasta provaP3, projeto Django cooperativa, app citricultura, rotas /citricultura/, DRF em /api/) e prepara o "
     "ambiente (.venv/dependências, web/.env, migrations, admin).", "sgs provap3", "sgs provap3",
     "sistema NN gerado e preparado em sistemas_gerados/provaP3",
     "Se a pasta provaP3 já existe, NÃO apaga: mostra o sistema e pergunta (s/N) antes de gerar do zero. "
     "O guia e o domínio estão em Gerador_Sistemas/ProvaPraticaP3/.", "comando sgs"),
    ("sgs cmd", "8 · SGS", "O estilo desta tela: sgs cmd = como o Prompt de Comando do Windows (preto e cinza, o "
     "padrão ao abrir) · sgs cmd sgs = as cores do SGS (prompt verde).", "sgs cmd [sgs]   ou   cmd [sgs]",
     "sgs cmd sgs", "a tela passa para as cores do SGS", "Sem o sgs na frente também vale: cmd · cmd sgs.",
     "comando sgs"),
    ("sgs topo", "8 · SGS", "Mostra/oculta os comandos principais no topo da tela (a tela abre com eles à mostra).",
     "sgs topo [sim|nao]", "sgs topo", "comandos do topo ocultos / à mostra", "", "comando sgs"),
    ("sgs foot", "8 · SGS", "Mostra/oculta as caixas de seleção embaixo do prompt (a tela abre com elas à mostra; "
     "a linha do comando sempre fica).", "sgs foot [sim|nao]", "sgs foot", "caixas de seleção ocultas / à mostra",
     "Alt+Enter maximiza a janela e, de novo, volta ao tamanho de antes.", "comando sgs"),
    ("sgs comand", "8 · SGS", "Este módulo: a lista numerada dos comandos.", "sgs comand [n]", "sgs comand 24",
     "(a explicação do comando 24)", "Dentro do módulo, digitar só o número também funciona.", "comando sgs"),
    ("sgs exit", "8 · SGS", "Sai do módulo comand e volta para a tela principal (como estava).", "sgs exit   ou   exit",
     "sgs exit", "(a tela principal volta)", "", "comando sgs"),
    ("history", "8 · SGS", "Os comandos digitados nesta sessão (↑/↓ também navegam).", "history", "history",
     "  1  sgs listar\n  2  cd 01", "", "da tela"),
]


# Só exemplos que apenas LEEM ganham o botão "executar" (nada que gere, mude configuração ou suba servidor).
SO_LEITURA = ("pwd", "ls", "cd", "tree", "cat ", "head ", "tail ", "python --version", "which ", "pip list",
              "python manage.py check", "python manage.py showmigrations", "git status", "history",
              "sgs listar", "sgs info", "sgs padroes", "sgs dominios", "sgs servidores", "sgs comand", "sgs wiki",
              "sgs cancelar", "sgs tipos", "sgs tutorial", "sgs hub")


def _comando_executavel(exemplo):
    """O exemplo vira um botão "executar" se não tem nada para preencher e só lê (history -c/-d apagam: não)."""
    return ("<" not in exemplo and " NN" not in exemplo and not exemplo.startswith(("history -c", "history -d"))
            and (exemplo == "sgs" or exemplo.startswith(SO_LEITURA)))


def listar():
    """Blocos da lista numerada, agrupada por etapa da esteira."""
    blocos = [{"t": "titulo", "texto": "SGS · COMAND — comandos da esteira de desenvolvimento"},
              {"t": "texto", "cor": "suave",
               "texto": "digite o número (ou sgs comand n) para ver a explicação · sgs exit volta para a tela principal"}]
    etapa_atual, linhas = None, []
    for n, (comando, etapa, oque, *_resto) in enumerate(CATALOGO, 1):
        if etapa != etapa_atual:
            if linhas:
                blocos.append({"t": "tabela", "colunas": ["nº", "comando", "o que faz"], "linhas": linhas})
            blocos.append({"t": "titulo", "texto": etapa})
            etapa_atual, linhas = etapa, []
        linhas.append([{"texto": f"{n:02d}", "cmd": f"sgs comand {n}"}, comando, oque])
    blocos.append({"t": "tabela", "colunas": ["nº", "comando", "o que faz"], "linhas": linhas})
    return blocos


def detalhe(n):
    """Blocos com a explicação do comando n (1-based). ValueError se n não existe."""
    if not 1 <= n <= len(CATALOGO):
        raise ValueError(f"não existe o comando {n} — use de 1 a {len(CATALOGO)} (sgs comand para a lista)")
    comando, etapa, oque, uso, exemplo, saida, dica, na_tela = CATALOGO[n - 1]
    blocos = [{"t": "titulo", "texto": f"{n:02d} · {comando}"},
              {"t": "texto", "texto": oque},
              {"t": "texto", "cor": "destaque", "texto": "uso:"}, {"t": "codigo", "texto": uso},
              {"t": "texto", "cor": "destaque", "texto": "exemplo:"}, {"t": "codigo", "texto": exemplo},
              {"t": "texto", "cor": "destaque", "texto": "retorno típico:"}, {"t": "saida", "texto": saida}]
    if dica:
        blocos.append({"t": "texto", "cor": "aviso", "texto": "dica: " + dica})
    blocos.append({"t": "texto", "cor": "suave", "texto": f"etapa: {etapa} · na tela: {na_tela}"})
    navegacao = []
    if _comando_executavel(exemplo):
        navegacao.append({"texto": f"executar: {exemplo}", "cmd": exemplo})
    if n > 1:
        navegacao.append({"texto": f"◀ {n - 1:02d}", "cmd": f"sgs comand {n - 1}"})
    if n < len(CATALOGO):
        navegacao.append({"texto": f"{n + 1:02d} ▶", "cmd": f"sgs comand {n + 1}"})
    navegacao += [{"texto": "lista", "cmd": "sgs comand"}, {"texto": "sgs exit", "cmd": "sgs exit"}]
    blocos.append({"t": "tabela", "colunas": [""] * len(navegacao), "linhas": [navegacao]})
    return blocos

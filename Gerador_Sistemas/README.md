# SGS - Sistema Gerador de Sistema (ILP-037 · P3)

Monta, **sem IA**, um sistema de exemplo completo para **qualquer assunto de prova**: código comentado,
testes, ADRs, README explicativo e, se você quiser, um site Django **pronto para subir** (Bootstrap e
temas, `.env`, migrations, superusuário, PWA). **A mesma entrada gera sempre a mesma saída, byte a byte**
(há teste que garante isso).

| Peça | Para quê |
|---|---|
| [`tela_prompt.py`](tela_prompt.py) | o **SGS**: tela estilo terminal no navegador (porta 8100) |
| [`gerar_sistema.py`](gerar_sistema.py) | o gerador (também roda sozinho, pela linha de comando) |
| [`sgs_terminal.py`](sgs_terminal.py) · [`sgs_comand.py`](sgs_comand.py) · [`sgs_perguntas.py`](sgs_perguntas.py) | terminal da tela · help numerado · perguntas antes de gerar |
| [`temas_web.py`](temas_web.py) | cores dos 10 temas × 6 tons (pasta `temas/`) e das 20 paletas, com contraste WCAG |
| [`dominios.py`](dominios.py) · [`catalogo_100_dominios.txt`](catalogo_100_dominios.txt) | os **100 domínios** em 10 setores: a lista do usuário (sistema, entidade, 30 palavras) + os dados de cada um |
| [`tipos_campos.py`](tipos_campos.py) | **identificador de tipos**: acha os campos do pedido e deduz o tipo pelo nome (texto, inteiro, decimal, sim/não, data) |
| `recursos/bootstrap-5.3.3/` | Bootstrap copiado para dentro do projeto (ver [`recursos/README.md`](recursos/README.md)) |
| `temas/` · `Instruçõs de desenvolvimento DJANGO/` · `motor-id-interno/` | referências usadas nas opções da camada web |
| `referencias/` | cópia da Wikipédia (lista GoF) com fonte, revisão, data da consulta (22/11/2026) e licença |
| `tests/` | testes do gerador e do SGS (`python -m pytest -v` nesta pasta) |
| `sistemas_gerados/` | onde os sistemas são criados (e o registro dos números fixos) |

---

## 1. Rodar o SGS

No WSL, na raiz do projeto:

```bash
source .venv/bin/activate
python Gerador_Sistemas/tela_prompt.py
```

Abre em **http://127.0.0.1:8100**, numa janela de app (PWA). Ctrl+C no terminal para parar;
`--sem-abrir` só sobe o servidor. A tela começa com duas linhas: o nome e os comandos principais.

| O que você digita | O que acontece |
|---|---|
| `sgs gerar <pedido>` | **gera** (ou começa as perguntas, se “Perguntar antes de gerar” estiver marcado) |
| `sgs gerar -sp <pedido>` | gera **sem perguntar**; sozinho, no meio das perguntas, encerra e gera |
| texto solto | só é **anotado** na tela (nada é gerado por engano) |
| `cd`, `ls`, `pwd`, `tree`, `cat`, `source .venv/bin/activate`, `python manage.py migrate/runserver…`, `pytest`, `bash iniciar.sh` | terminal (com ou sem `sgs` na frente) — `sgs comand` explica cada um |
| `sgs …` | configura, lista, roda e explica (digite só `sgs`) |

Principais comandos `sgs`:

| Comando | O que faz |
|---|---|
| `sgs listar` · `sgs info NN` · `sgs testar NN` | sistemas pelo **número fixo** (01, 02…, dado na geração) |
| `sgs rodar NN [porta]` · `sgs parar NN` · `sgs servidores` | sobe/derruba o site; o SGS é o 00 (porta 8100), o 01 roda na 8101… |
| `sgs comandos NN` | comandos de terminal para rodar o sistema fora da tela |
| `sgs comand [n]` · `sgs exit` | help numerado da esteira de desenvolvimento · volta à tela principal |
| `sgs estilo [simples\|cmd\|bootstrap\|web]` · `sgs tema [T01…T10] [tom] [P01…P20]` | formatação das páginas geradas |
| `sgs tipos <campos>` | mostra o tipo que cada campo recebe pelo nome e quais viram pergunta (ex.: `sgs tipos nome, idade, status`) |
| `sgs cancelar` | desiste das perguntas em andamento |
| `sgs dominios [termo]` | os 100 domínios por setor; com termo, só os que batem (`sgs dominios saude`, `sgs dominios pet`) |
| `sgs padroes` · `sgs config` · `sgs pwa=false` · `sgs wiki` · `clear` | catálogo, configuração, PWA, referência, limpar |

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

## 4. Os 100 domínios, por setor

A lista vem do usuário ([`catalogo_100_dominios.txt`](catalogo_100_dominios.txt), lida sem alteração): ID,
domínio, sistema, entidade e 30 palavras que ativam cada um. O resto (atributos com validação, variantes do
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
- os 100 domínios × 28 padrões (núcleo), um domínio novo por setor com Django e, com `SGS_TESTE_COMPLETO=1`, os 100 com Django;
- a pontuação do domínio, o desempate e o filtro `sgs dominios <termo>`;
- os 4 estilos;
- os temas, com contraste;
- UUID, LNNL, `apps/` e baseline;
- os campos a mais de cada tipo (texto, inteiro, decimal, sim/não, data) e o identificador de tipos;
- o modo exercício (questionário, código completo);
- o determinismo, inclusive dos binários;
- as perguntas e o `-sp`;
- o terminal e o `sgs comand`;
- subir e derrubar um site de verdade.

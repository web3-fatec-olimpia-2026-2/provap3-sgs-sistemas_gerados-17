"""
SGS · TUTORIAL — a página /tutorial (sgs tutorial) e a barra de navegação que liga, lado a lado, as páginas de
estudo servidas pela tela: Tutorial · Wiki (padrões GoF) · Django Study Hub · SGS.

As cópias de referência (pasta referencias/) NÃO são editadas no disco: a barra é acrescentada na hora de servir.
Tudo é texto fixo (sem JavaScript), no mesmo visual escuro da tela.
"""
import html
import re

PAGINAS = [("/tutorial", "Tutorial"), ("/referencia", "Wiki · padrões GoF"), ("/hub", "Django Study Hub"),
           ("/", "← SGS")]

ESTILO_NAV = ("position:sticky;top:0;z-index:2147483000;display:flex;flex-wrap:wrap;gap:2px 0;align-items:center;"
              "padding:6px 14px;background:#0c0c0c;border-bottom:1px solid #2c2c2c;"
              "font:13px/1.5 Consolas,'Cascadia Mono',monospace;color:#7c7c7c")


def barra(atual):
    """A barra do topo, com a página atual em destaque. Os itens são separados por | (sem espaço)."""
    itens = []
    for i, (href, rotulo) in enumerate(PAGINAS):
        estilo = "color:#16c60c;font-weight:700;text-decoration:none" if href == atual else \
            "color:#61d6d6;text-decoration:underline dotted"
        itens.append(("<span style='color:#7c7c7c'>|</span>" if i else "")
                     + f'<a href="{href}" style="{estilo}">{html.escape(rotulo)}</a>')
    return f'<nav id="sgs-nav" style="{ESTILO_NAV}">{"".join(itens)}</nav>'


def com_barra(pagina_html, atual):
    """Acrescenta a barra logo depois do <body …> de uma página (cópia de referência) — só na resposta."""
    return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + barra(atual), pagina_html, count=1, flags=re.I)


SECOES = [
    ("comecar", "1. Começar: gerar e subir um sistema", """
<p>Tudo se digita no prompt da tela do SGS. <b>NN</b> é o número do sistema (veja com <code>sgs listar</code>);
<code>-sp</code> = <b>sem perguntar</b> (aplica direto) · <code>-sv</code> = <b>sem versão</b> (edita o próprio sistema;
sem ele, cria a cópia NN.1).</p>
<pre>sgs gerar hotel com desconto por tipo de cliente   <i># gera (as caixas de baixo valem: + Django, testes…)</i>
sgs listar                                        <i># os sistemas e a porta de cada um</i>
sgs rodar 16                                      <i># sobe o site → http://127.0.0.1:6116/</i></pre>
<p>As palavras do pedido escolhem o <b>domínio</b> (<code>sgs dominios saude</code>) e os <b>padrões de projeto</b>
(<code>sgs padroes</code>). Com a caixa <i>Perguntar antes de gerar</i>, o SGS pergunta antes — <code>sgs gerar -sp</code>
encerra as perguntas e gera.</p>"""),
    ("classe", "2. Uma CLASSE nova (módulo) num sistema", """
<p>Cada classe nova é uma app Django a mais no sistema: <b>formulário</b>, <b>CRUD</b> (lista, novo, detalhe, editar,
excluir), <b>API REST</b>, <b>testes</b> e o núcleo dela com os padrões pedidos.</p>
<pre>sgs app 16 destinos de viagem com os campos cidade e pais        <i># com “Perguntar”: pergunta e…</i>
sgs app -sp                                                       <i># …aplica as respostas</i>
sgs app 16 -sp destinos de viagem entidade=Destino -sv           <i># direto, numa linha</i></pre>
<p>O <b>nome da classe</b> vem do pedido (“destinos de viagem” → <code>Destino</code>) ou de <code>entidade=Nome</code>.
Ela fica em <code>/destinos/</code> (cadastro em <code>/destinos/novo/</code>) e na API em <code>/destinos/api/v1/</code>.</p>"""),
    ("ligar", "3. Interligar classes (campo de referência)", """
<pre>sgs app 16 -sp destinos de viagem ligar=Viagcert.destino -sv     <i># cria a Destino e já liga</i>
sgs ligar 16 Voo.destino Destino -sv                              <i># liga duas classes que JÁ existem</i>
sgs ligar 16                                                      <i># as classes do sistema e o passo a passo</i></pre>
<p><code>Classe.campo Alvo</code>: a <b>Classe</b> ganha o <b>campo</b>, que aponta para o <b>Alvo</b>. No formulário vira
uma lista de escolha; na API, o id do alvo. É opcional: apagar o alvo só limpa o campo.</p>"""),
    ("campos", "4. Campos e TIPOS", """
<p>Campos a mais vão no próprio pedido. O <b>tipo</b> vem do nome (identificador de tipos) ou vai junto:</p>
<pre>sgs gerar pet shop com os campos nome, idade, peso, vacinado, data_retorno
sgs app 16 -sp voos com os campos numero:int, partida:data entidade=Voo -sv
sgs tipos nome, idade, peso, vacinado, status          <i># mostra o tipo que cada nome recebe</i></pre>
<table><tr><th>tipo</th><th>escreva</th><th>exemplos de nome óbvio</th></tr>
<tr><td>texto</td><td><code>:str</code></td><td>nome, cidade, email</td></tr>
<tr><td>inteiro</td><td><code>:int</code></td><td>idade, ano, dias, quantidade</td></tr>
<tr><td>decimal</td><td><code>:float</code></td><td>preco, valor_*, peso, taxa</td></tr>
<tr><td>sim/não</td><td><code>:bool</code></td><td>ativo, vacinado, tem_*</td></tr>
<tr><td>data</td><td><code>:data</code></td><td>data_*, nascimento, validade</td></tr></table>
<p>Nome ambíguo (<code>codigo</code>, <code>status</code>…) vira <b>pergunta</b> quando “Perguntar” está marcado.</p>"""),
    ("padrao", "5. O PADRÃO de um campo — o @property (encapsulamento)", """
<p>Cada campo com regra vira um <b>@property</b> na classe do núcleo: o <i>setter</i> é a “fechadura” que recusa o que
não segue o padrão. No Django, a mesma regra vira <i>validators</i> (ou <i>choices</i>) no model, no form e na API.</p>
<pre>sgs incrementar 16                                         <i># os campos e o padrão de cada um</i>
sgs incrementar 16 Viagcert.voo inteiro>=1 -sv             <i># MODIFICA: negativo e letras recusados</i>
sgs incrementar 16 Viagcert.noites inteiro:1..15 -sv       <i># faixa</i>
sgs incrementar 16 Destino.continente lista:America,Europa,Asia -sv   <i># campo NOVO, lista fechada</i>
sgs incrementar 16 Destino.pais                            <i># sem o padrão: a regra de hoje + comandos prontos</i></pre>
<table><tr><th>padrão</th><th>o campo aceita</th></tr>
<tr><td><code>inteiro>=0</code></td><td>inteiro a partir do mínimo (negativo e letras: não)</td></tr>
<tr><td><code>inteiro:1..30</code> · <code>decimal:0..100</code></td><td>número numa faixa</td></tr>
<tr><td><code>decimal>=0</code></td><td>decimal a partir do mínimo</td></tr>
<tr><td><code>lista:a,b,c</code> · <code>lista:1,2,3</code></td><td>só esses valores (no form: lista de escolha)</td></tr>
<tr><td><code>texto</code> · <code>texto-livre</code> · <code>simnao</code> · <code>data</code></td>
<td>obrigatório · opcional · True/False · AAAA-MM-DD</td></tr></table>
<p>O que sai no núcleo (<code>nucleo/entidades.py</code>) para <code>voo inteiro>=1</code>:</p>
<pre class="codigo">@property
def voo(self):
    return self._voo

@voo.setter
def voo(self, valor):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError("voo deve ser um número inteiro")
    if valor &lt; 1:
        raise ValueError("voo deve ser no mínimo 1")
    self._voo = valor</pre>
<p>A classe é <b>refeita</b> pelo gerador (determinístico): testes, form e API acompanham; o banco ganha a migration;
o site no ar reinicia sozinho. O que quebraria a classe é recusado sem mexer em nada.</p>"""),
    ("projeto", "6. PADRÕES DE PROJETO da classe (Strategy, State, Observer…)", """
<p>O @property é o padrão de <b>cada campo</b>. Os padrões GoF valem para a <b>classe</b> e vêm do pedido (as palavras
ativam) ou de <code>padroes=</code>:</p>
<pre>sgs padroes                                  <i># os 28 padrões, por categoria, e as palavras que os ativam</i>
sgs gerar hotel com estados da reserva e avisos aos hóspedes      <i># → State + Observer</i>
sgs gerar loja prova                         <i># grupos: prova (9 da P3), gof, criacao, estrutural, comportamental, todos</i>
sgs app 16 -sp voos padroes=state,observer entidade=Voo -sv       <i># classe nova com esses padrões</i></pre>
<p>Toda classe com site já leva o <b>Strategy</b> (o Service usa as políticas). A pergunta <i>Máquina de estados</i>
(sgs app) acrescenta o <b>State</b>. A explicação de cada padrão: <a href="/referencia">Wiki</a> e o README do sistema
(o tripé da P3: o que faz · por que assim · o que muda).</p>"""),
    ("api", "7. A API REST e os campos de cada endpoint", """
<pre>sgs api config 16                            <i># cada endpoint, campo a campo (clique: ocultar/expor)</i>
sgs api config 16 /api/ noites=sim codigo=nao
sgs api config 16 todos=sim                  <i># sem endpoint: vale para TODOS</i>
sgs api config 16 padrao                     <i># volta ao padrão</i></pre>
<p>Por app: <code>/api/v1/</code> (REST: GET, POST, PUT, PATCH, DELETE) e <code>/api/</code> (o resumo, link “API” do
site); nos módulos com o nome na frente (<code>/destinos/api/v1/</code>). Quem chama escolhe entre os expostos:
<code>/api/v1/?campos=viajante,valor_final</code> · a lista: <code>/api/v1/campos/</code>.</p>"""),
    ("versoes", "8. Versões, rodar, testar e parar", """
<pre>sgs editar 16                <i># cópia 16.1 (porta 61161) — o 16 não muda</i>
sgs rodar 16 · sgs parar 16 · sgs servidores
sgs testar 16                <i># núcleo + web</i>
sgs comandos 16              <i># os mesmos passos para o terminal do WSL</i></pre>
<p>Porta: 6100 + NN (16 → 6116); versão: a porta + o último dígito (16.1 → 61161). Porta ocupada: a tela pergunta se
encerra o anterior (s/N).</p>"""),
    ("atalhos", "9. A tela: atalhos e ajuda", """
<table><tr><th>tecla / comando</th><th>faz</th></tr>
<tr><td>TAB ou →</td><td>completa com a sugestão marcada (a caixa de até 5 sugestões)</td></tr>
<tr><td>↑ / ↓</td><td>com a caixa aberta: andam nas sugestões · fechada: histórico (sobrevive ao F5)</td></tr>
<tr><td>Esc · clear · history · history -c</td><td>fecha a caixa · limpa a tela · histórico · limpa o histórico</td></tr>
<tr><td><code>sgs visual powershell</code> · <code>sgs visual sgs</code></td><td>a cor da janela (ou clique no topo)</td></tr>
<tr><td><code>sgs</code> · <code>sgs comand</code></td><td>ajuda · a lista numerada de todos os comandos</td></tr></table>
<p>Todo comando do terminal funciona com ou sem <code>sgs</code> na frente (<code>ls</code> = <code>sgs ls</code>).</p>"""),
]


def pagina():
    """A página /tutorial inteira (HTML fixo)."""
    indice = "".join(f'<a href="#{ancora}">{html.escape(titulo)}</a>' for ancora, titulo, _ in SECOES)
    corpo = "".join(f'<section id="{ancora}"><h2>{html.escape(titulo)}</h2>{conteudo}</section>'
                    for ancora, titulo, conteudo in SECOES)
    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SGS — tutorial</title>
<link rel="icon" href="/icone-192.png">
<style>
  :root {{ --fundo:#0c0c0c; --painel:#151515; --texto:#cccccc; --forte:#f2f2f2; --suave:#7c7c7c; --verde:#16c60c;
          --ciano:#61d6d6; --amarelo:#e5c07b; --borda:#2c2c2c; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin:0; background:var(--fundo); color:var(--texto);
               font:15px/1.6 "Segoe UI", system-ui, sans-serif; }}
  main {{ max-width: 980px; margin: 0 auto; padding: 18px 18px 60px; }}
  h1 {{ color: var(--verde); font: 700 22px/1.3 Consolas, monospace; margin: 8px 0 4px; }}
  h2 {{ color: var(--amarelo); font-size: 17px; margin: 30px 0 8px; border-bottom: 1px dashed var(--borda);
        padding-bottom: 4px; }}
  .indice {{ display:flex; flex-wrap:wrap; gap:4px 14px; font-size:13.5px; margin: 10px 0 0; }}
  .indice a, a {{ color: var(--ciano); }}
  b {{ color: var(--forte); }}
  code {{ font-family: Consolas, "Cascadia Mono", monospace; color: var(--forte); background: var(--painel);
          padding: 0 4px; border-radius: 3px; }}
  pre {{ font: 13.5px/1.55 Consolas, "Cascadia Mono", monospace; background: var(--painel); color: var(--forte);
         border-left: 3px solid var(--verde); padding: 10px 14px; overflow-x: auto; white-space: pre; }}
  pre i {{ color: var(--suave); font-style: normal; }}
  pre.codigo {{ border-left-color: #6ea8fe; color: #d4d4d4; }}
  table {{ border-collapse: collapse; margin: 6px 0 10px; font-size: 14px; }}
  th {{ color: var(--ciano); text-align: left; font-weight: 600; border-bottom: 1px solid var(--borda); }}
  th, td {{ padding: 3px 18px 3px 0; vertical-align: top; }}
  .sub {{ color: var(--suave); margin: 0; }}
</style>
</head>
<body>
{barra("/tutorial")}
<main>
<h1>sgs tutorial — o SGS em 9 passos</h1>
<p class="sub">Prático e rápido: cada passo é um comando para copiar. Exemplos no sistema 16 (ViagemCerta).</p>
<nav class="indice">{indice}</nav>
{corpo}
</main>
</body>
</html>
"""


def resumo():
    """[(passo, comando principal)] — o que o sgs tutorial mostra no próprio terminal."""
    return [("gerar e subir", "sgs gerar <pedido> · sgs listar · sgs rodar NN"),
            ("classe nova", "sgs app NN <pedido> [entidade=Nome] [-sv]"),
            ("interligar", "sgs app NN <pedido> ligar=Classe.campo · sgs ligar NN Classe.campo Alvo"),
            ("campos e tipos", "… com os campos nome, idade:int · sgs tipos <campos>"),
            ("padrão do campo (@property)", "sgs incrementar NN Classe.campo inteiro>=1 | lista:a,b | texto…"),
            ("padrões de projeto", "sgs padroes · padroes=state,observer no sgs app"),
            ("API", "sgs api config NN [endpoint campo=sim|nao] · ?campos=a,b"),
            ("versões e sites", "sgs editar NN · sgs rodar/parar/testar NN"),
            ("tela", "TAB/→ · ↑/↓ · history · sgs visual powershell")]

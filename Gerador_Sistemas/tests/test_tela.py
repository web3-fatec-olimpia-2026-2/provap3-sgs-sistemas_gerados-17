"""
Testes do SGS (tela_prompt.py + sgs_terminal.py + sgs_comand.py).

1) As regras são funções puras (processar, Config, numerar, executar_linha…): testadas direto.
2) O servidor é testado de verdade numa porta livre, com http.client — sem navegador e sem abrir janelas.
Tudo acontece em pastas temporárias (tmp_path): nada vai para sistemas_gerados/ nem para o sgs_config.json real.
"""
import http.client
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request

import pytest

import gerar_sistema as gs
import sgs_comand
import tela_prompt as tela

PEDIDO = "biblioteca onde a multa varia conforme o tipo de leitor"


@pytest.fixture
def ctx(tmp_path):
    """Contexto isolado: sistemas em tmp/saida, config em tmp/cfg.json, terminal preso em tmp."""
    contexto = tela.Contexto(saida=tmp_path / "saida", config=tmp_path / "cfg.json", raiz=tmp_path)
    yield contexto
    contexto.servidores.parar_todos()


def rodar(ctx, linha, **opcoes):
    return tela.executar_linha(linha, ctx, opcoes)


def textos(resposta):
    """Todo o texto dos blocos (para procurar palavras na resposta)."""
    return json.dumps(resposta.get("blocos", []), ensure_ascii=False)


def porta_qualquer():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------- gerar: só com "sgs gerar"
def test_texto_solto_so_e_anotado_e_nao_gera(ctx):
    r = rodar(ctx, PEDIDO)
    assert r["ok"] and r["nota"] and "nada foi gerado" in textos(r)
    assert f"sgs gerar {PEDIDO}" in textos(r)                        # atalho para gerar, se quiser
    assert tela.sistemas(ctx.saida) == []


def test_sgs_gerar_pedido_livre(ctx):
    r = rodar(ctx, f"sgs gerar {PEDIDO}", testar=False)
    c = r["cartao"]
    assert r["ok"] and c["numero"] == "01" and c["dominio"] == "biblioteca"
    assert "strategy" in [p["chave"] for p in c["padroes"]]
    assert c["porta"] == ctx.config.valores["porta_base"] + 1


def test_sgs_gerar_direto_por_dominio_e_grupo(ctx):
    r = rodar(ctx, "sgs gerar hotel criacao", testar=False)
    assert [p["chave"] for p in r["cartao"]["padroes"]] == ["encapsulamento"] + gs.CATEGORIAS["criacao"]


def test_sgs_gerar_sem_pedido_explica(ctx):
    assert rodar(ctx, "sgs gerar")["ok"] is False


def test_caixas_valem_para_o_sgs_gerar(ctx):
    r = rodar(ctx, "sgs gerar loja com extras opcionais", testar=False, estudo=False, comentarios=False)
    assert r["cartao"]["estudo"] is False and r["cartao"]["comentarios"] is False


def test_processar_pedido_vazio_e_longo(tmp_path):
    assert tela.processar("   ", saida=tmp_path)["ok"] is False
    assert tela.processar("x" * (tela.LIMITE_PEDIDO + 1), saida=tmp_path)["ok"] is False


def test_processar_com_testes_e_exercicio(tmp_path):
    r = tela.processar("loja com extras opcionais no pedido", exercicio=True, saida=tmp_path)
    rotulos = {t["rotulo"]: t for t in r["testes"]}
    assert rotulos["núcleo (Python puro)"]["codigo"] == 0 and rotulos["núcleo (Python puro)"]["conta"] is True
    assert r["exercicio"] is True and "exercicios.html" in str(r["arquivos"])


# ---------------------------------------------------------------- número fixo e porta
def test_numero_e_dado_na_geracao_e_nao_muda(ctx):
    rodar(ctx, "sgs gerar loja com extras opcionais", testar=False)          # 01 (l…)
    rodar(ctx, f"sgs gerar {PEDIDO}", testar=False)                         # 02 (b… — vem antes no alfabeto)
    numeros = tela.numerar(ctx.saida)
    assert sorted(numeros.values()) == [1, 2]
    loja = next(n for nome, n in numeros.items() if nome.startswith("loja"))
    assert loja == 1                                                         # não virou 02 por causa do alfabeto
    rodar(ctx, "sgs gerar loja com extras opcionais", testar=False)          # gerar de novo mantém o número
    assert tela.numerar(ctx.saida) == numeros


def test_pasta_gerada_fora_da_tela_ganha_o_proximo_numero(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    gs.gerar(dominio="cinema", padroes=["strategy"], saida=ctx.saida)       # pela linha de comando
    assert sorted(tela.numerar(ctx.saida).values()) == [1, 2]


def test_listar_por_numero_com_o_sgs_como_00(ctx):
    rodar(ctx, "sgs gerar loja com extras opcionais", testar=False)
    rodar(ctx, f"sgs gerar {PEDIDO}", testar=False)
    tabela = next(b for b in rodar(ctx, "sgs listar")["blocos"] if b["t"] == "tabela")
    numeros = [linha[0]["texto"] for linha in tabela["linhas"]]
    assert numeros == ["00", "01", "02"]
    base = ctx.config.valores["porta_base"]
    assert [linha[5] for linha in tabela["linhas"]][1:] == [str(base + 1), str(base + 2)]


def test_numero_invalido_explica(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    for linha in ("sgs info", "sgs info 9", "sgs testar abc", "sgs rodar 0"):
        r = rodar(ctx, linha)
        assert r["ok"] is False and "sgs listar" in textos(r), linha


def test_info_aceita_01_e_1(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    assert rodar(ctx, "sgs info 01")["cartao"]["numero"] == rodar(ctx, "sgs info 1")["cartao"]["numero"] == "01"


# ---------------------------------------------------------------- perguntas antes de gerar
def titulo_da_pergunta(resposta):
    return next(b["texto"] for b in resposta["blocos"] if b["t"] == "titulo")


def test_perguntas_rodadas_e_sgs_gerar_sp(ctx):
    ctx.config.alterar("perguntar", "sim")
    ctx.config.alterar("testar", "nao")
    # config: estudo e comentários MARCADOS (não perguntados); Django, exercício, notas e testes desmarcados
    r = rodar(ctx, "sgs gerar loja com extras opcionais")
    assert r["pergunta"] == "pergunta 1/10 · rodada 1" and tela.sistemas(ctx.saida) == []   # nada gerado ainda
    assert titulo_da_pergunta(r).endswith("Django")
    r = rodar(ctx, "sim")                                     # Django? sim
    assert titulo_da_pergunta(r).endswith("Estilo")
    r = rodar(ctx, "cmd")                                     # estilo cmd → tema e tom NÃO se aplicam: pulados
    titulos = []
    while "refinar" not in r["pergunta"]:
        titulos.append(titulo_da_pergunta(r))
        r = rodar(ctx, "2" if titulos[-1].endswith("Identificador") else "")
    assert titulos[0].endswith("Padrões") and not any("Tema" in t or "Tom" in t for t in titulos)
    assert not any(t.endswith(("Finalidade", "Comentários no código")) for t in titulos)     # marcadas
    assert len(titulos) == 8 and "Refinar" in textos(r)       # 2 + 8 = 10 perguntas na rodada
    r = rodar(ctx, "sim")                                     # mais 10 perguntas
    assert r["pergunta"] == "pergunta 1/10 · rodada 2"
    r = rodar(ctx, "sgs gerar -sp")                           # para de perguntar e gera
    assert r["ok"] and r["pergunta"] is None and ctx.questionario is None
    c = r["cartao"]
    assert c["django"] and c["web"]["estilo"] == "cmd" and c["web"]["id_publico"] == "uuid" and c["testes"] == []


def test_caixas_marcadas_nao_sao_perguntadas(ctx):
    import sgs_perguntas
    q = sgs_perguntas.Questionario("hotel com desconto", ctx.config.valores, marcadas=sgs_perguntas.CAIXAS)
    chaves = []
    while not q.refinar:
        chaves.append(q.pergunta_atual()["chave"])
        q.responder("")
    assert chaves[0] == "estilo" and not set(chaves) & set(sgs_perguntas.CAIXAS) and len(chaves) == 10
    args = q.argumentos()
    assert args["django"] and args["exercicio"] and args["estudo"] and args["web"]["comentarios_web"]


def test_resposta_invalida_repete_a_pergunta(ctx):
    ctx.config.alterar("perguntar", "sim")
    rodar(ctx, "sgs gerar hotel com desconto")
    r = rodar(ctx, "talvez")
    assert "sim ou não" in textos(r) and r["pergunta"] == "pergunta 1/10 · rodada 1"
    r = rodar(ctx, "sim")
    assert rodar(ctx, "99")["pergunta"] == "pergunta 2/10 · rodada 1"      # opção inexistente: repete a 2


def test_gerar_sp_de_cara_nao_pergunta(ctx):
    ctx.config.alterar("perguntar", "sim")
    r = rodar(ctx, "sgs gerar -sp loja com extras opcionais", testar=False)
    assert r["cartao"]["numero"] == "01" and r["pergunta"] is None


def test_sgs_no_meio_das_perguntas_e_cancelar(ctx):
    ctx.config.alterar("perguntar", "sim")
    rodar(ctx, "sgs gerar hotel com desconto")
    r = rodar(ctx, "sgs listar")
    assert r["pergunta"] and "pergunta pendente" in textos(r)
    assert rodar(ctx, "sgs cancelar")["pergunta"] is None and tela.sistemas(ctx.saida) == []
    assert rodar(ctx, "sgs gerar -sp")["ok"] is False                       # nada em andamento


def test_sem_django_nao_pergunta_da_web_e_depois_pergunta_padroes_um_a_um(ctx):
    import sgs_perguntas
    q = sgs_perguntas.Questionario("hotel com desconto", ctx.config.valores)    # Django = não (padrão)
    chaves = []
    while not q.esgotado:
        p = q.pergunta_atual()
        if p is None:
            q.responder("sim")                                 # refinar: mais perguntas
            continue
        if p["chave"].startswith("padrao:"):
            break
        chaves.append(p["chave"])
        q.responder("")
    assert not {"estilo", "tema", "tom", "id_publico", "estrutura"} & set(chaves)
    padrao = p["chave"].split(":")[1]
    q.responder("sim")
    assert padrao in q.argumentos()["padroes"]


def chaves_da_rodada(q):
    chaves = []
    while not q.refinar:
        chaves.append(q.pergunta_atual()["chave"])
        yield chaves[-1]


def test_so_os_campos_de_tipo_duvidoso_sao_perguntados(ctx):
    import sgs_perguntas
    q = sgs_perguntas.Questionario("pet shop com os campos nome, idade, vacinado, codigo_pet e tamanho",
                                   ctx.config.valores, marcadas=sgs_perguntas.CAIXAS)
    respostas = {"tipo:codigo_pet": "INT", "tipo:tamanho": "texto"}
    chaves = []
    for chave in chaves_da_rodada(q):
        chaves.append(chave)
        q.responder(respostas.get(chave, ""))
    tipos = [c for c in chaves if c.startswith("tipo:")]
    assert tipos == ["tipo:codigo_pet", "tipo:tamanho"]          # nome, idade e vacinado são óbvios
    assert "campos" not in chaves                                 # o pedido já listou os campos
    assert chaves.index("tipo:codigo_pet") == chaves.index("padroes") + 1   # logo na 1ª rodada
    campos = {c["nome"]: c["tipo"] for c in q.argumentos()["campos"]}
    assert campos == {"nome": "str", "idade": "int", "vacinado": "bool", "codigo_pet": "int", "tamanho": "str"}
    assert "codigo_pet (inteiro (INT))" in json.dumps(q.resumo(), ensure_ascii=False)


def test_pedido_sem_campos_pergunta_quais_e_depois_o_tipo_dos_duvidosos(ctx):
    import sgs_perguntas
    q = sgs_perguntas.Questionario("hotel com desconto", ctx.config.valores, marcadas=sgs_perguntas.CAIXAS)
    chaves = []
    for chave in chaves_da_rodada(q):
        chaves.append(chave)
        q.responder({"campos": "varanda, andar", "tipo:varanda": "sim/não"}.get(chave, ""))
    assert "campos" in chaves and "tipo:varanda" in chaves and "tipo:andar" not in chaves
    assert q.argumentos()["campos"] == [{"nome": "varanda", "tipo": "bool"}, {"nome": "andar", "tipo": "int"}]


def test_enter_na_pergunta_de_campos_e_nenhum(ctx):
    import sgs_perguntas
    q = sgs_perguntas.Questionario("hotel com desconto", ctx.config.valores, marcadas=sgs_perguntas.CAIXAS)
    for _ in chaves_da_rodada(q):
        q.responder("")
    assert q.argumentos()["campos"] is None


def test_gerar_com_campos_do_questionario(tmp_path):
    r = tela.processar("hotel com desconto", campos=[{"nome": "varanda", "tipo": "bool"}], testar=True, saida=tmp_path)
    assert r["ok"] and r["campos"] == [{"nome": "varanda", "tipo": "bool", "rotulo": "sim/não (BOOL)",
                                        "certeza": "informado"}]
    assert all(t["codigo"] == 0 for t in r["testes"]), r["testes"]


def test_sgs_tipos_mostra_a_deducao(ctx):
    r = rodar(ctx, "sgs tipos nome, idade, status")
    assert r["ok"] and "inteiro (INT)" in textos(r) and "DÚVIDA" in textos(r)
    assert "nome:str idade:int status:str" in textos(r)
    assert "nomes que já são óbvios" in textos(rodar(ctx, "sgs tipos"))


def test_sgs_dominios_mostra_setores_e_filtra(ctx):
    r = rodar(ctx, "sgs dominios")
    tabela = next(b for b in r["blocos"] if b["t"] == "tabela")
    assert len(tabela["linhas"]) == 10 and "100 domínios" in textos(r)            # só os setores: tela limpa
    r = rodar(ctx, "sgs dominios pet")
    assert r["ok"] and "petshop" in textos(r) and "Pet Shop Amigo" in textos(r) and "cinema" not in textos(r)
    assert rodar(ctx, "sgs dominios zzzz")["ok"] is False


def test_pergunta_de_dominio_mostra_os_mais_pontuados_e_aceita_qualquer_um(ctx):
    import sgs_perguntas
    q = sgs_perguntas.Questionario("pet shop com banho e tosa", ctx.config.valores, marcadas=sgs_perguntas.CAIXAS)
    assert q.decisoes["dominio"] == "petshop"
    while q.pergunta_atual() is None or q.pergunta_atual()["chave"] != "dominio":
        q.responder("sim" if q.pergunta_atual() is None else "")
    opcoes = [v for v, _ in q.pergunta_atual()["opcoes"]]
    assert opcoes[0] == "petshop" and "generico" in opcoes and len(opcoes) <= 8
    assert q.responder("hemocentro") is None                                    # fora da lista, mas existe
    assert (q.decisoes["dominio"], q.decisoes["sistema"], q.decisoes["entidade"]) == \
        ("hemocentro", "Hemocentro Vida", "DoacaoSangue")                        # nome e entidade acompanham


def test_sgs_estilo_e_tema(ctx):
    assert rodar(ctx, "sgs estilo cmd")["config"]["estilo"] == "cmd"
    assert rodar(ctx, "sgs estilo neon")["ok"] is False
    r = rodar(ctx, "sgs tema T04 escuro")
    assert (r["config"]["tema"], r["config"]["tom"]) == ("T04", "escuro")
    assert rodar(ctx, "sgs tema T10 P12")["config"]["paleta"] == "P12"
    assert "Profissional" in textos(rodar(ctx, "sgs tema"))


def test_config_das_opcoes_web(ctx):
    assert rodar(ctx, "sgs config estilo=bootstrap id_publico=uuid estrutura=apps seguranca=baseline")["ok"]
    for ruim in ("estilo=neon", "tema=T11", "lnnl_tipo=93", "estrutura=pastas"):
        assert rodar(ctx, f"sgs config {ruim}")["ok"] is False, ruim


# ---------------------------------------------------------------- sgs comand · exit · clear · pwa
def test_sgs_comand_lista_numerada(ctx):
    r = rodar(ctx, "sgs comand")
    assert r["tela"] == "comand"
    numeros = [linha[0]["texto"] for b in r["blocos"] if b["t"] == "tabela" for linha in b["linhas"]]
    assert numeros == [f"{n:02d}" for n in range(1, len(sgs_comand.CATALOGO) + 1)]
    assert "runserver" in textos(r) and "source .venv/bin/activate" in textos(r)


def test_sgs_comand_n_explica_o_comando(ctx):
    n = next(i for i, c in enumerate(sgs_comand.CATALOGO, 1) if c[0] == "python manage.py runserver")
    r = rodar(ctx, f"sgs comand {n}")
    assert r["tela"] == "comand" and "Starting development server" in textos(r)
    assert rodar(ctx, "sgs comand 999")["ok"] is False


def test_botao_executar_so_em_comandos_de_leitura():
    for comando, *_ in sgs_comand.CATALOGO:
        pass
    executaveis = [c[4] for c in sgs_comand.CATALOGO if sgs_comand._comando_executavel(c[4])]
    assert "pwd" in executaveis and "sgs listar" in executaveis
    assert not any(e.startswith(("sgs gerar", "sgs config", "sgs pwa", "bash iniciar", "cp ")) for e in executaveis)


def test_exit_clear_e_history(ctx):
    assert rodar(ctx, "sgs exit")["tela"] == "principal" and rodar(ctx, "exit")["tela"] == "principal"
    assert rodar(ctx, "sgs clear")["limpar"] and rodar(ctx, "clear")["limpar"]
    assert rodar(ctx, "sgs cls")["limpar"] and rodar(ctx, "cls")["limpar"]
    assert "sgs clear" in textos(rodar(ctx, "sgs history")) and "sgs clear" in textos(rodar(ctx, "history"))


# ---------------------------------------------------------------- histórico global (arquivo: sobrevive ao F5)
def test_historico_vai_para_o_arquivo_e_volta_numa_tela_nova(ctx, tmp_path):
    rodar(ctx, "pwd")
    rodar(ctx, "pwd")                                                       # repetido seguido: entra uma vez
    r = rodar(ctx, "sgs config admin_senha=segredo99")
    assert r["gravado"] == "sgs config admin_senha=********"               # a página recebe o que foi gravado
    linhas = (tmp_path / ".sgs_historico").read_text(encoding="utf-8").splitlines()
    assert linhas == ["pwd", "sgs config admin_senha=********"]             # a senha NÃO vai para o arquivo
    nova = tela.Contexto(saida=tmp_path / "saida", config=tmp_path / "cfg.json", raiz=tmp_path)   # F5 / tela nova
    assert nova.historico.linhas() == linhas
    assert "    1  pwd" in textos(rodar(nova, "history"))


def test_history_n_c_e_d_com_ou_sem_sgs(ctx):
    for comando in ("pwd", "ls", "whoami"):
        rodar(ctx, comando)
    assert rodar(ctx, "history 2")["blocos"][0]["texto"].splitlines() == ["    3  whoami", "    4  history 2"]
    r = rodar(ctx, "sgs history -d 1")
    assert r["historico"][0] == "ls"                                        # a página troca a lista dela
    r = rodar(ctx, "sgs history -c")
    assert r["historico"] == [] and ctx.historico.linhas() == []
    assert "out of range" in textos(rodar(ctx, "history -d 99"))
    assert "numeric argument" in textos(rodar(ctx, "history abc"))


def test_resposta_de_pergunta_nao_entra_no_historico(ctx):
    ctx.config.alterar("perguntar", True)
    rodar(ctx, "sgs gerar loja com extras opcionais", testar=False)
    rodar(ctx, "")                                                          # Enter = padrão
    rodar(ctx, "2")
    assert ctx.historico.linhas() == ["sgs gerar loja com extras opcionais"]


TERMINAL_VERIFICADOS = ["pwd", "ls", "ls -la", "ll", "cd ..", "cd -", "tree -L 1", "cat README.md", "head -n 1 README.md",
                        "tail -n 1 README.md", "echo oi", "whoami", "date", "uname", "hostname", "which python",
                        "python --version", "pip list", "git status", "history", "history 3", "clear", "cls", "exit",
                        "source .venv/bin/activate", "deactivate", "cd 01", "python -m pytest --version"]


def test_todos_os_comandos_listados_funcionam_com_e_sem_sgs(ctx, tmp_path):
    """Varre o que a tela LISTA: os comandos padrão (com e sem "sgs" na frente), os exemplos de leitura do
    sgs comand e os comandos sgs. Nenhum pode cair em "comando desconhecido" nem virar anotação."""
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    (tmp_path / "README.md").write_text("oi\n", encoding="utf-8")
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "activate").write_text("#", encoding="utf-8")
    sgs = sorted({c[4] for c in sgs_comand.CATALOGO if sgs_comand._comando_executavel(c[4])} |
                 {"sgs", "sgs listar", "sgs info 01", "sgs comandos 01", "sgs ligar 01", "sgs incrementar 01",
                  "sgs padroes", "sgs dominios saude", "sgs tipos nome, idade", "sgs config", "sgs estilo", "sgs tema",
                  "sgs pwa", "sgs servidores", "sgs comand", "sgs comand 3", "sgs wiki", "sgs cancelar", "sgs exit",
                  "sgs clear", "sgs cls", "sgs history", "sgs help", "sgs tutorial", "sgs hub", "sgs cmd", "sgs cmd sgs", "cmd",
                  "cmd sgs", "sgs topo", "sgs foot"})
    formas = sgs + [forma for linha in TERMINAL_VERIFICADOS for forma in (linha, f"sgs {linha}")]
    falhas = []
    for linha in formas:
        rodar(ctx, "cd ~")
        r = rodar(ctx, linha)
        if r.get("nota") or "comando desconhecido" in textos(r):
            falhas.append(linha)
    assert falhas == [], falhas
    for manage in ("python manage.py check", "sgs python manage.py check"):        # Django, nas duas formas
        rodar(ctx, "cd 01")
        assert "no issues" in textos(rodar(ctx, manage)), manage


# ---------------------------------------------------------------- intellisense (sugestões enquanto se digita)
def test_sugestoes_tem_historico_pastas_sistemas_sgs_e_terminal_com_e_sem_sgs(ctx, tmp_path):
    (tmp_path / "pasta_a").mkdir()
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    rodar(ctx, "sgs listar")
    itens = tela.sugestoes(ctx)
    comandos = [i["cmd"] for i in itens]
    assert comandos[:2] == ["sgs topo", "sgs foot"]                         # sempre as duas primeiras
    assert comandos[2] == "sgs listar" and itens[2]["tipo"] == "historico"      # depois, o mais recente
    for esperado in ("cd pasta_a", "sgs rodar 01", "sgs incrementar 01", "cd 01", "sgs gerar ", "sgs ligar ",
                     "sgs incrementar ", "ls", "sgs ls", "history -c", "sgs history -c", "python manage.py runserver"):
        assert esperado in comandos, esperado
    assert len(comandos) == len(set(comandos))                                   # sem repetidos


def test_pagina_tem_o_intellisense(servidor):
    html = pedir(servidor, "GET", "/")[2].decode("utf-8")
    assert 'id="sugestoes"' in html and 'id="fantasma"' in html and "MAX_SUG = 5" in html
    assert 'ev.key === "Tab"' in html and "escolherSugestao" in html and '"mousedown"' in html
    assert 'ev.key === "ArrowRight" && caixaAberta()' in html                  # → no fim da linha = TAB
    assert '(ev.key === "ArrowUp" || ev.key === "ArrowDown") && caixaAberta()' in html   # ↑/↓ andam na caixa
    status, tipo, corpo = pedir(servidor, "GET", "/sugestoes")
    assert status == 200 and any(i["cmd"] == "sgs listar" for i in json.loads(corpo)["itens"])


def test_comandos_padrao_tambem_com_sgs(ctx, tmp_path):
    assert rodar(ctx, "sgs pwd")["blocos"][0]["texto"] == str(tmp_path.resolve())
    assert "Linux" in textos(rodar(ctx, "sgs uname")) and rodar(ctx, "sgs date")["blocos"][0]["cor"] is None
    assert rodar(ctx, "sgs whoami")["blocos"][0]["texto"] and rodar(ctx, "sgs hostname")["blocos"][0]["cor"] is None
    assert "aviso" in textos(rodar(ctx, "hostname outro-nome")) and "aviso" in textos(rodar(ctx, "date -s 10:00"))


# ---------------------------------------------------------------- portas: 6100, versões e portas presas
def test_porta_padrao_6100_e_config_salva_com_8100_migra(tmp_path):
    assert tela.PORTA_PADRAO == 6100 and tela.CONFIG_INICIAL["porta_base"] == 6100
    (tmp_path / "antiga.json").write_text('{"porta_base": 8100}', encoding="utf-8")
    assert tela.Config(tmp_path / "antiga.json").valores["porta_base"] == 6100
    (tmp_path / "minha.json").write_text('{"porta_base": 7000}', encoding="utf-8")
    assert tela.Config(tmp_path / "minha.json").valores["porta_base"] == 7000     # escolha do usuário fica


@pytest.mark.parametrize("numero, porta", [("01", 6101), ("01.1", 61011), ("01.3", 61013), ("01.9", 61019),
                                           ("01.19", 61019), ("01.99", 61019), ("01.10", 61010), ("99.9", 61999)])
def test_porta_da_versao_usa_o_ultimo_digito(numero, porta):
    assert tela.porta_de(tela.Num.ler(numero), 6100) == porta


def test_porta_da_versao_nao_passa_de_65535():
    with pytest.raises(ValueError, match="65535"):
        tela.porta_de(tela.Num(1, 3), 8100)                                 # 81013 não existe


def test_num_le_mostra_e_ordena():
    assert tela.Num.ler("1.3") == tela.Num(1, 3) and str(tela.Num(1, 3)) == "01.3" and str(tela.Num(7)) == "07"
    assert tela.Num(2) == 2 and tela.Num(2, 1) != 2 and tela.Num.ler("abc") is None and tela.Num.ler("1.100") is None
    assert sorted([tela.Num(2), tela.Num(1, 2), tela.Num(1)]) == [tela.Num(1), tela.Num(1, 2), tela.Num(2)]


def test_sgs_editar_cria_versoes_e_o_original_nao_muda(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    original = ctx.pasta_do_numero(1)
    (original / ".venv").mkdir()
    (original / ".venv" / "pesado.txt").write_text("não vai na cópia", encoding="utf-8")
    antes = (original / "README.md").read_text(encoding="utf-8")
    r = rodar(ctx, "sgs editar 01")
    assert r["ok"] and r["cartao"]["numero"] == "01.1" and r["cartao"]["porta"] == 61011
    assert (original / "README.md").read_text(encoding="utf-8") == antes             # o original não mudou
    v1 = ctx.pasta_do_numero("01.1")
    assert v1.name == original.name + "_v1" and not (v1 / ".venv").exists()
    assert "## Versão 01.1" in (v1 / "README.md").read_text(encoding="utf-8")
    assert rodar(ctx, "sgs editar 01.1")["cartao"]["numero"] == "01.2"               # versão da versão: próxima do 01
    tabela = next(b for b in rodar(ctx, "sgs listar")["blocos"] if b["t"] == "tabela")
    assert [linha[0]["texto"] for linha in tabela["linhas"]] == ["00", "01", "01.1", "01.2"]
    assert [linha[5] for linha in tabela["linhas"]][1:] == ["6101", "61011", "61012"]
    assert rodar(ctx, "cd 01.2")["prompt"]["cwd"].endswith("_v2")
    assert rodar(ctx, "sgs info 1.1")["cartao"]["numero"] == "01.1"
    assert sorted(tela.numerar(ctx.saida).values()) == [1]                          # versão não vira sistema novo
    rodar(ctx, "sgs gerar cinema strategy", testar=False)
    assert rodar(ctx, "sgs info 02")["ok"] and rodar(ctx, "sgs editar 9")["ok"] is False


def test_porta_em_time_wait_conta_como_livre():
    """Depois de derrubar um site, as conexões ficam ~60 s em TIME_WAIT: isso NÃO pode travar a porta."""
    servidor = socket.socket()
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("127.0.0.1", 0))
    servidor.listen()
    porta = servidor.getsockname()[1]
    cliente = socket.create_connection(("127.0.0.1", porta))
    conexao, _ = servidor.accept()
    conexao.close()                                                          # o servidor fecha primeiro → TIME_WAIT
    time.sleep(0.2)
    cliente.close()
    servidor.close()
    assert tela.porta_livre(porta)


def test_quem_escuta_na_porta_e_a_tela_nunca_se_encerra(ctx):
    with socket.socket() as escuta:
        escuta.bind(("127.0.0.1", 0))
        escuta.listen()
        porta = escuta.getsockname()[1]
        assert tela.processo_na_porta(porta)["pid"] == os.getpid()
        dono = ctx.dono_da_porta(porta)
        assert dono["encerrar"] is None                                     # é o próprio processo: não se mata
        assert tela.encerrar_pid(os.getpid()) is False
    assert tela.processo_na_porta(porta) is None


def segurar_porta(porta, *marcas):
    """Um processo à parte escutando na porta (como um site esquecido no ar)."""
    codigo = ("import socket, time\ns = socket.socket()\ns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
              f"s.bind(('127.0.0.1', {porta}))\ns.listen()\ntime.sleep(120)\n")
    processo = subprocess.Popen([sys.executable, "-c", codigo, *marcas], start_new_session=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    limite = time.monotonic() + 10
    while tela.porta_livre(porta) and time.monotonic() < limite:
        time.sleep(0.1)
    return processo


def test_tela_nova_encerra_os_sites_orfaos_da_anterior(ctx, tmp_path):
    porta = porta_qualquer()
    orfao = segurar_porta(porta, "manage.py", "runserver", f"127.0.0.1:{porta}")
    try:
        ctx.saida.mkdir(parents=True, exist_ok=True)
        (ctx.saida / tela.SERVIDORES).write_text(json.dumps({
            "loja": {"pid": orfao.pid, "porta": porta, "pasta": "x"},
            "outro": {"pid": os.getpid(), "porta": porta, "pasta": "y"}}), encoding="utf-8")   # não é runserver
        nova = tela.Contexto(saida=ctx.saida, config=tmp_path / "cfg.json", raiz=tmp_path)
        assert nova.servidores.encerrar_orfaos() == [("loja", porta)]
        assert orfao.wait(timeout=10) is not None and tela.porta_livre(porta)
        assert not (ctx.saida / tela.SERVIDORES).exists()
    finally:
        if orfao.poll() is None:
            orfao.kill()


def test_porta_ocupada_pergunta_s_encerra_o_dono_n_deixa(ctx):
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    porta = porta_qualquer()
    dono = segurar_porta(porta)
    try:
        r = rodar(ctx, f"sgs rodar 01 {porta}")
        assert r["pergunta"] == "forçar? s/N" and f"processo {dono.pid}" in textos(r) and r["dica"]
        r = rodar(ctx, "n")
        assert r["pergunta"] is None and dono.poll() is None                # n: nada foi encerrado
        rodar(ctx, f"sgs rodar 01 {porta}")
        r = rodar(ctx, "s")
        assert r["ok"] and "liberada" in textos(r), textos(r)
        assert dono.wait(timeout=10) is not None
        with urllib.request.urlopen(f"http://127.0.0.1:{porta}/", timeout=10) as resposta:
            assert resposta.status == 200
        assert "já estava no ar" in textos(rodar(ctx, f"sgs rodar 01 {porta}"))   # de novo: só reabre
        assert ctx.historico.linhas()[-1] == f"sgs rodar 01 {porta}"            # "s" e "n" não entram no histórico
        assert json.loads((ctx.saida / tela.SERVIDORES).read_text(encoding="utf-8"))   # anotado para a próxima tela
        assert rodar(ctx, "sgs parar 01")["ok"] and tela.porta_livre(porta)
        assert not (ctx.saida / tela.SERVIDORES).exists()
    finally:
        if dono.poll() is None:
            dono.kill()


def test_versao_na_porta_de_outra_pergunta_e_troca(ctx):
    """Como a 01.9 e a 01.19 (mesma porta): subir uma com a outra no ar pergunta e, com s, troca."""
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    rodar(ctx, "sgs editar 01")
    porta = porta_qualquer()
    assert rodar(ctx, f"sgs rodar 01 {porta}")["ok"]
    rodar(ctx, "cd 01.1")
    r = rodar(ctx, f"python manage.py runserver {porta}")                   # o runserver da tela também pergunta
    assert r["pergunta"] == "forçar? s/N" and "o sistema 01 (site que a tela subiu)" in textos(r)
    r = rodar(ctx, "sim")
    assert r["ok"] and "Starting development server" in textos(r), textos(r)
    ativos = ctx.servidores.ativos()
    assert list(ativos) == [ctx.pasta_do_numero("01.1").name] and ativos[list(ativos)[0]]["porta"] == porta
    rodar(ctx, "sgs parar todos")
    assert tela.porta_livre(porta)


# ---------------------------------------------------------------- módulos (sgs app)
def test_sgs_app_cria_versao_com_o_modulo_e_tudo_passa(ctx):
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    original = ctx.pasta_do_numero(1)
    principal = tela.app_django(original)
    (original / "web" / ".env").write_text("SECRET_KEY=x\nPORTA=6101\n", encoding="utf-8")
    r = rodar(ctx, "sgs app 01 clinica veterinaria com desconto por convenio entidade=Consulta")
    assert r["ok"], textos(r)
    c = r["cartao"]
    assert c["numero"] == "01.1" and c["modulos"] == ["consultas"] and "/consultas/api/v1/" in textos(r)
    assert c["testes"] and all(t["codigo"] == 0 for t in c["testes"]), c["testes"]
    v1 = ctx.pasta_do_numero("01.1")
    assert not (original / "web" / "consultas").exists()                          # o original não mudou
    for arquivo in ("settings.py", "models.py", "forms.py", "views.py", "api.py", "urls.py", "nucleo/politicas.py",
                    "tests/test_api.py", "tests/nucleo/test_politicas.py", "README.md"):
        assert (v1 / "web" / "consultas" / arquivo).exists(), arquivo
    assert '"consultas",' in (v1 / "web" / "config" / "settings.py").read_text(encoding="utf-8")
    assert 'path("consultas/", include("consultas.urls"))' in (v1 / "web" / "config" / "urls.py").read_text(encoding="utf-8")
    assert f"makemigrations {principal} consultas" in (v1 / "iniciar.sh").read_text(encoding="utf-8")
    assert "PORTA=61011" in (v1 / "web" / ".env").read_text(encoding="utf-8")
    assert tela.apps_django(v1) == [principal, "consultas"]
    assert f"makemigrations {principal} consultas" in textos(rodar(ctx, "sgs comandos 01.1"))


def test_sgs_app_explica_nome_repetido_e_sistema_sem_django(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    assert "Django" in textos(rodar(ctx, "sgs app 01 estoque com extras"))
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    principal = next(iter(gs.entidades_do_projeto(ctx.pasta_do_numero(2))))
    r = rodar(ctx, f"sgs app 02 loja com desconto entidade={principal}")         # essa classe já existe
    assert r["ok"] is False and "entidade=" in textos(r)
    assert [str(n) for n, _ in tela.sistemas(ctx.saida)] == ["01", "02"]           # nada foi copiado
    assert rodar(ctx, "sgs app 02")["ok"] is False
    r = rodar(ctx, "sgs app 02 -sp voos ligar=NaoExiste.destino")                  # ligação errada: nada muda
    assert r["ok"] is False and "não existe a classe" in textos(r) and not gs.ler_modulos(ctx.pasta_do_numero(2))


def responder_ate(ctx, r, titulo, resposta):
    """Responde Enter (padrão) até chegar na pergunta `titulo`, e aí responde `resposta`."""
    for _ in range(15):
        atual = next((b["texto"] for b in r["blocos"] if b["t"] == "titulo"), "")
        if atual.endswith(f"— {titulo}"):
            return rodar(ctx, resposta)
        r = rodar(ctx, "")
    raise AssertionError(f"a pergunta {titulo!r} não apareceu")


def test_sgs_app_pergunta_o_nome_pelo_contexto_liga_e_edita_sem_versao(ctx):
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    principal = next(iter(gs.entidades_do_projeto(ctx.pasta_do_numero(1))))
    ctx.config.alterar("perguntar", True)
    r = rodar(ctx, "sgs app 01 destinos de viagem com os campos cidade e pais")
    assert r["pergunta"] and "Funcionalidade nova" in textos(r) and "Pelo pedido: Destino" in textos(r)
    assert r["dica"].endswith("sgs app -sp aplica agora")
    r = rodar(ctx, "")                                                          # Enter: fica o nome do contexto
    assert "Versão ou edição" in textos(r)
    r = rodar(ctx, "2")                                                         # editar o próprio 01 (sem versão)
    assert f"{principal}.destino → Destino" in textos(r)                       # a ligação já usa o nome escolhido
    r = rodar(ctx, "2")                                                         # a classe que existe ganha o campo
    assert "Nome do campo" in textos(r) and "destino" in textos(r)
    rodar(ctx, "")                                                              # Enter: o campo se chama destino
    r = rodar(ctx, "sgs app -sp", testar=False)
    assert r["ok"], textos(r)
    assert "sem versão" in textos(r) and f"{principal}.destino → Destino" in textos(r)
    assert [str(n) for n, _ in tela.sistemas(ctx.saida)] == ["01"]                 # nenhuma versão nova
    pasta = ctx.pasta_do_numero(1)
    app_principal = gs.entidades_do_projeto(pasta)[principal]["caminho"]
    modelo = (pasta / "web" / app_principal / "models.py").read_text(encoding="utf-8")
    assert 'destino = models.ForeignKey("destinos.Destino"' in modelo
    assert r["cartao"]["modulos"] == ["destinos"] and ctx.questionario is None
    assert ctx.historico.linhas() == ["sgs gerar loja com extras opcionais",           # respostas não entram
                                      "sgs app 01 destinos de viagem com os campos cidade e pais", "sgs app -sp"]
    testes = r["cartao"]["testes"]                                              # "Rodar testes" marcada: rodou
    assert testes and all(t["codigo"] == 0 for t in testes), testes


def test_sgs_incrementar_lista_os_campos_e_modifica_sem_versao(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)                        # sem Django: rápido
    lista = rodar(ctx, "sgs incrementar 01")
    assert "Reserva.quarto" in textos(lista) and "lista:janela,meio,corredor" in textos(lista)
    r = rodar(ctx, "sgs incrementar 01 Reserva.quarto inteiro>=0 -sv")
    assert r["ok"] and "sem versão" in textos(r) and "modificado" in textos(r), textos(r)
    assert r["cartao"]["testes"] and all(t["codigo"] == 0 for t in r["cartao"]["testes"])
    assert "if valor < 0:" in (ctx.pasta_do_numero(1) / "nucleo" / "entidades.py").read_text(encoding="utf-8")
    assert [str(n) for n, _ in tela.sistemas(ctx.saida)] == ["01"]
    assert "não fecha" in textos(rodar(ctx, "sgs incrementar 01 Reserva.diarias decimal>=0 -sv"))
    r = rodar(ctx, "sgs incrementar 01 Reserva.vista simnao", testar=False)     # sem -sv: versão nova
    assert r["ok"] and r["cartao"]["numero"] == "01.1"


def test_sgs_incrementar_pergunta_classe_campo_e_padrao(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    ctx.config.alterar("perguntar", True)
    r = rodar(ctx, "sgs incrementar 01")
    assert r["pergunta"] and "— Classe" in textos(r)
    r = rodar(ctx, "")                                                          # a Reserva (a única)
    assert "— Campo" in textos(r) and "um campo NOVO" in textos(r)
    r = rodar(ctx, "novo")                                                      # um campo novo…
    assert "Nome do campo novo" in textos(r)
    r = rodar(ctx, "assento")
    assert "Padrão do campo" in textos(r)
    r = rodar(ctx, "lista")                                                     # …com uma lista fechada
    assert "Valor da regra" in textos(r)
    assert "pelo menos 2" in textos(rodar(ctx, "janela"))                       # lista de um valor só: repete
    r = rodar(ctx, "janela, corredor")
    assert "Versão ou edição" in textos(r)
    rodar(ctx, "2")                                                             # editar o próprio 01
    r = rodar(ctx, "sgs incrementar -sp")
    assert r["ok"], textos(r)
    entidades = (ctx.pasta_do_numero(1) / "nucleo" / "entidades.py").read_text(encoding="utf-8")
    assert "if valor not in ('janela', 'corredor',):" in entidades and ctx.questionario is None


def test_ligar_e_incrementar_explicam_o_que_fazer(ctx):
    """Com o alvo que ainda não existe, o ligar ensina a criar e ligar; sem o padrão, o incrementar mostra o campo."""
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    principal = next(iter(gs.entidades_do_projeto(ctx.pasta_do_numero(1))))
    como = textos(rodar(ctx, "sgs ligar 01"))
    assert "Como usar" in como and "crie a outra classe primeiro" in como and f"ligar={principal}.destino" in como
    r = rodar(ctx, f"sgs ligar 01 {principal}.destino Destino")
    assert r["ok"] is False and "ainda não existe" in textos(r)
    assert f"sgs app 01 destinos ligar={principal}.destino" in textos(r)                # o comando que resolve
    assert "Como usar" in textos(rodar(ctx, "sgs ligar 01 Nada.destino Destino"))
    campo = gs.classes_do_projeto(ctx.pasta_do_numero(1))[principal]["atributos"][0]["nome"]
    r = rodar(ctx, f"sgs incrementar 01 {principal}.{campo}")                          # sem o padrão
    assert "hoje:" in textos(r) and f"sgs incrementar 01 {principal}.{campo} inteiro>=0 -sv" in textos(r)
    assert "será CRIADO" in textos(rodar(ctx, f"sgs incrementar 01 {principal}.assento"))
    assert "Como usar" in textos(rodar(ctx, "sgs incrementar 01"))
    m = gs.preparar_modulo(ctx.pasta_do_numero(1), "destinos de viagem")["modulo"]
    assert m["padroes"] == ["encapsulamento", "strategy"]                              # sem palavra de padrão: mínimo


def test_sgs_api_config_escolhe_os_campos_de_cada_endpoint(ctx):
    pytest.importorskip("django")
    import ast as ast_mod
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    rodar(ctx, "sgs app 01 -sp destinos de viagem -sv", testar=False)
    pasta = ctx.pasta_do_numero(1)
    principal = next(c for c in gs.entidades_do_projeto(pasta) if c != "Destino")
    app = gs.entidades_do_projeto(pasta)[principal]["app"]
    campo = gs.classes_do_projeto(pasta)[principal]["atributos"][0]["nome"]
    tabela = textos(rodar(ctx, "sgs api config 01"))
    assert all(rota in tabela for rota in ("/api/v1/", "/api/", "/destinos/api/v1/", "/destinos/api/"))
    r = rodar(ctx, f"sgs api config 01 /api/v1/ {campo}=nao titulo=sim")
    assert r["ok"] and r["blocos"][0]["texto"].startswith("✓ /api/v1/"), textos(r)
    assert rodar(ctx, "sgs api config 01 destinos.resumo total=sim")["ok"]
    settings = (pasta / "web" / "config" / "settings.py").read_text(encoding="utf-8")

    def bloco_de(prefixo):
        return ast_mod.literal_eval(re.search(rf"^{prefixo}_API_CAMPOS = (.+)$", settings, re.M).group(1))
    assert bloco_de(app.upper()) == {"v1": {campo: False, "titulo": True}}
    assert bloco_de("DESTINOS") == {"resumo": {"total": True}}
    assert gs.ler_api_campos(pasta)[app]["v1"][campo] is False
    erro = rodar(ctx, "sgs api config 01 /nada/ total=nao")
    assert erro["ok"] is False and "não existe" in textos(erro)
    assert "não é campo" in textos(rodar(ctx, "sgs api config 01 /api/v1/ voar=nao"))
    testes = gs.executar_testes(pasta, type("S", (), {"exercicio": False, "django": True})())
    assert all(t["codigo"] == 0 for t in testes), testes                        # a escolha não quebra os testes
    rodar(ctx, "sgs api config 01 /api/v1/ padrao")                                 # volta ao padrão
    assert app not in gs.ler_api_campos(pasta)


def test_sgs_api_config_sem_endpoint_vale_para_todos_e_reinicia_o_site(ctx):
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    pasta = ctx.pasta_do_numero(1)
    porta = porta_qualquer()
    assert rodar(ctx, f"sgs rodar 01 {porta}")["ok"]
    r = rodar(ctx, "sgs api config 01 todos=sim")                                  # sem endpoint: todos
    assert r["ok"] and "/api/v1/: expostos" in textos(r) and "/api/: expostos" in textos(r), textos(r)
    assert "foi reiniciado" in textos(r)                                           # o site volta com a escolha
    with urllib.request.urlopen(f"http://127.0.0.1:{porta}/api/v1/campos/", timeout=10) as resposta:
        campos = json.loads(resposta.read())
    assert campos["expostos"]["resumo"] == campos["disponiveis"]                   # o site no ar já mostra tudo
    assert rodar(ctx, "sgs api config 01 padrao")["ok"] and gs.ler_api_campos(pasta) == {}
    assert "não é campo" in textos(rodar(ctx, "sgs api config 01 voar=sim"))
    rodar(ctx, "sgs parar todos")


def test_sgs_api_config_atualiza_uma_app_de_antes(ctx):
    """App gerada antes dos campos configuráveis (sem API_CAMPOS): a 1ª mudança refaz a classe e tudo passa."""
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar hotel strategy", django=True, testar=False)
    pasta = ctx.pasta_do_numero(1)
    app = gs.entidades_do_projeto(pasta)["Reserva"]["app"]
    configuracao = pasta / "web" / app / "settings.py"
    configuracao.write_text(configuracao.read_text(encoding="utf-8").replace('"API_CAMPOS": {},', ""), encoding="utf-8")
    assert "vieram de uma versão anterior" in textos(rodar(ctx, "sgs api config 01"))
    r = rodar(ctx, "sgs api config 01 /api/v1/ observacao=nao")
    assert r["ok"] and "foi refeita" in textos(r), textos(r)
    assert '"API_CAMPOS": {}' in configuracao.read_text(encoding="utf-8")
    assert all(t["codigo"] == 0 for t in gs.executar_testes(pasta, type("S", (), {"exercicio": False, "django": True})()))


def test_sgs_ligar_lista_as_classes_e_liga_numa_versao(ctx):
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    assert rodar(ctx, "sgs app 01 -sp voos entidade=Voo -sv", testar=False)["ok"]        # direto, sem perguntas
    principal = next(c for c in gs.entidades_do_projeto(ctx.pasta_do_numero(1)) if c != "Voo")
    lista = rodar(ctx, "sgs ligar 01")
    assert "Voo" in textos(lista) and principal in textos(lista)
    r = rodar(ctx, f"sgs ligar 01 Voo.{principal.lower()} {principal}", testar=False)
    assert r["ok"], textos(r)
    assert r["cartao"]["numero"] == "01.1"                                          # sem -sv: versão nova
    v1 = ctx.pasta_do_numero("01.1")
    assert f'models.ForeignKey("' in (v1 / "web" / "voos" / "models.py").read_text(encoding="utf-8")
    assert "ForeignKey" not in (ctx.pasta_do_numero(1) / "web" / "voos" / "models.py").read_text(encoding="utf-8")
    assert "já tem um campo" in textos(rodar(ctx, f"sgs ligar 01.1 Voo.{principal.lower()} {principal} -sv"))


def test_sgs_pwa(ctx):
    assert ctx.config.valores["pwa"] is True                              # todo projeto começa em PWA
    r = rodar(ctx, "sgs pwa=false")
    assert r["ok"] and r["config"]["pwa"] is False and tela.Config(ctx.config.caminho).valores["pwa"] is False
    assert rodar(ctx, "sgs pwa true")["config"]["pwa"] is True
    assert "PWA ligado" in textos(rodar(ctx, "sgs pwa"))
    assert rodar(ctx, "sgs pwa=talvez")["ok"] is False


def test_ajuda_lista_os_comandos(ctx):
    r = rodar(ctx, "sgs")
    assert "sgs gerar" in textos(r) and "sgs comand" in textos(r) and "sgs pwa" in textos(r)


def test_config_pelo_sgs(ctx):
    r = rodar(ctx, "sgs config porta_base=8300 estudo=nao")
    assert r["ok"] and r["config"]["porta_base"] == 8300 and r["config"]["estudo"] is False
    assert rodar(ctx, "sgs config porta_base=1")["ok"] is False


@pytest.mark.parametrize("chave, valor", [("nao_existe", "1"), ("django", "talvez"), ("porta_base", "80"),
                                          ("admin_senha", "123"), ("admin_email", "sem-arroba"),
                                          ("admin_usuario", "com espaço")])
def test_config_recusa_valor_invalido(tmp_path, chave, valor):
    with pytest.raises(ValueError):
        tela.Config(tmp_path / "x.json").alterar(chave, valor)


def test_config_estragada_volta_ao_padrao(tmp_path):
    (tmp_path / "x.json").write_text("{isto não é json", encoding="utf-8")
    assert tela.Config(tmp_path / "x.json").valores == tela.CONFIG_INICIAL


def test_padroes_e_comando_desconhecido(ctx):
    tabelas = [b for b in rodar(ctx, "sgs padroes gof")["blocos"] if b["t"] == "tabela"]
    assert sum(len(t["linhas"]) for t in tabelas) == 23
    assert rodar(ctx, "sgs voar")["ok"] is False


# ---------------------------------------------------------------- terminal (com ou sem sgs)
def test_pwd_cd_ls_e_prompt(ctx, tmp_path):
    (tmp_path / "pasta").mkdir()
    (tmp_path / "pasta" / "a.txt").write_text("olá", encoding="utf-8")
    assert rodar(ctx, "pwd")["blocos"][0]["texto"] == str(tmp_path.resolve())
    r = rodar(ctx, "cd pasta")
    assert r["prompt"]["cwd"] == "~/pasta" and r["blocos"] == []
    assert "a.txt" in textos(rodar(ctx, "ls"))
    assert rodar(ctx, "sgs cd ..")["prompt"]["cwd"] == "~"                 # com sgs na frente também
    assert rodar(ctx, "cd -")["prompt"]["cwd"] == "~/pasta"


def test_cd_nao_sai_do_projeto_e_avisa_pasta_inexistente(ctx):
    assert "fora do projeto" in textos(rodar(ctx, "cd /etc"))
    assert "No such file or directory" in textos(rodar(ctx, "cd nao_existe"))
    assert rodar(ctx, "cd ../..")["prompt"]["cwd"] == "~"


def test_cd_nn_entra_no_sistema(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    assert rodar(ctx, "cd 01")["prompt"]["cwd"].endswith("hotel_resort__strategy")
    assert "README.md" in textos(rodar(ctx, "ls"))


def test_cat_mascara_segredos_do_env(ctx, tmp_path):
    (tmp_path / ".env").write_text("SECRET_KEY=abc123\nDJANGO_SUPERUSER_PASSWORD=minhasenha\nDEBUG=1\n", encoding="utf-8")
    saida = textos(rodar(ctx, "cat .env"))
    assert "abc123" not in saida and "minhasenha" not in saida and "DEBUG=1" in saida


def test_source_e_deactivate_mudam_o_prompt(ctx, tmp_path):
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "activate").write_text("# ativa", encoding="utf-8")
    assert rodar(ctx, "source .venv/bin/activate")["prompt"]["venv"] == ".venv"
    assert rodar(ctx, "deactivate")["prompt"]["venv"] == ""
    assert "No such file" in textos(rodar(ctx, "source nao/bin/activate"))


def test_python_version_e_pip_install_simulado(ctx, tmp_path):
    assert "Python 3" in textos(rodar(ctx, "python --version"))
    (tmp_path / "requirements.txt").write_text("pytest>=8.0\npacote-que-nao-existe-xyz>=1\n", encoding="utf-8")
    saida = textos(rodar(ctx, "pip install -r requirements.txt"))
    assert "Requirement already satisfied: pytest>=8.0" in saida and "faltando: pacote-que-nao-existe-xyz" in saida


@pytest.mark.parametrize("linha", ["rm -rf .", "mkdir x", "sudo apt install y", "pip install django",
                                   "python", "git push", "cp a b"])
def test_comandos_perigosos_ou_interativos_sao_recusados(ctx, linha):
    r = rodar(ctx, linha)
    assert r["blocos"] and r["blocos"][0].get("cor") in ("aviso", "erro") and not r.get("nota"), linha


def test_pytest_de_verdade_e_variavel_na_frente(ctx):
    rodar(ctx, "sgs gerar hotel decorator", testar=False, exercicio=True)
    rodar(ctx, "cd 01")
    assert "passed" in textos(rodar(ctx, "DEBUG=0 python -m pytest -q"))
    assert "failed" not in textos(rodar(ctx, "python -m pytest -q"))        # exercício = questionário: código verde
    assert "exercicios.html" in textos(rodar(ctx, "ls"))


def test_django_pelo_terminal_ajusta_o_manage_py_e_roda_o_site(ctx):
    pytest.importorskip("django")
    porta = porta_qualquer()
    ctx.config.alterar("porta_base", porta - 1)                             # o sistema 01 roda nesta porta livre
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    rodar(ctx, "cd 01")
    check = rodar(ctx, "python manage.py check")                            # está na pasta do sistema: ajusta
    assert "ajuste" in textos(check) and "no issues" in textos(check)
    assert "interativo" in textos(rodar(ctx, "python manage.py createsuperuser"))
    rodar(ctx, "bash iniciar.sh env")
    assert "DJANGO_SUPERUSER_USERNAME=admin" in (ctx.pasta_do_numero(1) / "web" / ".env").read_text(encoding="utf-8")
    assert "OK" in textos(rodar(ctx, "python manage.py migrate"))
    r = rodar(ctx, "python manage.py runserver")
    assert f"http://127.0.0.1:{porta}/" in textos(r)                       # porta 6100+NN (aqui: a livre)
    with urllib.request.urlopen(f"http://127.0.0.1:{porta}/manifest.webmanifest", timeout=10) as resposta:
        assert json.loads(resposta.read())["display"] == "standalone"      # o site gerado é PWA
    assert str(porta) in textos(rodar(ctx, "sgs servidores"))
    assert rodar(ctx, "sgs parar 01")["ok"] and tela.porta_livre(porta)


def test_sgs_rodar_prepara_e_sobe(ctx):
    pytest.importorskip("django")
    rodar(ctx, "sgs gerar loja com extras opcionais", django=True, testar=False)
    ctx.config.alterar("admin_usuario", "professor")
    porta = porta_qualquer()
    r = rodar(ctx, f"sgs rodar 01 {porta}")
    assert r["ok"], textos(r)
    with urllib.request.urlopen(f"http://127.0.0.1:{porta}/", timeout=10) as resposta:
        assert resposta.status == 200
    env = (ctx.pasta_do_numero(1) / "web" / ".env").read_text(encoding="utf-8")
    assert "DJANGO_SUPERUSER_USERNAME=professor" in env and "troque-esta-chave" not in env
    assert rodar(ctx, f"sgs parar {porta}")["ok"] and tela.porta_livre(porta)


def test_rodar_sistema_sem_django_explica(ctx):
    rodar(ctx, "sgs gerar hotel strategy", testar=False)
    r = rodar(ctx, "sgs rodar 01")
    assert r["ok"] is False and "Django" in textos(r)


# ---------------------------------------------------------------- ler arquivos (visualizador)
@pytest.mark.parametrize("pasta, caminho", [("{pasta}", "../../segredo.txt"), ("..", "segredo.txt"), ("", "x"),
                                            ("alheia", "nota.txt"), ("{pasta}", "web/.env")])
def test_ler_arquivo_recusa_fora_do_sistema(tmp_path, pasta, caminho):
    saida = tmp_path / "saida"
    r = tela.processar(PEDIDO, testar=False, saida=saida)
    (tmp_path / "segredo.txt").write_text("não pode aparecer", encoding="utf-8")
    (saida / "alheia").mkdir()
    (saida / "alheia" / "nota.txt").write_text("minha", encoding="utf-8")
    (saida / r["pasta"] / "web").mkdir()
    (saida / r["pasta"] / "web" / ".env").write_text("SENHA=x", encoding="utf-8")
    assert tela.ler_arquivo(pasta.format(pasta=r["pasta"]), caminho, saida)["ok"] is False
    assert tela.ler_arquivo(r["pasta"], "README.md", saida)["ok"] is True


# ---------------------------------------------------------------- servidor HTTP
@pytest.fixture
def servidor(tmp_path):
    s = tela.criar_servidor(0, tmp_path / "saida", config=tmp_path / "cfg.json", raiz=tmp_path)
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    yield s.server_address[1]
    s.shutdown()
    s.ctx.servidores.parar_todos()
    s.server_close()


def pedir(porta, metodo, caminho, corpo=None, cabecalhos=None):
    c = http.client.HTTPConnection("127.0.0.1", porta, timeout=60)
    c.request(metodo, caminho, body=corpo, headers=cabecalhos or {})
    r = c.getresponse()
    dados = r.read()
    c.close()
    return r.status, r.getheader("Content-Type", ""), dados


def postar(porta, caminho, dados):
    status, tipo, corpo = pedir(porta, "POST", caminho, json.dumps(dados), {"Content-Type": "application/json"})
    return status, json.loads(corpo)


def test_pagina_tem_os_comandos_do_topo_e_o_terminal(servidor):
    status, tipo, html = pedir(servidor, "GET", "/")
    html = html.decode("utf-8")
    assert status == 200 and tipo.startswith("text/html")
    assert "<title>SGS</title>" in html and 'class="banner"' not in html   # na barra só a sigla; topo sem o nome
    assert "Sistema Gerador de Sistema" not in html
    principais = re.search(r"const PRINCIPAIS = (\[.*?\]);", html, re.S).group(1)
    assert '"sgs comand"' in principais and "pwa" not in principais       # pwa só na lista completa
    comandos = {c.strip() for c, _ in json.loads(principais)}
    assert {"sgs", "sgs gerar", "sgs listar", "sgs rodar", "sgs estilo", "sgs config", "clear", "sgs info",
            "sgs parar", "sgs app", "sgs ligar", "sgs incrementar", "sgs api config", "sgs dominios", "sgs tipos",
            "sgs tutorial", "sgs wiki", "sgs hub", "sgs cmd"} <= comandos
    assert 'c.trim().replace(/^sgs /, "")' in html                         # no topo, sem o "sgs" na frente
    assert '<p class="principais" id="principais"></p>' in html and '[i ? "|" : "", item]' in html   # "|" sem espaço
    assert "max-width: 1100px" not in html                                 # até o fim da tela
    assert "VISUAIS" not in html and "janela[" not in html                  # o estilo muda por comando (sgs cmd)
    assert '<html lang="pt-br" data-visual="cmd" data-topo="0" data-rodape="0">' in html   # cmd, sem topo nem caixas
    assert 'fixa ? -1 : pontuar(s.cmd, t)' in html                        # sgs topo e sgs foot sempre primeiro
    assert ':root[data-topo="0"] #principais { display: none; }' in html                   # sgs topo
    assert ':root[data-rodape="0"] .opcoes { display: none; }' in html                     # sgs foot: o prompt fica
    assert 'id="enviar"' not in html and "Executar" not in html          # sem botão executar (Enter executa)
    assert 'ev.key === "Enter" && ev.altKey' in html and "window.resizeTo" in html   # Alt+Enter maximiza/volta
    assert ':root[data-visual="cmd"]' in html and "#0c0c0c" in html and "--prompt: #cccccc" in html
    assert "--marca: #cccccc" in html and "appearance: none" in html      # caixas do rodapé sem cor
    assert "flex-wrap: nowrap" in html and "(valem para o sgs gerar)" not in html   # rodapé numa linha só
    assert "exemplos" not in html.lower()                                 # sem exemplos na tela inicial
    assert 'id="cursor"' in html and 'rel="manifest"' in html and "serviceWorker" in html
    assert 'class="ps1-linha"' in html and 'id="seta">&gt;</span>' in html
    assert 'modoCmd() ? ">" : "$>"' in html and 'replaceAll("/", "\\\\")' in html   # ~\pasta> · no sgs, "$>"
    assert "trocarHistorico(d.historico)" in html                          # o histórico volta depois do F5
    for opcao in ("django", "exercicio", "testar", "estudo", "comentarios", "comentarios_web", "perguntar"):
        assert f'data-opcao="{opcao}"' in html                           # as caixas da geração
    assert "innerHTML" not in html


def test_pwa_do_sgs(servidor):
    status, tipo, corpo = pedir(servidor, "GET", "/manifest.webmanifest")
    assert status == 200 and json.loads(corpo)["display"] == "standalone"
    status, tipo, corpo = pedir(servidor, "GET", "/sw.js")
    assert status == 200 and "javascript" in tipo
    for tamanho in (192, 512):
        status, tipo, corpo = pedir(servidor, "GET", f"/icone-{tamanho}.png")
        assert status == 200 and corpo[:8] == b"\x89PNG\r\n\x1a\n"


def test_comando_pelo_servidor(servidor):
    status, r = postar(servidor, "/comando", {"linha": PEDIDO})
    assert status == 200 and r["nota"] and r["prompt"]["cwd"] == "~"
    status, r = postar(servidor, "/comando", {"linha": "sgs gerar hotel strategy", "opcoes": {"testar": False}})
    assert r["ok"] and r["cartao"]["numero"] == "01"
    status, r = postar(servidor, "/comando", {"linha": "sgs config"})
    assert "admin_senha" not in r["config"]


def test_config_pelo_servidor(servidor):
    assert postar(servidor, "/config", {"django": True})[1]["config"]["django"] is True
    assert json.loads(pedir(servidor, "GET", "/config")[2])["config"]["django"] is True
    assert postar(servidor, "/config", {"porta_base": 1})[1]["ok"] is False


def test_referencia_da_wikipedia(servidor):
    """/referencia leva para a pasta referencias/: assim o CSS da cópia (caminho relativo) carrega — a formatação
    da Wikipédia volta. A barra Tutorial | Wiki | Hub entra só na resposta (o arquivo não muda)."""
    status, _, _ = pedir(servidor, "GET", "/referencia")
    assert status == 302
    status, tipo, html = pedir(servidor, "GET", "/referencias/wikipedia_padrao_de_projeto_de_software.html")
    html = html.decode("utf-8")
    assert status == 200 and tipo.startswith("text/html")
    assert "oldid=" in html and "22/11/2026" in html and "Abstract Factory" in html
    assert 'href="/tutorial"' in html and 'href="/hub"' in html             # lado a lado com o tutorial
    css = re.search(r'href="(wikipedia_padrao_de_projeto_de_software_arquivos/[^"]+\.css)"', html).group(1)
    status, tipo, _ = pedir(servidor, "GET", "/referencias/" + css)
    assert status == 200 and tipo.startswith("text/css")
    arquivo = (tela.PASTA_REFERENCIAS / "wikipedia_padrao_de_projeto_de_software.html").read_text(encoding="utf-8")
    assert 'href="/tutorial"' not in arquivo                               # a cópia fica intacta


def test_tutorial_e_django_study_hub(servidor):
    status, tipo, html = pedir(servidor, "GET", "/tutorial")
    html = html.decode("utf-8")
    assert status == 200 and tipo.startswith("text/html")
    for trecho in ("sgs app", "sgs ligar", "sgs incrementar", "@property", "sgs api config", 'href="/referencia"',
                   'href="/hub"'):
        assert trecho in html, trecho
    status, _, _ = pedir(servidor, "GET", "/hub")
    assert status == 302
    status, tipo, html = pedir(servidor, "GET", "/referencias/django_study_hub.html")
    assert status == 200 and 'href="/tutorial"' in html.decode("utf-8")


def test_respostas_grandes_vao_em_gzip_se_o_navegador_aceitar(servidor):
    """Pelo repasse localhost do WSL2, respostas de ~200 KB travavam no fim: o texto grande vai comprimido."""
    import gzip
    css = "/referencias/wikipedia_padrao_de_projeto_de_software_arquivos/estilo1.css"
    conexao = http.client.HTTPConnection("127.0.0.1", servidor, timeout=10)
    conexao.request("GET", css, headers={"Accept-Encoding": "gzip, deflate, br"})
    r = conexao.getresponse()
    comprimido = r.read()
    assert r.status == 200 and r.getheader("Content-Encoding") == "gzip"
    assert int(r.getheader("Content-Length")) == len(comprimido) < 60_000
    original = (tela.PASTA_REFERENCIAS / css.removeprefix("/referencias/")).read_bytes()
    assert gzip.decompress(comprimido) == original
    status, _, corpo = pedir(servidor, "GET", css)                       # sem Accept-Encoding: como está
    assert status == 200 and corpo == original


@pytest.mark.parametrize("caminho", ["/referencias/../tela_prompt.py", "/referencias/%2e%2e/tela_prompt.py",
                                     "/referencias/README.md", "/referencias/nada.html"])
def test_referencias_nao_servem_fora_da_pasta_nem_outros_tipos(servidor, caminho):
    assert pedir(servidor, "GET", caminho)[0] == 404


def test_sgs_tutorial_hub_e_wiki_abrem_lado_a_lado(ctx):
    r = rodar(ctx, "sgs tutorial")
    assert r["ok"] and r["abrir"] == "/tutorial"
    assert "sgs incrementar" in textos(r) and "sgs ligar" in textos(r)
    for comando in ("sgs tutorial", "sgs wiki", "sgs hub"):
        botoes = [b for b in rodar(ctx, comando)["blocos"] if b["t"] == "botoes"]
        assert [c["href"] for c in botoes[0]["itens"]] == ["/tutorial", "/referencia", "/hub"], comando


def test_sgs_cmd_troca_o_estilo_da_tela(ctx, tmp_path):
    assert ctx.config.valores["visual"] == "cmd"                           # o padrão: Prompt de Comando
    r = rodar(ctx, "sgs cmd sgs")
    assert r["ok"] and r["config"]["visual"] == "sgs" and "sgs cmd" in textos(r)
    assert rodar(ctx, "sgs cmd")["config"]["visual"] == "cmd"              # sozinho: volta ao estilo cmd
    assert rodar(ctx, "cmd sgs")["config"]["visual"] == "sgs"              # sem o sgs na frente também
    assert rodar(ctx, "cmd")["config"]["visual"] == "cmd"
    assert rodar(ctx, "sgs cmd roxo")["ok"] is False
    assert rodar(ctx, "sgs visual sgs")["config"]["visual"] == "sgs"       # o nome antigo continua valendo
    (tmp_path / "antigo.json").write_text(json.dumps({"visual": "powershell"}), encoding="utf-8")
    assert tela.Config(tmp_path / "antigo.json").valores["visual"] == "cmd"   # config antiga → cmd
    itens = {i["cmd"] for i in tela.sugestoes(ctx)}
    assert {"sgs cmd", "sgs cmd sgs", "cmd", "cmd sgs", "sgs topo", "sgs foot"} <= itens   # no intellisense


def test_sgs_topo_e_sgs_foot_alternam(ctx):
    assert ctx.config.valores["topo"] is False and ctx.config.valores["rodape"] is False  # abre sem os dois
    assert rodar(ctx, "sgs topo")["config"]["topo"] is True                # mostra
    assert rodar(ctx, "sgs topo")["config"]["topo"] is False               # de novo: oculta
    assert rodar(ctx, "sgs foot")["config"]["rodape"] is True              # mostra as caixas
    assert rodar(ctx, "sgs foot")["config"]["rodape"] is False             # de novo: oculta
    assert rodar(ctx, "sgs topo sim")["config"]["topo"] is True            # sim/não fixa
    assert rodar(ctx, "sgs topo talvez")["ok"] is False


def test_a_tela_pelo_django_python_manage_py_runserver(tmp_path):
    """`python manage.py runserver` (pasta Gerador_Sistemas) serve a MESMA tela do tela_prompt.py: a view do
    Django repassa tudo para atender() — página, comandos, Host 127.0.0.1, POST só em JSON, gzip e o início."""
    import gzip
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        porta = s.getsockname()[1]
    ambiente = {**os.environ, "SGS_SAIDA": str(tmp_path / "saida"), "SGS_CONFIG": str(tmp_path / "cfg.json"),
                "SGS_RAIZ": str(tmp_path), "PYTHONUNBUFFERED": "1"}
    ambiente.pop("DJANGO_SETTINGS_MODULE", None)
    ambiente.pop(tela.MARCA_TELA, None)              # (se a bateria rodar de dentro da tela, ela marca o ambiente)
    processo = subprocess.Popen([sys.executable, "manage.py", "runserver", f"127.0.0.1:{porta}", "--noreload",
                                 "--sem-abrir"], cwd=tela.AQUI, env=ambiente, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
    try:
        for _ in range(150):                                               # até 30 s para subir
            if processo.poll() is not None or not tela.porta_livre(porta):
                break
            time.sleep(0.2)
        assert processo.poll() is None, processo.stdout.read()
        time.sleep(0.3)
        status, tipo, html = pedir(porta, "GET", "/")
        assert status == 200 and tipo.startswith("text/html") and "<title>SGS</title>" in html.decode("utf-8")
        status, r = postar(porta, "/comando", {"linha": "sgs listar"})
        assert status == 200 and r["ok"] and "sistema(s)" in textos(r)
        status, cfg = postar(porta, "/config", {})
        assert cfg["config"]["visual"] == "cmd" and cfg["config"]["topo"] is False   # o início do SGS rodou
        assert cfg["config"]["rodape"] is False and cfg["config"]["pwa"] is True
        assert pedir(porta, "POST", "/comando", "linha=sgs",
                     {"Content-Type": "application/x-www-form-urlencoded"})[0] == 415   # só JSON
        assert pedir(porta, "GET", "/", None, {"Host": "site-malicioso.com"})[0] in (400, 403)   # só 127.0.0.1
        assert pedir(porta, "GET", "/nada")[0] == 404
        assert pedir(porta, "GET", "/referencia")[0] == 302
        css = "/referencias/wikipedia_padrao_de_projeto_de_software_arquivos/estilo1.css"
        conexao = http.client.HTTPConnection("127.0.0.1", porta, timeout=30)
        conexao.request("GET", css, headers={"Accept-Encoding": "gzip"})
        resposta = conexao.getresponse()
        assert resposta.getheader("Content-Encoding") == "gzip"
        assert gzip.decompress(resposta.read()) == (tela.PASTA_REFERENCIAS / css.removeprefix("/referencias/")).read_bytes()
        conexao.close()
    finally:
        processo.terminate()
        processo.wait(timeout=15)
    saida = processo.stdout.read()
    assert "Sistemas gerados em:" in saida and str(tmp_path / "saida") in saida


def test_runserver_do_sgs_abre_na_porta_6100():
    """Sem porta, o runserver do SGS usa a 6100 (o 00), como o tela_prompt.py — e aceita --sem-abrir."""
    ambiente = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    r = subprocess.run([sys.executable, "manage.py", "shell", "-c",
                        "from sgs_web.management.commands.runserver import Command as C; print(C.default_port)"],
                       cwd=tela.AQUI, env=ambiente, capture_output=True, text=True, timeout=60)
    assert r.stdout.strip().splitlines()[-1] == "6100", r.stderr          # (o shell do Django 6 avisa antes)
    ajuda = subprocess.run([sys.executable, "manage.py", "runserver", "--help"], cwd=tela.AQUI, env=ambiente,
                           capture_output=True, text=True, timeout=60).stdout
    assert "--sem-abrir" in ajuda


def test_runserver_do_sgs_dentro_da_propria_tela_nao_abre_outro(tmp_path):
    """Digitado DENTRO da tela (que marca o ambiente), o manage.py da tela recusa: um 2º SGS encerraria os sites
    do 1º e trocaria o config."""
    ambiente = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    ambiente.update({tela.MARCA_TELA: "6100", "SGS_CONFIG": str(tmp_path / "cfg.json"),
                     "SGS_SAIDA": str(tmp_path / "saida")})
    r = subprocess.run([sys.executable, "manage.py", "runserver", "--noreload", "--sem-abrir"], cwd=tela.AQUI,
                       env=ambiente, capture_output=True, text=True, timeout=60)
    assert r.returncode != 0 and "PRÓPRIA tela do SGS" in r.stderr and "cd NN" in r.stderr
    assert not (tmp_path / "cfg.json").exists()                            # nada foi preparado


def test_ao_abrir_sem_topo_nem_caixas(ctx):
    ctx.config.alterar("topo", True)
    ctx.config.alterar("rodape", True)
    ctx.config.alterar("pwa", False)
    tela.preparar_inicio(ctx)
    v = ctx.config.valores
    assert (v["visual"], v["pwa"], v["topo"], v["rodape"]) == ("cmd", True, False, False)
    assert all(v[caixa] for caixa in tela.OPCOES_CAIXA)                    # as caixas começam marcadas


def test_sgs_topo_e_sgs_foot_sao_sempre_as_duas_primeiras_sugestoes(ctx):
    for linha in ("sgs listar", "sgs tema", "sgs config"):                 # o histórico vem antes de tudo…
        rodar(ctx, linha)
    itens = tela.sugestoes(ctx)
    assert [i["cmd"] for i in itens[:2]] == ["sgs topo", "sgs foot"]     # …menos destas duas
    assert itens[0]["tipo"] == itens[1]["tipo"] == "fixo"


def test_janela_de_app_num_perfil_so_do_sgs():
    """Perfil próprio = sem extensões e sem o SGS instalado: a janela abre sem o ícone de extensão e sem o ⋮."""
    exe, url = "/mnt/c/chrome.exe", "http://127.0.0.1:6100/"
    linha = tela.comando_janela_app(exe, url, r"C:\Users\x\AppData\Local\SGS\navegador")
    assert linha[0] == exe and linha[-1] == f"--app={url}"
    assert r"--user-data-dir=C:\Users\x\AppData\Local\SGS\navegador" in linha and "--disable-extensions" in linha
    assert tela.comando_janela_app(exe, url, "") == [exe, f"--app={url}"]   # sem perfil: não mexe nas extensões
    assert tela.NAVEGADORES[0].endswith("chrome.exe")


@pytest.mark.parametrize("metodo, caminho, corpo, cabecalhos, esperado", [
    ("POST", "/comando", "linha=sgs", {"Content-Type": "application/x-www-form-urlencoded"}, 415),
    ("POST", "/comando", "{nao e json", {"Content-Type": "application/json"}, 400),
    ("GET", "/", None, {"Host": "site-malicioso.com"}, 403),
    ("GET", "/nada", None, None, 404),
])
def test_servidor_recusa(servidor, metodo, caminho, corpo, cabecalhos, esperado):
    assert pedir(servidor, metodo, caminho, corpo, cabecalhos)[0] == esperado

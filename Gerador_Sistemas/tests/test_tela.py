"""
Testes do SGS (tela_prompt.py + sgs_terminal.py + sgs_comand.py).

1) As regras são funções puras (processar, Config, numerar, executar_linha…): testadas direto.
2) O servidor é testado de verdade numa porta livre, com http.client — sem navegador e sem abrir janelas.
Tudo acontece em pastas temporárias (tmp_path): nada vai para sistemas_gerados/ nem para o sgs_config.json real.
"""
import http.client
import json
import re
import socket
import threading
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
    assert f"http://127.0.0.1:{porta}/" in textos(r)                       # porta 8100+NN (aqui: a livre)
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


def test_pagina_tem_as_duas_linhas_do_topo_e_o_terminal(servidor):
    status, tipo, html = pedir(servidor, "GET", "/")
    html = html.decode("utf-8")
    assert status == 200 and tipo.startswith("text/html")
    assert '<p class="banner">SGS - Sistema Gerador de Sistema</p>' in html
    principais = re.search(r"const PRINCIPAIS = (\[.*?\]);", html, re.S).group(1)
    assert '"sgs comand"' in principais and "pwa" not in principais       # pwa só na lista completa
    assert "exemplos" not in html.lower()                                 # sem exemplos na tela inicial
    assert 'id="cursor"' in html and 'rel="manifest"' in html and "serviceWorker" in html
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
    status, tipo, html = pedir(servidor, "GET", "/referencia")
    html = html.decode("utf-8")
    assert status == 200 and "oldid=" in html and "22/11/2026" in html and "Abstract Factory" in html


@pytest.mark.parametrize("metodo, caminho, corpo, cabecalhos, esperado", [
    ("POST", "/comando", "linha=sgs", {"Content-Type": "application/x-www-form-urlencoded"}, 415),
    ("POST", "/comando", "{nao e json", {"Content-Type": "application/json"}, 400),
    ("GET", "/", None, {"Host": "site-malicioso.com"}, 403),
    ("GET", "/nada", None, None, 404),
])
def test_servidor_recusa(servidor, metodo, caminho, corpo, cabecalhos, esperado):
    assert pedir(servidor, metodo, caminho, corpo, cabecalhos)[0] == esperado

"""Testes do PRÓPRIO gerador: cada domínio gera um sistema cujos testes passam, a saída é
determinística, a análise do assunto segue as regras, e o modo exercício (questionário)/spec/erros funcionam."""
import json
import os
import re
import subprocess
import sys

import pytest

import gerar_sistema as g


def rodar_pytest(pasta, **ambiente):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=pasta,
                       capture_output=True, text=True, env=dict(os.environ, **ambiente))
    return r.returncode, r.stdout[-800:]


def arquivos(pasta):
    return {str(p.relative_to(pasta)): p.read_bytes() for p in sorted(pasta.rglob("*")) if p.is_file()}


# ---------------------------------------------------------------- geração ponta a ponta
@pytest.mark.parametrize("dominio", list(g.DOMINIOS))
def test_todo_dominio_gera_um_sistema_cujos_testes_passam(tmp_path, dominio):
    destino, s = g.gerar(dominio=dominio, padroes=["todos"], saida=tmp_path)
    assert s.padroes == g.ORDEM_PADROES
    codigo, saida = rodar_pytest(destino)
    assert codigo == 0, saida


def test_camada_django_gerada_passa(tmp_path):
    pytest.importorskip("django")
    pytest.importorskip("pytest_django")
    destino, s = g.gerar(dominio="estacionamento", padroes=["mvvm"], django=True, saida=tmp_path)
    assert "strategy" in s.padroes                      # --django inclui o Strategy (o Service usa)
    codigo, saida = rodar_pytest(destino / "web")
    assert codigo == 0, saida


def test_saida_e_deterministica(tmp_path):
    a, _ = g.gerar(dominio="cinema", padroes=["todos"], django=True, saida=tmp_path / "a")
    b, _ = g.gerar(dominio="cinema", padroes=["todos"], django=True, saida=tmp_path / "b")
    assert arquivos(a) == arquivos(b)


def test_especificacao_salva_regenera_o_mesmo_sistema(tmp_path):
    a, _ = g.gerar(dominio="clinica", padroes=["strategy", "facade"], saida=tmp_path / "a")
    b, _ = g.gerar(spec=str(a / "especificacao.json"), saida=tmp_path / "b", nome=a.name)
    iguais = {k for k in arquivos(a) if k != "README.md"}
    assert {k: arquivos(a)[k] for k in iguais} == {k: arquivos(b)[k] for k in iguais}


# ---------------------------------------------------------------- análise do assunto (regras fixas)
def test_assunto_escolhe_dominio_e_padroes():
    r = g.analisar_assunto("Biblioteca onde a multa varia conforme o tipo de leitor e o pagamento usa um gateway de terceiro")
    assert r["dominio"] == "biblioteca"
    assert "strategy" in r["padroes"] and "adapter" in r["padroes"]


def test_frase_de_adapter_nao_conta_como_dominio():
    assert g.analisar_assunto("loja que integra uma biblioteca de pagamento externa")["dominio"] == "loja"


def test_assunto_sem_dominio_vira_generico_com_nome_extraido():
    r = g.analisar_assunto("sistema de observatório astronômico com extras opcionais")
    assert (r["dominio"], r["sistema"], r["padroes"]) == ("generico", "Observatório Astronômico", ["decorator"])


# ---------------------------------------------------------------- os 300 domínios (catalogo_100_dominios.txt)
def test_catalogo_tem_os_300_dominios_em_21_setores_e_o_101_da_prova():
    assert len(g.DOMINIOS) == 300
    assert [g.INFO_DOMINIOS[c]["id"] for c in g.DOMINIOS] == [f"{n:03d}" for n in range(1, 301)]
    assert len({i["setor"] for i in g.INFO_DOMINIOS.values()}) == 21
    assert g.INFO_DOMINIOS["citricultura"] == {"id": "101", "setor": "Prova Prática P3 (ISW-030)"}
    originais = {"hotel": "001", "cinema": "002", "clinica": "011", "academia": "012", "loja": "023",
                 "biblioteca": "045", "estacionamento": "055", "generico": "100"}
    assert {c: g.INFO_DOMINIOS[c]["id"] for c in originais} == originais
    assert len({d["sistema"].lower() for d in g.DOMINIOS.values()}) == 300
    for chave, d in g.DOMINIOS.items():
        esperado = 101 if chave == "citricultura" else 100
        assert len(d["palavras"]) == esperado and not any("_" in p for p in d["palavras"]), chave   # "_" vira frase


def test_os_8_dominios_originais_so_trocaram_as_palavras():
    import dominios
    for chave in ("hotel", "biblioteca", "loja", "generico"):
        atual = {k: v for k, v in g.DOMINIOS[chave].items() if k != "palavras"}
        assert chave not in dominios.DADOS and atual["atributos"] and atual["sistema"]
    assert "cafe manha" in g.DOMINIOS["hotel"]["palavras"]                           # cafe_manha → frase


@pytest.mark.parametrize("pedido, dominio", [
    ("sistema de pet shop com banho e tosa", "petshop"),
    ("oficina mecânica com ordem de serviço e troca de óleo", "oficina"),
    ("lava rápido com polimento e cera", "lava_rapido"),
    ("controle de rebanho de gado nelore", "pecuaria"),
    ("casa de eventos com buffet e decoração", "eventos"),
    ("vacina e castração na clínica veterinária", "veterinaria"),
    ("cartório com certidão de nascimento e reconhecimento de firma", "cartorio"),
    ("hemocentro com doação de sangue e tipagem", "hemocentro"),
    ("sistema de cadastro de clientes com relatório", "generico"),       # só palavras genéricas
])
def test_dominio_por_pontos(pedido, dominio):
    assert g.analisar_assunto(pedido)["dominio"] == dominio


def test_nome_do_dominio_vale_mais_3_pontos():
    pontos = {c: p for p, c, _ in g.pontuar_dominios(g.normalizar("lava rapido"))}
    assert pontos["lava_rapido"] == 1 + g.BONUS_NOME                    # a palavra "lava rapido" + o nome


def test_empate_e_deterministico_pela_ordem_do_catalogo():
    ranking = g.pontuar_dominios(g.normalizar("poltrona"))               # cinema (002) e teatro (005): 1 ponto
    assert [c for _, c, _ in ranking[:2]] == ["cinema", "teatro"]
    assert g.analisar_assunto("poltrona")["dominio"] == "cinema"
    assert "generico" not in [c for _, c, _ in g.pontuar_dominios(g.normalizar("sistema de cadastro"))]


def test_filtrar_dominios_por_termo():
    saude = {c for c, *_ in g.filtrar_dominios("saude")}
    assert {"clinica", "hospital", "hemocentro", "transporte_saude"} <= saude and "cinema" not in saude
    assert {c for c, *_ in g.filtrar_dominios("045")} == {"biblioteca"}
    assert len(g.filtrar_dominios()) == 300 and g.filtrar_dominios("zzzz") == []


# ---------------------------------------------------------------- domínio 101: o perfil da Prova Prática P3
def test_dominio_101_vem_do_arquivo_da_prova_sem_alteracao():
    linha = (g.AQUI / "ProvaPraticaP3" / "domínio 101.txt").read_text(encoding="utf-8").strip()
    _, chave, sistema, entidade, palavras = (p.strip() for p in linha.split("|"))
    d = g.DOMINIOS["citricultura"]
    assert (chave, d["sistema"], d["entidade"]) == ("citricultura", sistema, entidade)
    assert d["palavras"] == [p.strip().replace("_", " ") for p in palavras.split(",")]       # as 101 palavras
    assert len(d["palavras"]) == 101
    assert g.montar_spec(assunto="cooperativa de citros: entrega de laranja na safra").dados["sistema"] == sistema


def test_perfil_da_prova_p3_pasta_projeto_app_rotas_drf_e_pytest(tmp_path):
    """O sistema do domínio 101 sai como no guia da prova: pasta provaP3 (relativa, em sistemas_gerados),
    projeto cooperativa, app citricultura, rotas /citricultura/, DRF em /api/ e o pytest.ini do guia."""
    destino, s = g.gerar(dominio="citricultura", padroes=["prova"], django=True, saida=tmp_path)
    assert destino == tmp_path / "provaP3" and (s.projeto, s.app, s.rota, s.drf) == ("cooperativa", "citricultura",
                                                                                     "citricultura/", True)
    web = destino / "web"
    for arquivo in ("cooperativa/settings.py", "cooperativa/urls.py", "cooperativa/wsgi.py", "citricultura/models.py",
                    "citricultura/serializers.py", "citricultura/api_drf.py", "citricultura/tests/test_drf.py"):
        assert (web / arquivo).exists(), arquivo
    assert not (web / "config").exists()
    ini = (web / "pytest.ini").read_text(encoding="utf-8")
    assert "DJANGO_SETTINGS_MODULE = cooperativa.settings" in ini and "python_files = tests.py test_*.py" in ini
    settings = (web / "cooperativa" / "settings.py").read_text(encoding="utf-8")
    assert '"rest_framework",' in settings and '"citricultura",' in settings and 'ROOT_URLCONF = "cooperativa.urls"' in settings
    urls = (web / "cooperativa" / "urls.py").read_text(encoding="utf-8")
    assert 'path("api/", include("citricultura.api_drf"))' in urls and 'path("citricultura/", include(' in urls
    assert 'RedirectView.as_view(url="/citricultura/"' in urls
    assert "djangorestframework>=" in (destino / "requirements.txt").read_text(encoding="utf-8")
    assert "Prova Prática P3" in (destino / "README.md").read_text(encoding="utf-8")
    assert json.loads((destino / "especificacao.json").read_text(encoding="utf-8"))["perfil"]["pasta"] == "provaP3"
    textos = "".join(p.read_text(encoding="utf-8") for p in destino.rglob("*") if p.suffix in (".py", ".ini", ".sh"))
    assert not re.search(r"\bconfig[./](settings|urls|wsgi|env)\b", textos)          # nada ficou com o nome antigo
    with pytest.raises(g.ErroGerador, match="não substituo"):                          # a pasta de trabalho fica
        g.gerar(dominio="citricultura", padroes=["prova"], django=True, saida=tmp_path)
    assert g.gerar(dominio="citricultura", padroes=["prova"], django=True, saida=tmp_path, regerar_fixa=True)[0] == destino
    assert g.pacote_do_projeto(destino) == "cooperativa"
    assert {e["rota"] for e in g.endpoints_do_projeto(destino)} == {"/citricultura/api/v1/", "/citricultura/api/"}
    codigo, saida = rodar_pytest(web)                                                   # inclusive os testes do DRF
    assert codigo == 0, saida


def test_sem_perfil_continua_igual_config_e_app_na_raiz(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    assert (s.projeto, s.rota, s.drf, s.pasta) == ("config", "", False, None)
    urls = (destino / "web" / "config" / "urls.py").read_text(encoding="utf-8")
    assert 'path("", include("reservas.urls")),' in urls and "RedirectView" not in urls and "api_drf" not in urls
    assert "import include, path\n\nfrom . import pwa" in urls
    assert "rest_framework" not in (destino / "web" / "config" / "settings.py").read_text(encoding="utf-8")
    assert "python_files = test_*.py" in (destino / "web" / "pytest.ini").read_text(encoding="utf-8")


def test_listar_agrupa_por_setor_e_filtra(capsys):
    assert g.principal(["--listar", "pet"]) == 0
    saida = capsys.readouterr().out
    assert "[Serviços Pessoais, Pets e Estética]" in saida and "petshop" in saida and "PADRÕES" not in saida


@pytest.mark.parametrize("dominio", ["parque", "hemocentro", "construcao", "acougue", "merenda", "transporte_saude",
                                     "cemiterio", "petshop", "rh", "fazenda"])
def test_um_dominio_novo_por_setor_com_django_passa(tmp_path, dominio):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio=dominio, padroes=["prova"], django=True, saida=tmp_path, web={"estilo": "web"})
    assert re.fullmatch(r"[a-z0-9_]+", destino.name)
    for pasta in (destino, destino / "web"):
        codigo, saida = rodar_pytest(pasta)
        assert codigo == 0, saida


def test_nome_com_e_comercial_e_escapado_no_html(tmp_path):
    destino, s = g.gerar(dominio="construcao", padroes=["strategy"], django=True, saida=tmp_path,
                         web={"estilo": "bootstrap"})
    assert s.sistema == "Casa & Obra" and destino.name.startswith("casa_obra__")
    base = (destino / "web" / s.app / "templates" / s.app / "base.html").read_text(encoding="utf-8")
    assert "Casa &amp; Obra" in base and "Casa & Obra" not in base


@pytest.mark.skipif(not os.environ.get("SGS_TESTE_COMPLETO"), reason="lento: SGS_TESTE_COMPLETO=1 testa os 100 com Django")
@pytest.mark.parametrize("dominio", list(g.DOMINIOS))
def test_todos_os_100_com_django_e_todos_os_padroes(tmp_path, dominio):
    destino, _ = g.gerar(dominio=dominio, padroes=["todos"], django=True, saida=tmp_path)
    for pasta in (destino, destino / "web"):
        codigo, saida = rodar_pytest(pasta)
        assert codigo == 0, saida


def test_assunto_sem_padrao_reconhecido_gera_os_da_prova(tmp_path):
    destino, s = g.gerar(assunto="um sistema de hotel", saida=tmp_path)
    assert s.padroes == [p for p in g.ORDEM_PADROES if p in g.PROVA] and s.origem.get("sem_padrao")
    assert destino.name == "hotel_resort__prova"


def test_padroes_por_apelido_e_ordem_canonica():
    assert g.normalizar_padroes(["decorador, fachada"]) == ["encapsulamento", "decorator", "facade"]
    assert g.normalizar_padroes(["factory-method", "observador"]) == ["encapsulamento", "factory_method", "observer"]


# ---------------------------------------------------------------- catálogo GoF (referência: Wikipédia)
def test_os_23_padroes_gof_por_categoria():
    assert [len(g.CATEGORIAS[c]) for c in ("criacao", "estrutural", "comportamental")] == [5, 7, 11]
    assert len(g.GOF) == len(set(g.GOF)) == 23 and len(g.ORDEM_PADROES) == 28
    for p in g.ORDEM_PADROES:
        assert p in g.PADROES and g.PADROES[p]["tripe"]
        assert p == "encapsulamento" or p in g.GERADORES
    assert (g.Path(g.__file__).parent / g.REFERENCIA_GOF).exists()


@pytest.mark.parametrize("grupo, esperado", [("criacao", g.CATEGORIAS["criacao"]), ("estruturais", g.CATEGORIAS["estrutural"]),
                                              ("comportamental", g.CATEGORIAS["comportamental"]), ("gof", g.GOF)])
def test_grupo_expande_para_os_padroes(grupo, esperado):
    assert g.normalizar_padroes([grupo]) == ["encapsulamento"] + esperado


def test_assunto_pede_um_grupo_inteiro():
    r = g.analisar_assunto("clínica com todos os padrões de criação")
    assert r["dominio"] == "clinica" and r["padroes"] == g.CATEGORIAS["criacao"]


def test_nome_da_pasta_usa_o_grupo(tmp_path):
    assert g.gerar(dominio="hotel", padroes=["gof"], saida=tmp_path)[0].name == "hotel_resort__gof"
    assert g.gerar(dominio="hotel", padroes=["criacao"], django=True, saida=tmp_path)[0].name == \
        "hotel_resort__criacao_strategy_web"                         # o --django inclui o Strategy
    assert g.gerar(dominio="hotel", padroes=["criacao", "bridge"], saida=tmp_path)[0].name == "hotel_resort__criacao_bridge"
    longo = g.gerar(dominio="hotel", padroes=["singleton", "factory_method", "abstract_factory", "builder",
                                               "bridge", "composite", "flyweight"], saida=tmp_path)[0].name
    assert longo.startswith("hotel_resort__8padroes_") and len(longo) < 50


@pytest.mark.parametrize("web", [{"estilo": "web", "tema": "T10", "tom": "tom3"}, {"estilo": "cmd"}, {"estilo": "bootstrap"}])
def test_nome_da_pasta_so_tem_letras_numeros_e_sublinhado(tmp_path, web):
    nome = g.gerar(dominio="generico", sistema="Pet Shop+", padroes=["prova", "state"], django=True, exercicio=True,
                   saida=tmp_path, web=web)[0].name
    assert re.fullmatch(r"[a-z0-9_]+", nome), nome


# ---------------------------------------------------------------- modos: só gerar · apenas o código
def test_so_gerar_tira_o_material_de_estudo_e_continua_passando(tmp_path):
    destino, s = g.gerar(dominio="academia", padroes=["comportamental", "prova"], estudo=False, saida=tmp_path)
    assert destino.name.endswith("_direto")
    assert not list(destino.rglob("antes_*.py")) and not (destino / "docs").exists()
    assert "Roteiro de estudo" not in (destino / "README.md").read_text(encoding="utf-8")
    codigo, saida = rodar_pytest(destino)
    assert codigo == 0, saida


def test_sem_comentarios_tira_comentarios_e_docstrings(tmp_path):
    destino, _ = g.gerar(dominio="cinema", padroes=["todos"], comentarios=False, saida=tmp_path)
    for arquivo in destino.rglob("*.py"):
        codigo = arquivo.read_text(encoding="utf-8")
        assert not any(linha.lstrip().startswith("#") for linha in codigo.splitlines()), arquivo
        arvore = g.ast.parse(codigo)
        for no in g.ast.walk(arvore):
            if isinstance(no, (g.ast.Module, g.ast.ClassDef, g.ast.FunctionDef)):
                assert g.ast.get_docstring(no) is None, arquivo
    codigo, saida = rodar_pytest(destino)
    assert codigo == 0, saida


def test_remover_comentarios_nao_muda_o_codigo():
    original = ('"""Módulo."""\nimport os  # sistema\n\n\nclass A:\n    """Classe."""\n\n    def f(self):\n'
                '        """Só docstring."""\n\n    def g(self):\n        # explica\n        return "# não é comentário"\n')
    limpo = g.remover_comentarios(original)
    assert "Módulo" not in limpo and "explica" not in limpo and "# não é comentário" in limpo
    assert "        pass" in limpo
    assert limpo.startswith("import os\n")


def test_remover_referencias_antes_em_cadeia():
    teste = ("import pytest\n\nfrom nucleo.antes_x import Velho\nfrom nucleo.x import Novo\n\n\n"
             "def ajuda():\n    return Velho()\n\n\ndef test_usa_ajuda():\n    assert ajuda()\n\n\n"
             "def test_so_novo():\n    assert Novo()\n")
    limpo = g.remover_referencias_antes(teste)
    assert "Velho" not in limpo and "test_usa_ajuda" not in limpo and "test_so_novo" in limpo


def test_django_sai_pronto_para_rodar(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    assert (destino / "iniciar.sh").stat().st_mode & 0o111            # executável
    exemplo = (destino / "web" / ".env.example").read_text(encoding="utf-8")
    assert "DJANGO_SUPERUSER_USERNAME=" in exemplo and "SECRET_KEY=" in exemplo
    assert (destino / "web" / s.app / "management" / "commands" / "garantir_admin.py").exists()
    assert "Django>=" in (destino / "requirements.txt").read_text(encoding="utf-8")
    assert "web/.env" in (destino / ".gitignore").read_text(encoding="utf-8")


def test_requirements_tem_o_python_o_django_os_testes_e_os_pontuais():
    """O requirements.txt de cada sistema: o Python exigido (cabeçalho), o Django e o que ele usa, os testes e as
    dependências PONTUAIS deste sistema (pelas opções escolhidas) — cada linha com o porquê."""
    baseline = g.montar_arquivos(g.montar_spec(dominio="hotel", django=True, web={"seguranca": "baseline"}), "x")
    req = baseline["requirements.txt"]
    assert "# Python: 3.12 ou mais novo" in req and "python3 --version" in req
    for linha in ("Django>=6.0,<7.0", "asgiref>=3.9.1", "sqlparse>=0.5.0", 'tzdata; sys_platform == "win32"',
                  "pytest>=8.0", "pytest-django>=4.9", "argon2-cffi>=23.1"):
        assert re.search(rf"^{re.escape(linha)} +# \S", req, re.M), linha           # cada uma com o porquê
    assert req.index("# --- deste sistema ---") < req.index("argon2-cffi")
    basica = g.montar_arquivos(g.montar_spec(dominio="biblioteca", django=True), "x")["requirements.txt"]
    assert "argon2" not in basica and "nenhuma a mais" in basica               # pontual só quando a opção pede
    nucleo = g.montar_arquivos(g.montar_spec(dominio="academia"), "x")["requirements.txt"]
    assert "Django" not in nucleo and "pytest>=8.0" in nucleo and "pytest-django" not in nucleo
    iniciar = baseline["iniciar.sh"]
    assert "sys.version_info < (3, 12)" in iniciar                             # confere o Python antes do .venv
    assert "--no-index" in iniciar and 'import django, pytest, pytest_django' not in iniciar   # confere TODAS


@pytest.mark.parametrize("django", [False, True])
def test_gitignore_tem_o_minimo_das_instrucoes_django(tmp_path, django):
    destino, _ = g.gerar(dominio="hotel", padroes=["strategy"], django=django, saida=tmp_path)
    linhas = (destino / ".gitignore").read_text(encoding="utf-8").splitlines()
    minimo = [".venv/", ".env", "*.pyc", "__pycache__/", "*.log", ".DS_Store", "media/", "staticfiles/"]  # §4.7
    assert all(item in linhas for item in minimo + ["db.sqlite3", "*Zone.Identifier", "!.env.example"])
    assert ("web/.env" in linhas) is django


# ---------------------------------------------------------------- camada web: estilos, temas e Instruções Django
@pytest.mark.parametrize("dominio, web", [
    ("loja", {"estilo": "cmd", "comentarios_web": True}),
    ("clinica", {"estilo": "web", "tema": "T09", "tom": "escuro", "id_publico": "uuid"}),
    ("cinema", {"estilo": "bootstrap", "id_interno": True, "lnnl_tipo": "35", "estrutura": "apps", "seguranca": "baseline"}),
])
def test_opcoes_web_geram_django_que_passa(tmp_path, dominio, web):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio=dominio, padroes=["strategy"], django=True, saida=tmp_path, web=web)
    codigo, saida = rodar_pytest(destino / "web")
    assert codigo == 0, saida
    assert json.loads((destino / "especificacao.json").read_text(encoding="utf-8"))["web"] == s.web


def test_modo_exercicio_com_django_poe_o_questionario_no_site(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="generico", sistema="Petshop", padroes=["prova", "state"], django=True,
                         exercicio=True, saida=tmp_path, web={"estilo": "web", "tema": "T10", "estrutura": "apps"})
    assert "TODO" not in (destino / "nucleo" / "politicas.py").read_text(encoding="utf-8")   # código completo
    assert not (destino / "gabarito").exists() and not (destino / "conftest.py").exists()
    app = destino / "web" / "apps" / s.app
    assert (app / "templates" / s.app / "exercicios.html").exists() and (app / "tests" / "test_exercicios.py").exists()
    assert 'name="exercicios"' in (app / "urls.py").read_text(encoding="utf-8")
    codigo, saida = rodar_pytest(destino / "web")                     # inclui o teste da página /exercicios/
    assert codigo == 0, saida


def test_estrutura_apps_e_lnnl(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path,
                         web={"estrutura": "apps", "id_interno": True})
    app = destino / "web" / "apps" / s.app
    assert (app / "README.md").exists() and (destino / "web" / "apps" / "__init__.py").exists()
    assert 'name = "apps.reservas"' in (app / "apps.py").read_text(encoding="utf-8")
    assert (app / "lnnl.py").read_bytes() == g.MOTOR_LNNL.read_bytes()              # cópia fiel do motor
    assert not (destino / "web" / s.app).exists()


# ---------------------------------------------------------------- API REST e módulos (apps a mais: sgs app)
def test_toda_app_django_tem_api_rest_e_settings_da_app(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    app = destino / "web" / s.app
    urls = (app / "urls.py").read_text(encoding="utf-8")
    assert 'path("api/v1/", api.colecao' in urls and 'path("api/v1/<int:pk>/", api.item' in urls
    assert '"API_LIMITE"' in (app / "settings.py").read_text(encoding="utf-8")
    api = (app / "api.py").read_text(encoding="utf-8")
    assert "csrf_exempt" not in api and "ReservaForm(para_form(dados)" in api     # o MESMO form valida a API
    assert "enforce_csrf_checks=True" in (app / "tests" / "test_api.py").read_text(encoding="utf-8")
    assert "RESERVAS_API_ESCRITA=False" in (app / "tests" / "test_api.py").read_text(encoding="utf-8")
    assert 'path("api/v1/campos/", api.campos' in urls and 'path("api/", api.resumo' in urls      # campos por endpoint
    assert '"API_CAMPOS": {}' in (app / "settings.py").read_text(encoding="utf-8") and "?campos=" in api


def test_modulo_entra_no_projeto_e_tudo_passa(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    pasta, plano = g.gerar_modulo(destino, "estacionamento com estados da vaga e relatorio")
    m = plano["modulo"]
    assert pasta == destino / "web" / m["app"] and m["pacote"] == m["app"] and "strategy" in m["padroes"]
    assert (pasta / "nucleo" / "politicas.py").exists() and (pasta / "tests" / "nucleo" / "fabrica.py").exists()
    assert not any(re.search(r"^\s*(from|import) (nucleo|tests\.fabrica)\b", p.read_text(encoding="utf-8"), re.M)
                   for p in pasta.rglob("*.py"))                       # o núcleo do módulo mora DENTRO da app
    assert [x["app"] for x in g.ler_modulos(destino)] == [m["app"]]
    rotas = (destino / "web" / "config" / "urls.py").read_text(encoding="utf-8")
    assert rotas.index(f'path("{m["app"]}/"') < rotas.index('path("", include(')   # antes da raiz
    assert f"makemigrations {s.app} {m['app']}" in (destino / "iniciar.sh").read_text(encoding="utf-8")
    assert rodar_pytest(destino)[0] == 0                              # o núcleo do projeto continua passando
    codigo, saida = rodar_pytest(destino / "web")                      # telas + API + núcleo dos DOIS
    assert codigo == 0, saida


def test_modulo_em_estrutura_apps_uuid_e_sem_comentarios(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="cinema", padroes=["prova"], django=True, saida=tmp_path, comentarios=False,
                         web={"estrutura": "apps", "id_publico": "uuid"})
    pasta, plano = g.gerar_modulo(destino, "biblioteca com multa por tipo de leitor", entidade="Emprestimo")
    assert plano["modulo"]["pacote"] == "apps.emprestimos" and pasta == destino / "web" / "apps" / "emprestimos"
    assert '"apps.emprestimos",' in (destino / "web" / "config" / "settings.py").read_text(encoding="utf-8")
    codigo, saida = rodar_pytest(destino / "web")
    assert codigo == 0, saida


def test_modulo_com_nome_repetido_reservado_ou_sem_django_explica(tmp_path):
    destino, _ = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    with pytest.raises(g.ErroGerador, match="entidade=Nome"):
        g.preparar_modulo(destino, "hotel com reserva", entidade="Reserva")   # Reserva já é a app principal
    with pytest.raises(g.ErroGerador, match="reservado"):
        g.preparar_modulo(destino, "estoque", entidade="App")         # app "apps" (a pasta das apps)
    sem_django, _ = g.gerar(dominio="cinema", padroes=["strategy"], saida=tmp_path)
    with pytest.raises(g.ErroGerador, match="Django"):
        g.preparar_modulo(sem_django, "estoque")
    assert g.ler_modulos(destino) == []                                # planejar não escreve nada


@pytest.mark.parametrize("pedido, nome", [("destinos de viagem", "Destino"), ("cadastro de horários de voos", "Horario"),
                                          ("controle de opções", "Opcao"), ("hotéis", "Hotel"), ("de da do", None)])
def test_nome_da_funcionalidade_vem_do_contexto_do_pedido(pedido, nome):
    assert g.nome_do_pedido(pedido) == nome


def test_ligar_classes_poe_a_referencia_no_form_na_api_e_nos_testes(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path, web={"id_publico": "uuid"})
    g.gerar_modulo(destino, "destinos de viagem com os campos cidade e pais")
    lig = g.ligar_classes(destino, "reserva", None, "destino")         # sem campo: o nome vem do alvo
    assert (lig["origem"], lig["campo"], lig["alvo"]) == ("Reserva", "destino", "Destino")
    app = destino / "web" / s.app
    assert 'destino = models.ForeignKey("destinos.Destino"' in (app / "models.py").read_text(encoding="utf-8")
    assert '"destino", "tipo"]' in (app / "forms.py").read_text(encoding="utf-8")
    assert (app / "tests" / "test_ligacao_destino.py").exists() and g.ler_ligacoes(destino)[0]["campo"] == "destino"
    with pytest.raises(g.ErroGerador, match="já tem um campo"):
        g.ligar_classes(destino, "Reserva", "destino", "Destino")
    with pytest.raises(g.ErroGerador, match="não existe a classe"):
        g.planejar_ligacao(destino, "Reserva", "voo", "Voo")
    codigo, saida = rodar_pytest(destino / "web")                     # inclui o test_ligacao_destino.py
    assert codigo == 0, saida


# ---------------------------------------------------------------- incrementar/modificar um campo (sgs incrementar)
@pytest.mark.parametrize("texto, esperado", [
    ("inteiro>=0", {"tipo": "int", "regra": "minimo", "min": 0}),
    ("inteiro:1..30", {"tipo": "int", "regra": "faixa", "min": 1, "max": 30}),
    ("decimal>=0", {"tipo": "float", "regra": "minimo", "min": 0.0}),
    ("lista:Janela, Meio, Corredor", {"tipo": "str", "regra": "lista", "opcoes": ["Janela", "Meio", "Corredor"]}),
    ("lista:1,2,3", {"tipo": "int", "regra": "lista", "opcoes": [1, 2, 3]}),
    ("multipla:urgente,vip,recorrente", {"tipo": "str", "regra": "multipla", "opcoes": ["urgente", "vip", "recorrente"]}),
    ("texto", {"tipo": "str", "regra": "obrigatorio"}),
    ("texto-livre", {"tipo": "str", "regra": "livre"}),
    ("texto-longo", {"tipo": "str", "regra": "texto_longo"}),
    ("simnão", {"tipo": "bool"}), ("booleano", {"tipo": "bool"}),
    ("data", {"tipo": "data"}),
    ("data-hora", {"tipo": "data_hora", "regra": "obrigatorio"}),
    ("moeda", {"tipo": "float", "regra": "moeda", "min": 0}),
    ("email", {"tipo": "str", "regra": "email"}),
    ("telefone", {"tipo": "str", "regra": "telefone"}),
    ("url", {"tipo": "str", "regra": "url"}),
    ("cpf", {"tipo": "str", "regra": "cpf"}),
    ("cnpj", {"tipo": "str", "regra": "cnpj"}),
    ("cep", {"tipo": "str", "regra": "cep"}),
    ("arquivo", {"tipo": "str", "regra": "arquivo"}),
    ("imagem", {"tipo": "str", "regra": "imagem"}),
    ("geolocalizacao", {"tipo": "str", "regra": "geolocalizacao"}),
    ("json", {"tipo": "json", "regra": "obrigatorio"}),
])
def test_ler_regra_do_campo(texto, esperado):
    regra = g.ler_regra(texto)
    assert {k: regra.get(k) for k in esperado} == esperado
    assert g.ler_regra(g.regra_em_texto({"nome": "x", **regra})) == regra       # ida e volta


@pytest.mark.parametrize("texto", ["qualquer", "inteiro:5..1", "lista:so_um", "lista:a,a", "multipla:unico", "multipla:a,a"])
def test_regra_do_campo_invalida_explica(texto):
    with pytest.raises(g.ErroGerador):
        g.ler_regra(texto)


def test_incrementar_todos_novos_tipos_categorizados_e_tudo_passa(tmp_path):
    """Todos os tipos categorizados (Primitivos, Seleção, Negócio e Estruturados) funcionam fim a fim no núcleo e Django."""
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    novos_campos = [
        ("descricao_longa", "texto-longo"),
        ("agendado_em", "data-hora"),
        ("etiquetas", "multipla:urgente,vip,recorrente"),
        ("taxa_servico", "moeda"),
        ("email_contato", "email"),
        ("telefone_contato", "telefone"),
        ("site_referencia", "url"),
        ("cpf_hospede", "cpf"),
        ("cnpj_empresa", "cnpj"),
        ("cep_endereco", "cep"),
        ("comprovante", "arquivo"),
        ("foto_quarto", "imagem"),
        ("coordenadas", "geolocalizacao"),
        ("metadados", "json"),
    ]
    for campo, regra in novos_campos:
        res = g.incrementar_campo(destino, "Reserva", campo, regra)
        assert res["acao"] == "novo", (campo, regra)
    modelo = (destino / "web" / s.app / "models.py").read_text(encoding="utf-8")
    for trecho in ("models.TextField", "models.DateTimeField", "models.EmailField", "models.URLField",
                   "models.JSONField", "validar_cpf", "validar_cnpj", "validar_cep", "validar_telefone",
                   "validar_arquivo", "validar_imagem", "validar_geolocalizacao", "validar_multipla_etiquetas"):
        assert trecho in modelo, trecho
    forms_txt = (destino / "web" / s.app / "forms.py").read_text(encoding="utf-8")
    assert 'datetime-local' in forms_txt and 'Textarea' in forms_txt
    cod_nucleo, out_nucleo = rodar_pytest(destino)
    assert cod_nucleo == 0, out_nucleo
    cod_web, out_web = rodar_pytest(destino / "web")
    assert cod_web == 0, out_web


def test_gerar_com_infra_seguranca_e_bibliotecas_tudo_passa(tmp_path):
    """Passo 2 completo: UUIDv4, LNNL, apps/, baseline, PostgreSQL, Redis, Argon2id, Fernet, 2FA, RBAC, Anti-Bot, Rate Limit, Anymail, TinyMCE."""
    pytest.importorskip("django")
    web_opts = {
        "estilo": "web", "tema": "T03", "tom": "tom3",
        "id_publico": "uuid", "id_interno": True, "lnnl_tipo": "24",
        "estrutura": "apps", "seguranca": "baseline",
        "banco": "postgresql", "redis": True, "argon2": True, "fernet": True,
        "two_factor": True, "two_factor_expiracao": 15, "recuperacao_senha": True,
        "rbac": True, "antibot": True, "ratelimit": True, "anymail": True, "tinymce": True,
    }
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, web=web_opts, saida=tmp_path)
    reqs = (destino / "requirements.txt").read_text(encoding="utf-8")
    for pct in ("psycopg[binary]", "django-redis", "argon2-cffi", "cryptography", "pyotp",
                "django-ratelimit", "django-anymail", "django-tinymce"):
        assert pct in reqs, pct
    env_ex = (destino / "web" / ".env.example").read_text(encoding="utf-8")
    for var in ("DB_HOST=", "REDIS_URL=", "FERNET_KEY=", "TWO_FACTOR_EXPIRACAO_MIN=15",
                "ANYMAIL_API_KEY=", "ANTIBOT_PROVIDER=", "RATELIMIT_ENABLE="):
        assert var in env_ex, var
    for mod in ("crypto.py", "twofactor.py", "rbac.py", "antibot.py", "ratelimit.py"):
        assert (destino / "web" / "config" / mod).is_file(), mod
    assert (destino / "web" / "apps" / s.app / "tests" / "test_infra_seguranca.py").is_file()
    cod_nucleo, out_nucleo = rodar_pytest(destino)
    assert cod_nucleo == 0, out_nucleo
    cod_web, out_web = rodar_pytest(destino / "web")
    assert cod_web == 0, out_web

    # MongoDB + validações de erro
    destino_m, _ = g.gerar(dominio="cinema", padroes=["strategy"], django=True,
                           web={"banco": "mongodb"}, saida=tmp_path)
    assert "django-mongodb-backend" in (destino_m / "requirements.txt").read_text(encoding="utf-8")
    with pytest.raises(g.ErroGerador):
        g.normalizar_web({"banco": "oracle"})
    with pytest.raises(g.ErroGerador):
        g.normalizar_web({"two_factor_expiracao": 99})


def test_incrementar_modifica_e_acrescenta_campos_e_tudo_passa(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="hotel", padroes=["strategy", "state"], django=True, saida=tmp_path)
    modificado = g.incrementar_campo(destino, "Reserva", "quarto", "lista:101,102,103")
    novo = g.incrementar_campo(destino, "reserva", "assento", "lista:janela,corredor")
    assert (modificado["acao"], novo["acao"]) == ("modificado", "novo")
    entidades = (destino / "nucleo" / "entidades.py").read_text(encoding="utf-8")
    assert "if valor not in (101, 102, 103,):" in entidades and "def assento(self, valor):" in entidades  # @property
    modelo = (destino / "web" / s.app / "models.py").read_text(encoding="utf-8")
    assert "choices=[(101, '101')" in modelo and "default='janela'" in modelo       # default: linhas antigas
    espec = json.loads((destino / "especificacao.json").read_text(encoding="utf-8"))
    assert [a["nome"] for a in espec["atributos"]].index("assento") < [a["nome"] for a in espec["atributos"]].index("observacao")
    assert [x["campo"] for x in json.loads((destino / "incrementos.json").read_text(encoding="utf-8"))] == ["quarto", "assento"]
    assert rodar_pytest(destino)[0] == 0                              # núcleo: o setter recusa o que sai da lista
    codigo, saida = rodar_pytest(destino / "web")                      # Django: choices no model e no form
    assert codigo == 0, saida


def test_incrementar_campo_de_um_modulo_e_preservar_a_ligacao(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path)
    g.gerar_modulo(destino, "destinos de viagem com os campos cidade e pais")
    g.ligar_classes(destino, "Reserva", "destino", "Destino")
    g.incrementar_campo(destino, "Destino", "cidade", "lista:Paris,Roma,Lisboa")
    g.incrementar_campo(destino, "Reserva", "diarias", "inteiro:1..10")           # a Reserva é refeita…
    assert 'destino = models.ForeignKey("destinos.Destino"' in \
        (destino / "web" / s.app / "models.py").read_text(encoding="utf-8")      # …e a ligação volta
    assert any(a.get("opcoes") == ["Paris", "Roma", "Lisboa"] for a in g.ler_modulos(destino)[0]["atributos"])
    codigo, saida = rodar_pytest(destino / "web")
    assert codigo == 0, saida


def test_refazer_a_classe_sem_mudar_a_regra_da_os_mesmos_arquivos(tmp_path):
    """Determinístico: refazer a classe com a MESMA regra gera exatamente os arquivos que já estão no disco."""
    destino, s = g.gerar(dominio="cinema", padroes=["prova"], django=True, saida=tmp_path)
    plano = g.planejar_incremento(destino, s.ent, s.ident, "texto")
    diferentes = [c for c, conteudo in plano["arquivos"].items()
                  if (destino / c).read_bytes() != (conteudo if isinstance(conteudo, bytes) else conteudo.encode())]
    assert plano["acao"] == "modificado" and diferentes == []


def test_incrementar_explica_o_que_nao_pode(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], saida=tmp_path)       # sem Django: só o núcleo
    with pytest.raises(g.ErroGerador, match="não fecha"):
        g.planejar_incremento(destino, "Reserva", "diarias", "decimal>=0")           # a quantidade é inteira
    with pytest.raises(g.ErroGerador, match="não existe a classe"):
        g.planejar_incremento(destino, "Voo", "x", "texto")
    with pytest.raises(g.ErroGerador, match="não reconhecida"):
        g.planejar_incremento(destino, "Reserva", "x", "qualquer")
    g.incrementar_campo(destino, "Reserva", "quarto", "inteiro>=0")               # sistema sem Django também
    assert "if valor < 0:" in (destino / "nucleo" / "entidades.py").read_text(encoding="utf-8")
    assert rodar_pytest(destino)[0] == 0


def test_bootstrap_vem_de_dentro_do_projeto(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path, web={"estilo": "web"})
    vendor = destino / "web" / s.app / "static" / s.app / "vendor" / "bootstrap"
    assert (vendor / "bootstrap.min.css").read_bytes() == (g.BOOTSTRAP / "bootstrap.min.css").read_bytes()
    assert "--sgs-destaque" in (destino / "web" / s.app / "static" / s.app / "css" / "tema.css").read_text(encoding="utf-8")


def test_saida_com_binarios_e_deterministica(tmp_path):
    web = {"estilo": "web", "tema": "T10", "paleta": "P13", "id_interno": True, "comentarios_web": True}
    a, _ = g.gerar(dominio="loja", padroes=["strategy"], django=True, saida=tmp_path / "a", web=web)
    b, _ = g.gerar(dominio="loja", padroes=["strategy"], django=True, saida=tmp_path / "b", web=web)
    assert arquivos(a) == arquivos(b)


def test_temas_passam_no_contraste_wcag():
    import temas_web
    for tema in temas_web.TEMAS:
        for tom in temas_web.TONS:
            for paleta in (temas_web.PALETAS if tema == "T10" else ["P02"]):
                t = temas_web.resolver(tema, tom, paleta)
                minimo_escrita, minimo_destaque = (7.0, 4.5) if t["acessivel"] else (4.5, 3.0)
                assert t["contraste_escrita"] >= minimo_escrita and t["contraste_destaque"] >= minimo_destaque, (tema, tom)
    assert temas_web.resolver("T09", "escuro")["contraste_destaque"] == 7.54          # o valor citado em temas/


@pytest.mark.parametrize("web", [{"estilo": "neon"}, {"tema": "T11"}, {"tom": "medio"}, {"paleta": "P99"},
                                 {"lnnl_tipo": "93"}, {"lnnl_tipo": "10"}, {"cor": "#fff"}])
def test_opcao_web_invalida(tmp_path, web):
    with pytest.raises(g.ErroGerador):
        g.gerar(dominio="hotel", padroes=["strategy"], django=True, saida=tmp_path, web=web)


# ---------------------------------------------------------------- erros e segurança
def test_padrao_desconhecido():
    with pytest.raises(g.ErroGerador):
        g.normalizar_padroes(["padrao_que_nao_existe"])


def test_spec_invalida_explica_o_problema(tmp_path):
    ruim = tmp_path / "ruim.json"
    ruim.write_text(json.dumps({"entidade": "minha entidade"}), encoding="utf-8")
    with pytest.raises(g.ErroGerador, match="entidade"):
        g.gerar(spec=str(ruim), saida=tmp_path)


def test_nao_sobrescreve_sem_forcar(tmp_path):
    g.gerar(dominio="hotel", padroes=["strategy"], saida=tmp_path)
    with pytest.raises(g.ErroGerador, match="--forcar"):
        g.gerar(dominio="hotel", padroes=["strategy"], saida=tmp_path)


def test_nunca_apaga_pasta_que_nao_foi_gerada(tmp_path):
    (tmp_path / "hotel_resort__strategy").mkdir()
    with pytest.raises(g.ErroGerador, match="não foi criado pelo gerador"):
        g.gerar(dominio="hotel", padroes=["strategy"], saida=tmp_path, forcar=True)


# ---------------------------------------------------------------- modo exercício
def test_modo_exercicio_e_um_questionario_e_o_codigo_sai_completo(tmp_path):
    destino, s = g.gerar(dominio="hotel", padroes=["strategy", "decorator"], exercicio=True, saida=tmp_path / "ex")
    normal, _ = g.gerar(dominio="hotel", padroes=["strategy", "decorator"], saida=tmp_path / "normal")
    codigo_ex = {k: v for k, v in arquivos(destino).items() if k.startswith("nucleo")}
    assert codigo_ex == {k: v for k, v in arquivos(normal).items() if k.startswith("nucleo")}   # nada esvaziado
    pagina = (destino / "exercicios.html").read_text(encoding="utf-8")
    n = g.total_perguntas(s)
    assert n >= 3 * len(s.padroes)                              # smell, conceito, tripé, quando não usar…
    assert pagina.count("<details>") == n == pagina.count("<summary>Ver resposta</summary>")
    assert "<script" not in pagina and "@@" not in pagina
    assert f"{s.ent}." in pagina                                  # fala do código DESTE sistema (Reserva.…)
    codigo, saida = rodar_pytest(destino)                       # verde desde o início
    assert codigo == 0, saida
    assert not (normal / "exercicios.html").exists()


def test_questionario_escapa_html_e_marca_codigo():
    assert g.md_html("use `a < b` e **isso**") == "use <code>a &lt; b</code> e <strong>isso</strong>"


# ---------------------------------------------------------------- campos a mais (identificador de tipos)
def test_campos_de_todos_os_tipos_geram_sistema_correto(tmp_path):
    pytest.importorskip("django")
    destino, s = g.gerar(dominio="generico", padroes=["prova"], django=True, saida=tmp_path,
                         web={"estilo": "bootstrap"},
                         campos=["vacinado", "data_nascimento", "peso", "idade", "codigo", "total", "status:int"])
    tipos = {a["nome"]: a["tipo"] for a in s.atributos}
    assert (tipos["vacinado"], tipos["data_nascimento"], tipos["peso"], tipos["idade"], tipos["status"]) == \
        ("bool", "data", "float", "int", "int")
    assert "total" not in tipos                                         # reservado: ignorado com nota
    notas = " ".join(s.origem["notas"])
    assert "'codigo' já existe" in notas and "'total' ignorado" in notas
    assert [a["nome"] for a in s.atributos][-1] == "observacao"         # texto livre continua no fim
    entidades = (destino / "nucleo" / "entidades.py").read_text(encoding="utf-8")
    assert "from datetime import date" in entidades and "if not isinstance(valor, bool):" in entidades
    models = (destino / "web" / s.app / "models.py").read_text(encoding="utf-8")
    assert "vacinado = models.BooleanField(" in models and "data_nascimento = models.DateField(" in models
    assert '"type": "date"' in (destino / "web" / s.app / "forms.py").read_text(encoding="utf-8")
    spec = json.loads((destino / "especificacao.json").read_text(encoding="utf-8"))
    assert {"nome": "vacinado", "tipo": "bool", "regra": "obrigatorio", "min": None, "max": None} in spec["atributos"]
    for pasta in (destino, destino / "web"):                            # núcleo e Django: verdes
        codigo, saida = rodar_pytest(pasta)
        assert codigo == 0, saida


def test_campos_listados_no_assunto_entram_na_entidade(tmp_path):
    destino, s = g.gerar(assunto="pet shop com os campos nome do pet, raça, vacinado e data de nascimento, "
                                 "com desconto por tipo de cliente", saida=tmp_path)
    nomes = [a["nome"] for a in s.atributos]
    assert {"nome_pet", "raca", "vacinado", "data_nascimento"} <= set(nomes)
    assert [c["nome"] for c in s.origem["campos"]] == ["nome_pet", "raca", "vacinado", "data_nascimento"]
    codigo, saida = rodar_pytest(destino)
    assert codigo == 0, saida


def test_sem_campos_a_entidade_nao_muda(tmp_path):
    _, s = g.gerar(dominio="hotel", padroes=["strategy"], saida=tmp_path)
    assert [a["nome"] for a in s.atributos] == [a["nome"] for a in g.DOMINIOS["hotel"]["atributos"]]
    assert "campos" not in s.origem


def test_campos_pela_linha_de_comando(tmp_path, capsys):
    assert g.principal(["--dominio", "loja", "--padrao", "strategy", "--saida", str(tmp_path),
                        "--campos", "entregue", "peso_kg:float", "prazo"]) == 0
    saida = capsys.readouterr().out
    assert "entregue (sim/não (BOOL))" in saida and "'prazo': o tipo não é óbvio" in saida


def test_manage_py_e_iniciar_sh_isolam_django_settings_module_do_sgs(tmp_path):
    """Subprocessos herdam DJANGO_SETTINGS_MODULE=sgs_web.settings quando o SGS sobe via Django;
    o iniciar.sh e o web/manage.py gerados devem isolar essa variável para o sistema nunca quebrar."""
    pytest.importorskip("django")
    destino, _ = g.gerar(dominio="citricultura", padroes=["prova"], django=True, saida=tmp_path)
    iniciar = (destino / "iniciar.sh").read_text(encoding="utf-8")
    assert "unset DJANGO_SETTINGS_MODULE" in iniciar
    assert "achar_python_base" in iniciar
    assert (destino / "iniciar.sh").stat().st_mode & 0o111
    manage = (destino / "web" / "manage.py").read_text(encoding="utf-8")
    assert 'DJANGO_SETTINGS_MODULE") == "sgs_web.settings"' in manage
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "sgs_web.settings"}
    r = subprocess.run([sys.executable, "manage.py", "check"], cwd=destino / "web", env=env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


def test_modulo_sgs_dominios_cadastra_gera_e_remove(tmp_path):
    """sgs_dominios.py adiciona domínios personalizados (ID >= 301), gera sistemas completos com testes verdes
    e protege os 300 domínios nativos contra remoção."""
    import sgs_dominios
    extras = tmp_path / "dominios_extras.json"
    try:
        novo = sgs_dominios.cadastrar_dominio(
            "maremotriz", "Maré Oceânica", "TurbinaMare",
            "maremotriz, turbina submarina, forca das mares, oceano, barragem mare, geracao oceanica",
            ident="operador", recurso="estacao", quantidade="horas", preco="tarifa_hora", unidade="hora(s)",
            caminho=extras,
        )
        assert novo["id"] == 301 and novo["chave"] == "maremotriz" and len(novo["palavras"]) == 6
        g.recarregar_dominios(extras)
        assert "maremotriz" in g.DOMINIOS and g.INFO_DOMINIOS["maremotriz"]["id"] == "301"
        assert g.analisar_assunto("usina maremotriz com turbina submarina e forca das mares")["dominio"] == "maremotriz"
        destino, s = g.gerar(dominio="maremotriz", padroes=["strategy"], django=False, saida=tmp_path)
        assert s.sistema == "Maré Oceânica" and s.dados["entidade"] == "TurbinaMare"
        codigo, saida = rodar_pytest(destino)
        assert codigo == 0, saida
        with pytest.raises(ValueError, match="nativo"):
            sgs_dominios.remover_dominio("hotel", caminho=extras)
        with pytest.raises(ValueError, match="nativo"):
            sgs_dominios.remover_dominio("300", caminho=extras)
        removido = sgs_dominios.remover_dominio("maremotriz", caminho=extras)
        assert removido["chave"] == "maremotriz"
        g.recarregar_dominios(extras)
        assert "maremotriz" not in g.DOMINIOS
    finally:
        g.recarregar_dominios()

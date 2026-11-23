"""Testes do IDENTIFICADOR DE TIPOS (tipos_campos.py): o tipo de cada campo sai do nome, e só o que não é
óbvio fica marcado como dúvida (vira pergunta no questionário do SGS)."""
import pytest

import tipos_campos as t


@pytest.mark.parametrize("nome, tipo", [
    ("nome", "str"), ("raca", "str"), ("Raça", "str"), ("e_mail", "str"), ("telefone", "str"), ("placa", "str"),
    ("nome do pet", "str"), ("observacao", "str"),
    ("idade", "int"), ("ano de publicação", "int"), ("dias", "int"), ("tempo_meses", "int"), ("andar", "int"),
    ("peso", "float"), ("valor_frete", "float"), ("preço", "float"), ("altura_cm", "float"), ("salario", "float"),
    ("vacinado", "bool"), ("ativo", "bool"), ("tem_pedigree", "bool"), ("e_socio", "bool"),
    ("data de nascimento", "data"), ("nascimento", "data"), ("vencimento", "data"), ("criado_em", "data"),
])
def test_tipos_obvios_pelo_nome(nome, tipo):
    campo = t.identificar(nome)
    assert campo["tipo"] == tipo and campo["certeza"] == "obvio", campo


@pytest.mark.parametrize("nome", ["codigo", "numero", "status", "tamanho", "matricula", "nota", "prazo",
                                  "codigo_pet", "xyzzy", "pelo_curto"])
def test_nomes_ambiguos_ou_desconhecidos_ficam_em_duvida(nome):
    campo = t.identificar(nome)
    assert campo["certeza"] == "duvida" and campo["sugestao"] in t.TIPOS
    assert t.duvidosos([campo]) == [campo]


def test_tipo_informado_vence_a_deducao():
    campo = t.identificar("codigo", "int")
    assert campo["tipo"] == "int" and campo["certeza"] == "informado" and campo["sugestao"] == "str"
    with pytest.raises(ValueError):
        t.identificar("codigo", "texto")                 # a chave do tipo é str/int/float/bool/data


def test_regras_padrao_por_tipo():
    assert (t.identificar("idade")["regra"], t.identificar("idade")["min"], t.identificar("idade")["max"]) == ("faixa", 0, 130)
    assert t.identificar("peso")["regra"] == "minimo" and t.identificar("peso")["min"] == 0.0
    assert t.identificar("percentual")["max"] == 100.0
    assert t.identificar("observacao")["regra"] == "livre" and t.identificar("nome")["regra"] == "obrigatorio"
    assert t.identificar("vacinado")["regra"] == t.identificar("nascimento")["regra"] == "obrigatorio"


def test_extrai_a_lista_de_campos_do_pedido():
    campos = t.extrair_campos("pet shop com os campos nome do pet, raça, idade, peso, vacinado e data de nascimento")
    assert [c["nome"] for c in campos] == ["nome_pet", "raca", "idade", "peso", "vacinado", "data_nascimento"]
    biblioteca = t.extrair_campos("biblioteca contendo titulo, autor e isbn, que usa strategy")
    assert [c["nome"] for c in biblioteca] == ["titulo", "autor", "isbn"]


def test_tipo_escrito_junto_no_pedido():
    campos = t.extrair_campos("clínica com os seguintes campos: idade:int, peso (decimal), retorno (data), status")
    assert [(c["nome"], c["tipo"]) for c in campos] == [("idade", "int"), ("peso", "float"), ("retorno", "data"),
                                                         ("status", None)]


@pytest.mark.parametrize("pedido", [
    "sistema de pet shop com banho e tosa, e extras opcionais como perfume e laço",
    "academia em que o preço muda conforme o plano do aluno e o pagamento passa por uma API de terceiro",
    "validar os campos obrigatórios e opcionais",
    "guarda os dados do cliente e o histórico",
    "hotel com desconto",
])
def test_pedido_sem_lista_de_campos_nao_inventa_campos(pedido):
    assert t.extrair_campos(pedido) == []


@pytest.mark.parametrize("resposta, tipo", [
    ("int", "int"), ("INT", "int"), ("Inteiro", "int"), ("inteiro (INT)", "int"), ("2", "int"),
    ("str", "str"), ("String", "str"), ("texto", "str"), ("1", "str"),
    ("float", "float"), ("decimal", "float"), ("real", "float"), ("3", "float"),
    ("bool", "bool"), ("sim/não", "bool"), ("booleano", "bool"), ("4", "bool"),
    ("data", "data"), ("DATE", "data"), ("5", "data"),
    ("talvez", None), ("", None), ("9", None),
])
def test_entende_a_resposta_do_tipo(resposta, tipo):
    assert t.tipo_da_resposta(resposta) == tipo


def test_le_a_lista_da_linha_de_comando_e_do_questionario():
    assert t.ler_lista(["nome:str idade:int", "peso (decimal), data de nascimento"]) == [
        ("nome", "str"), ("idade", "int"), ("peso", "float"), ("data_nascimento", None)]
    assert t.ler_lista([{"nome": "vacinado", "tipo": "bool"}]) == [("vacinado", "bool")]
    campos = t.analisar("nome, idade e vacinado")
    assert t.como_texto(campos) == "nome:str idade:int vacinado:bool"
    assert [c["nome"] for c in t.analisar("nome, nome, Nome")] == ["nome"]          # sem repetição


def test_nome_de_campo_vira_snake_case_simples():
    assert t.nome_campo("Data de Nascimento") == "data_nascimento"
    assert t.nome_campo("Preço/Unitário") == "preco_unitario"
    assert t.nome_campo("2 via") == "campo_2_via"

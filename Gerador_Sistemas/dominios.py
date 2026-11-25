"""
dominios.py — os 300 DOMÍNIOS do gerador (catálogo escrito à mão, determinístico, sem IA), incluindo o 101 da
Prova Prática P3 (citricultura), que tem PERFIL próprio (PERFIS, no fim: pasta, projeto/app Django, rotas, DRF).

Duas fontes, juntadas em gerar_sistema.DOMINIOS:
  1. catalogo_100_dominios.txt — a lista do catálogo (ID | DOMINIO | SISTEMA | ENTIDADE | PALAVRAS):
     nome do sistema, entidade e as 100 palavras que ativam cada domínio (001–100 e 102–300) + as 101 do 101.
  2. DADOS (abaixo + dominios_102_300.py) — o resto que cada sistema precisa, coerente com o setor: atributos com
     os papéis ident/quantidade/preço, variantes (Strategy), categorias (polimorfismo), extras (Decorator), gateway
     (Adapter), recursos e textos do painel, nomes de exemplo. Os 8 domínios originais (hotel, cinema,
     clinica, academia, loja, biblioteca, estacionamento, generico) continuam em gerar_sistema.py, iguais.

Formato compacto de cada domínio (uma chamada D por domínio; todos os textos sem aspas, chaves ou barra):
  recurso     "atributo:rótulo:n1 n2 n3"     atributo int (mínimo 1) + o recurso do painel e 3 números
  qtd         "atributo:max"                 quantidade (int, faixa 1..max)
  variantes   "conceito: Nome fator, …; Nova fator"
  categorias  "unidade: Classe = descrição preço; …"   (1ª = base, última = nova, o meio = subtipos)
  extras      "Classe valor texto; …; Percentual fator texto"   (o último é o percentual)
  painel      "título | livre | ocupado | ação livre | ação ocupado | zero | contagem"
"""
from pathlib import Path
from dominios_102_300 import SETORES_102_300, construir_dados_102_300

AQUI = Path(__file__).resolve().parent
CATALOGO = AQUI / "catalogo_100_dominios.txt"

SETORES = [(1, 10, "Hospedagem, Turismo e Lazer"), (11, 22, "Saúde e Bem-Estar"), (23, 34, "Comércio e Varejo"),
           (35, 44, "Alimentação e Gastronomia"), (45, 54, "Educação e Cultura"),
           (55, 64, "Mobilidade, Veículos e Logística"), (65, 72, "Imóveis, Condomínios e Serviços Urbanos"),
           (73, 80, "Serviços Pessoais, Pets e Estética"), (81, 90, "Finanças, Jurídico e Corporativo"),
           (91, 100, "Indústria, Agro, Mídia e Genérico"),
           (101, 101, "Prova Prática P3 (ISW-030)")] + SETORES_102_300

# Nomes de exemplo (o ident é sempre uma pessoa/organização): cada domínio pega 4, em sequência.
NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio", "Gabriela", "Henrique", "Isabela", "João",
         "Karina", "Lucas", "Mariana", "Nicolas", "Olívia", "Pedro", "Quésia", "Rafaela", "Samuel", "Tânia",
         "Ubiratan", "Valéria", "Wagner", "Yasmin", "Zeca", "Aline", "Bernardo", "Cecília", "Danilo", "Érica",
         "Felipe", "Giovana", "Hugo", "Iara", "Jonas", "Lívia", "Márcio", "Natália", "Otávio", "Priscila"]


def setor(numero):
    """Nome do setor de um ID do catálogo (1..300; o 101 é o domínio da Prova Prática P3)."""
    return next(nome for ini, fim, nome in SETORES if ini <= numero <= fim)


def ler_catalogo(caminho=CATALOGO):
    """[(id, chave, sistema, entidade, palavras)] na ordem do arquivo. "_" nas palavras vira espaço (frase)."""
    linhas = []
    for numero_linha, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        partes = [p.strip() for p in linha.split("|")]
        if len(partes) != 5 or not partes[0].isdigit():
            raise ValueError(f"{caminho.name}, linha {numero_linha}: use ID | DOMINIO | SISTEMA | ENTIDADE | PALAVRAS")
        numero, chave, sistema, entidade, palavras = partes
        lista = [p.strip().replace("_", " ") for p in palavras.split(",") if p.strip()]
        linhas.append((int(numero), chave, sistema, entidade, lista))
    return linhas


def A(nome, tipo, regra, minimo=None, maximo=None):
    """Atributo da entidade (o mesmo formato de gerar_sistema.A)."""
    return {"nome": nome, "tipo": tipo, "regra": regra, "min": minimo, "max": maximo}


def _nome_fator(texto):
    *nome, fator = texto.split()
    return [" ".join(nome), float(fator)]


def _classe_desc_preco(texto):
    classe, resto = (x.strip() for x in texto.split("=", 1))
    *descricao, preco = resto.split()
    return [classe, " ".join(descricao), float(preco)]


def D(ident, recurso, qtd, preco, unidade, precos, variantes, categorias, extras, gateway, painel,
      livre="observacao", nomes=None):
    nome_rec, rotulo_rec, numeros = recurso.split(":")
    nome_qtd, maximo = qtd.split(":")
    conceito, resto = (x.strip() for x in variantes.split(":", 1))
    itens, nova = resto.split(";")
    cat_unid, cats = (x.strip() for x in categorias.split(":", 1))
    cats = [_classe_desc_preco(c) for c in cats.split(";")]
    ext = [e.split() for e in extras.split(";")]
    ext = [[e[0], float(e[1]), " ".join(e[2:])] for e in ext]
    p = [x.strip() for x in painel.split("|")]
    return {
        "atributos": [A(ident, "str", "obrigatorio"), A(nome_rec, "int", "minimo", 1),
                      A(nome_qtd, "int", "faixa", 1, int(maximo)), A(preco, "float", "minimo", 0),
                      A(livre, "str", "livre")],
        "ident": ident, "quantidade": nome_qtd, "preco": preco, "unidade": unidade,
        "precos_exemplo": [float(x) for x in precos.split()],
        "variantes": {"conceito": conceito, "itens": [_nome_fator(i) for i in itens.split(",")],
                      "nova": _nome_fator(nova)},
        "categorias": {"unidade": cat_unid, "base": cats[0], "subtipos": cats[1:-1], "nova": cats[-1]},
        "extras": {"fixos": ext[:-1], "percentual": ext[-1]},
        "gateway": gateway,
        "recurso": rotulo_rec, "recursos": [int(x) for x in numeros.split()],
        "painel": dict(zip(("titulo", "livre", "ocupado", "acao_livre", "acao_ocupado", "zero", "contagem"), p)),
        "nomes": nomes,
    }


DADOS = {
    # ------------------------------------------------------------ 001-010 Hospedagem, Turismo e Lazer
    "parque": D("visitante", "atracao:atração:1 2 3", "pessoas:20", "valor_entrada", "pessoa(s)", "120 90 150 0",
                "tipo de visitante: Inteira 1, Meia 0.5, Grupo 0.85; Sazonal 0.7",
                "dia: PassaporteDiario = Passaporte diário 120; PassaporteVip = Passaporte VIP 220; "
                "PassaporteAnual = Passaporte anual 600; PassaporteNoturno = Passaporte noturno 80",
                "ArmarioParque 25 armário; AluguelBoia 15 boia; FotoOficial 40 foto oficial; PromocaoFamilia 0.85 -15% família",
                "PagaParque", "Atração | com vaga | LOTADA | Entrar | (fila cheia) | LOTADO - nenhuma atração com vaga | "
                              "atração(ões) com vaga"),
    "agencia_viagem": D("viajante", "voo:voo:301 302 303", "noites:30", "valor_noite", "noite(s)", "350 280 520 0",
                        "tipo de cliente: Comum 1, Fidelidade 0.92, Corporativo 0.85; Estudante 0.8",
                        "noite: Economico = Pacote econômico 350; Executivo = Pacote executivo 650; "
                        "Luxo = Pacote luxo 1200; Aventura = Pacote aventura 480",
                        "SeguroViagem 90 seguro viagem; Translado 120 translado; PasseioGuiado 150 passeio guiado; "
                        "AltaTemporada 1.25 +25% alta temporada",
                        "PagaTur", "Voo | com assentos | ESGOTADO | Reservar | (lista de espera) | "
                                   "ESGOTADO - nenhum voo com assento | voo(s) com assento"),
    "teatro": D("espectador", "fileira:fileira:1 2 3", "ingressos:8", "preco_ingresso", "ingresso(s)", "80 60 150 0",
                "tipo de ingresso: Inteira 1, Meia 0.5, Assinante 0.75; Promocional 0.6",
                "ingresso: Plateia = Plateia 80; Camarote = Camarote 180; Balcao = Balcão 60; Frisa = Frisa 120",
                "ProgramaPeca 15 programa da peça; Estacionamento 25 estacionamento; TacaEspumante 30 taça de espumante; "
                "NoiteEstreia 1.2 +20% estreia",
                "PagaCena", "Sessão | com lugares | ESGOTADA | Comprar | (esgotada) | "
                            "ESGOTADO - nenhuma sessão com lugar | sessão(ões) com lugar"),
    "museu": D("visitante", "sala:sala:1 2 3", "pessoas:30", "valor_ingresso", "pessoa(s)", "30 20 45 0",
               "tipo de visitante: Inteira 1, Estudante 0.5, Professor 0.5; Grupo Escolar 0.3",
               "visita: VisitaLivre = Visita livre 30; VisitaGuiada = Visita guiada 50; "
               "VisitaNoturna = Visita noturna 60; OficinaArte = Oficina de arte 40",
               "AudioGuia 15 audioguia; CatalogoImpresso 35 catálogo impresso; Fotografia 10 fotografia; "
               "DomingoGratis 0.5 -50% domingo",
               "PagaCultura", "Sala | aberta | FECHADA | Visitar | (em montagem) | FECHADO - nenhuma sala aberta | "
                              "sala(s) aberta(s)"),
    "clube": D("associado", "quadra:quadra:1 2 3", "meses:24", "mensalidade", "mês(es)", "250 180 400 0",
               "tipo de sócio: Titular 1, Dependente 0.5, Remido 0.3; Atleta 0.7",
               "mês: SocioIndividual = Sócio individual 250; SocioFamiliar = Sócio familiar 420; "
               "SocioJunior = Sócio júnior 150; SocioPatrimonial = Sócio patrimonial 600",
               "ArmarioClube 30 armário; Estacionamento 40 estacionamento; ReservaChurrasqueira 80 churrasqueira; "
               "Anuidade 0.9 -10% anuidade",
               "PagaClube", "Quadra | livre | RESERVADA | Reservar | (reservada) | LOTADO - nenhuma quadra livre | "
                            "quadra(s) livre(s)"),
    "camping": D("campista", "lote:lote:1 2 3", "noites:15", "valor_noite", "noite(s)", "60 45 90 0",
                 "tipo de campista: Avulso 1, Sócio Camping 0.8, Grupo 0.85; Feriado 1.3",
                 "noite: AreaBarraca = Área de barraca 60; AreaTrailer = Área de trailer 110; Chale = Chalé 220; "
                 "Glamping = Glamping 350",
                 "EnergiaEletrica 20 energia elétrica; Lenha 15 lenha; AluguelBarraca 50 aluguel de barraca; "
                 "BaixaTemporada 0.8 -20% baixa temporada",
                 "PagaTrilha", "Lote | livre | OCUPADO | Acampar | (ocupado) | LOTADO - nenhum lote livre | "
                               "lote(s) livre(s)"),
    "eventos": D("contratante", "salao:salão:1 2 3", "convidados:500", "valor_convidado", "convidado(s)", "120 95 180 0",
                 "tipo de evento: Social 1, Corporativo 1.1, Beneficente 0.8; Formatura 0.95",
                 "convidado: BuffetSimples = Buffet simples 120; BuffetCompleto = Buffet completo 180; "
                 "Coquetel = Coquetel 90; Banquete = Banquete 250",
                 "Dj 1500 DJ; Decoracao 2000 decoração; Fotografo 1200 fotógrafo; DataEspecial 1.15 +15% data especial",
                 "PagaFesta", "Salão | disponível | RESERVADO | Reservar | (reservado) | "
                              "SEM DATA - nenhum salão disponível | salão(ões) disponível(is)"),
    "temporada": D("hospede", "imovel:imóvel:11 12 13", "diarias:30", "valor_diaria", "diária(s)", "300 220 480 0",
                   "tipo de reserva: Normal 1, Semanal 0.85, Mensal 0.7; Feriado 1.4",
                   "diária: Apartamento = Apartamento 300; CasaPraia = Casa de praia 480; Chacara = Chácara 400; "
                   "Cabana = Cabana 250",
                   "TaxaLimpeza 150 taxa de limpeza; PetFriendly 80 pet friendly; EnxovalExtra 60 enxoval extra; "
                   "Reveillon 1.6 +60% réveillon",
                   "PagaEstadia", "Imóvel | livre | OCUPADO | Reservar | (ocupado) | LOTADO - nenhum imóvel livre | "
                                  "imóvel(is) livre(s)"),
    # ------------------------------------------------------------ 011-022 Saúde e Bem-Estar
    "hospital": D("paciente", "leito:leito:101 102 103", "diarias:60", "valor_diaria", "diária(s)", "900 650 1500 0",
                  "tipo de cobertura: Particular 1, Convênio 0.6, Empresa 0.75; Filantrópico 0.4",
                  "diária: Enfermaria = Enfermaria 900; ApartamentoHosp = Apartamento 1500; Uti = UTI 3500; "
                  "SemiIntensiva = Semi-intensiva 2200",
                  "Acompanhante 120 acompanhante; RefeicaoExtra 60 refeição extra; Fisioterapia 150 fisioterapia; "
                  "Urgencia 1.3 +30% urgência",
                  "HospPag", "Leito | livre | OCUPADO | Internar | (ocupado) | LOTADO - nenhum leito livre | "
                             "leito(s) livre(s)"),
    "odontologia": D("paciente", "cadeira:cadeira:1 2 3", "sessoes:12", "valor_sessao", "sessão(ões)", "200 150 350 0",
                     "tipo de convênio: Particular 1, Plano Odonto 0.6, Empresa 0.75; Social 0.5",
                     "sessão: Limpeza = Limpeza 200; Restauracao = Restauração 250; TratamentoCanal = Tratamento de canal 600; "
                     "Clareamento = Clareamento 800",
                     "Radiografia 60 radiografia; Anestesia 40 anestesia; Moldagem 90 moldagem; Emergencia 1.4 +40% emergência",
                     "OdontoPag", "Cadeira | livre | EM ATENDIMENTO | Agendar | (ocupada) | "
                                  "AGENDA CHEIA - nenhuma cadeira livre | cadeira(s) livre(s)"),
    "farmacia": D("cliente", "balcao:balcão:1 2 3", "unidades:20", "preco_unitario", "unidade(s)", "25.9 12.5 89.9 0",
                  "tipo de cliente: Comum 1, Convênio 0.85, Idoso 0.9; Farmácia Popular 0.1",
                  "unidade: Generico = Genérico 25.9; Referencia = Referência 45.9; Similar = Similar 30.5; "
                  "Manipulado = Manipulado 60",
                  "EntregaDomicilio 10 entrega em casa; AfericaoPressao 5 aferição de pressão; "
                  "AplicacaoInjetavel 15 aplicação de injetável; DescontoConvenio 0.85 -15% convênio",
                  "FarmaPag", "Balcão | livre | ATENDENDO | Atender | (aguardar) | FILA CHEIA - nenhum balcão livre | "
                              "balcão(ões) livre(s)"),
    "laboratorio": D("paciente", "box_coleta:box de coleta:1 2 3", "exames:15", "valor_exame", "exame(s)", "45 30 120 0",
                     "tipo de cobertura: Particular 1, Convênio 0.5, Empresa 0.7; Campanha 0.4",
                     "exame: Hemograma = Hemograma 45; Glicemia = Glicemia 25; Ultrassom = Ultrassom 180; "
                     "Tomografia = Tomografia 650",
                     "ColetaDomiciliar 60 coleta domiciliar; LaudoUrgente 40 laudo urgente; SegundaVia 10 segunda via; "
                     "Plantao 1.3 +30% plantão",
                     "LabPag", "Box de coleta | livre | EM COLETA | Coletar | (aguardar) | FILA CHEIA - nenhum box livre | "
                               "box(es) livre(s)"),
    "fisioterapia": D("paciente", "maca:maca:1 2 3", "sessoes:20", "valor_sessao", "sessão(ões)", "120 90 160 0",
                      "tipo de convênio: Particular 1, Convênio 0.6, Pacote Mensal 0.8; Social 0.5",
                      "sessão: Ortopedica = Fisioterapia ortopédica 120; PilatesClinico = Pilates clínico 140; "
                      "Rpg = RPG 160; Hidroterapia = Hidroterapia 150",
                      "Eletroterapia 30 eletroterapia; Bandagem 40 bandagem; AvaliacaoFisio 80 avaliação; "
                      "Domiciliar 1.5 +50% domiciliar",
                      "FisioPag", "Maca | livre | EM SESSÃO | Agendar | (ocupada) | AGENDA CHEIA - nenhuma maca livre | "
                                  "maca(s) livre(s)"),
    "psicologia": D("paciente", "consultorio:consultório:1 2 3", "sessoes:12", "valor_sessao", "sessão(ões)", "180 120 250 0",
                    "tipo de atendimento: Particular 1, Convênio 0.6, Social 0.4; Estudante 0.7",
                    "sessão: Individual = Terapia individual 180; Casal = Terapia de casal 250; "
                    "Infantil = Terapia infantil 200; Online = Terapia online 150",
                    "RelatorioPsi 150 relatório psicológico; AvaliacaoPsi 300 avaliação psicológica; "
                    "Devolutiva 100 sessão devolutiva; PacoteMensal 0.9 -10% pacote mensal",
                    "MentePag", "Consultório | livre | EM SESSÃO | Agendar | (ocupado) | "
                                "AGENDA CHEIA - nenhum consultório livre | consultório(s) livre(s)"),
    "nutricao": D("paciente", "consultorio:consultório:1 2 3", "consultas:12", "valor_consulta", "consulta(s)",
                  "220 150 300 0",
                  "tipo de plano: Avulso 1, Trimestral 0.85, Semestral 0.75; Atleta 0.9",
                  "consulta: Emagrecimento = Emagrecimento 220; Esportiva = Nutrição esportiva 260; "
                  "NutricaoClinica = Nutrição clínica 240; Gestante = Gestante 230",
                  "Bioimpedancia 60 bioimpedância; CardapioExtra 80 cardápio extra; RetornoOnline 70 retorno online; "
                  "Promocao 0.9 -10% promoção",
                  "NutriPag", "Consultório | livre | EM CONSULTA | Agendar | (ocupado) | "
                              "AGENDA CHEIA - nenhum consultório livre | consultório(s) livre(s)"),
    "otica": D("cliente", "bancada:bancada:1 2 3", "pares:6", "preco_par", "par(es)", "350 200 900 0",
               "tipo de cliente: Comum 1, Convênio 0.8, Fidelidade 0.9; Estudante 0.85",
               "par: Monofocal = Lente monofocal 350; Multifocal = Lente multifocal 900; LenteContato = Lente de contato 220; "
               "OculosSol = Óculos de sol 400",
               "Antirreflexo 120 antirreflexo; FiltroAzul 90 filtro de luz azul; Fotossensivel 180 fotossensível; "
               "Saldao 0.8 -20% saldão",
               "VisaoPag", "Bancada | livre | MONTANDO | Montar | (aguardar) | FILA CHEIA - nenhuma bancada livre | "
                           "bancada(s) livre(s)"),
    "spa": D("cliente", "cabine:cabine:1 2 3", "sessoes:10", "valor_sessao", "sessão(ões)", "180 120 280 0",
             "tipo de cliente: Avulso 1, Pacote Fidelidade 0.85, Hóspede 0.9; Aniversariante 0.8",
             "sessão: Relaxante = Massagem relaxante 180; PedrasQuentes = Pedras quentes 240; Shiatsu = Shiatsu 200; "
             "Drenagem = Drenagem linfática 190",
             "Ofuro 90 ofurô; Aromaterapia 40 aromaterapia; BanhoErvas 60 banho de ervas; FimSemana 1.2 +20% fim de semana",
             "ZenPag", "Cabine | livre | EM USO | Agendar | (ocupada) | AGENDA CHEIA - nenhuma cabine livre | "
                       "cabine(s) livre(s)"),
    "hemocentro": D("doador", "cadeira:cadeira de coleta:1 2 3", "bolsas:4", "custo_bolsa", "bolsa(s)", "180 150 260 0",
                    "tipo de doação: Voluntária 1, Reposição 0.95, Campanha 0.9; Aférese 1.4",
                    "bolsa: SangueTotal = Sangue total 180; Plasma = Plasma 220; Plaquetas = Plaquetas por aférese 450; "
                    "Hemacias = Concentrado de hemácias 260",
                    "Sorologia 60 sorologia; Fracionamento 80 fracionamento; TransporteRefrigerado 50 transporte refrigerado; "
                    "Emergencial 1.3 +30% emergencial",
                    "HemoPag", "Cadeira de coleta | livre | EM COLETA | Coletar | (aguardar) | "
                               "LOTADO - nenhuma cadeira livre | cadeira(s) livre(s)"),
    # ------------------------------------------------------------ 023-034 Comércio e Varejo
    "supermercado": D("cliente", "caixa:caixa:1 2 3", "itens:100", "preco_item", "item(ns)", "8.9 4.5 25 0",
                      "tipo de cliente: Comum 1, Clube Desconto 0.95, Atacado 0.88; Funcionário 0.85",
                      "item: Mercearia = Mercearia 8.9; Hortifruti = Hortifrúti 6.5; Acougue = Açougue 39.9; "
                      "Limpeza = Limpeza 12",
                      "Sacola 0.5 sacola; EntregaCasa 15 entrega em casa; EmbalagemPresente 3 embalagem para presente; "
                      "OfertaDia 0.9 -10% oferta do dia",
                      "PagaMercado", "Caixa | livre | OCUPADO | Passar | (fila) | FILA CHEIA - nenhum caixa livre | "
                                     "caixa(s) livre(s)"),
    "livraria": D("cliente", "estante:estante:1 2 3", "exemplares:30", "preco_exemplar", "exemplar(es)", "59.9 39.9 120 0",
                  "tipo de cliente: Comum 1, Professor 0.85, Estudante 0.9; Clube de Leitura 0.8",
                  "exemplar: Romance = Romance 59.9; Tecnico = Técnico 120; Infantil = Infantil 39.9; "
                  "Quadrinho = Quadrinho 35",
                  "EmbrulhoPresente 8 embrulho para presente; MarcaPagina 5 marcador de página; "
                  "Dedicatoria 20 dedicatória do autor; Lancamento 1.1 +10% lançamento",
                  "PagaLivro", "Estante | com exemplares | ESGOTADA | Comprar | (encomendar) | "
                               "ESGOTADO - nenhuma estante com exemplar | estante(s) com exemplar"),
    "vestuario": D("cliente", "provador:provador:1 2 3", "pecas:20", "preco_peca", "peça(s)", "89.9 49.9 199.9 0",
                   "tipo de cliente: Comum 1, Fidelidade 0.9, Atacado 0.8; Influenciador 0.7",
                   "peça: Camiseta = Camiseta 49.9; Calca = Calça 129.9; Vestido = Vestido 179.9; Jaqueta = Jaqueta 249.9",
                   "AjusteCostura 25 ajuste de costura; Embrulho 8 embrulho; Bordado 35 bordado; Liquidacao 0.7 -30% liquidação",
                   "PagaModa", "Provador | livre | OCUPADO | Provar | (aguardar) | LOTADO - nenhum provador livre | "
                               "provador(es) livre(s)"),
    "eletronicos": D("cliente", "vitrine:vitrine:1 2 3", "unidades:10", "preco_unitario", "unidade(s)", "1999 899 4500 0",
                     "tipo de cliente: Comum 1, Empresa 0.92, Estudante 0.95; Revenda 0.85",
                     "unidade: Celular = Celular 1999; Notebook = Notebook 4500; Tablet = Tablet 1500; "
                     "AcessorioTech = Acessório 150",
                     "GarantiaEstendida 300 garantia estendida; Pelicula 40 película; InstalacaoApps 60 configuração inicial; "
                     "BlackFriday 0.75 -25% black friday",
                     "PagaTech", "Vitrine | com estoque | ESGOTADA | Comprar | (avise-me) | "
                                 "SEM ESTOQUE - nenhuma vitrine com produto | vitrine(s) com estoque"),
    "joalheria": D("cliente", "vitrine:vitrine:1 2 3", "pecas:10", "preco_peca", "peça(s)", "1200 450 3500 0",
                   "tipo de cliente: Comum 1, Fidelidade 0.92, Noivos 0.88; Revenda 0.8",
                   "peça: Anel = Anel 1200; Alianca = Aliança 2400; Colar = Colar 1800; Brinco = Brinco 650",
                   "Gravacao 80 gravação; CaixaPresente 40 caixa de presente; Certificado 120 certificado de autenticidade; "
                   "DiaNamorados 0.9 -10% dia dos namorados",
                   "PagaJoia", "Vitrine | com peças | VAZIA | Ver | (repor) | SEM PEÇAS - nenhuma vitrine com peça | "
                               "vitrine(s) com peça"),
    "floricultura": D("cliente", "bancada:bancada:1 2 3", "arranjos:20", "preco_arranjo", "arranjo(s)", "120 80 250 0",
                      "tipo de cliente: Comum 1, Empresa 0.9, Cerimonial 0.85; Assinante 0.8",
                      "arranjo: Buque = Buquê 120; CoroaFlores = Coroa de flores 350; PlantaVaso = Planta em vaso 80; "
                      "CestaPresente = Cesta de presente 180",
                      "CartaoMensagem 10 cartão com mensagem; EntregaExpressa 30 entrega expressa; Chocolate 45 caixa de chocolate; "
                      "DiaMaes 1.2 +20% dia das mães",
                      "PagaFlor", "Bancada | livre | MONTANDO | Montar | (aguardar) | FILA CHEIA - nenhuma bancada livre | "
                                  "bancada(s) livre(s)"),
    "construcao": D("cliente", "deposito:depósito:1 2 3", "itens:200", "preco_item", "item(ns)", "45 12.5 189 0",
                    "tipo de cliente: Comum 1, Construtora 0.85, Profissional 0.9; Atacado 0.8",
                    "item: Cimento = Cimento 45; Tijolo = Milheiro de tijolo 890; Tinta = Tinta 189; Piso = Piso por metro 59.9",
                    "EntregaObra 80 entrega na obra; CorteMedida 25 corte sob medida; Munck 300 caminhão munck; "
                    "PagamentoVista 0.95 -5% à vista",
                    "PagaObra", "Depósito | abastecido | SEM ESTOQUE | Retirar | (aguardar) | "
                                "SEM ESTOQUE - nenhum depósito abastecido | depósito(s) abastecido(s)"),
    "autopecas": D("cliente", "prateleira:prateleira:1 2 3", "pecas:50", "preco_peca", "peça(s)", "180 45 650 0",
                   "tipo de cliente: Comum 1, Oficina 0.85, Frota 0.8; Revenda 0.75",
                   "peça: Filtro = Filtro 45; Pastilha = Pastilha de freio 180; Amortecedor = Amortecedor 420; "
                   "BateriaAuto = Bateria 650",
                   "Instalacao 80 instalação; GarantiaPeca 60 garantia estendida; Descarte 15 descarte ecológico; "
                   "Promocao 0.9 -10% promoção",
                   "PagaPecas", "Prateleira | com estoque | VAZIA | Vender | (encomendar) | "
                                "SEM ESTOQUE - nenhuma prateleira com peça | prateleira(s) com estoque"),
    "moveis": D("cliente", "ambiente:ambiente:1 2 3", "modulos:30", "preco_modulo", "módulo(s)", "850 600 1400 0",
                "tipo de cliente: Comum 1, Arquiteto 0.88, Construtora 0.8; Indicação 0.92",
                "módulo: CozinhaPlanejada = Cozinha planejada 850; Dormitorio = Dormitório 950; "
                "BanheiroPlanejado = Banheiro 700; HomeOffice = Home office 800",
                "Projeto3d 300 projeto 3D; Montagem 400 montagem; IluminacaoEmbutida 250 iluminação embutida; "
                "PagamentoVista 0.92 -8% à vista",
                "PagaMovel", "Ambiente | livre | EM MONTAGEM | Medir | (aguardar) | AGENDA CHEIA - nenhum ambiente livre | "
                             "ambiente(s) livre(s)"),
    "marketplace": D("vendedor", "vitrine:vitrine:1 2 3", "unidades:100", "preco_unitario", "unidade(s)", "79.9 29.9 349 0",
                     "tipo de vendedor: Comum 1, Profissional 0.95, Premium 0.9; Oficial 0.85",
                     "unidade: AnuncioClassico = Anúncio clássico 79.9; AnuncioPremium = Anúncio premium 129.9; "
                     "AnuncioFull = Anúncio full 99.9; AnuncioDestaque = Anúncio em destaque 149.9",
                     "Patrocinio 50 patrocínio; EtiquetaEnvio 12 etiqueta de envio; Fulfillment 25 armazenagem full; "
                     "CampanhaMkt 0.9 -10% campanha",
                     "SplitPag", "Vitrine | ativa | PAUSADA | Anunciar | (pausada) | SEM VITRINE - nenhuma vitrine ativa | "
                                 "vitrine(s) ativa(s)"),
    "brecho": D("consignante", "arara:arara:1 2 3", "pecas:50", "preco_peca", "peça(s)", "45 25 120 0",
                "tipo de consignante: Comum 1, Parceiro 0.9, Lojista 0.85; Bazar 0.6",
                "peça: RoupaUsada = Roupa usada 45; CalcadoUsado = Calçado usado 60; BolsaUsada = Bolsa 90; "
                "Vintage = Peça vintage 120",
                "Higienizacao 10 higienização; AjusteCostura 20 ajuste de costura; FotoAnuncio 5 foto para anúncio; "
                "Desapego 0.7 -30% desapego",
                "PagaCircular", "Arara | com peças | VAZIA | Expor | (repor) | SEM PEÇAS - nenhuma arara com peça | "
                                "arara(s) com peça"),
    # ------------------------------------------------------------ 035-044 Alimentação e Gastronomia
    "restaurante": D("cliente", "mesa:mesa:1 2 3", "pratos:20", "preco_prato", "prato(s)", "58 42 95 0",
                     "tipo de cliente: Comum 1, Fidelidade 0.9, Empresa 0.85; Aniversariante 0.8",
                     "prato: PratoExecutivo = Prato executivo 42; PratoChef = Prato do chef 95; Massa = Massa 58; "
                     "Salada = Salada 38",
                     "Couvert 12 couvert; Sobremesa 22 sobremesa; TacaVinho 80 taça de vinho; TaxaServico 1.1 +10% serviço",
                     "PagaMesa", "Mesa | livre | OCUPADA | Sentar | (aguardar) | LOTADO - nenhuma mesa livre | "
                                 "mesa(s) livre(s)"),
    "pizzaria": D("cliente", "forno:forno:1 2 3", "pizzas:10", "preco_pizza", "pizza(s)", "55 45 75 0",
                  "tipo de pedido: Balcão 1, Entrega 1.1, Retirada 0.95; Terça 0.7",
                  "pizza: Tradicional = Pizza tradicional 55; Especial = Pizza especial 68; PizzaDoce = Pizza doce 50; "
                  "Brotinho = Pizza brotinho 30",
                  "BordaRecheada 12 borda recheada; Refrigerante 10 refrigerante; IngredienteExtra 8 ingrediente extra; "
                  "ComboPizza 0.85 -15% combo",
                  "PagaPizza", "Forno | livre | ASSANDO | Assar | (aguardar) | FORNOS CHEIOS - nenhum forno livre | "
                               "forno(s) livre(s)"),
    "lanchonete": D("cliente", "chapa:chapa:1 2 3", "lanches:10", "preco_lanche", "lanche(s)", "32 25 45 0",
                    "tipo de pedido: Balcão 1, Delivery 1.1, Drive Thru 1; Estudante 0.85",
                    "lanche: Classico = Burger clássico 32; Smash = Smash burger 28; Artesanal = Burger artesanal 42; "
                    "Vegano = Burger vegano 35",
                    "BatataFrita 14 batata frita; Bacon 6 bacon extra; Milkshake 18 milkshake; ComboDuplo 0.85 -15% combo duplo",
                    "PagaBurger", "Chapa | livre | PREPARANDO | Preparar | (aguardar) | COZINHA CHEIA - nenhuma chapa livre | "
                                  "chapa(s) livre(s)"),
    "padaria": D("cliente", "forno:forno:1 2 3", "unidades:100", "preco_unitario", "unidade(s)", "0.9 6.5 45 0",
                 "tipo de cliente: Balcão 1, Encomenda 0.95, Empresa 0.85; Revenda 0.75",
                 "unidade: PaoFrances = Pão francês 0.9; PaoQueijo = Pão de queijo 2.5; Bolo = Bolo 45; Salgado = Salgado 6.5",
                 "EmbalagemPadaria 2 embalagem; EntregaCasa 8 entrega em casa; RecheioEspecial 10 recheio especial; "
                 "FinalDia 0.6 -40% fim do dia",
                 "PagaPadaria", "Forno | livre | ASSANDO | Assar | (aguardar) | FORNOS CHEIOS - nenhum forno livre | "
                                "forno(s) livre(s)"),
    "cafeteria": D("cliente", "maquina:máquina:1 2 3", "xicaras:20", "preco_bebida", "xícara(s)", "9.5 7 18 0",
                   "tipo de cliente: Comum 1, Clube Café 0.9, Estudante 0.85; Barista Convidado 1.2",
                   "xícara: Expresso = Expresso 7; Cappuccino = Cappuccino 12; Latte = Latte 13; Coado = Café coado 9.5",
                   "LeiteVegetal 3 leite vegetal; Chantilly 2.5 chantilly; Cookie 8 cookie; HappyHour 0.8 -20% happy hour",
                   "PagaCafe", "Máquina | livre | PREPARANDO | Preparar | (aguardar) | FILA CHEIA - nenhuma máquina livre | "
                               "máquina(s) livre(s)"),
    "delivery": D("cliente", "moto:moto:1 2 3", "volumes:20", "valor_volume", "volume(s)", "12 8 25 0",
                  "tipo de entrega: Normal 1, Agendada 0.9, Expressa 1.5; Assinante 0.8",
                  "volume: VolumePequeno = Volume pequeno 8; VolumeMedio = Volume médio 12; VolumeGrande = Volume grande 25; "
                  "Refrigerado = Volume refrigerado 18",
                  "SeguroEntrega 5 seguro; RetornoRemetente 10 retorno ao remetente; Noturna 8 entrega noturna; "
                  "DiaChuva 1.2 +20% chuva",
                  "PagaEntrega", "Moto | livre | EM ROTA | Despachar | (em rota) | SEM MOTOS - nenhuma moto livre | "
                                 "moto(s) livre(s)"),
    "acougue": D("cliente", "balcao:balcão:1 2 3", "quilos:30", "preco_quilo", "quilo(s)", "69.9 39.9 129.9 0",
                 "tipo de cliente: Comum 1, Restaurante 0.88, Fidelidade 0.95; Churrasqueiro 0.9",
                 "quilo: Picanha = Picanha 129.9; Alcatra = Alcatra 69.9; CarneMoida = Carne moída 39.9; Costela = Costela 34.9",
                 "TemperoCasa 8 tempero da casa; EmbalagemVacuo 5 embalagem a vácuo; Espetinho 12 montagem de espetinho; "
                 "KitChurrasco 0.9 -10% kit churrasco",
                 "PagaCarne", "Balcão | livre | ATENDENDO | Atender | (aguardar) | FILA CHEIA - nenhum balcão livre | "
                              "balcão(ões) livre(s)"),
    "hortifruti": D("cliente", "banca:banca:1 2 3", "quilos:50", "preco_quilo", "quilo(s)", "6.9 3.5 12.9 0",
                    "tipo de cliente: Comum 1, Restaurante 0.85, Feirante 0.8; Clube Orgânico 0.9",
                    "quilo: Fruta = Fruta 6.9; Verdura = Verdura 3.5; Legume = Legume 5.9; Organico = Orgânico 12.9",
                    "CestaMontada 15 cesta montada; Higienizacao 6 higienização; EntregaCasa 10 entrega em casa; "
                    "Xepa 0.5 -50% xepa",
                    "PagaFeira", "Banca | abastecida | VAZIA | Comprar | (repor) | SEM PRODUTO - nenhuma banca abastecida | "
                                 "banca(s) abastecida(s)"),
    "sorveteria": D("cliente", "freezer:freezer:1 2 3", "bolas:10", "preco_bola", "bola(s)", "9 7 14 0",
                    "tipo de cliente: Comum 1, Fidelidade 0.9, Criança 0.8; Festa 0.75",
                    "bola: SorveteTradicional = Sorvete tradicional 7; Gelato = Gelato 12; Acai = Açaí 14; "
                    "ZeroAcucar = Zero açúcar 10",
                    "Cobertura 3 cobertura; Casquinha 2 casquinha; Granola 2.5 granola; Verao 0.85 -15% verão",
                    "PagaGelato", "Freezer | abastecido | VAZIO | Servir | (repor) | SEM SORVETE - nenhum freezer abastecido | "
                                  "freezer(s) abastecido(s)"),
    "adega": D("cliente", "prateleira:prateleira:1 2 3", "garrafas:24", "preco_garrafa", "garrafa(s)", "89 45 320 0",
               "tipo de cliente: Comum 1, Clube Vinho 0.85, Restaurante 0.8; Sommelier 0.9",
               "garrafa: VinhoTinto = Vinho tinto 89; Espumante = Espumante 110; Whisky = Whisky 320; "
               "CervejaArtesanal = Cerveja artesanal 25",
               "Gelo 8 gelo; CaixaPresente 30 caixa de presente; Harmonizacao 50 harmonização; Degustacao 0.9 -10% degustação",
               "PagaAdega", "Prateleira | abastecida | VAZIA | Vender | (repor) | SEM ESTOQUE - nenhuma prateleira abastecida | "
                            "prateleira(s) abastecida(s)"),
    # ------------------------------------------------------------ 045-054 Educação e Cultura
    "escola": D("aluno", "sala:sala:1 2 3", "meses:12", "mensalidade", "mês(es)", "850 600 1200 0",
                "tipo de bolsa: Regular 1, Irmãos 0.9, Bolsista 0.5; Filho de Professor 0.4",
                "mês: Fundamental1 = Fundamental I 850; Fundamental2 = Fundamental II 950; EnsinoMedio = Ensino médio 1200; "
                "EducacaoInfantil = Educação infantil 700",
                "MaterialEscolar 180 material escolar; Uniforme 150 uniforme; TransporteEscolar 220 transporte escolar; "
                "Antecipado 0.95 -5% pagamento antecipado",
                "PagaEscola", "Sala | com vagas | LOTADA | Matricular | (lista de espera) | SEM VAGAS - nenhuma sala com vaga | "
                              "sala(s) com vaga"),
    "faculdade": D("aluno", "laboratorio:laboratório:1 2 3", "creditos:30", "valor_credito", "crédito(s)", "180 120 250 0",
                   "tipo de aluno: Regular 1, Fies 0.5, Prouni 0.2; Ex Aluno 0.85",
                   "crédito: Graduacao = Graduação 180; PosGraduacao = Pós-graduação 250; Extensao = Extensão 120; "
                   "Ead = EAD 90",
                   "Diploma 250 emissão de diploma; HistoricoEscolar 40 histórico escolar; Carteirinha 20 carteirinha; "
                   "Pontualidade 0.9 -10% pontualidade",
                   "PagaCampus", "Laboratório | com vagas | LOTADO | Inscrever | (lista de espera) | "
                                 "SEM VAGAS - nenhum laboratório com vaga | laboratório(s) com vaga"),
    "idiomas": D("aluno", "turma:turma:1 2 3", "meses:24", "mensalidade", "mês(es)", "380 290 550 0",
                 "tipo de plano: Regular 1, Semestral 0.9, Empresa 0.8; Intercambista 0.85",
                 "mês: Ingles = Inglês 380; Espanhol = Espanhol 340; Frances = Francês 420; Mandarim = Mandarim 550",
                 "MaterialDidatico 220 material didático; AulaVip 150 aula VIP; ProvaCertificacao 600 prova de certificação; "
                 "Promocao 0.85 -15% promoção",
                 "PagaIdioma", "Turma | com vagas | LOTADA | Matricular | (lista de espera) | "
                               "SEM VAGAS - nenhuma turma com vaga | turma(s) com vaga"),
    "autoescola": D("aluno", "veiculo:veículo:1 2 3", "aulas:40", "valor_aula", "aula(s)", "90 70 120 0",
                    "tipo de aluno: Avulso 1, Pacote Completo 0.85, Renovação 0.9; Reciclagem 0.8",
                    "aula: CategoriaA = Categoria A (moto) 70; CategoriaB = Categoria B (carro) 90; "
                    "CategoriaC = Categoria C (caminhão) 140; CategoriaD = Categoria D (ônibus) 160",
                    "Simulador 60 simulador; TaxaDetran 250 taxa do Detran; AulaExtra 95 aula extra; "
                    "Antecipado 0.93 -7% pagamento antecipado",
                    "PagaDirecao", "Veículo | livre | EM AULA | Agendar | (ocupado) | AGENDA CHEIA - nenhum veículo livre | "
                                   "veículo(s) livre(s)"),
    "musica": D("aluno", "estudio:estúdio:1 2 3", "aulas:16", "valor_aula", "aula(s)", "120 90 180 0",
                "tipo de aluno: Avulso 1, Mensal 0.85, Banda 0.7; Bolsista 0.5",
                "aula: Violao = Violão 90; Piano = Piano 140; BateriaMusical = Bateria 120; Canto = Canto 110",
                "AluguelInstrumento 40 aluguel de instrumento; GravacaoEstudio 200 gravação em estúdio; Partitura 15 partitura; "
                "Recital 1.1 +10% temporada de recital",
                "PagaSom", "Estúdio | livre | EM ENSAIO | Reservar | (ocupado) | AGENDA CHEIA - nenhum estúdio livre | "
                           "estúdio(s) livre(s)"),
    "ead": D("aluno", "trilha:trilha:1 2 3", "modulos:20", "valor_modulo", "módulo(s)", "49.9 29.9 99.9 0",
             "tipo de acesso: Avulso 1, Assinante 0.7, Empresa 0.8; Vitalício 1.5",
             "módulo: ModuloBasico = Módulo básico 29.9; Intermediario = Módulo intermediário 49.9; "
             "Avancado = Módulo avançado 79.9; Bootcamp = Bootcamp 99.9",
             "CertificadoDigital 30 certificado digital; Mentoria 120 mentoria; ApostilaImpressa 60 apostila impressa; "
             "Lancamento 0.7 -30% lançamento",
             "PagaEad", "Trilha | aberta | ENCERRADA | Inscrever | (encerrada) | SEM TURMAS - nenhuma trilha aberta | "
                        "trilha(s) aberta(s)"),
    "creche": D("responsavel", "sala:sala:1 2 3", "meses:12", "mensalidade", "mês(es)", "1100 800 1600 0",
                "tipo de período: Integral 1, Meio Período 0.6, Irmãos 0.9; Funcionário 0.5",
                "mês: Bercario = Berçário 1300; Maternal = Maternal 1100; Infantil1 = Infantil I 1000; "
                "Infantil2 = Infantil II 950",
                "Alimentacao 250 alimentação; KitFraldas 120 kit fraldas; TransporteCreche 200 transporte; "
                "Antecipado 0.95 -5% pagamento antecipado",
                "PagaCreche", "Sala | com vagas | LOTADA | Matricular | (lista de espera) | SEM VAGAS - nenhuma sala com vaga | "
                              "sala(s) com vaga"),
    "merenda": D("escola", "cozinha:cozinha:1 2 3", "porcoes:1000", "custo_porcao", "porção(ões)", "4.5 3.2 6.8 0",
                 "tipo de cardápio: Regular 1, Agricultura Familiar 0.9, Especial 1.3; Emergencial 1.5",
                 "porção: CafeManha = Café da manhã 3.2; Almoco = Almoço 6.8; LancheEscolar = Lanche 4.5; "
                 "DietaEspecial = Dieta especial 7.5",
                 "FrutaExtra 1.2 fruta extra; SucoNatural 1.5 suco natural; Sobremesa 1.8 sobremesa; "
                 "RepassePnae 0.8 -20% repasse PNAE",
                 "PagaMerenda", "Cozinha | operando | PARADA | Servir | (manutenção) | SEM COZINHA - nenhuma cozinha operando | "
                                "cozinha(s) operando",
                 nomes=["EMEF Centro", "EMEF Jardim", "EMEI Vila Nova", "EE Bela Vista"]),
    "pesquisa": D("pesquisador", "laboratorio:laboratório:1 2 3", "horas:200", "custo_hora", "hora(s)", "150 90 300 0",
                  "tipo de projeto: Institucional 1, Bolsa Capes 0.5, Parceria Indústria 1.3; Iniciação 0.3",
                  "hora: Bancada = Bancada 90; Microscopia = Microscopia 300; Computacao = Computação 150; "
                  "PesquisaCampo = Pesquisa de campo 120",
                  "RevisaoIdioma 400 revisão de idioma; TaxaPublicacao 1500 taxa de publicação; Doi 50 registro DOI; "
                  "Fomento 0.6 -40% fomento",
                  "PagaFomento", "Laboratório | livre | EM USO | Reservar | (ocupado) | AGENDA CHEIA - nenhum laboratório livre | "
                                 "laboratório(s) livre(s)"),
    # ------------------------------------------------------------ 055-064 Mobilidade, Veículos e Logística
    "oficina": D("cliente", "elevador:elevador:1 2 3", "horas:40", "valor_hora", "hora(s)", "150 120 220 0",
                 "tipo de cliente: Particular 1, Frota 0.85, Seguradora 0.9; Revisão Programada 0.8",
                 "hora: Mecanica = Mecânica geral 150; Eletrica = Elétrica 160; Funilaria = Funilaria 180; "
                 "Injecao = Injeção eletrônica 200",
                 "Diagnostico 120 diagnóstico com scanner; Guincho 250 guincho; LavagemCarro 40 lavagem; "
                 "Urgencia 1.3 +30% urgência",
                 "PagaOficina", "Elevador | livre | EM SERVIÇO | Atender | (ocupado) | OFICINA CHEIA - nenhum elevador livre | "
                                "elevador(es) livre(s)"),
    "locadora": D("locatario", "veiculo:veículo:11 12 13", "diarias:30", "valor_diaria", "diária(s)", "150 110 280 0",
                  "tipo de cliente: Comum 1, Empresa 0.85, Fidelidade 0.9; Mensal 0.7",
                  "diária: Economico = Econômico 110; Sedan = Sedã 150; Suv = SUV 220; Utilitario = Utilitário 180",
                  "ProtecaoTotal 45 proteção total; CondutorAdicional 25 condutor adicional; Cadeirinha 15 cadeirinha; "
                  "Feriado 1.25 +25% feriado",
                  "PagaRodovia", "Veículo | disponível | ALUGADO | Alugar | (alugado) | SEM CARROS - nenhum veículo disponível | "
                                 "veículo(s) disponível(is)"),
    "concessionaria": D("cliente", "vaga_patio:vaga do pátio:1 2 3", "veiculos:5", "preco_veiculo", "veículo(s)",
                        "89900 65900 159900 0",
                        "tipo de compra: Varejo 1, Frotista 0.9, Taxista 0.88; Funcionário 0.85",
                        "veículo: Hatch = Hatch 65900; Sedan = Sedã 89900; Suv = SUV 159900; Picape = Picape 189900",
                        "Emplacamento 1800 emplacamento; Blindagem 45000 blindagem; KitAcessorios 2500 kit acessórios; "
                        "FeiraoMes 0.95 -5% feirão do mês",
                        "PagaMotors", "Vaga do pátio | com carro | VAZIA | Mostrar | (aguardar) | "
                                      "PÁTIO VAZIO - nenhuma vaga com carro | vaga(s) com carro"),
    "transportadora": D("cliente", "caminhao:caminhão:1 2 3", "toneladas:40", "valor_tonelada", "tonelada(s)",
                        "280 220 450 0",
                        "tipo de cliente: Spot 1, Contrato 0.85, Indústria 0.9; Retorno 0.6",
                        "tonelada: CargaSeca = Carga seca 220; Refrigerada = Carga refrigerada 380; "
                        "Perigosa = Carga perigosa 450; Fracionada = Carga fracionada 280",
                        "SeguroCarga 300 seguro de carga; Escolta 800 escolta; Descarga 150 descarga; Urgente 1.3 +30% urgente",
                        "PagaFrete", "Caminhão | disponível | EM VIAGEM | Carregar | (em viagem) | "
                                     "FROTA OCUPADA - nenhum caminhão disponível | caminhão(ões) disponível(is)"),
    "lava_rapido": D("cliente", "box:box:1 2 3", "veiculos:10", "valor_lavagem", "veículo(s)", "60 40 180 0",
                     "tipo de cliente: Avulso 1, Fidelidade 0.85, Frota 0.8; Assinante 0.7",
                     "veículo: LavagemSimples = Lavagem simples 40; LavagemCompleta = Lavagem completa 60; "
                     "Polimento = Polimento 180; HigienizacaoInterna = Higienização interna 150",
                     "Cera 25 cera; Aspiracao 15 aspiração; LavagemMotor 35 lavagem do motor; DiaChuva 0.8 -20% dia de chuva",
                     "PagaBrilho", "Box | livre | LAVANDO | Lavar | (aguardar) | FILA CHEIA - nenhum box livre | "
                                   "box(es) livre(s)"),
    "posto": D("cliente", "bomba:bomba:1 2 3", "litros:200", "preco_litro", "litro(s)", "5.89 3.99 6.19 0",
               "tipo de cliente: Comum 1, Frota Conveniada 0.95, Aplicativo 0.97; Taxista 0.93",
               "litro: Gasolina = Gasolina comum 5.89; Etanol = Etanol 3.99; Diesel = Diesel S10 6.19; "
               "Aditivada = Gasolina aditivada 6.09",
               "TrocaOleo 120 troca de óleo; Calibragem 2 calibragem; Ducha 25 ducha; ClienteFiel 0.95 -5% fidelidade",
               "PagaPosto", "Bomba | livre | ABASTECENDO | Abastecer | (aguardar) | FILA CHEIA - nenhuma bomba livre | "
                            "bomba(s) livre(s)"),
    "transporte_publico": D("passageiro", "onibus:ônibus:101 102 103", "viagens:60", "tarifa", "viagem(ns)", "4.4 2.2 6.5 0",
                            "tipo de passageiro: Comum 1, Estudante 0.5, Vale Transporte 1; Integração 0.6",
                            "viagem: Onibus = Ônibus 4.4; Metro = Metrô 5; Brt = BRT 4.4; Trem = Trem 5.2",
                            "CartaoNovo 20 cartão novo; SegundaViaCartao 15 segunda via do cartão; TaxaRecarga 1 taxa de recarga; "
                            "Domingo 0.5 -50% domingo",
                            "PagaPasse", "Ônibus | em operação | RECOLHIDO | Embarcar | (recolhido) | "
                                         "SEM FROTA - nenhum ônibus em operação | ônibus em operação"),
    "bicicletaria": D("ciclista", "bancada:bancada:1 2 3", "servicos:10", "valor_servico", "serviço(s)", "80 50 250 0",
                      "tipo de cliente: Comum 1, Equipe 0.85, Entregador 0.8; Assinante 0.75",
                      "serviço: RevisaoSimples = Revisão simples 80; RevisaoCompleta = Revisão completa 160; "
                      "BikeFit = Bike fit 250; Sangria = Sangria de freio 50",
                      "Lubrificacao 20 lubrificação; CamaraAr 35 câmara de ar; LavagemBike 30 lavagem; Inverno 0.85 -15% inverno",
                      "PagaPedal", "Bancada | livre | EM MANUTENÇÃO | Atender | (ocupada) | "
                                   "OFICINA CHEIA - nenhuma bancada livre | bancada(s) livre(s)"),
    "transporte_saude": D("paciente", "veiculo:veículo:1 2 3", "quilometros:500", "custo_km", "km", "3.5 2.8 6 0",
                          "tipo de transporte: Eletivo 1, Tratamento Fora 0.9, Urgência 1.5; Hemodiálise 0.8",
                          "km: Van = Van 2.8; MicroOnibus = Micro-ônibus 3.5; Ambulancia = Ambulância simples 4.5; "
                          "UtiMovel = UTI móvel 6",
                          "AcompanhantePaciente 30 acompanhante; Oxigenio 60 oxigênio; Cadeirante 40 adaptação para cadeirante; "
                          "Noturno 1.25 +25% noturno",
                          "RepasseSaude", "Veículo | disponível | EM VIAGEM | Agendar | (em viagem) | "
                                          "SEM VEÍCULO - nenhum veículo disponível | veículo(s) disponível(is)"),
    # ------------------------------------------------------------ 065-072 Imóveis, Condomínios e Serviços Urbanos
    "imobiliaria": D("locatario", "imovel:imóvel:11 12 13", "meses:36", "valor_aluguel", "mês(es)", "1800 1200 3500 0",
                     "tipo de cliente: Residencial 1, Comercial 1.2, Estudante 0.9; Corporativo 1.1",
                     "mês: Apartamento = Apartamento 1800; Casa = Casa 2200; SalaComercial = Sala comercial 2500; "
                     "Kitnet = Kitnet 1100",
                     "Vistoria 250 vistoria; SeguroIncendio 45 seguro incêndio; TaxaContrato 400 taxa de contrato; "
                     "ReajusteIgpm 1.06 +6% reajuste IGP-M",
                     "PagaLar", "Imóvel | disponível | ALUGADO | Visitar | (alugado) | SEM IMÓVEIS - nenhum imóvel disponível | "
                                "imóvel(is) disponível(is)"),
    "condominio": D("morador", "bloco:bloco:1 2 3", "meses:12", "taxa_mensal", "mês(es)", "650 480 950 0",
                    "tipo de unidade: Tipo A 1, Cobertura 1.5, Garden 1.2; Studio 0.7",
                    "mês: Apartamento2q = Apartamento 2 quartos 650; Apartamento3q = Apartamento 3 quartos 850; "
                    "CoberturaDuplex = Cobertura duplex 1300; LojaTerrea = Loja térrea 900",
                    "FundoReserva 65 fundo de reserva; SalaoFestas 150 salão de festas; VagaExtra 80 vaga extra; "
                    "Antecipado 0.95 -5% pagamento antecipado",
                    "PagaCondo", "Bloco | liberado | EM OBRA | Acessar | (em obra) | INTERDITADO - nenhum bloco liberado | "
                                 "bloco(s) liberado(s)"),
    "coworking": D("membro", "mesa:mesa:1 2 3", "horas:200", "valor_hora", "hora(s)", "25 15 60 0",
                   "tipo de plano: Avulso 1, Mensal 0.7, Empresa 0.65; Startup 0.6",
                   "hora: Rotativa = Estação rotativa 15; MesaFixa = Mesa fixa 25; SalaPrivativa = Sala privativa 60; "
                   "SalaReuniao = Sala de reunião 45",
                   "Impressoes 10 impressões; Locker 30 locker; EnderecoFiscal 150 endereço fiscal; "
                   "Comunidade 0.9 -10% comunidade",
                   "PagaHub", "Mesa | livre | OCUPADA | Reservar | (ocupada) | LOTADO - nenhuma mesa livre | mesa(s) livre(s)"),
    "lavanderia": D("cliente", "maquina:máquina:1 2 3", "quilos:30", "preco_quilo", "quilo(s)", "18 12 35 0",
                    "tipo de cliente: Avulso 1, Mensalista 0.8, Hotel 0.75; Estudante 0.85",
                    "quilo: LavarPassar = Lavar e passar 18; SoLavar = Só lavar 12; LavagemSeco = Lavagem a seco 35; "
                    "PecaDelicada = Peça delicada 28",
                    "Edredom 40 edredom; TiraManchas 15 tira-manchas; ColetaEntrega 10 coleta e entrega; Urgente 1.4 +40% urgente",
                    "PagaLava", "Máquina | livre | LAVANDO | Lavar | (aguardar) | LOTADO - nenhuma máquina livre | "
                                "máquina(s) livre(s)"),
    "cemiterio": D("responsavel", "quadra:quadra:1 2 3", "anos:30", "taxa_anual", "ano(s)", "350 200 900 0",
                   "tipo de concessão: Temporária 1, Perpétua 2.5, Social 0.3; Familiar 1.2",
                   "ano: Gaveta = Gaveta 200; JazigoFamiliar = Jazigo familiar 900; Ossuario = Ossuário 150; "
                   "Columbario = Columbário 180",
                   "Lapide 450 lápide; ManutencaoJazigo 120 manutenção; Exumacao 600 exumação; Isencao 0.5 -50% isenção parcial",
                   "PagaMunicipio", "Quadra | com vagas | LOTADA | Sepultar | (sem vaga) | SEM VAGAS - nenhuma quadra com vaga | "
                                    "quadra(s) com vaga"),
    "prefeitura": D("cidadao", "guiche:guichê:1 2 3", "parcelas:12", "valor_parcela", "parcela(s)", "180 90 450 0",
                    "tipo de contribuinte: Comum 1, Isento Parcial 0.5, Empresa 1.2; Aposentado 0.6",
                    "parcela: Iptu = IPTU 180; Iss = ISS 450; Alvara = Alvará 300; TaxaLixo = Taxa de lixo 90",
                    "CertidaoNegativa 25 certidão; SegundaViaGuia 5 segunda via; VistoriaObra 150 vistoria; "
                    "CotaUnica 0.9 -10% cota única",
                    "PagaCidade", "Guichê | livre | ATENDENDO | Chamar | (aguardar) | FILA CHEIA - nenhum guichê livre | "
                                  "guichê(s) livre(s)"),
    "cartorio": D("requerente", "guiche:guichê:1 2 3", "vias:10", "emolumento", "via(s)", "95 45 380 0",
                  "tipo de requerente: Comum 1, Urgente 1.5, Idoso 0.9; Gratuidade Parcial 0.5",
                  "via: Nascimento = Certidão de nascimento 45; Casamento = Certidão de casamento 60; "
                  "Escritura = Escritura 380; Procuracao = Procuração 95",
                  "Apostilamento 120 apostilamento; ReconhecimentoFirma 9 reconhecimento de firma; Autenticacao 7 autenticação; "
                  "PedidoDigital 0.9 -10% pedido digital",
                  "PagaCartorio", "Guichê | livre | ATENDENDO | Chamar | (aguardar) | FILA CHEIA - nenhum guichê livre | "
                                  "guichê(s) livre(s)"),
    "energia": D("cliente", "inversor:inversor:1 2 3", "kwh:1000", "tarifa_kwh", "kWh", "0.85 0.65 1.2 0",
                 "tipo de tarifa: Convencional 1, Branca 0.9, Rural 0.7; Baixa Renda 0.5",
                 "kWh: Residencial = Residencial 0.85; Comercial = Comercial 0.95; Industrial = Industrial 0.75; "
                 "RuralIrrigante = Rural irrigante 0.6",
                 "Telemetria 25 telemetria; InstalacaoMedidor 150 instalação; RelatorioMensal 15 relatório mensal; "
                 "HorarioPonta 1.3 +30% horário de ponta",
                 "PagaEnergia", "Inversor | gerando | DESLIGADO | Ligar | (manutenção) | SEM GERAÇÃO - nenhum inversor gerando | "
                                "inversor(es) gerando"),
    # ------------------------------------------------------------ 073-080 Serviços Pessoais, Pets e Estética
    "petshop": D("tutor", "box:box:1 2 3", "banhos:8", "valor_banho", "banho(s)", "60 45 120 0",
                 "tipo de cliente: Avulso 1, Pacote Mensal 0.8, Fidelidade 0.9; Filhote 0.7",
                 "banho: PortePequeno = Porte pequeno 45; PorteMedio = Porte médio 60; PorteGrande = Porte grande 90; "
                 "Gato = Gato 70",
                 "HidratacaoPelo 25 hidratação; CorteUnha 15 corte de unha; TaxiDog 30 táxi dog; TercaFeira 0.85 -15% terça",
                 "PagaPet", "Box | livre | EM BANHO | Agendar | (ocupado) | AGENDA CHEIA - nenhum box livre | box(es) livre(s)"),
    "veterinaria": D("tutor", "consultorio:consultório:1 2 3", "consultas:12", "valor_consulta", "consulta(s)",
                     "180 130 320 0",
                     "tipo de cliente: Particular 1, Plano Pet 0.7, Protetor 0.5; Retorno 0.4",
                     "consulta: ClinicoGeral = Clínico geral 180; DermatologiaVet = Dermatologia 220; "
                     "CirurgiaVet = Cirurgia 800; Vacinacao = Vacinação 90",
                     "ExameLab 120 exame laboratorial; Microchip 90 microchip; DiariaInternacao 250 diária de internação; "
                     "Plantao 1.5 +50% plantão",
                     "PagaVet", "Consultório | livre | EM ATENDIMENTO | Agendar | (ocupado) | "
                                "AGENDA CHEIA - nenhum consultório livre | consultório(s) livre(s)"),
    "barbearia": D("cliente", "cadeira:cadeira:1 2 3", "servicos:6", "valor_servico", "serviço(s)", "45 35 70 0",
                   "tipo de cliente: Avulso 1, Clube Barba 0.8, Fidelidade 0.9; Infantil 0.7",
                   "serviço: CorteCabelo = Corte 45; Barba = Barba 35; CorteBarba = Corte e barba 70; Degrade = Degradê 50",
                   "ToalhaQuente 10 toalha quente; Sobrancelha 15 sobrancelha; Pigmentacao 40 pigmentação; "
                   "Sabado 1.15 +15% sábado",
                   "PagaBarba", "Cadeira | livre | ATENDENDO | Agendar | (ocupada) | AGENDA CHEIA - nenhuma cadeira livre | "
                                "cadeira(s) livre(s)"),
    "salao_beleza": D("cliente", "estacao:estação:1 2 3", "servicos:6", "valor_servico", "serviço(s)", "80 50 250 0",
                      "tipo de cliente: Avulso 1, Fidelidade 0.9, Noiva 1.3; Aniversariante 0.8",
                      "serviço: Escova = Escova 50; Coloracao = Coloração 180; Manicure = Manicure 35; "
                      "Progressiva = Progressiva 250",
                      "HidratacaoCapilar 60 hidratação; DesignSobrancelha 40 design de sobrancelha; Maquiagem 120 maquiagem; "
                      "SegundaFeira 0.85 -15% segunda-feira",
                      "PagaBeleza", "Estação | livre | ATENDENDO | Agendar | (ocupada) | AGENDA CHEIA - nenhuma estação livre | "
                                    "estação(ões) livre(s)"),
    "tatuagem": D("cliente", "maca:maca:1 2 3", "horas:12", "valor_hora", "hora(s)", "300 250 450 0",
                  "tipo de cliente: Comum 1, Retorno 0.9, Flash Day 0.7; Convidado 1.2",
                  "hora: Fineline = Fineline 250; Realismo = Realismo 450; Blackwork = Blackwork 320; Aquarela = Aquarela 380",
                  "DesenhoAutoral 150 desenho autoral; Retoque 100 retoque; PomadaCicatrizacao 35 pomada de cicatrização; "
                  "SemanaTattoo 0.85 -15% semana da tatuagem",
                  "PagaInk", "Maca | livre | EM SESSÃO | Agendar | (ocupada) | AGENDA CHEIA - nenhuma maca livre | "
                             "maca(s) livre(s)"),
    "fotografia": D("cliente", "estudio:estúdio:1 2 3", "horas:12", "valor_hora", "hora(s)", "350 250 600 0",
                    "tipo de cliente: Pessoa Física 1, Empresa 1.2, Noivos 0.9; Estudante 0.8",
                    "hora: Retrato = Retrato 250; CasamentoFoto = Casamento 600; FotoProduto = Fotografia de produto 300; "
                    "Newborn = Newborn 400",
                    "AlbumImpresso 450 álbum impresso; FotoExtra 25 foto extra; Drone 300 drone; Feriado 1.3 +30% feriado",
                    "PagaFoto", "Estúdio | livre | EM ENSAIO | Reservar | (ocupado) | AGENDA CHEIA - nenhum estúdio livre | "
                                "estúdio(s) livre(s)"),
    "assistencia": D("cliente", "bancada:bancada:1 2 3", "horas:20", "valor_hora", "hora(s)", "120 90 180 0",
                     "tipo de cliente: Comum 1, Empresa 0.85, Revenda 0.8; Estudante 0.9",
                     "hora: ReparoCelular = Celular 120; ReparoNotebook = Notebook 150; Videogame = Videogame 130; "
                     "Microsolda = Placa (microsolda) 180",
                     "DiagnosticoTecnico 60 diagnóstico; Backup 80 backup de dados; PecaExpressa 50 peça expressa; "
                     "Urgente 1.4 +40% urgente",
                     "PagaReparo", "Bancada | livre | EM REPARO | Consertar | (ocupada) | LOTADO - nenhuma bancada livre | "
                                   "bancada(s) livre(s)"),
    "despachante": D("cliente", "guiche:guichê:1 2 3", "documentos:10", "valor_documento", "documento(s)", "180 120 450 0",
                     "tipo de cliente: Particular 1, Revenda 0.85, Frota 0.8; Urgente 1.5",
                     "documento: Licenciamento = Licenciamento 180; Transferencia = Transferência 450; "
                     "Emplacamento = Emplacamento 350; SegundaViaCrv = Segunda via do CRV 220",
                     "VistoriaVeicular 150 vistoria; ProcuracaoDoc 60 procuração; EntregaDocumento 30 entrega do documento; "
                     "LoteVeiculos 0.9 -10% lote de veículos",
                     "PagaDoc", "Guichê | livre | ATENDENDO | Atender | (aguardar) | FILA CHEIA - nenhum guichê livre | "
                                "guichê(s) livre(s)"),
    # ------------------------------------------------------------ 081-090 Finanças, Jurídico e Corporativo
    "banco": D("correntista", "agencia:agência:1 2 3", "parcelas:48", "valor_parcela", "parcela(s)", "450 250 1200 0",
               "tipo de conta: Digital 1, Premium 0.9, Universitária 0.95; Empresarial 1.1",
               "parcela: EmprestimoPessoal = Empréstimo pessoal 450; Consignado = Consignado 300; "
               "Veicular = Financiamento veicular 1200; Imobiliario = Financiamento imobiliário 2500",
               "SeguroPrestamista 25 seguro prestamista; TarifaCadastro 15 tarifa de cadastro; CartaoAdicional 10 cartão adicional; "
               "Portabilidade 0.9 -10% portabilidade",
               "OpenFinance", "Agência | aberta | FECHADA | Atender | (fechada) | FORA DO AR - nenhuma agência aberta | "
                              "agência(s) aberta(s)"),
    "contabilidade": D("empresa", "carteira:carteira:1 2 3", "meses:12", "honorario_mensal", "mês(es)", "600 350 1500 0",
                       "tipo de empresa: Simples 1, Mei 0.4, Lucro Presumido 1.5; Lucro Real 2.2",
                       "mês: Comercio = Comércio 600; Servicos = Serviços 550; Industria = Indústria 1200; Holding = Holding 900",
                       "AberturaEmpresa 1200 abertura de empresa; FolhaPagamento 45 folha por funcionário; "
                       "DeclaracaoIrpf 250 declaração IRPF; ContratoAnual 0.9 -10% contrato anual",
                       "PagaContabil", "Carteira | com vaga | CHEIA | Atender | (cheia) | SEM VAGA - nenhuma carteira com vaga | "
                                       "carteira(s) com vaga",
                       nomes=["Padaria Sol", "Oficina Lua", "Loja Mar", "Studio Rio"]),
    "advocacia": D("cliente", "vara:vara:1 2 3", "horas:100", "valor_hora", "hora(s)", "450 300 800 0",
                   "tipo de cliente: Pessoa Física 1, Empresa 1.3, Sindicato 0.8; Pro Bono 0.1",
                   "hora: Civel = Cível 450; Trabalhista = Trabalhista 350; Criminal = Criminal 600; Tributario = Tributário 700",
                   "Diligencia 200 diligência; Parecer 1500 parecer; CopiaProcesso 50 cópia do processo; "
                   "ContratoAnual 0.85 -15% contrato anual",
                   "PagaJuris", "Vara | com pauta | SEM PAUTA | Protocolar | (aguardar) | RECESSO - nenhuma vara com pauta | "
                                "vara(s) com pauta"),
    "seguradora": D("segurado", "corretora:corretora:1 2 3", "meses:12", "premio_mensal", "mês(es)", "180 90 450 0",
                    "tipo de cliente: Novo 1, Renovação 0.9, Frota 0.8; Jovem Condutor 1.3",
                    "mês: SeguroAuto = Seguro auto 180; SeguroVida = Seguro de vida 90; "
                    "SeguroResidencial = Seguro residencial 70; SeguroEmpresarial = Seguro empresarial 450",
                    "CarroReserva 25 carro reserva; Assistencia24h 15 assistência 24h; Vidros 12 cobertura de vidros; "
                    "SemSinistro 0.85 -15% sem sinistro",
                    "PagaSeguro", "Corretora | atendendo | FECHADA | Cotar | (fechada) | "
                                  "SEM ATENDIMENTO - nenhuma corretora atendendo | corretora(s) atendendo"),
    "rh": D("funcionario", "departamento:departamento:1 2 3", "horas_extras:60", "valor_hora", "hora(s) extra(s)",
            "45 30 90 0",
            "tipo de hora extra: Normal 1, Noturna 1.2, Domingo 2; Feriado 2",
            "hora: Operacional = Operacional 30; TecnicoRh = Técnico 45; GestaoRh = Gestão 90; Estagio = Estágio 20",
            "ValeTransporte 220 vale-transporte; ValeRefeicao 600 vale-refeição; PlanoSaude 450 plano de saúde; "
            "Coparticipacao 0.9 -10% coparticipação",
            "PagaFolha", "Departamento | com vaga | COMPLETO | Contratar | (completo) | "
                         "SEM VAGAS - nenhum departamento com vaga | departamento(s) com vaga"),
    "crm": D("contato", "funil:funil:1 2 3", "licencas:50", "valor_licenca", "licença(s)", "120 80 250 0",
             "tipo de cliente: Pequeno 1, Médio 0.9, Enterprise 0.8; Parceiro 0.75",
             "licença: PlanoBasico = Plano básico 80; PlanoPro = Plano pro 120; PlanoEnterprise = Plano enterprise 250; "
             "PlanoStartup = Plano startup 60",
             "Implantacao 2000 implantação; TreinamentoCrm 800 treinamento; IntegracaoErp 1500 integração; "
             "ContratoAnual 0.85 -15% contrato anual",
             "PagaCrm", "Funil | ativo | PAUSADO | Prospectar | (pausado) | SEM FUNIL - nenhum funil ativo | funil(is) ativo(s)"),
    "helpdesk": D("solicitante", "fila:fila:1 2 3", "horas:40", "valor_hora", "hora(s)", "90 70 150 0",
                  "tipo de contrato: Avulso 1, Contrato Mensal 0.75, Parceiro 0.8; Crítico 1.5",
                  "hora: Nivel1 = Nível 1 70; Nivel2 = Nível 2 90; Nivel3 = Nível 3 150; AtendimentoCampo = Atendimento em campo 120",
                  "AcessoRemoto 30 acesso remoto; VisitaTecnica 120 visita técnica; RelatorioSuporte 50 relatório; "
                  "ForaHorario 1.5 +50% fora do horário",
                  "PagaSuporte", "Fila | aberta | PARADA | Atender | (parada) | SEM ATENDENTES - nenhuma fila aberta | "
                                 "fila(s) aberta(s)"),
    "almoxarifado": D("requisitante", "prateleira:prateleira:1 2 3", "unidades:500", "custo_unitario", "unidade(s)",
                      "12.5 4.9 89 0",
                      "tipo de centro de custo: Produção 1, Administrativo 1.05, Manutenção 0.95; Projeto Especial 1.1",
                      "unidade: Epi = EPI 35; FerramentaUso = Ferramenta 89; MaterialEscritorio = Material de escritório 4.9; "
                      "MaterialLimpeza = Material de limpeza 12.5",
                      "Etiquetagem 2 etiquetagem; FreteInterno 30 frete interno; ContagemInventario 50 contagem de inventário; "
                      "CompraLote 0.9 -10% compra em lote",
                      "PagaCompras", "Prateleira | abastecida | VAZIA | Requisitar | (repor) | "
                                     "SEM ESTOQUE - nenhuma prateleira abastecida | prateleira(s) abastecida(s)"),
    "projetos": D("responsavel", "quadro:quadro:1 2 3", "horas:160", "valor_hora", "hora(s)", "120 90 200 0",
                  "tipo de projeto: Interno 1, Cliente 1.3, Pesquisa 0.8; Manutenção 0.9",
                  "hora: Desenvolvimento = Desenvolvimento 120; DesignProduto = Design 110; QualidadeQa = Qualidade (QA) 90; "
                  "GestaoProjeto = Gestão 150",
                  "Consultoria 300 consultoria; Documentacao 80 documentação; TreinamentoEquipe 200 treinamento; "
                  "Retainer 0.85 -15% contrato contínuo",
                  "PagaAgil", "Quadro | ativo | ARQUIVADO | Planejar | (arquivado) | SEM QUADROS - nenhum quadro ativo | "
                              "quadro(s) ativo(s)"),
    "auditoria": D("analista", "ativo:ativo:1 2 3", "horas:120", "valor_hora", "hora(s)", "250 180 400 0",
                   "tipo de contrato: Avulso 1, Contrato Anual 0.8, Governo 0.9; Emergencial 1.5",
                   "hora: PentestWeb = Pentest web 250; PentestRede = Pentest de rede 280; AuditoriaLgpd = Auditoria LGPD 220; "
                   "RespostaIncidente = Resposta a incidente 400",
                   "Reteste 800 reteste; RelatorioExecutivo 500 relatório executivo; TreinamentoPhishing 1200 treinamento antiphishing; "
                   "ParceiroSec 0.9 -10% parceiro",
                   "PagaSec", "Ativo | auditado | VULNERÁVEL | Auditar | (corrigir) | ALERTA - nenhum ativo auditado | "
                              "ativo(s) auditado(s)"),
    # ------------------------------------------------------------ 091-100 Indústria, Agro, Mídia e Genérico
    "fabrica": D("cliente", "maquina:máquina:1 2 3", "lotes:50", "custo_lote", "lote(s)", "2500 1800 4200 0",
                 "tipo de pedido: Normal 1, Recorrente 0.92, Exportação 1.1; Urgente 1.3",
                 "lote: Usinagem = Usinagem 2500; Estampagem = Estampagem 1800; MontagemIndustrial = Montagem 3200; "
                 "PinturaIndustrial = Pintura industrial 2100",
                 "InspecaoQualidade 300 inspeção de qualidade; EmbalagemIndustrial 150 embalagem; LaudoTecnico 200 laudo técnico; "
                 "Escala 0.9 -10% ganho de escala",
                 "PagaIndustria", "Máquina | livre | PRODUZINDO | Programar | (em setup) | "
                                  "PRODUÇÃO CHEIA - nenhuma máquina livre | máquina(s) livre(s)"),
    "fazenda": D("produtor", "talhao:talhão:1 2 3", "hectares:1000", "custo_hectare", "hectare(s)", "3200 2500 4800 0",
                 "tipo de produtor: Familiar 1, Cooperado 0.92, Empresarial 1.05; Arrendatário 1.1",
                 "hectare: Soja = Soja 3200; Milho = Milho 2800; Cafe = Café 4800; Algodao = Algodão 4200",
                 "AnaliseSolo 180 análise de solo; Pulverizacao 250 pulverização; SeguroRural 120 seguro rural; "
                 "PlantioDireto 0.9 -10% plantio direto",
                 "PagaAgro", "Talhão | pronto | EM COLHEITA | Plantar | (em colheita) | SEM ÁREA - nenhum talhão pronto | "
                             "talhão(ões) pronto(s)"),
    "pecuaria": D("produtor", "piquete:piquete:1 2 3", "cabecas:500", "valor_cabeca", "cabeça(s)", "2800 2200 4500 0",
                  "tipo de venda: Mercado 1, Frigorífico Parceiro 1.05, Leilão 1.1; Reposição 0.9",
                  "cabeça: Bezerro = Bezerro 2200; Novilha = Novilha 2800; BoiGordo = Boi gordo 4500; Matriz = Matriz 3800",
                  "Vacinacao 25 vacinação; Gta 15 emissão de GTA; FreteBoiadeiro 60 frete boiadeiro; "
                  "ArrobaAlta 1.08 +8% arroba em alta",
                  "PagaBoi", "Piquete | com pasto | EM DESCANSO | Soltar | (descanso) | SEM PASTO - nenhum piquete com pasto | "
                             "piquete(s) com pasto"),
    "grafica": D("cliente", "impressora:impressora:1 2 3", "milheiros:50", "preco_milheiro", "milheiro(s)", "120 80 450 0",
                 "tipo de cliente: Comum 1, Agência 0.85, Revenda 0.8; Evento 1.1",
                 "milheiro: CartaoVisita = Cartão de visita 80; Panfleto = Panfleto 120; Banner = Banner 450; Adesivo = Adesivo 150",
                 "ArteFinal 90 arte final; Verniz 60 verniz localizado; Laminacao 70 laminação; Urgente 1.5 +50% urgente",
                 "PagaGrafica", "Impressora | livre | IMPRIMINDO | Imprimir | (aguardar) | FILA CHEIA - nenhuma impressora livre | "
                                "impressora(s) livre(s)"),
    "radio_tv": D("anunciante", "faixa:faixa de horário:1 2 3", "insercoes:200", "valor_insercao", "inserção(ões)",
                  "350 180 1200 0",
                  "tipo de anunciante: Varejo 1, Agência 0.8, Governo 1.1; Patrocinador 0.7",
                  "inserção: Spot15 = Spot de 15s 180; Spot30 = Spot de 30s 350; PatrocinioPrograma = Patrocínio 1200; "
                  "Merchandising = Merchandising 900",
                  "Locucao 150 locução; Jingle 1500 jingle; Vinheta 400 vinheta; HorarioNobre 1.5 +50% horário nobre",
                  "PagaMidia", "Faixa de horário | livre | VENDIDA | Anunciar | (vendida) | GRADE CHEIA - nenhuma faixa livre | "
                               "faixa(s) livre(s)"),
    "streaming": D("assinante", "servidor:servidor:1 2 3", "meses:24", "mensalidade", "mês(es)", "39.9 25.9 59.9 0",
                   "tipo de plano: Individual 1, Família 1.5, Estudante 0.5; Anual 0.83",
                   "mês: PlanoBasico = Plano básico 25.9; PlanoHd = Plano HD 39.9; PlanoUltra = Plano 4K 59.9; "
                   "PlanoMobile = Plano mobile 19.9",
                   "TelaExtra 10 tela extra; DownloadOffline 5 download offline; CanaisEsporte 30 canais de esporte; "
                   "PromocaoStream 0.5 -50% promoção",
                   "PagaStream", "Servidor | online | FORA DO AR | Assistir | (instável) | FORA DO AR - nenhum servidor online | "
                                 "servidor(es) online"),
    "esportes": D("equipe", "quadra:quadra:1 2 3", "jogos:38", "taxa_jogo", "jogo(s)", "350 250 600 0",
                  "tipo de equipe: Amadora 1, Federada 1.2, Escolar 0.6; Veterana 0.8",
                  "jogo: Futebol = Futebol 350; Futsal = Futsal 250; Volei = Vôlei 220; Basquete = Basquete 260",
                  "Arbitragem 200 arbitragem; AmbulanciaJogo 300 ambulância; Transmissao 500 transmissão; "
                  "FinalTorneio 1.3 +30% final",
                  "PagaLiga", "Quadra | livre | EM JOGO | Agendar | (em jogo) | SEM QUADRAS - nenhuma quadra livre | "
                              "quadra(s) livre(s)",
                  nomes=["Leões FC", "Águias EC", "Tigres AC", "Falcões SC"]),
    "ong": D("doador", "projeto:projeto:1 2 3", "meses:12", "valor_mensal", "mês(es)", "50 30 200 0",
             "tipo de doador: Pessoa Física 1, Empresa 1.5, Padrinho 1.2; Voluntário 0.5",
             "mês: ProjetoEducacao = Projeto educação 50; ProjetoAlimentacao = Projeto alimentação 30; "
             "ResgateAnimal = Resgate animal 40; ProjetoSaude = Projeto saúde 60",
             "CestaBasica 120 cesta básica; KitEscolar 80 kit escolar; Agasalho 50 agasalho; "
             "DoacaoCasada 1.5 +50% doação casada",
             "PagaSolidario", "Projeto | aberto | ENCERRADO | Doar | (encerrado) | SEM PROJETOS - nenhum projeto aberto | "
                              "projeto(s) aberto(s)"),
    "igreja": D("fiel", "salao:salão:1 2 3", "meses:12", "contribuicao_mensal", "mês(es)", "100 50 300 0",
                "tipo de membro: Membro Ativo 1, Jovem 0.5, Líder 1.2; Visitante 0.3",
                "mês: Dizimo = Dízimo 100; Oferta = Oferta 50; Missoes = Missões 80; FundoConstrucao = Fundo de construção 150",
                "Retiro 250 retiro; AcampamentoIgreja 180 acampamento; MaterialEstudo 40 material de estudo; "
                "CampanhaAnual 1.1 +10% campanha",
                "PagaComunidade", "Salão | livre | EM CULTO | Reservar | (ocupado) | AGENDA CHEIA - nenhum salão livre | "
                                  "salão(ões) livre(s)"),
    # ------------------------------------------------------------ 101 Prova Prática P3 (ISW-030 Web III)
    # Cooperativa Citrícola: o cooperado entrega lotes de citros (caixas de 40,8 kg) colhidos nos talhões.
    "citricultura": D("cooperado", "talhao:talhão:1 2 3", "caixas:5000", "preco_caixa", "caixa(s)", "38 32 52 0",
                      "destino da fruta: Indústria 1, Mesa 1.25, Exportação 1.4; Refugo 0.3",
                      "caixa: LaranjaPera = Laranja Pera 38; LaranjaValencia = Laranja Valência 40; "
                      "LimaoTahiti = Limão Tahiti 45; TangerinaPonkan = Tangerina Ponkan 52",
                      "Frete 120 frete até a indústria; Classificacao 60 classificação por calibre; "
                      "CamaraFria 90 câmara fria; BonusQualidade 1.1 +10% bônus de qualidade (brix)",
                      "PagaCoop", "Talhão | pronto para colher | EM COLHEITA | Colher | (em colheita) | "
                                  "ENTRESSAFRA - nenhum talhão pronto | talhão(ões) pronto(s)"),
}
DADOS.update(construir_dados_102_300(D))

# PERFIL de um domínio: as particularidades do sistema gerado — nome da pasta, projeto e app Django, rota do app,
# DRF e o pytest.ini. Sem perfil, vale o de sempre (pasta <sistema>__<padrões>…, projeto "config", app = plural da
# entidade, rotas na raiz). Fica nos dados do domínio, então vai para o especificacao.json do sistema e continua
# valendo nas edições (sgs app, ligar, incrementar, api config).
PERFIS = {
    # O ambiente da Prova Prática P3 (ProvaPraticaP3/GUIA_Ambiente_Django_Maquinas_FATEC*.pdf): pasta provaP3,
    # `django-admin startproject cooperativa .`, `startapp citricultura`, "rest_framework" e "citricultura" em
    # INSTALLED_APPS, pytest.ini com DJANGO_SETTINGS_MODULE = cooperativa.settings e python_files = tests.py test_*.py.
    # Caminho RELATIVO: o sistema sai em sistemas_gerados/provaP3 (no lab, a mesma pasta fica em ~/provaP3).
    "citricultura": {"nome": "Prova Prática P3 — ISW-030 Desenvolvimento Web III", "pasta": "provaP3",
                     "projeto": "cooperativa", "app": "citricultura", "rota": "citricultura/", "drf": True,
                     "pytest_arquivos": "tests.py test_*.py"},
}
for _chave, _perfil in PERFIS.items():
    DADOS[_chave]["perfil"] = _perfil


def montar(dominios_base, caminho_extras=None):
    """DOMINIOS completos (300 nativos + extras personalizados de dominios_extras.json), + INFO {chave: {"id", "setor"}}.

    dominios_base: os 8 domínios originais (dados completos no gerar_sistema.py). As palavras deles passam a
    ser as do catálogo; sistema e entidade precisam bater com o catálogo (senão é erro de cadastro).
    """
    import sgs_dominios

    dominios, info, k = {}, {}, 0
    for numero, chave, sistema, entidade, palavras in ler_catalogo():
        if chave in dominios:
            raise ValueError(f"catálogo: domínio {chave!r} repetido")
        if chave in dominios_base:
            d = dict(dominios_base[chave])
            if (d["sistema"], d["entidade"]) != (sistema, entidade):
                raise ValueError(f"catálogo: {chave} diverge de gerar_sistema.DOMINIOS ({d['sistema']}/{d['entidade']})")
            d["palavras"] = palavras
        else:
            if chave not in DADOS:
                raise ValueError(f"catálogo: faltam os dados do domínio {chave!r} em dominios.py")
            dados = dict(DADOS[chave])
            if dados["nomes"] is None:
                dados["nomes"] = [NOMES[(4 * k + j) % len(NOMES)] for j in range(4)]
            k += 1
            d = {"sistema": sistema, "palavras": palavras, "entidade": entidade, **dados}
        dominios[chave] = d
        info[chave] = {"id": f"{numero:03d}", "setor": setor(numero)}
    sobra = set(DADOS) - set(dominios)
    if sobra:
        raise ValueError(f"dominios.py tem dados de domínios fora do catálogo: {sorted(sobra)}")
    for idx, item in enumerate(sgs_dominios.ler_extras(caminho_extras)):
        chave = item["chave"]
        if chave in dominios:
            continue
        dominios[chave] = sgs_dominios.construir_dados_dominio(item, k + idx)
        info[chave] = {"id": f"{int(item['id']):03d}", "setor": item.get("setor") or sgs_dominios.SETOR_PADRAO}
    return dominios, info

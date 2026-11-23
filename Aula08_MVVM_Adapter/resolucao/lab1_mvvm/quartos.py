"""
Aula 08 — Lab 1 — MVVM (RESOLVIDO).

Painel de quartos do Resort. A função original tela_quartos() decidia, no meio do
desenho, o texto do status, o rótulo do botão, o "R$" e o "LOTADO". Para testar
"quando aparece LOTADO?" era preciso ler a string da tela.

MVVM aqui:
  MODEL      = o dict do quarto (dado cru: numero, categoria, diaria, ocupado)
  VIEWMODEL  = QuartoViewModel / PainelQuartosVM → traduzem dado cru em
               dado-PRONTO-para-tela, sem saber desenhar (testáveis sem renderizar)
  VIEW       = tela_quartos_mvvm() → "burra de propósito": só costura o que o VM preparou
"""

# ---------------------------------------------------------------------------
# MODEL — dados (viriam do banco em Web III)
# ---------------------------------------------------------------------------
QUARTOS = [
    {"numero": 101, "categoria": "comum", "diaria": 200.0, "ocupado": False},
    {"numero": 201, "categoria": "suite", "diaria": 500.0, "ocupado": True},
    {"numero": 301, "categoria": "presidencial", "diaria": 1200.0, "ocupado": False},
]


# ---------------------------------------------------------------------------
# ANTES (o smell) — mantido para provar que a saída final não mudou
# ---------------------------------------------------------------------------
def tela_quartos(quartos):
    linhas = []
    livres = 0
    for q in quartos:
        if q["ocupado"]:
            status = "INDISPONIVEL"
            botao = "(ocupado)"
        else:
            status = "livre"
            botao = "Reservar"
            livres += 1
        preco = f"R$ {q['diaria']:.2f}"
        linhas.append(
            f"Quarto {q['numero']} [{q['categoria']}] - {preco} - {status} - {botao}"
        )
    if livres:
        rodape = f"{livres} quarto(s) livre(s)"
    else:
        rodape = "LOTADO - nenhum quarto livre"
    return "\n".join(linhas) + "\n" + rodape


# ---------------------------------------------------------------------------
# VIEWMODEL — prepara a "vitrine" (o maître que empra o prato)
# ---------------------------------------------------------------------------
class QuartoViewModel:
    """Prepara UM quarto para exibição. Não sabe o que é tela: entrega texto pronto."""

    def __init__(self, quarto):
        # dados que a tela mostra como estão
        self.numero = quarto["numero"]
        self.categoria = quarto["categoria"]
        # ESTADO DERIVADO: a tela não precisa saber que "disponível = não ocupado"
        self.disponivel = not quarto["ocupado"]
        # RÓTULOS CONDICIONAIS: a decisão de "como mostrar" mora aqui, num lugar só
        self.status_label = "livre" if self.disponivel else "INDISPONIVEL"
        self.botao_label = "Reservar" if self.disponivel else "(ocupado)"
        # FORMATAÇÃO: duas casas decimais e prefixo R$
        self.preco_formatado = f"R$ {quarto['diaria']:.2f}"


class PainelQuartosVM:
    """Prepara o PAINEL inteiro: um ViewModel por quarto, a contagem e o rodapé."""

    def __init__(self, quartos):
        # composição: o painel É FEITO de QuartoViewModels (não repete a lógica deles)
        self.itens = [QuartoViewModel(q) for q in quartos]
        # conta usando o estado já preparado (disponivel), não o dado cru
        self.livres = sum(1 for item in self.itens if item.disponivel)
        if self.livres:
            self.rodape = f"{self.livres} quarto(s) livre(s)"
        else:
            self.rodape = "LOTADO - nenhum quarto livre"


# ---------------------------------------------------------------------------
# VIEW — só lê o que o ViewModel preparou. ZERO if de decisão aqui.
# ---------------------------------------------------------------------------
def tela_quartos_mvvm(quartos):
    painel = PainelQuartosVM(quartos)
    linhas = [
        f"Quarto {i.numero} [{i.categoria}] - {i.preco_formatado} - "
        f"{i.status_label} - {i.botao_label}"
        for i in painel.itens
    ]
    return "\n".join(linhas) + "\n" + painel.rodape


# No Django (servidor), não há data binding: o ViewModel é só esta "preparação" chamada
# antes do render. Ex.: render(request, "painel.html", {"painel": PainelQuartosVM(qs)}).
# No Alpine.js (navegador), x-model faz o binding reativo — o MVVM "clássico".

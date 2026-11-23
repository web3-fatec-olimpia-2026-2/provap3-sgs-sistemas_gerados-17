"""
SOLUCAO DO PROFESSOR -- Lab 1 (MVVM)

Nao distribua este arquivo antes da correcao. Para validar, copie o conteudo
das duas classes por cima de quartos.py e rode os testes: todos verdes.

A ideia do MVVM aqui:
  - MODEL    = o dict do quarto (o dado cru: numero, categoria, diaria, ocupado)
  - VIEW     = a funcao tela_quartos_mvvm(), que so LE o que o VM preparou
  - VIEWMODEL= QuartoViewModel / PainelQuartosVM, que traduzem dado cru em
               dado-pronto-para-tela, SEM saber desenhar.

Regra e apresentacao agora moram no ViewModel e sao testaveis sem renderizar.
"""


class QuartoViewModel:
    def __init__(self, quarto):
        self.numero = quarto["numero"]
        self.categoria = quarto["categoria"]
        self.disponivel = not quarto["ocupado"]
        self.status_label = "livre" if self.disponivel else "INDISPONIVEL"
        self.botao_label = "Reservar" if self.disponivel else "(ocupado)"
        self.preco_formatado = f"R$ {quarto['diaria']:.2f}"


class PainelQuartosVM:
    def __init__(self, quartos):
        self.itens = [QuartoViewModel(q) for q in quartos]
        self.livres = sum(1 for i in self.itens if i.disponivel)
        if self.livres:
            self.rodape = f"{self.livres} quarto(s) livre(s)"
        else:
            self.rodape = "LOTADO - nenhum quarto livre"


# ---------------------------------------------------------------------------
# A VIEW agora e burra de proposito: nao decide nada, so le o ViewModel.
# Compare com o tela_quartos() original -- sumiu todo o 'if de negocio' daqui.
# ---------------------------------------------------------------------------
def tela_quartos_mvvm(quartos):
    painel = PainelQuartosVM(quartos)
    linhas = [
        f"Quarto {i.numero} [{i.categoria}] - {i.preco_formatado} - "
        f"{i.status_label} - {i.botao_label}"
        for i in painel.itens
    ]
    return "\n".join(linhas) + "\n" + painel.rodape

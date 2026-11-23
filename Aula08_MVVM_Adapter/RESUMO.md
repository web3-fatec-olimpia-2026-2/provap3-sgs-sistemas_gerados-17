# Aula 08 — MVVM e Adapter (aula dupla)

> ILP-037 · 09/10/2026
> Fontes: `ILP037_Aula08_Slides.pdf`, roteiros `LAB1_ROTEIRO_MVVM.md` e `LAB2_ROTEIRO_Adapter.md`,
> laboratórios (zips em `material_original/`), soluções do professor, homeworks 08a/b/c,
> `perguntas-frequentes-mvvm-adapter.pdf`, áudio. (No Teams: mapa mental e guia no NotebookLM.)

## PARTE 1 — MVVM, a 4ª arquitetura

### O smell
Mesmo com o Service (Aula 07), sobra lógica na tela: **como mostrar** — texto do status, rótulo
do botão, "R$", "LOTADO". Para testar "quando aparece LOTADO?" é preciso ler a string da tela.

### ViewModel
> Camada que pega o **dado cru** e devolve o **dado pronto para a tela**, sem saber que é uma tela.
> A View só exibe o que o ViewModel preparou.

```python
class QuartoViewModel:
    def __init__(self, q):
        self.disponivel = not q["ocupado"]                                   # estado derivado
        self.status_label = "livre" if self.disponivel else "INDISPONIVEL"   # rótulo condicional
        self.botao_label = "Reservar" if self.disponivel else "(ocupado)"
        self.preco_formatado = f"R$ {q['diaria']:.2f}"                       # formatação
```
Analogia: estoque (Model) → governança (Service) → **maître** que empra (ViewModel) → garçom que só serve (View).

### As 4 arquiteturas ⭐

| | dado | regra | quem prepara a tela | apresentação |
|---|---|---|---|---|
| MVC | Model | Controller | — | View |
| MVT (Django) | Model | View | — | Template |
| MVP | Model | Presenter | Presenter (empurra) | View passiva |
| MVVM | Model | (Service) | **ViewModel** (a View **puxa**) | View |

- **Alpine.js `x-model`** = data binding = MVVM clássico, reativo, no navegador.
- **No servidor (Django)** não há binding → ViewModel é só classe/função de **preparação** antes do
  `render`. Não invente "observables".
- **Quando NÃO criar ViewModel:** a tela mostra o dado como ele é (`{nome}`, `{preço}`) — nada a preparar.

### Service × ViewModel
**Service** separa a **regra de negócio** (o que o sistema *faz*: desconto, pode reservar?).
**ViewModel** separa a **lógica de exibição** (como *aparece*: "livre/INDISPONIVEL", "R$"). Convivem.

## PARTE 2 — Adapter (1º padrão ESTRUTURAL)

### O smell
Após migrar para o Neon, o serviço ganhou `if self.usa_neon:` em cada método — o detalhe do banco
vazou para a regra de negócio.

### Adapter (GoF — estrutural)
> Uma peça que **veste um objeto com a interface que o cliente já espera**, traduzindo as chamadas
> por dentro. O cliente não muda; o objeto adaptado não muda; o adaptador fica no meio.
> "Adapter não conserta a peça. Ele faz a peça caber." (tomada europeia × brasileira)

| Papel | No lab |
|---|---|
| **Alvo** (Target) | `ReservaRepository` (`salvar`/`buscar`) |
| **Adaptado** (Adaptee) | `ClienteNeon` (`execute`/`fetch_one`) — código de terceiro |
| **Adapter** | `NeonReservaAdapter` — traduz chamada **e** formato (`{"ticket": n}` → `n`) |

- **Prova = substituibilidade:** o mesmo teste roda com `ArmazenamentoLocal` e com o adapter.
  Trocar de banco = trocar o objeto injetado (OCP).
- **Delimitação em Python:** duck typing dispensa Adapter formal quando você controla as duas
  pontas. **Adapter se justifica quando o adaptado é de terceiro** (driver, lib de pagamento, API).
  "Adapte o que você não controla."

## Atividades

| Atividade | Resolução |
|---|---|
| Lab 1 — MVVM | `resolucao/lab1_mvvm/quartos.py` + `tests/test_painel.py` (8 originais + 3) |
| Lab 2 — Adapter | `resolucao/lab2_adapter/reservas.py` + `tests/test_adapter.py` (7 originais + 5) |
| HW 08A/08B/08C | `resolucao/homework/hw08_respostas.md` |

## Para a prova
- Explicar linha a linha o `NeonReservaAdapter.salvar` (onde está a tradução de chamada e de formato).
- Dizer por que `status_label` fica no ViewModel e não na tela.
- Service × ViewModel; quando Adapter é cerimônia (duck typing).

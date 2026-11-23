# Aula 05 — O primeiro padrão: Strategy

> ILP-037 · 04/09/2026
> Fontes: `ILP037_Aula05_Slides.pdf`, `ILP037_Aula05_LAB_ROTEIRO.md`, laboratório
> (`material_original/ILP037_Laboratorio_Aula05/`), homeworks 05a/b/c, `SOLUCAO_PROFESSOR_Aula05.py`,
> `strategy-10-questions.pdf`, `strategy-study-guide.pdf`, `faq-marco1.pdf`, `guia-fechamento-marco1.pdf`, áudios.

## 1. O smell
```python
class Reserva:
    def total(self):
        base = self.diarias * self.valor_diaria
        if self.tipo_hospede == "comum":        return base
        elif self.tipo_hospede == "fidelidade": return base * 0.90
        elif self.tipo_hospede == "parceiro":   return base * 0.80
        # cada convênio novo = mais um elif AQUI (abre a Reserva de novo)
```
Funciona — o problema é de **design**: não está **fechado para modificação**.

## 2. Strategy (GoF — comportamental)
> **Uma família de algoritmos, cada um numa classe, intercambiáveis. O objeto (contexto) recebe
> uma estratégia e DELEGA.**

```python
class TarifaFidelidade:
    def aplicar(self, base): return base * 0.90

class Reserva:
    def __init__(self, diarias, valor_diaria, tarifa):
        self.tarifa = tarifa                     # recebe a estratégia (composição)
    def total(self):
        return self.tarifa.aplicar(self.diarias * self.valor_diaria)   # delega, sem if
```

| Peça | No exemplo |
|---|---|
| Contexto | `Reserva` |
| Interface da estratégia | método `aplicar(base)` |
| Estratégias concretas | `TarifaComum`, `TarifaFidelidade`, `TarifaParceiro`, `TarifaVIP` |

- **Strategy ≠ polimorfismo:** polimorfismo é o *recurso da linguagem*; Strategy é a *arquitetura* que o organiza (contexto + família de estratégias + delegação).
- **Delegar:** o contexto transfere o cálculo para o objeto que entende daquela regra.
- **Em Python a estratégia pode ser uma função** (funções são objetos de 1ª classe): `Reserva(2, 200, lambda b: b*0.5)`.
- Estratégia pode ser **trocada em tempo de execução** (`r.tarifa = TarifaParceiro()`).

## 3. Quando NÃO usar ⭐
- Um comportamento só, que nunca varia → três classes são **cerimônia**; uma função resolve.
- "Strategy cabe quando a família **VARIA**. Sem variação, é fachada."

## 4. Refatoração com rede de segurança
Os testes fixam o comportamento: **refatorar = mudar a forma sem mudar o resultado** (400, 360, 320
continuam iguais). Se um teste fica vermelho, você quebrou algo — volte.

## 5. Marco 1 (11/09)
Avalia a **decisão de design** (Caderno). ADR com 5 seções: Contexto · Decisão · **Alternativa
descartada** (a que mais conta) · Consequência · Commit. O erro que custa nota:
**descrever** ("usamos @property") em vez de **justificar** ("escolhemos @property em vez de
validar na tela, porque…").

## 6. Atividades

| Atividade | Resolução |
|---|---|
| Lab Strategy (+ VIP, + versão com função) | `resolucao/lab/tarifa.py`; antes: `resolucao/lab/tarifa_antes.py`; testes: `resolucao/lab/tests/test_tarifa.py` |
| HW 05a — Refatore | `resolucao/homework/hw05a_README.md` (aponta para o lab) |
| HW 05b — Quando não usar (IA vedada) | `resolucao/homework/hw05b_quando_nao_usar.md` |
| HW 05c — Consolidar Marco 1 + ADR Strategy | `resolucao/homework/ADR-005-strategy-e-checklist-marco1.md` |

## 7. Para a prova
- Identificar o smell e refatorar um `if/elif` para Strategy **mantendo os testes verdes**.
- Explicar `self.tarifa.aplicar(base)` — o que é delegar e por que não há `if`.
- Dizer quando Strategy seria exagero.

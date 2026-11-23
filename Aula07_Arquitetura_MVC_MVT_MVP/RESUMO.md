# Aula 07 — Arquitetura: MVC × MVT × MVP

> ILP-037 · 18/09/2026
> Fontes: `ILP037_Aula07_Slides.pdf`, `ILP037_Aula07_LAB_ROTEIRO.md`, laboratório
> (`material_original/ILP037_Laboratorio_Aula07/`), homeworks 07a/b/c, `SOLUCAO_PROFESSOR_Aula07.py`,
> `faq-arquitetura-10-perguntas.pdf`, `study-guide-arquitetura.pdf`, áudio.

## 1. O smell: a view que faz tudo
Busca + regra (`if tipo == "fidelidade"`) + apresentação (`f"{hospede}: R$ ..."`) no mesmo laço.
Para testar a conta, é preciso chamar a view e ler texto. **A regra não tem vida própria.**

## 2. Três nomes, um princípio ⭐
> Todas dizem: **separe o dado, a regra e a apresentação.** Discordam só em *onde* cada parte mora
> e *quem chama quem*.

| | dado | regra | apresentação |
|---|---|---|---|
| **MVC** | Model | Controller | View |
| **MVT** (Django) | Model | **View** | Template |
| **MVP** | Model | Presenter | View **passiva** |

- No Django, a "**View**" é a **regra** (o Controller do MVC); o **Template** é a tela.
- MVP não é nativo do Django; a tela é um "totem burro" que repassa eventos ao Presenter e mostra o que recebe.
- "Não decorem as siglas — reconheçam a separação no código."

## 3. Extrair o Service
```python
class RelatorioService:                    # SÓ a regra; não sabe o que é web
    def calcular(self):
        linhas = [(r["hospede"], self._total(r)) for r in self.reservas]
        return linhas, sum(t for _, t in linhas)   # devolve DADOS

def relatorio_reservas_view(reservas):     # view FINA: chama e formata
    linhas, total = RelatorioService(reservas).calcular()
    return formata(linhas, total)
```
- **Testável sem HTTP:** `service.calcular()` direto — sem request, template ou servidor.
- "A regra que sabe o que é web só pode ser testada subindo a web. Testar fica caro. O que é caro,
  ninguém faz." → **Testabilidade é consequência de boa arquitetura.**
- É o **SRP em escala de camadas**. No projeto Django: `services.py`, entre View e Model.

## 4. Quando NÃO extrair (antifachada)
View que só lista e renderiza está ótima — **sem Service**. Service se justifica quando há
**cálculo, decisão ou orquestração de vários passos**.

## 5. Atividades

| Atividade | Resolução |
|---|---|
| Lab: extrair `RelatorioService` | `resolucao/lab/relatorio.py` (+ `relatorio_antes.py`), testes em `resolucao/lab/tests/test_relatorio.py` |
| HW 07a/07b/07c | `resolucao/homework/hw07_respostas.md` |

## 6. Para a prova
- Montar a tabela MVC/MVT/MVP de cabeça e explicar por que a "View" do Django é a regra.
- Extrair um service de uma função que mistura cálculo e texto, mantendo a saída idêntica.
- Dizer quando **não** criar Service.

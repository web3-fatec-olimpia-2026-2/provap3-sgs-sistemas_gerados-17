# Aula 04 — Polimorfismo: muitos tipos, uma interface

> ILP-037 · 28/08/2026
> Fontes: `ILP037_Aula04_Slides.pdf`, `ILP037_Aula04_LAB_ROTEIRO.md`, laboratório
> (`material_original/ILP037_Laboratorio_Aula04/`), homeworks 04a/b/c, `SOLUCAO_PROFESSOR_Aula04.py`,
> `polimorfismo-faq.pdf`, `polimorfismo-guia-estudo.pdf`, áudio em `midia/`.

## 1. O problema: o `if` que cresce
```python
def imprimir_diaria(quarto):
    if quarto.tipo == "comum": return 200
    elif quarto.tipo == "suite": return 500
    elif quarto.tipo == "presidencial": return 1200
    # cada categoria nova = mais um elif AQUI (mexer em código estável e testado)
```

## 2. Herdar × sobrescrever
- **Herdar:** a subclasse ganha o que é igual (construtor, métodos) — `class Suite(Quarto)`.
- **Sobrescrever (override):** a subclasse **reescreve** um método herdado — mesmo nome e
  assinatura, resposta diferente.
- Se não sobrescrever, o Python procura na filha, não acha e **sobe para a mãe** (usa o padrão).
- Sobrescreva **só o que precisa** especializar.
- Dá para reaproveitar a regra da mãe: `super().preco_noite()`.

## 3. Polimorfismo
> Vários tipos respondem ao **mesmo método**, cada um a seu modo; uma função trata todos pela
> **mesma interface**, sem perguntar o tipo.

```python
def imprimir_diaria(quarto):
    return f"{quarto.descricao()}: R$ {quarto.preco_noite()}"   # zero if
```
- O Python escolhe **em tempo de execução** qual `preco_noite()` chamar, pelo tipo real do objeto.
- **Herança ≠ polimorfismo:** herança cria a relação "é-um"; polimorfismo usa essa relação para
  **variar comportamento**.
- **Aberto ao novo:** `Chale(Quarto)` funciona em `imprimir_diaria` sem mudar uma linha →
  "aberto para crescer, fechado para quebrar" (é o **OCP**, que ganha nome na Aula 06).

| Com `if/elif` | Com polimorfismo |
|---|---|
| tipo novo = mexer na função (risco) | tipo novo = classe nova, função intacta |

## 4. Como achar oportunidade no projeto
Procure `if/elif` decidindo por **categoria/tipo** algo que é a **mesma ação**: desconto por tipo
de cliente, pagamento por forma, frete por modalidade, notificação por canal.

## 5. Ponte para padrões
Polimorfismo é o pilar de quase todos os padrões (Strategy na Aula 05, Factory Method, etc.):
o chamador depende só de uma **interface comum**.

## 6. Atividades

| Atividade | Resolução |
|---|---|
| Lab (Suite, Presidencial + desafio Chale) | `resolucao/lab/quartos.py`, `resolucao/lab/tests/test_quartos.py` (5 originais + 4 meus) |
| HW 04a — Sobrescreva | `resolucao/homework/hw04a_sobrescreva.py` + teste |
| HW 04b — O que é polimorfismo (IA vedada) | `resolucao/homework/hw04b_polimorfismo.md` |
| HW 04c — ADR polimorfismo (equipe) | `resolucao/homework/ADR-004-polimorfismo.md` |
| Extra: interface com `abc` | `resolucao/extra/interface_abc.py` + teste |

## 7. Para a prova
- Diferença herdar × sobrescrever; o que acontece se não sobrescrever.
- Por que a função polimórfica não precisa de `if` e o que significa "aberto ao novo".

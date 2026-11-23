# Aula 06 — Princípios de design: SRP e OCP · dia do Marco 1

> ILP-037 · 11/09/2026
> Fontes: `ILP037_Aula06_Slides.pdf`, `ILP037_Aula06_LAB_ROTEIRO.md`, laboratório
> (`material_original/ILP037_Laboratorio_Aula06/`), homeworks 06a/b/c, `SOLUCAO_PROFESSOR_Aula06.py`,
> `ILP037_Marco1_GUIA_com_exemplos.md`, `ILP037_Marco1_Slides_Expositiva.pdf`
> (+ `Extras/Apresentacao_Marco1/`).

## 1. O smell: a classe que faz tudo
```python
class Reserva:
    def total(self): ...                 # 1. regra de negócio
    def formatar_recibo(self): ...       # 2. apresentação
    def salvar_em_arquivo(self, c): ...  # 3. infraestrutura
```
Mudou o layout? mexe aqui. Mudou o destino (banco)? mexe aqui. Mudou a regra? mexe aqui.
**Três motivos para mudar a mesma classe.**

## 2. SRP — Single Responsibility Principle
> **Uma classe deve ter um só motivo para mudar.**

| Classe | Responsabilidade | Muda quando… |
|---|---|---|
| `Reserva` | dados + `total()` (negócio) | a regra do total muda |
| `ReciboFormatter` | `formatar(reserva)` (apresentação) | o layout muda |
| `ArquivoRepository` | `salvar(texto, caminho)` (infraestrutura) | o destino muda |

⚠️ **NÃO é "uma classe por método".** O critério é "um motivo para mudar" — separar demais é tão
ruim quanto juntar demais.

## 3. OCP — Open/Closed Principle
> **Aberto para estender, fechado para modificação**: acrescenta-se comportamento sem alterar o que
> já funciona.

- Vocês já fizeram: a `TarifaVIP` da Aula 05 entrou **sem tocar na Reserva**.
- **OCP não é prever todo futuro:** abstrai-se onde a variação **já apareceu**, não para o "e se".

## 4. Princípio × padrão ⭐

| Princípio | Padrão |
|---|---|
| diretriz geral — o **"o quê"** | solução nomeada — um **"como"** |
| OCP: "estenda sem modificar" | Strategy: políticas trocáveis |
| vale para todo o código | resolve um problema específico |

**Strategy é UM jeito de seguir o OCP** (há outros: herança + override, função como parâmetro…).
"Primeiro a mão, depois o nome."

## 5. Marco 1 — como a banca avalia
Rúbrica (guia do professor): 5 seções preenchidas 25% · **justifica, não só descreve 30%** ·
alternativa descartada real 20% · commit 10% · defesa oral 15%.
**Zera:** caderno fora do GitHub · ADRs vazios · IA não declarada · ninguém sabe defender.

## 6. Atividades

| Atividade | Resolução |
|---|---|
| Lab SRP | `resolucao/lab/recibo.py` (+ antes em `recibo_antes.py`), testes em `resolucao/lab/tests/test_recibo.py` |
| HW 06a/06b/06c | `resolucao/homework/hw06_respostas.md` |

## 7. Para a prova
- Olhar uma classe e listar os **motivos para mudar**; separar sem sobre-separar.
- Explicar por que `ReciboFormatter.formatar(reserva)` recebe a reserva por parâmetro.
- Diferença princípio × padrão com o exemplo da tarifa.

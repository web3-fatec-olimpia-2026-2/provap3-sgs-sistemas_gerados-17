# Aula 10 — Sprint 3 & Decorator

> ILP-037 · 06/11/2026
> Fontes: `ILP037_Aula10_Slides.pdf`, `ILP037_Aula10_LAB_ROTEIRO_Decorator.md`, lab (zip),
> homeworks 10a/b/c, `CHECKLIST_Sprint3_ILP-037.md`, `guia_decorator_aula10.pdf`,
> `study_guide_decorator_aula10.pdf`, áudio "Padrões Decorator, Adapter e Facade na prática".

## 1. Onde a disciplina está

| Bloco | Conteúdo | Pergunta que responde |
|---|---|---|
| Fundamentos OO | encapsulamento, herança, polimorfismo | como organizar o código |
| Comportamento | Strategy | como trocar um comportamento |
| Princípios | SRP, OCP | onde cortar e como estender |
| Arquitetura | MVC, MVT, MVP, MVVM | onde mora cada decisão |
| Estruturais | Adapter, Facade, **Decorator** | como as peças se encaixam |

**O fio de tudo:** nenhum padrão é obrigatório — a competência é **decidir se cabe e dizer por quê**.
Datas: **27/11 P3 (prova prática individual)** · 04/12 Caderno · 11/12 encerramento.

## 2. O smell: pilha de flags
```python
def preco_com_extras(diaria, noites, cafe=False, transfer=False, late=False):
    total = diaria * noites
    if cafe: total += 40.0
    if transfer: total += 80.0      # cada extra novo: + parâmetro, + if, mexe em quem chama
```
Subclasse por combinação seria pior (explosão: `ReservaComCafeETransfer`...).

## 3. Decorator (GoF — estrutural)
> Cada extra vira um **embrulho** que recebe uma reserva (ou outro extra já embrulhado),
> implementa a **mesma interface** e **acrescenta a sua parte**. Empilha em qualquer ordem, em
> tempo de execução. "O embrulho não troca o presente — acrescenta por cima."

```python
class ServicoExtra:                        # base: embrulha e delega
    def __init__(self, reserva): self._reserva = reserva
    def preco(self): return self._reserva.preco()

class ComCafeDaManha(ServicoExtra):
    def preco(self): return self._reserva.preco() + 40.0          # de dentro + a minha parte
    def descricao(self): return self._reserva.descricao() + " + cafe da manha"

ComTransfer(ComCafeDaManha(ReservaBase(200, 2))).preco()   # 400 + 40 + 80 = 520
```
- Ordem não muda o preço quando cada camada **soma valor fixo**; muda se a camada altera
  comportamento (ex.: desconto percentual) — ver `ComDescontoFidelidade` no lab.

## 4. O trio estrutural ⭐

| Padrão | O que faz | Intenção |
|---|---|---|
| **Adapter** | traduz a interface de **uma** peça | fazer **caber** |
| **Facade** | cria interface nova para **vários** subsistemas | **esconder** complexidade |
| **Decorator** | embrulha e **soma** responsabilidade, **mesma** interface | **acrescentar** sem alterar |

Adapter e Decorator embrulham um objeto; o Adapter **muda** a interface; o Decorator **mantém** —
por isso empilha.

## 5. Delimitação em Python
- O **`@decorator`** do Python decora **funções** (callable); o padrão **Decorator** decora **objetos**.
  Mesma ideia, mecanismos diferentes. (`@property` da Aula 02 era a "semente".)
- **Soma fixa → lista de extras + `sum()`** resolve; Decorator ganha quando o extra muda comportamento.
- Cadeias muito profundas são difíceis de depurar.

## 6. Atividades

| Atividade | Resolução |
|---|---|
| Lab Decorator | `resolucao/lab/reserva.py` + testes (6 originais + 11) |
| HW 10A/10B/10C | `resolucao/homework/hw10_respostas.md` |

## 7. Para a prova
- Implementar um decorador novo (ex.: `ComPet`) sem tocar nos outros.
- Explicar por que a interface igual permite empilhar e o que muda em relação ao Adapter.
- `@` do Python × padrão Decorator.

# 🧩 Kit de Revisão pré-P3 — ILP-037
### Técnicas de Programação II · FATEC Olímpia · 2026/2 · Aula 11 (13/11)
### Individual · **🔴 sem IA** · ensaio para a Prova Prática de 27/11

## 🎯 Para que serve esta atividade
- **Problema que ela resolve:** chegar na **Prova Prática (P3, 27/11)** sabendo **explicar** seu
  código — não só fazer rodar.
- **O que você vai conseguir fazer depois:** olhar um trecho de código, dizer **qual padrão** está
  ali e **por quê**, e prever o que ele faz.
- **Onde isso aparece no mercado:** em qualquer revisão de código (*code review*) e entrevista
  técnica, alguém vai pedir: "explica o que esse trecho faz e por que você fez assim".
- **Conceito que ela treina:** os padrões do semestre e a decisão de **quando aplicar** cada um.

> **🔴 Uso de IA nesta atividade: VEDADO.** A P3 é individual e sem IA. Se você treinar com a IA
> respondendo por você, vai chegar na prova sem o que ela cobra: **a sua explicação**. Use o
> material da disciplina (slides, roteiros, seu Caderno de Design).
>
> **Como a P3 funciona (combinado, por escrito):** o professor vai sortear **uma função ou bloco**
> do seu código e pedir que você: (1) diga **o que** faz; (2) **por que** foi escrita assim; (3) o
> que acontece **se** mudar um trecho. **Código funcionando sem explicação não pontua integral.**

---

## Parte 1 — Reconhecer o padrão *(escreva a resposta ao lado)*

Para cada situação, diga **qual padrão** cabe e **em uma frase, por quê**.

1. Há um `if/elif` escolhendo entre três jeitos de calcular o frete. → padrão: ______ · porquê: ______
2. Fazer um pedido chama estoque + pagamento + nota + e-mail, sempre na ordem. → ______ · ______
3. A biblioteca de pagamento usa `charge()`, mas seu sistema espera `processar()`. → ______ · ______
4. O cliente pode somar "embrulho para presente", "cartão" e "entrega expressa" em qualquer combinação. → ______ · ______

*(Gabarito no fim — tente **antes** de olhar.)*

---

## Parte 2 — Prever o resultado *(sem rodar)*

Leia e escreva **o que imprime** e **por quê**.

**2.1** (diária 200, 2 noites; café +40; transfer +80)
```python
r = ComTransfer(ComCafeDaManha(ReservaBase(200, 2)))
print(r.preco())
```
Resposta: ______  Por quê: ______________________

**2.2**
```python
class TarifaParceiro:
    def calcular(self, diaria): return diaria * 0.8
class Reserva:
    def __init__(self, diaria, tarifa): self.diaria, self.tarifa = diaria, tarifa
    def total(self): return self.tarifa.calcular(self.diaria)
print(Reserva(500, TarifaParceiro()).total())
```
Resposta: ______  Qual padrão é esse? ______

---

## Parte 3 — Achar o erro *(conceitual, não de sintaxe)*

**3.1** Um colega escreveu o decorador assim e o preço veio **errado** (sem somar o café):
```python
class ComCafeDaManha(ServicoExtra):
    def preco(self):
        return self._reserva.preco()          # <-- o que falta aqui?
```
O que corrigir: ______________________  Por quê: ______________________

**3.2** Este "Adapter" não deixa empilhar nem mantém o contrato esperado. Ele é mesmo um Adapter,
ou virou outra coisa? Explique:
```python
class Tudo:
    def salvar(self, x): ...
    def calcular_frete(self, x): ...
    def enviar_email(self, x): ...
    def gerar_pdf(self, x): ...
```
Resposta: ______________________ *(dica: quantos "trabalhos" diferentes ele faz?)*

---

## Parte 4 — A pergunta da P3 *(metacognição — escreva de verdade)*

Escolha **um** padrão que a sua equipe **aplicou** (ou **decidiu não aplicar**) no projeto e
responda, em 3–5 linhas, como se o professor tivesse perguntado na prova:
- Que **problema** no código motivou a decisão?
- **Por que** esse padrão (ou por que **nenhum**)?
- O que **mudaria** se você removesse/alterasse ele?

______________________________________________________________________

---

## 🔑 Gabarito *(olhe só depois de tentar)*

- **Parte 1:** 1) **Strategy** (troca o mesmo cálculo sem `if`); 2) **Facade** (esconde a
  orquestração de vários subsistemas); 3) **Adapter** (traduz a interface de uma peça para caber);
  4) **Decorator** (soma opcionais empilháveis mantendo a interface).
- **2.1:** **520.0** — 400 (base) + 40 (café) + 80 (transfer). Cada decorador soma a sua parte.
- **2.2:** **400.0** — 500 × 0,8. É o **Strategy** (a `Reserva` delega o cálculo à estratégia).
- **3.1:** faltou **somar a parte do café**: `return self._reserva.preco() + 40.0`. Sem isso o
  decorador só delega e não acrescenta nada.
- **3.2:** não é Adapter — virou um **God object** (faz quatro trabalhos sem relação). Adapter
  traduz **uma** interface; isto deveria ser separado (SRP).

---

*Kit de Revisão pré-P3 — ILP-037 — FATEC Olímpia — 2026/2. Exemplos executados e conferidos. Uso de IA vedado nesta atividade (preparação individual para a P3).*

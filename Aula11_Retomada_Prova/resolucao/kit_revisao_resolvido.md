# Kit de Revisão pré-P3 — RESOLVIDO e explicado

> ⚠️ O kit é para ser feito **sozinho e sem IA** (é o ensaio da P3). Use esta resolução **depois**
> de tentar, para corrigir e entender o porquê. As previsões das Partes 2 e 3 foram conferidas
> rodando — ver `verificacao_kit/`.

---

## Parte 1 — Reconhecer o padrão

| # | Situação | Padrão | Por quê (1 frase) |
|---|---|---|---|
| 1 | `if/elif` escolhendo entre 3 jeitos de calcular o frete | **Strategy** | É uma família de cálculos que varia; cada frete vira uma classe com a mesma interface e o pedido delega, sem `if` (e frete novo não reabre o código). |
| 2 | Pedido chama estoque + pagamento + nota + e-mail, sempre na ordem | **Facade** | São **vários** subsistemas orquestrados na mesma ordem; um ponto de entrada (`checkout.finalizar()`) esconde a orquestração e tira o acoplamento de quem chama. |
| 3 | Lib de pagamento usa `charge()`, o sistema espera `processar()` | **Adapter** | É **uma** peça de terceiro com interface incompatível que não controlo; o adapter traduz `processar()` → `charge()` para ela caber. |
| 4 | "embrulho para presente", "cartão", "entrega expressa" em qualquer combinação | **Decorator** | São opcionais **empilháveis** que mantêm a interface (`preco`/`descricao`) e somam a sua parte; evita flags e explosão de subclasses. |

**Como pensar (para outras situações):** procure o *smell* antes do nome —
`if/elif por tipo` → Strategy · `uma peça fala outra língua` → Adapter · `vários passos em ordem
repetidos` → Facade · `opcionais combináveis` → Decorator · `classe com vários motivos para mudar`
→ SRP · `tela decidindo rótulo/regra` → ViewModel/Service.

---

## Parte 2 — Prever o resultado (sem rodar)

### 2.1
```python
r = ComTransfer(ComCafeDaManha(ReservaBase(200, 2)))
print(r.preco())
```
**Imprime `520.0`.**
Por quê: a chamada entra pela camada de fora. `ComTransfer.preco()` chama `ComCafeDaManha.preco()`,
que chama `ReservaBase.preco()` = 200 × 2 = **400**; o café soma 40 → **440**; o transfer soma 80 →
**520**. Sai `520.0` (float) porque os `PRECO` dos decoradores são `40.0` e `80.0`.

### 2.2
```python
class TarifaParceiro:
    def calcular(self, diaria): return diaria * 0.8
class Reserva:
    def __init__(self, diaria, tarifa): self.diaria, self.tarifa = diaria, tarifa
    def total(self): return self.tarifa.calcular(self.diaria)
print(Reserva(500, TarifaParceiro()).total())
```
**Imprime `400.0`** (500 × 0,8 — float por causa do `0.8`).
**Padrão: Strategy** — a `Reserva` (contexto) recebe a estratégia no construtor e **delega**
`self.tarifa.calcular(...)`; não há `if`.

---

## Parte 3 — Achar o erro (conceitual)

### 3.1 O decorador que não soma
```python
class ComCafeDaManha(ServicoExtra):
    def preco(self):
        return self._reserva.preco()          # <-- falta a parte dele
```
**Correção:** `return self._reserva.preco() + self.PRECO` (ou `+ 40.0`).
**Por quê:** a receita do Decorator é *"chama o de dentro **e soma a sua parte**"*. Do jeito que está,
ele só **delega** (é o comportamento herdado de `ServicoExtra`) — o embrulho existe mas não acrescenta
nada, então `ComCafeDaManha(ReservaBase(200, 2)).preco()` dá 400 em vez de 440. (Mesmo erro do
"verificação de saída" do material: devolveu 200 em vez de 240.)

### 3.2 O falso "Adapter"
```python
class Tudo:
    def salvar(self, x): ...
    def calcular_frete(self, x): ...
    def enviar_email(self, x): ...
    def gerar_pdf(self, x): ...
```
**Não é Adapter — virou um _God object_.** Faz quatro trabalhos sem relação (persistência, regra de
frete, notificação, apresentação), ou seja, tem **quatro motivos para mudar** → viola o **SRP**.
Um Adapter traduz **uma** interface de **uma** peça para outra que já existe; aqui não há tradução
nenhuma. Correção: separar em `Repositorio`, `CalculadoraFrete` (ou estratégias de frete),
`Notificador` e `GeradorPdf`; se alguém precisar chamar vários em ordem, aí sim uma **Facade** que
**delega** a eles (sem reimplementar).

---

## Parte 4 — A pergunta da P3 (modelo de resposta)

> Escreva a **sua**, sobre o projeto da **sua** equipe. Abaixo, um modelo no formato que a banca
> espera (problema → por que esse padrão → o que mudaria), usando o Strategy do Resort.

"No cálculo da tarifa da reserva tínhamos um `if/elif` por tipo de hóspede que crescia a cada
convênio novo e nos obrigava a reabrir a classe `Reserva`, já testada. Escolhemos **Strategy**: cada
tarifa virou uma classe com `aplicar(base)` e a `Reserva` recebe a tarifa e delega; descartamos um
dicionário de percentuais porque a tarifa de feriado tem regra de prazo, não só percentual. Se eu
remover o Strategy e voltar ao `if`, o resultado continua igual, mas cada tarifa nova volta a mexer
na `Reserva` (perdemos o OCP) e os testes de todas as tarifas passam a depender da mesma função."

E o caso "não aplicamos": "Na tela de contato **não** criamos ViewModel: ela só exibe nome e
telefone como estão, sem rótulo condicional nem formatação — seria cerimônia."

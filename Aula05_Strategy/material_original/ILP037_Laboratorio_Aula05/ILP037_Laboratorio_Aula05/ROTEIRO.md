# 🔬 Laboratório — Aula 05 · Strategy

**ILP-037 · Refatorar o `if/elif` para Strategy · ~40 min**

> Você vai pegar uma classe `Reserva` que calcula desconto com um `if/elif` que cresce a cada tipo de hóspede (o *smell*), e refatorar para **Strategy**: cada política de tarifa vira uma classe. No fim, você acrescenta um tipo novo **sem tocar na `Reserva`** — provando que o código ficou aberto ao novo.
>
> **O que torna este lab diferente:** o código **já funciona** no começo. Os 3 testes passam. Você não está consertando um bug — está melhorando o **design**, sem quebrar o que funciona. É isso que refatorar significa.
>
> **Python puro, não Django.** Exemplos do professor. A ponte com o projeto vem no homework.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Ambiente *(3 min)*

🖥️ Na pasta do laboratório:
```bash
ls
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```
✅ Você vê `tarifa.py`, `tests/`, `pytest.ini`, e o `(.venv)` na linha.

---

## PASSO 1 — Veja o *smell*, e veja que ele funciona *(6 min)*

🖥️ Rode os testes **antes de mexer em nada**:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 3 verdes.** O código funciona — comum dá 400, fidelidade 360, parceiro 320.

📝 Abra `tarifa.py`. Olhe o método `total()`:

```python
    def total(self):
        base = self.diarias * self.valor_diaria
        if self.tipo_hospede == "comum":
            return base
        elif self.tipo_hospede == "fidelidade":
            return base * 0.90
        elif self.tipo_hospede == "parceiro":
            return base * 0.80
        else:
            raise ValueError("tipo de hospede desconhecido")
```

**O problema não é que está errado — é que cada novo tipo de hóspede obriga a abrir esta classe e mexer neste `if`.** Um novo convênio, um novo desconto, e você edita a `Reserva` de novo, arriscando quebrar o que já funciona. Esse é o *smell*.

> 💭 Os 3 testes verdes são a sua **rede de segurança**. A regra da refatoração: eles têm que continuar verdes o tempo todo. Se um ficar vermelho, você mudou o comportamento — e refatorar é mudar a forma, não o comportamento.

---

## PASSO 2 — Cada política vira uma classe *(12 min)*

📝 No topo do `tarifa.py`, **antes** da classe `Reserva`, crie uma classe para cada política de tarifa. Cada uma tem um método `aplicar(base)`:

```python
class TarifaComum:
    def aplicar(self, base):
        return base

class TarifaFidelidade:
    def aplicar(self, base):
        return base * 0.90

class TarifaParceiro:
    def aplicar(self, base):
        return base * 0.80
```

> 💭 Cada classe é uma **estratégia** — um jeito de calcular a tarifa. Elas são intercambiáveis: todas sabem `aplicar(base)`, cada uma a seu modo. Isso é polimorfismo (da Aula 04), agora organizado num padrão.

---

## PASSO 3 — A `Reserva` recebe a estratégia e delega *(10 min)*

📝 Reescreva a `Reserva`: em vez de guardar um `tipo_hospede` e decidir com `if`, ela **recebe uma estratégia** e **delega** o cálculo:

```python
class Reserva:
    def __init__(self, diarias, valor_diaria, tarifa):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        self.tarifa = tarifa          # recebe a ESTRATEGIA, nao um texto

    def total(self):
        base = self.diarias * self.valor_diaria
        return self.tarifa.aplicar(base)   # delega - sem if
```

📝 **Agora atualize os testes** para a nova assinatura. Abra `tests/test_tarifa.py` e troque o texto pela estratégia. Por exemplo:

```python
from tarifa import Reserva, TarifaComum, TarifaFidelidade, TarifaParceiro

def test_comum():
    assert Reserva(2, 200, TarifaComum()).total() == 400

def test_fidelidade():
    assert Reserva(2, 200, TarifaFidelidade()).total() == 360.0

def test_parceiro():
    assert Reserva(2, 200, TarifaParceiro()).total() == 320.0
```

> 💭 Atualizar o teste faz parte da refatoração: a interface mudou (agora se passa um objeto, não um texto), mas o **resultado** de cada teste é o mesmo — 400, 360, 320. Se os números mudassem, você teria quebrado o comportamento.

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: os 3 verdes de volta.** Mesmo resultado, design melhor. O `if/elif` sumiu.

---

## PASSO 4 — Prove que ficou aberto ao novo *(6 min)*

Agora o pagamento da refatoração. Acrescente um tipo de tarifa **novo** — sem tocar na classe `Reserva`.

📝 Em `tests/test_tarifa.py`, adicione:

```python
def test_aberto_ao_novo():
    # uma tarifa VIP nova, criada SEM mexer na classe Reserva
    class TarifaVIP:
        def aplicar(self, base):
            return base * 0.50
    assert Reserva(2, 200, TarifaVIP()).total() == 200.0
```

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 4 verdes.** Você criou um comportamento novo e a `Reserva` **nem soube** — não mudou uma linha dela. Compare com o `if/elif` do começo, onde um tipo novo obrigava a editar a `Reserva`. Isso é o Strategy pagando: **aberto para estender, fechado para modificar.**

---

## ✅ Você firmou este lab quando

- [ ] Os testes ficaram verdes o tempo todo (a rede de segurança nunca quebrou)
- [ ] O `if/elif` sumiu da `Reserva`
- [ ] Você acrescentou um tipo novo sem tocar na `Reserva`
- [ ] Você sabe dizer **quando Strategy seria exagero** (veja abaixo)

---

## ⚠️ Quando NÃO usar Strategy *(o critério que vale nota no homework)*

Strategy cabe quando há uma **família de comportamentos que varia** — várias políticas de tarifa, como aqui. **Não cabe** quando há um comportamento só, que nunca muda: aí três classes de estratégia são cerimônia inútil, e uma função simples resolve.

E uma nota de Python: aqui a estratégia poderia ser até **uma função** passada no lugar do objeto — em Python não é obrigatório criar classe. Usamos classes porque deixam o padrão visível. O importante é reconhecer a **variação**; a forma é secundária.

---

*Laboratório — Aula 05 — ILP-037 — FATEC Olímpia — 2026/2*

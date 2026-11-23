# 03 — Achar o erro (conceitual)

O código **roda**, mas o design está errado ou o padrão foi mal aplicado. Diga **o que está
errado**, **por quê** e **como corrigir**.

### E1 — Strategy que não é Strategy
```python
class Reserva:
    def __init__(self, diarias, valor, tarifa):
        self.diarias, self.valor, self.tarifa = diarias, valor, tarifa
    def total(self):
        base = self.diarias * self.valor
        if isinstance(self.tarifa, TarifaFidelidade):
            return base * 0.9
        elif isinstance(self.tarifa, TarifaParceiro):
            return base * 0.8
        return base
```

### E2 — Setter que não protege a criação
```python
class Produto:
    def __init__(self, preco):
        self._preco = preco                 # ← atenção aqui
    @property
    def preco(self): return self._preco
    @preco.setter
    def preco(self, v):
        if v < 0: raise ValueError("preço negativo")
        self._preco = v
p = Produto(-10)                            # passa?
```

### E3 — Adapter que vaza o formato do terceiro
```python
class NeonReservaAdapter(ReservaRepository):
    def __init__(self, cliente): self._cliente = cliente
    def salvar(self, reserva):
        return self._cliente.execute("INSERT_RESERVA", reserva)     # devolve {"ticket": n}
    def buscar(self, rid):
        return self._cliente.fetch_one(rid)                          # devolve {"found":..., "row":...}
```

### E4 — Facade que virou God object
```python
class RecepcaoFacade:
    def reservar(self, quarto, hospede, noites):
        if quarto in {101, 205}: return {"ok": False}
        precos = {101: 200, 201: 500}
        total = precos[quarto] * noites * (0.9 if noites > 7 else 1)
        with open("reservas.csv", "a") as f: f.write(f"{quarto},{hospede},{total}\n")
        smtplib.SMTP("smtp...").sendmail(...)
        return {"ok": True, "total": total}
```

### E5 — ViewModel com regra de negócio e HTML
```python
class PedidoViewModel:
    def __init__(self, pedido):
        self.total = pedido["valor"] * (0.9 if pedido["cliente_vip"] else 1)   # regra
        self.html = f"<span class='verde'>R$ {self.total:.2f}</span>"           # desenho
```

### E6 — SRP exagerado
```python
class CalculaDiaria: ...
class MultiplicaPorNoites: ...
class SomaTaxa: ...
class ArredondaValor: ...
class RetornaTotal: ...
```

### E7 — Decorator que muda a interface
```python
class ComCafe(ServicoExtra):
    def preco_com_cafe(self):               # ← nome diferente
        return self._reserva.preco() + 40
r = ComTransfer(ComCafe(ReservaBase(200, 2)))
print(r.preco())
```

### E8 — Service que sabe de web
```python
class RelatorioService:
    def calcular(self, request):
        reservas = request.GET.getlist("reservas")
        total = sum(...)
        return HttpResponse(f"TOTAL: {total}")
```

---
---

## Gabarito

- **E1:** É o mesmo `if/elif` disfarçado: a `Reserva` continua conhecendo cada tarifa (`isinstance`), então tarifa nova ainda reabre a `Reserva`. **Correção:** cada tarifa implementa `aplicar(base)` e a Reserva faz só `return self.tarifa.aplicar(base)` — delegar, sem perguntar o tipo.
- **E2:** **Passa** — o `__init__` grava direto em `self._preco`, pulando o setter; o objeto nasce inválido. **Correção:** `self.preco = preco` no `__init__` (passa pelo setter e valida já na criação).
- **E3:** O adapter traduz a **chamada** mas não o **formato**: `salvar` devolve `{"ticket": n}` em vez de `int`, e `buscar` devolve o embrulho do driver. O formato do terceiro vaza para o sistema. **Correção:** `return int(resp["ticket"])` e `return None if resp is None else resp["row"]`.
- **E4:** A fachada **executa** as regras (disponibilidade, tabela de preços, desconto, gravação em CSV, SMTP) em vez de **delegar** — virou God object, com vários motivos para mudar e impossível de testar sem arquivo/servidor. **Correção:** subsistemas separados (`Disponibilidade`, `Tarifa`, `Reservas`, `Notificador`) injetados no `__init__`; a fachada só chama na ordem.
- **E5:** Misturou camadas: o desconto VIP é **regra de negócio** (→ Service), e o HTML é **desenho** (→ template/View). O ViewModel deve só **preparar dados prontos**: `total_formatado = "R$ 90.00"`, `cor = "verde"`. Assim o template fica burro e a regra testável sem tela.
- **E6:** SRP **não é uma classe por método**. Esses passos são uma única responsabilidade ("calcular o total da diária") e não mudam por motivos diferentes. **Correção:** uma classe/função `calcular_total`. Separar demais é tão ruim quanto juntar demais.
- **E7:** Quebra o contrato: `ComCafe` não sobrescreve `preco()`, então só delega (o café **não** é somado) e `preco_com_cafe` nunca é chamado por quem está por fora. Resultado: `480` em vez de `520`. O Decorator **mantém a interface** — é isso que permite empilhar. **Correção:** `def preco(self): return self._reserva.preco() + 40`.
- **E8:** O Service conhece `request` e devolve `HttpResponse` — a regra voltou a "saber o que é web", então só se testa subindo a web. **Correção:** `calcular(self, reservas) -> (linhas, total)` recebendo e devolvendo **dados**; a view lê o request, chama o service e monta a resposta.

# 02 — Prever o resultado (sem rodar)

Escreva **o que imprime** e **por quê**. Só depois confira no gabarito — e, se quiser, rode
`prever/test_previsoes.py` (as respostas do gabarito estão lá como testes).

### P1 — Decorator
```python
r = ComCafeDaManha(ComLateCheckout(ReservaBase(150, 3)))   # café +40, late +60
print(r.preco())
print(r.descricao())          # base: "Reserva 3 noite(s)"
```

### P2 — Strategy trocada em tempo de execução
```python
r = Reserva(2, 300, TarifaComum())          # aplicar(base): comum=base; parceiro=base*0.8
print(r.total())
r.tarifa = TarifaParceiro()
print(r.total())
```

### P3 — Property
```python
class Conta:
    def __init__(self, saldo): self.saldo = saldo
    @property
    def saldo(self): return self._saldo
    @saldo.setter
    def saldo(self, v):
        if v < 0: raise ValueError("negativo")
        self._saldo = v
c = Conta(100)
try:
    c.saldo = -5
except ValueError as e:
    print("erro:", e)
print(c.saldo)
```

### P4 — Herança e sobrescrita
```python
class Quarto:
    def preco_noite(self): return 200
    def descricao(self): return f"{self.__class__.__name__}: R$ {self.preco_noite()}"
class Suite(Quarto):
    def preco_noite(self): return 500
class Master(Suite):
    pass
print(Master().descricao())
```

### P5 — Adapter
```python
cliente = ClienteNeon()                   # execute(...) -> {"ticket": n}, n começa em 1
repo = NeonReservaAdapter(cliente)
a = repo.salvar({"h": "Ana"})
b = repo.salvar({"h": "Bia"})
print(a, b, type(b).__name__)
print(repo.buscar(3))
```

### P6 — Facade com quarto ocupado
```python
facade = RecepcaoFacade(Disponibilidade([101]), Tarifa(), Reservas(), notif := Notificador())
print(facade.reservar(101, "Ana", 2))
print(facade.reservar(201, "Bia", 2))     # tarifa 201 = 500/noite
print(len(notif.enviadas))
```

### P7 — ViewModel
```python
painel = PainelQuartosVM([
    {"numero": 1, "categoria": "c", "diaria": 99.5, "ocupado": True},
    {"numero": 2, "categoria": "c", "diaria": 100,  "ocupado": True},
])
print(painel.livres, "|", painel.rodape, "|", painel.itens[0].preco_formatado)
```

### P8 — Decorator que muda comportamento (desconto %)
```python
a = ComDesconto10(ComTransfer(ReservaBase(100, 1)))    # transfer +80; desconto = *0.9
b = ComTransfer(ComDesconto10(ReservaBase(100, 1)))
print(a.preco(), b.preco())
```

---
---

## Gabarito

- **P1:** `550.0` e `Reserva 3 noite(s) + late checkout + cafe da manha`. Base 450; a camada de dentro (late) soma 60 → 510 e aparece **primeiro** na descrição; a de fora (café) soma 40 → 550 e aparece por último. *A descrição segue a ordem do embrulho, o preço não.*
- **P2:** `600` e depois `480.0`. Mesma `Reserva`, estratégia trocada no atributo; o contexto só delega.
- **P3:** `erro: negativo` e depois `100`. O setter barra o -5 **antes** de gravar, então o estado válido (100) é preservado.
- **P4:** `Master: R$ 500`. `Master` não sobrescreve nada → o Python sobe para `Suite` (500); `descricao` é a da `Quarto`, mas `self` é um `Master`, então `self.preco_noite()` resolve para a versão da `Suite` e o nome da classe é "Master".
- **P5:** `1 2 int` e `None`. O adapter desembrulha `{"ticket": n}` em `int`; o id 3 não existe → `fetch_one` devolve `None` e o adapter repassa `None`.
- **P6:** `{'ok': False, 'motivo': 'indisponivel'}`, depois `{'ok': True, 'reserva_id': 1, 'total': 1000.0}` e `1`. Quarto ocupado não grava nem notifica, por isso o 1º id gerado é 1 e só há 1 mensagem.
- **P7:** `0 | LOTADO - nenhum quarto livre | R$ 99.50`.
- **P8:** `162.0 170.0`. Em `a` o desconto vem por fora: (100+80)×0,9 = 162. Em `b` vem por dentro: 100×0,9 + 80 = 170. **Com camada que multiplica, a ordem importa.**

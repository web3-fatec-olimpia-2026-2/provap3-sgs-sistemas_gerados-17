# 🧪 Roteiro de Laboratório — Decorator
### ILP-037 · Aula 10 · Resort de Olímpia · Python puro · ~40 min

> **Objetivo:** somar serviços extras a uma reserva (café da manhã, transfer, late checkout)
> **empilhando embrulhos** — cada extra implementa a mesma interface e acrescenta a sua parte.
>
> **Pacote do aluno:** `ILP037_Laboratorio_Aula10_Decorator.zip`
> **Solução do professor (não distribuir):** `SOLUCAO_PROFESSOR_Aula10_Decorator.py`

---

## Antes de começar

**🖥️ terminal:**
```
unzip ILP037_Laboratorio_Aula10_Decorator.zip
cd ILP037_Lab_Decorator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v
```
**Resultado esperado:** a **maioria vermelha**. Só `test_reserva_base` passa — os decoradores
ainda só delegam, sem somar nada.

> `ModuleNotFoundError`? Confira que está **dentro** de `ILP037_Lab_Decorator` (onde está o
> `pytest.ini`) e com o `.venv` ativado.

---

## O "antes" — o cheiro

**📝 VS Code** — abra `reserva.py`. Veja `preco_com_extras()`: resolve os extras com `cafe=True`,
`transfer=True`, `late=True` e uma pilha de ifs. Cada extra novo = mais um parâmetro, mais um if,
e mexer em todo mundo que chama. É isso que o Decorator substitui.

---

## Passo 1 — O primeiro decorador (café da manhã)

**📝 VS Code** — complete `ComCafeDaManha`: chame o de dentro e **some** a sua parte:

```python
class ComCafeDaManha(ServicoExtra):
    PRECO = 40.0
    def preco(self):
        return self._reserva.preco() + self.PRECO
    def descricao(self):
        return self._reserva.descricao() + " + cafe da manha"
```

**🖥️ terminal:**
```
python3 -m pytest -v -k "um_extra"
```
**Resultado esperado:** `test_um_extra_soma_e_descreve` verde.

> **Leia o que você fez:** `ComCafeDaManha(ReservaBase(200,2))` — o decorador embrulha a reserva.
> `preco()` chama o `preco()` de dentro (400) e soma 40. O de dentro **não mudou**.

---

## Passo 2 — Os outros dois (transfer e late checkout)

**📝 VS Code** — mesma receita, mudando o valor e o texto:

```python
class ComTransfer(ServicoExtra):
    PRECO = 80.0
    def preco(self):
        return self._reserva.preco() + self.PRECO
    def descricao(self):
        return self._reserva.descricao() + " + transfer"

class ComLateCheckout(ServicoExtra):
    PRECO = 60.0
    def preco(self):
        return self._reserva.preco() + self.PRECO
    def descricao(self):
        return self._reserva.descricao() + " + late checkout"
```

**🖥️ terminal — rode tudo:**
```
python3 -m pytest -v
```
**Resultado esperado:** **6 verdes**.

---

## Passo 3 — Empilhar

Repare no teste `test_dois_extras_empilham`:
```python
ComTransfer(ComCafeDaManha(ReservaBase(200.0, 2)))
```
É um embrulho dentro do outro. O `ComTransfer.preco()` chama o `ComCafeDaManha.preco()`, que chama
o `ReservaBase.preco()`. Cada camada **soma só a sua parte** — por isso
`test_ordem_nao_muda_o_preco` passa: tanto faz a ordem, o total é o mesmo.

> **A chave:** todos têm a **mesma interface** (`preco`/`descricao`). É isso que permite empilhar.
> Se cada extra tivesse um método diferente (como no Adapter), não dava.

---

## ✅ Pronto quando...
- [ ] `python3 -m pytest` mostra **6 passed**
- [ ] cada decorador **chama o de dentro e soma** — não reescreve a reserva
- [ ] você consegue explicar por que a ordem dos extras não muda o preço

---

## Delimitação em Python (o freio)

- **O `@` do Python é outra coisa:** `@decorator`/`@property` decoram **funções** (um callable). O
  padrão **Decorator** do GoF (este lab) decora **objetos** para somar responsabilidade. Mesma
  ideia de embrulhar, mecanismos diferentes.
- **Soma fixa não precisa de Decorator:** se o extra só acrescenta um número, uma **lista de
  extras + `sum()`** já resolve. O Decorator ganha quando o extra também muda **comportamento**.
- **Cadeias muito profundas** ficam difíceis de depurar.

### Decorator × Adapter (para o Homework 2)
- Ambos **embrulham um objeto**.
- **Adapter** **muda** a interface (traduz para outra que já existe) — para a peça **caber**.
- **Decorator** **mantém** a mesma interface e só **soma** comportamento — por isso **empilha**.

*Fonte da delimitação: GIRIDHAR, Aprendendo Padrões de Projeto em Python. Ficha formal do padrão:
GAMMA et al., Padrões de Projetos.*

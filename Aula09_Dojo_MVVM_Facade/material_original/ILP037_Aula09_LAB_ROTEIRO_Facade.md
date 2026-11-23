# 🧪 Roteiro de Laboratório — Facade
### ILP-037 · Aula 09 · Resort de Olímpia · Python puro · ~40 min

> **Objetivo:** esconder a orquestração de quatro subsistemas (Disponibilidade, Tarifa,
> Reservas, Notificador) atrás de uma fachada única — `RecepcaoFacade.reservar(...)`.
>
> **Pacote do aluno:** `ILP037_Laboratorio_Aula09_Facade.zip`
> **Solução do professor (não distribuir):** `SOLUCAO_PROFESSOR_Aula09_Facade.py`

---

## Antes de começar

**🖥️ terminal:**
```
unzip ILP037_Laboratorio_Aula09_Facade.zip
cd ILP037_Lab_Facade
python3 -m pytest -v
```
**Resultado esperado:** a **maioria vermelha**. A `RecepcaoFacade` ainda não orquestra nada.
(Um teste passa por acaso — o que só confere que o método `reservar` existe.)

> `ModuleNotFoundError`? Confira que está **dentro** de `ILP037_Lab_Facade` (onde está o
> `pytest.ini`).

---

## O "antes" — o cheiro

**📝 VS Code** — abra `recepcao.py`. Veja `fazer_reserva_na_mao()`: o cliente chama os **quatro**
subsistemas na ordem (disponibilidade → tarifa → grava → notifica) e ainda carrega a regra
(se ocupado, aborta). Toda tela que reservar repetiria isso. É o acoplamento que a fachada resolve.

---

## Passo 1 — Guardar os subsistemas

**📝 VS Code** — complete o `__init__` da `RecepcaoFacade`:

```python
    def __init__(self, disponibilidade, tarifa, reservas, notificador):
        self._disp = disponibilidade
        self._tar = tarifa
        self._rep = reservas
        self._notif = notificador
```

**🖥️ terminal:**
```
python3 -m pytest -v -k "so_fala_com_a_facade"
```
Já deve estar verde (confirma que a fachada tem o ponto de entrada `reservar`).

---

## Passo 2 — O caminho feliz (quarto livre)

**📝 VS Code** — no `reservar`, orquestre os quatro na ordem e devolva o resultado:

```python
    def reservar(self, quarto, hospede, noites):
        if not self._disp.esta_livre(quarto):
            return {"ok": False, "motivo": "indisponivel"}
        total = self._tar.calcular(quarto, noites)
        rid = self._rep.gravar(quarto, hospede, noites, total)
        self._notif.enviar(hospede, f"Reserva {rid} confirmada - total R$ {total:.2f}")
        return {"ok": True, "reserva_id": rid, "total": total}
```

**🖥️ terminal:**
```
python3 -m pytest -v
```
**Resultado esperado:** **5 verdes**.

> **Leia os verdes:** `test_reserva_ok_grava_no_repositorio` e `test_reserva_ok_notifica_o_hospede`
> provam que a fachada **orquestrou** — gravou e notificou — sem o cliente tocar nos subsistemas.
> `test_quarto_ocupado_nao_grava_nem_notifica` prova que a regra (abortar se ocupado) está dentro.

---

## Passo 3 — Compare com o "na mão"

Abra `fazer_reserva_na_mao()` de novo e ponha lado a lado com o seu `reservar()`. É a **mesma
sequência** — mas agora mora **num lugar só**, atrás de um nome simples. O cliente deixou de
conhecer os quatro subsistemas.

**A fachada NÃO reimplementou a regra** de nenhum subsistema — ela só os chamou na ordem. Isso é
o coração do Facade: **orquestrar**, não executar.

---

## ✅ Pronto quando...
- [ ] `python3 -m pytest` mostra **5 passed**
- [ ] a fachada chama os quatro subsistemas; não reescreve a lógica de nenhum
- [ ] você consegue explicar por que o cliente agora só precisa conhecer a `RecepcaoFacade`

---

## Delimitação em Python (o freio)

- **Às vezes uma função basta:** se a orquestração é simples e sem estado, uma função de módulo
  já é a fachada — não precisa de classe.
- **Facade não é prisão:** ela não impede o acesso direto aos subsistemas; só oferece o caminho fácil.
- **Cuidado com o *God object*:** a fachada **delega**; não vira um monstro que faz tudo. Não
  enfileire chamadas numa fachada só por enfeite.

### Facade × Adapter (para o Homework 2)
- **Adapter:** muda a interface de **uma** peça (um driver) para ela **caber** numa interface existente.
- **Facade:** cria uma interface **nova e simples** na frente de **vários** subsistemas, para **esconder** a complexidade.

*Fonte da delimitação: GIRIDHAR, Aprendendo Padrões de Projeto em Python. Ficha formal do padrão:
GAMMA et al., Padrões de Projetos.*

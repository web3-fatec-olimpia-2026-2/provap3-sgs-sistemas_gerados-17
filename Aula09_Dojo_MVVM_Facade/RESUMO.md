# Aula 09 — Dojo de MVVM & Facade

> ILP-037 · 16/10/2026
> Fontes: `ILP037_Aula09_Slides.pdf`, `ILP037_Aula09_DOJO_MVVM_GUIA.md`, `ILP037_Aula09_LAB_ROTEIRO_Facade.md`,
> zips do Dojo e do Lab, soluções do professor, homeworks 09a/b/c, `faq-facade-adapter (1).pdf`,
> `guia-estudo-facade-adapter.pdf`, áudio.

## PARTE 1 — Coding Dojo (Randori): MVVM de novo
- **Dojo** = treino em grupo, revezando no teclado; sem nota. Objetivo: tornar o movimento reflexo.
- Kata: painel de check-in que decide **selo** (VERDE/AMARELO/CINZA), **rótulo** e a **regra**
  (só `confirmada` **e** `pago` faz check-in).
- Movimento: `CheckinViewModel` com `pode_checkin`, `selo`, `acao_label`.
- "Status novo 'em análise'? Mexe no ViewModel; a tela nem sabe."

## PARTE 2 — Facade (estrutural)

### O smell: o cliente orquestra tudo
`fazer_reserva_na_mao(...)` conhece **4 subsistemas**, a **ordem** e a **regra**; cada tela que
reserva repete isso; um 5º passo muda todas.

### Facade
> **Um ponto de entrada simples que esconde a orquestração de vários subsistemas.** O cliente fala
> só com a fachada; ela chama os bastidores na ordem certa. ("A recepção não faz as camas — sabe a
> quem pedir, e em que ordem.")

```python
class RecepcaoFacade:
    def __init__(self, disp, tar, rep, notif): ...      # segura os subsistemas
    def reservar(self, quarto, hospede, noites):        # UM ponto de entrada
        if not self._disp.esta_livre(quarto): return {"ok": False, "motivo": "indisponivel"}
        total = self._tar.calcular(quarto, noites)
        rid = self._rep.gravar(quarto, hospede, noites, total)
        self._notif.enviar(hospede, f"Reserva {rid} confirmada - total R$ {total:.2f}")
        return {"ok": True, "reserva_id": rid, "total": total}
```

### Facade ≠ Adapter ⭐

| | Adapter (Aula 08) | Facade (Aula 09) |
|---|---|---|
| quantos objetos | **um** (o driver incompatível) | **vários** subsistemas |
| interface | **traduz** para uma que **já existe** | **cria uma nova**, mais simples |
| intenção | fazer a peça **caber** | **esconder** a complexidade |

### Delimitação em Python
- **Às vezes uma função basta** (orquestração simples, sem estado). Classe quando há subsistemas/config a segurar.
- **Não é prisão**: não impede acesso direto aos subsistemas.
- **Cuidado com o God object**: a fachada **delega**, não executa a regra de cada subsistema.

## Atividades

| Atividade | Resolução |
|---|---|
| Dojo MVVM | `resolucao/dojo_mvvm/checkin.py` + testes (4 originais + 2) |
| Lab Facade | `resolucao/lab_facade/recepcao.py` + testes (5 originais + 6) |
| HW 09A/09B/09C | `resolucao/homework/hw09_respostas.md` |

## Para a prova
- Escrever uma fachada que orquestra subsistemas **sem** reimplementar regra.
- Tabela Adapter × Facade (um × vários; traduz × cria interface nova).
- Quando o Facade é exagero e o risco de God object.

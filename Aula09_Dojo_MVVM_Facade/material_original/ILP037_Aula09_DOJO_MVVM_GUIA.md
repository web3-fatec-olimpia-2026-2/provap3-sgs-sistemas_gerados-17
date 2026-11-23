# 🥋 Guia do Coding Dojo — MVVM (Randori)
### ILP-037 · Aula 09 · para o professor conduzir · ~33 min

> **Pacote do kata:** `ILP037_Dojo_Aula09_MVVM.zip` (base vermelha, projetável).
> **Solução:** `SOLUCAO_PROFESSOR_Aula09_Dojo_MVVM.py` (não projetar antes).
> Objetivo do Dojo: **reproduzir** o movimento do MVVM da Aula 08 num cenário novo, firmando-o.

---

## Formato — Randori

- A turma resolve **uma** base, juntos. Uma máquina projetada.
- **Reveza no teclado** a cada teste que passa (ou a cada ~4 min). Quem digita **fala em voz
  alta** o que pensa; a plateia só sugere quando o piloto pede.
- **Sem nota.** O valor é o processo: reconhecer o cheiro e aplicar o movimento em grupo.
- Se a turma for tímida, **você abre** (pilota o 1º teste) e passa o teclado.

---

## O cenário

Painel de **check-in do dia** na recepção. Cada reserva tem `status`
(`confirmada`/`pendente`) e `pago` (True/False). A tela `painel_checkin()` decide — no meio do
laço — o **selo** (VERDE/AMARELO/CINZA), o **rótulo do botão** e a **regra** (só `confirmada` +
`pago` faz check-in). É o mesmo cheiro da Aula 08.

**Movimento:** extrair `CheckinViewModel` com `pode_checkin`, `selo`, `acao_label` (+ `hospede`,
`quarto`). 4 testes, começam vermelhos.

---

## Condução passo a passo (sugestão de tempo)

| Tempo | O que fazer |
|---|---|
| 0–3 min | Projetar `painel_checkin()`. Perguntar à turma: "onde está a decisão de exibição? e a regra?" |
| 3–6 min | Rodar `python3 -m pytest -v` → 4 vermelhos. Ler **um** erro em voz alta com a turma. |
| 6–12 min | Piloto 1: preencher `hospede`, `quarto` e `pode_checkin`. Rodar. Ver `test_dados_preservados` e parte do 1º teste reagirem. |
| 12–22 min | Troca de piloto: `selo` e `acao_label` para o caso VERDE e AMARELO. Rodar a cada passo. |
| 22–30 min | Troca de piloto: caso CINZA (pendente). Rodar → **4 verdes**. |
| 30–33 min | Fechar: "qual teste **lia** a tela? Nenhum. Por quê o `selo` está no ViewModel e não na tela?" |

---

## Gabarito do movimento (para você acompanhar)

```python
class CheckinViewModel:
    def __init__(self, reserva):
        self.hospede = reserva["hospede"]
        self.quarto = reserva["quarto"]
        self.pode_checkin = reserva["status"] == "confirmada" and reserva["pago"]
        if self.pode_checkin:
            self.selo = "VERDE"; self.acao_label = "Fazer check-in"
        elif reserva["status"] == "confirmada":
            self.selo = "AMARELO"; self.acao_label = "Aguardando pagamento"
        else:
            self.selo = "CINZA"; self.acao_label = "Nao disponivel"
```

---

## Critério de "pronto" (Dojo)
- [ ] 4 verdes em `python3 -m pytest`
- [ ] nenhum teste lê a string da tela
- [ ] a turma consegue dizer, em uma frase, por que `pode_checkin` virou atributo do ViewModel

## Se o Dojo fluir rápido
Puxe a reflexão: "e se amanhã entrar um status novo, 'em análise'? Onde você mexe — na tela ou no
ViewModel?" (resposta: no ViewModel; a tela nem sabe). Isso prepara a cabeça para o Facade
(mudança isolada num ponto só).

## Se o Dojo travar
É o lugar certo para travar. Desacelere, volte ao erro, resolva junto. O travamento aqui vale
mais que uma aula inteira sem erro — é diagnóstico gratuito de quem não firmou o MVVM.

*Fonte do conteúdo: material próprio (Aula 08, MVVM). Prática no formato Coding Dojo/Randori.*

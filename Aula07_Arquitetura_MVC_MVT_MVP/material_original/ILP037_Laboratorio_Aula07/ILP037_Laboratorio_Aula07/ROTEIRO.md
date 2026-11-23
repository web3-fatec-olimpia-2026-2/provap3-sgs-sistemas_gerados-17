# 🔬 Laboratório — Aula 07 · Extrair um Service testável sem HTTP

**ILP-037 · Arquitetura: a regra de negócio não sabe o que é web · ~35 min**

> Você vai pegar uma "view" que **faz coisas demais** — calcula os totais **e** monta o texto da resposta — e extrair a regra de negócio para um **Service** que se testa **sem subir servidor**. A view fica fina: só orquestra.
>
> **Por que isto importa:** hoje, para testar o cálculo, você é obrigado a chamar a view inteira e ler o texto. Depois da refatoração, você testa a regra **direto**, sem HTTP, sem request, sem template. Testabilidade é consequência de boa arquitetura — e é o que o SRP da semana passada faz em escala de camadas.
>
> **Python puro, não Django.** A função imita uma view do Django (recebe dados, devolve texto), mas roda em qualquer máquina — para focar no conceito, não na configuração.
>
> **Marcações:** 🖥️ terminal · 📝 editor · ✅ resultado esperado.

---

## PASSO 0 — Ambiente *(3 min)*

🖥️ Na pasta do laboratório:
```bash
ls
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```
✅ Você vê `relatorio.py`, `tests/`, `pytest.ini`, e o `(.venv)` na linha.

---

## PASSO 1 — Veja o *smell* *(6 min)*

🖥️ Rode os testes:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: 1 verde, 1 vermelho.**
- ✅ `test_saida_final` — passa (o relatório funciona)
- ❌ `test_service_sem_http` — falha (`RelatorioService` não existe ainda)

📝 Abra `relatorio.py`. Olhe a `relatorio_reservas_view`. Ela faz **duas coisas misturadas**:
1. **Calcula** o total de cada reserva com desconto (regra de negócio)
2. **Monta** o texto do relatório (apresentação)

**O *smell*:** a regra de negócio está **presa dentro da view**. Para testar só o cálculo — "uma fidelidade de 2×100 dá 180?" — você é obrigado a chamar a view inteira e procurar o número no meio do texto. A regra não tem vida própria.

> 💭 Numa view Django de verdade, seria pior: você teria que simular um `request`, subir o ambiente, e ler um `HttpResponse`. A regra de negócio ficaria refém da camada web.

---

## PASSO 2 — Entenda o alvo: MVC, MVT, MVP *(5 min)*

Todas as arquiteturas que você vai ver hoje — MVC, MVT (do Django), MVP — dizem a **mesma coisa**: **separe** o que é dado, o que é regra, e o que é apresentação. Elas discordam só em *onde* cada parte mora e *quem* conversa com quem.

O que elas têm em comum, e é o que importa: **a regra de negócio não deve saber o que é web.** Se ela sabe, você não consegue testá-la sem subir a web — e testar fica caro, então ninguém testa.

O teste `test_service_sem_http` é a sua especificação: ele quer um `RelatorioService` com um método `calcular()` que devolve **dados** (não texto), testável sozinho.

---

## PASSO 3 — Extraia o Service *(15 min)*

📝 No `relatorio.py`, crie a classe `RelatorioService` — só o cálculo, devolvendo **dados**:

```python
class RelatorioService:
    def __init__(self, reservas):
        self.reservas = reservas

    def _total_reserva(self, r):
        base = r["diarias"] * r["valor"]
        descontos = {"fidelidade": 0.90, "parceiro": 0.80}
        return base * descontos.get(r["tipo"], 1.0)

    def calcular(self):
        linhas = [(r["hospede"], self._total_reserva(r)) for r in self.reservas]
        total_geral = sum(t for _, t in linhas)
        return linhas, total_geral
```

📝 Agora deixe a view **fina** — ela só chama o service e formata:

```python
def relatorio_reservas_view(reservas, request=None):
    linhas, total_geral = RelatorioService(reservas).calcular()
    corpo = "\n".join(f"{nome}: R$ {total:.2f}" for nome, total in linhas)
    return f"RELATORIO\n{corpo}\nTOTAL: R$ {total_geral:.2f}"
```

> 💭 Repare no que aconteceu: o `RelatorioService` **não sabe o que é web**. Ele recebe dados, devolve dados. A view virou uma casca fina que **orquestra** — pega o resultado do service e formata. Cada um tem uma responsabilidade (é o SRP da Aula 06, agora entre camadas).

🖥️ Rode:
```bash
python3 -m pytest tests/ -v
```
✅ **Esperado: os 2 verdes.** A saída final continua idêntica (você não quebrou nada), e agora a regra é testável sozinha.

---

## PASSO 4 — Veja a testabilidade que você ganhou *(6 min)*

🖥️ No Python, teste a regra **sem tocar na view**:
```bash
python3
```
```python
>>> from relatorio import RelatorioService
>>> svc = RelatorioService([{"hospede":"Teste","diarias":5,"valor":100,"tipo":"parceiro"}])
>>> svc.calcular()
([('Teste', 400.0)], 400.0)
```
✅ Você calculou e conferiu a regra **sem view, sem request, sem texto**. Isso é o que "testável sem HTTP" quer dizer — e é impossível de fazer quando tudo está grudado na view. Saia com `exit()`.

---

## ✅ Você firmou este lab quando

- [ ] Os 2 testes estão verdes
- [ ] O `RelatorioService` não tem nada de "web" dentro dele
- [ ] Você sabe explicar por que a saída idêntica prova que a refatoração foi segura
- [ ] Você entende por que testar a regra ficou **mais fácil** depois

---

## 🔗 A ponte com o seu projeto *(o homework)*

No projeto da sua equipe (Django), a mesma coisa acontece: as **views** tendem a inchar — buscam dados, aplicam regra **e** montam a resposta. O homework pede que você ache uma view assim no projeto e **planeje** (não precisa implementar) como extrair um Service. É o MVT do Django ganhando uma camada de serviço testável.

> **MVT do Django:** Model (dados) · View (a lógica — é o "Controller" do MVC) · Template (apresentação). O Service que você extraiu hoje é uma camada **a mais**, entre a View e o Model, onde a regra de negócio complexa mora — testável sem HTTP.

---

*Laboratório — Aula 07 — ILP-037 — FATEC Olímpia — 2026/2*

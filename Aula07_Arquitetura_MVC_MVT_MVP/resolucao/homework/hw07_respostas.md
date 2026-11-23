# Homeworks da Aula 07

## 07a — Extraia o Service
Resolvido no laboratório: [`../lab/relatorio.py`](../lab/relatorio.py).

| Critério | Onde |
|---|---|
| Service com a regra e nada de web (4) | `RelatorioService` + `test_service_nao_conhece_web` |
| Teste do Service sem chamar a view (3) | `test_service_sem_http`, `test_desconto_por_tipo`, `test_lista_vazia` |
| Saída final idêntica (2) | `test_saida_identica_a_versao_faz_tudo` (compara com `relatorio_antes.py`) |

## 07b — A regra não sabe o que é web (IA vedada — modelo de estudo)

**Modelo (4 linhas):**
Se o cálculo do desconto mora dentro da view, a única porta para executá-lo é uma requisição:
preciso montar request, subir o Django e garimpar o número no HTML, então cada teste é lento e
chato e acaba não sendo escrito. Tirando a regra para um Service que só recebe e devolve dados,
consigo chamar `calcular()` direto e checar dezenas de casos em milissegundos, o que me deixa
mudar o código sem medo — e de quebra a mesma regra pode servir uma API ou um relatório sem copiar a conta.

**Checklist (10 pts):** regra presa à web só se testa subindo a web (4) · conecta a separação ao
ganho de testabilidade (4) · autoral, 3–5 linhas (2).

## 07c — ADR planejando a extração de um Service (equipe) — modelo

```markdown
# ADR 007 — Extrair um ReservaService da view `checkout`

## Contexto
A view `checkout` busca a reserva, calcula o total (diárias × valor, desconto por tipo de hóspede,
taxa de turismo de 5%) e monta o contexto do template. A regra de preço está presa na view: só dá
para testá-la com o test client, simulando um POST.

## Decisão
Extrair `ReservaService.calcular_total(reserva)` para `reservas/services.py`, devolvendo um
dicionário com base, desconto, taxa e total. A view passa a: buscar a reserva → chamar o service →
montar o contexto.

## Alternativa descartada
Deixar a regra na view e testar com `Client().post(...)`. Descartado: teste lento, acoplado à URL/
template, e a regra não poderia ser reaproveitada no relatório financeiro nem na API.
Não extraímos service da view `lista_quartos`: ela só lista e renderiza (seria fachada).

## Consequência
Regra testável sem HTTP e reaproveitável. Custo: um arquivo/camada a mais para a equipe entender.

## Status
Planejado — extração na sprint (Marco 2).
```

Esqueleto de como ficaria no Django (ilustrativo):
```python
# reservas/services.py  — não importa nada de django.http
class ReservaService:
    DESCONTOS = {"fidelidade": 0.90, "parceiro": 0.80}
    def calcular_total(self, diarias, valor, tipo):
        base = diarias * valor
        return base * self.DESCONTOS.get(tipo, 1.0)

# reservas/views.py — fina
def checkout(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    total = ReservaService().calcular_total(reserva.diarias, reserva.valor, reserva.tipo)
    return render(request, "reservas/checkout.html", {"reserva": reserva, "total": total})
```

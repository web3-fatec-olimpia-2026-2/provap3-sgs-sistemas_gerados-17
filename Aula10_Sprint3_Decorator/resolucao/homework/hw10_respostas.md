# Homeworks da Aula 10

## 10A — Lab Decorator
[`../lab/reserva.py`](../lab/reserva.py) → 6 testes originais + 11 meus (as 8 combinações batem
com a versão de flags; extra repetido; decorador que muda comportamento).

## 10B — Decorator × Adapter (IA vedada — modelo de estudo)

**Modelo (4 linhas):**
Os dois guardam um objeto dentro de outro, mas com objetivos opostos. O Adapter existe porque a
peça de dentro fala uma língua diferente da que o sistema espera, então por fora ele oferece **outra**
interface (`salvar`) e traduz para a de dentro (`execute`) — não faz sentido adaptar um adapter.
O Decorator **mantém a mesma** interface por dentro e por fora (`preco`/`descricao`) e só soma algo
ao resultado; como quem está por fora parece igual a quem está por dentro, ele mesmo pode ser
embrulhado de novo, e é isso que deixa empilhar `ComTransfer(ComCafeDaManha(...))`.

**Checklist:** mudar × manter a interface · manter a interface ⇒ poder empilhar · 3–5 linhas.

## 10C — ADR do Decorator + checklist do Sprint 3 (equipe) — modelo

```markdown
# ADR 011 — Decorator nos adicionais do pedido de reserva

- Status: aceito

## Contexto
`reservas/services.py::calcular_total(reserva, cafe=False, transfer=False, spa=False, pet=False)`
cresceu para 4 flags. O "pet" não soma valor fixo: cobra 15% sobre as diárias; o "spa" depende do
número de hóspedes. A descrição do que foi contratado é montada em outro lugar, separada do preço.

## Decisão
APLICAMOS Decorator: `ReservaComponente` (preco/descricao) e decoradores `ComCafe`, `ComTransfer`,
`ComSpa`, `ComPet`, empilhados conforme o formulário.

## Justificativa
Os extras não são só números fixos (pet = percentual; spa = por hóspede), então uma lista + `sum()`
não bastaria; cada camada soma comportamento mantendo a interface, por isso empilha e preço e
descrição andam juntos. Não confundir com o `@` do Python (decora função, não objeto).
NÃO aplicamos no "desconto de cupom": é um único percentual fixo — um campo e uma conta resolvem.

## Consequências
Novo adicional = nova classe; `calcular_total` e quem chama não mudam (OCP). Custo: cadeia longa é
mais difícil de depurar — limitamos a montagem a uma função `montar_reserva(form)`.
```

Checklist do Sprint 3: ver o modelo em
[`../../material_original/CHECKLIST_Sprint3_ILP-037.md`](../../material_original/CHECKLIST_Sprint3_ILP-037.md)
— a seção **3 (Preparação para a P3)** está trabalhada em `Treino_Prova/`.

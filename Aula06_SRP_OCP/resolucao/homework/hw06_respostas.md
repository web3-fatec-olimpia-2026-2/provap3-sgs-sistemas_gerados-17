# Homeworks da Aula 06

## 06a — Separe as responsabilidades
Resolvido no laboratório: [`../lab/recibo.py`](../lab/recibo.py) (3 classes + as duas linhas de
comentário no fim do arquivo) e [`../lab/tests/test_recibo.py`](../lab/tests/test_recibo.py)
(`test_recibo_identico_ao_da_versao_faz_tudo` compara com [`recibo_antes.py`](../lab/recibo_antes.py)).

Cuidado com o exagero (critério de 2 pts): **não** criei uma classe por método. São três
responsabilidades → três classes. `emitir_recibo` é só uma função que junta as peças.

## 06b — Princípio ou padrão? (IA vedada — modelo de estudo)

**Modelo (4 linhas):**
Um princípio é um objetivo de qualidade que serve para qualquer trecho do código; o OCP pede que
eu consiga acrescentar comportamento sem editar o que já está funcionando e testado. Um padrão é
uma receita com nome para chegar lá num tipo de problema específico. Na tarifa, o OCP era a meta
("convênio novo não pode obrigar a abrir a Reserva") e o Strategy foi o caminho escolhido: cada
tarifa numa classe trocável — mas eu poderia atingir o mesmo princípio de outro jeito, como herança
com método sobrescrito (Aula 04) ou uma função passada por parâmetro.

**Checklist (10 pts):** princípio = diretriz geral, o "o quê" (3) · padrão = solução nomeada, um
"como" (3) · Strategy é um jeito de seguir o OCP (3) · autoral (1).

## 06c — Responsabilidade misturada (equipe, opcional) — modelo de ADR

```markdown
# ADR 006 — Responsabilidade misturada na view `lista_reservas`

## Contexto
A view `lista_reservas` faz três coisas: busca as reservas no banco (ORM), calcula o total com
desconto de cada uma (regra de negócio) e monta o texto do relatório (apresentação).

## Decisão
Registrado como dívida de design para o Marco 2: hoje funciona e separar agora atrasaria a Sprint.
Quando separar: regra → `services.py`; formatação → template/serializer; a view só orquestra.

## Consequência
Ao separar: a regra fica testável sem subir o Django e sem request. Custo de deixar: cada mudança
de layout ou de desconto mexe na mesma função, e o teste exige montar request + banco.
```

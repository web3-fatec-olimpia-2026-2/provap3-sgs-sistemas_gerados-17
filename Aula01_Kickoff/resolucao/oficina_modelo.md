# Oficina Aula 01 — Modelagem em objetos (modelo de preenchimento)

> A oficina é feita **pela equipe, sobre o tema do projeto de Web III**. Abaixo, um modelo
> preenchido com o domínio-exemplo que o professor usa em todas as aulas (hotel), para servir
> de referência de *como* responder cada passo. Troque pelo domínio da sua equipe.

## 1. Entidades (substantivos do negócio, no singular)
Hóspede · Quarto · Reserva · Pagamento · Funcionário

## 2. O que cada entidade guarda (atributos)
| Entidade | Atributos |
|---|---|
| Hóspede | nome, documento, telefone, hospedado |
| Quarto | número, tipo (standard/luxo), diária, disponível |
| Reserva | hóspede, quarto, data de entrada, data de saída, status |
| Pagamento | reserva, valor, forma, data |
| Funcionário | nome, cargo |

## 3. O que cada entidade sabe fazer (métodos — ações da PRÓPRIA entidade, verbo no infinitivo)
| Entidade | Métodos |
|---|---|
| Hóspede | fazer_check_in(), fazer_check_out(), esta_hospedado() |
| Quarto | ocupar(), liberar(), calcular_diaria() |
| Reserva | confirmar(), cancelar(), calcular_total(), quantidade_de_noites() |
| Pagamento | aprovar(), estornar() |

> Atenção ao critério: "ações da própria entidade, não coisas que outra pessoa faz com ela".
> Ex.: `Reserva.calcular_total()` é da reserva; "recepcionista cria reserva" não é método de Reserva.

## 4. Quem conhece quem (relações)
```
Hóspede ──faz──> Reserva ──ocupa──> Quarto
                    │
                    └──é paga por──> Pagamento
```

## 5. Entidade central
**Reserva** — é ela que liga o hóspede ao quarto e ao pagamento; quase toda regra de negócio
(datas, total, cancelamento) passa por ela.

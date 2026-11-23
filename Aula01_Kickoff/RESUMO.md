# Aula 01 — Kickoff: o acordo, a engrenagem e o objeto

> ILP-037 · 07/08/2026 · Prof. José Ceron Neto
> Fontes: `material_original/_FATEC____ILP037___Aula_01.pdf`, `Folha_da_Oficina_Aula01_ILP-037.pdf`

## 1. Como a disciplina funciona

- 100% laboratório, **sobre o mesmo projeto/repositório de Web III** (segunda constrói → sexta entende e refatora).
- Artefato próprio: **Caderno de Design** (`/docs/design/`): registro de decisões (ADRs), catálogo de padrões, diário de refatoração e diagramas.
- **Critério que mais reprova:** *padrão aplicado sem um problema que o justifique conta zero* (e exagero desconta). Avalia-se **reconhecer o problema, decidir se o padrão cabe e justificar a alternativa descartada** — não decorar nome/diagrama.
- Avaliação: `Média = Cad×0,4 + Marcos×0,3 + Contínua×0,2 + Portfólio×0,1`. A "rodada individual de 27/11" é a **P3 (prova prática)**.
- IA: livre para explicar conceitos; **vedada** na arguição, defesa dos marcos e rodada de 27/11. "IA é permitida. Não saber explicar o que ela produziu, não." Assistentes exageram em padrões (Factory/Singleton onde bastava uma função) — **isso é o erro que a rubrica pune**.

## 2. Classe × objeto

| Conceito | Definição | Analogia |
|---|---|---|
| **Classe** | Descrição de um tipo: quais dados guarda e quais operações oferece. Existe **uma vez**, no código-fonte. | Planta do apartamento-tipo |
| **Objeto (instância)** | Entidade concreta criada **em execução** a partir da classe, com seus **próprios valores**. | Cada apartamento construído |
| **Atributo** | Dado mantido pelo objeto (seu estado). `objeto.atributo` | |
| **Método** | Operação declarada na classe e invocada sobre um objeto. | |
| **`self`** | 1º parâmetro de todo método de instância; recebe o objeto sobre o qual o método foi chamado. | |

**Erro mais frequente:** escrever `nome = ...` em vez de `self.nome = ...` dentro do método — o primeiro cria uma variável local que morre ali; o segundo altera o objeto.

```python
class Hospede:
    def __init__(self, nome, documento):   # construtor: roda na criação do objeto
        self.nome = nome                    # atributo de instância
        self.documento = documento
        self.hospedado = False

    def fazer_check_in(self):               # método de instância
        self.hospedado = True

ana = Hospede("Ana Souza", "123")
bruno = Hospede("Bruno Lima", "456")
ana.fazer_check_in()
ana.hospedado    # True
bruno.hospedado  # False  → estado é do OBJETO, não da classe
```

**Por que OO existe:** com dado e comportamento separados, cada entidade nova exige variáveis novas e alterar a função. Com dado+comportamento reunidos, entidade nova = objeto novo; nenhum outro trecho muda. *Todo padrão de projeto do semestre é um arranjo entre objetos.*

## 3. Oficina — modelagem em objetos (roteiro)

1. **Entidades** (substantivos do negócio, no singular) → candidatas a classe.
2. **O que cada uma guarda** → atributos.
3. **O que cada uma sabe fazer** (ações da própria entidade, verbo no infinitivo) → métodos.
4. **Quem conhece quem** (setas com o motivo) → relações.
5. **Entidade central** (e por quê, em uma frase).

A folha vira o tema da equipe, o `models.py` (Web III) e a 1ª página do Caderno de Design.

## 4. Atividades da aula

| Atividade | Onde está resolvida |
|---|---|
| Homework 01 — Meu objeto do dia a dia (classe com 3 atributos e 3 métodos; não pode ser hóspede/quarto/reserva) | `resolucao/homework/hw01_meu_objeto.py` + teste |
| Homework 01b — Classe × objeto com suas palavras (3 a 5 linhas) | `resolucao/homework/hw01b_classe_x_objeto.md` |
| Oficina — folha da equipe | `resolucao/oficina_modelo.md` (modelo de preenchimento usando o domínio-exemplo de hotel) |

## 5. Para a prova (P3)

- Saber explicar `self`, construtor `__init__`, atributo de instância e por que o estado é do objeto.
- Diferença classe × objeto em uma frase.

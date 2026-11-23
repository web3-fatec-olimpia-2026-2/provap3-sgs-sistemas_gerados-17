# 📝 Homework 02a — Proteja um atributo

**ILP-037 Técnicas de Programação II · FATEC Olímpia · CST em DSM · 2026/2**
**Individual · Prazo: quarta-feira, 20/08, 23h59 · 10 pontos**

---

## O que você precisa saber antes de começar

Esta tarefa é sobre **encapsulamento** — fazer um objeto proteger os próprios dados de valores inválidos.

**O problema.** Quando você cria uma classe, os atributos ficam "públicos": qualquer código pode escrever qualquer coisa neles. Veja:

```python
class Produto:
    def __init__(self, nome, estoque):
        self.nome = nome
        self.estoque = estoque

p = Produto("Café", 10)
p.estoque = -50      # o objeto ACEITA isso, sem reclamar
```

Um estoque de **menos cinquenta** não faz sentido, mas o código aceitou. A regra ("estoque não pode ser negativo") existe só na sua cabeça — o código não garante nada.

**A solução: `@property` com `setter`.** Ela transforma o atributo numa operação que **valida antes de gravar**:

```python
class Produto:
    def __init__(self, nome, estoque):
        self.nome = nome
        self.estoque = estoque        # usa o setter abaixo

    @property                          # o jeito de LER (getter)
    def estoque(self):
        return self._estoque           # note o sublinhado: dado interno

    @estoque.setter                    # o jeito de ESCREVER (setter)
    def estoque(self, novo):
        if novo < 0:
            raise ValueError("estoque nao pode ser negativo")
        self._estoque = novo
```

Agora `p.estoque = -50` **levanta um erro** em vez de aceitar. O objeto se protege.

Três nomes para guardar:
- **atributo interno** (`self._estoque`, com sublinhado): onde o dado fica guardado de verdade
- **getter** (`@property`): o método que roda quando alguém **lê** `p.estoque`
- **setter** (`@estoque.setter`): o método que roda quando alguém **escreve** `p.estoque = ...`, e que **valida**

---

## A tarefa

No seu curso anterior você já criou uma classe simples — uma entidade do seu dia a dia (um carro, um aluno, uma ordem de serviço, o que for). **Se você não tem nenhuma, crie uma agora**, com pelo menos dois atributos.

**Faça:**

1. Na sua classe, escolha **um atributo que tenha uma regra** — um valor que não pode ser qualquer coisa.
   Exemplos de regra: uma idade não pode ser negativa; uma nota vai de 0 a 10; uma quantidade não fica abaixo de zero; um preço não é negativo.

2. Transforme esse atributo numa **`@property` com `setter`** que valida a regra e levanta **`ValueError`** quando o valor é inválido — igual ao exemplo do `estoque` acima.

3. Embaixo da classe, escreva **três linhas de comentário** respondendo: qual regra você protegeu, e **por que escolheu esse atributo** e não outro.

---

## Como entregar

- Um arquivo **`.py`** com a sua classe. *(Se preferir escrever à mão, uma foto legível serve.)*
- Entregue no **Teams**, na tarefa correspondente do Módulo 02.

---

## Como será avaliado *(10 pontos)*

| Critério | Pontos |
|---|---|
| O `setter` realmente barra o valor inválido (levanta `ValueError`) | 4 |
| A regra escolhida faz sentido para aquela entidade | 3 |
| Você escolheu um atributo que **tem** regra — não um texto livre qualquer | 2 |
| As três linhas explicam a escolha | 1 |

**Uma dica que também é critério:** não coloque `@property` em atributo que não tem regra (um nome, um texto livre). Proteger o que não precisa de proteção é só peso no código. A habilidade aqui é escolher **onde** proteger.

---

## Uso de IA nesta tarefa

**Nível 2 — permitido com declaração.** Você pode usar IA para tirar dúvida ou destravar. Mas:
- se copiar mais de 5 linhas geradas, escreva num comentário: `# Assistido por IA (ferramenta): "resumo do que pedi"`;
- você precisa **saber explicar cada linha** — isso pode ser cobrado depois.

---

*Homework 02a — ILP-037 — FATEC Olímpia — 2026/2*

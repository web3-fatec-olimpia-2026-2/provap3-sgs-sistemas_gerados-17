# Aula 02 — Guardar bem: encapsulamento e propriedades

> ILP-037 · 14/08/2026
> Fontes: `ILP037_Aula02_Encapsulamento.pdf`, `complementar_onedrive/guia-estudo-encapsulamento.pdf`,
> `guia-faq-encapsulamento.pdf`, `homeworks_onedrive/*.md`, 8 vídeos em `material_original/midia/`
> e o branch `aula-02` do repositório `Extras/repo_ilp_referencia`.

## 1. O problema: atributo público = "cofre sem fechadura"

```python
class Reserva(models.Model):          # model de Web III: CLASSE = MODEL = TABELA
    diarias = models.IntegerField()
    valor = models.DecimalField(max_digits=8, decimal_places=2)

r = Reserva(); r.valor = -50; r.diarias = 0; r.save()   # aceita e grava lixo
```
A regra de negócio ("ao menos 1 diária", "valor nunca negativo") existe só na cabeça do programador.

## 2. Encapsulamento

> **Princípio pelo qual um objeto controla o acesso ao próprio estado**: em vez de deixar
> qualquer código ler/escrever seus atributos, expõe operações que garantem que ele nunca entre
> em estado inválido.

- Sem encapsulamento: quem escreve no dado precisa validar — e vai esquecer; a regra se espalha.
- Com encapsulamento: o objeto valida sozinho, num lugar só.
- Python não tem "privado" de verdade: há a **convenção do sublinhado** (`self._valor`) + a ferramenta **`@property`**.

## 3. `@property` + setter (getter/setter transparentes)

```python
class Reserva:
    def __init__(self, diarias, valor_diaria):
        self.diarias = diarias              # passa pelo setter → valida já na criação
        self.valor_diaria = valor_diaria

    @property
    def valor_diaria(self):                 # GETTER: roda em r.valor_diaria
        return self._valor_diaria           # dado interno, com sublinhado

    @valor_diaria.setter
    def valor_diaria(self, novo):           # SETTER: roda em r.valor_diaria = x
        if novo < 0:
            raise ValueError("valor_diaria nao pode ser negativo")
        self._valor_diaria = novo

    @property
    def total(self):                        # PROPERTY CALCULADA (sem setter = só leitura)
        return self.diarias * self.valor_diaria
```

- **Para quem usa, nada muda** (`r.valor = 100`, `print(r.valor)`). Isso é **refatoração**: mudar por dentro preservando o comportamento por fora — "o verbo da disciplina".
- **Atributo calculado** (`total`): não guardar dado derivado, senão `diarias` muda e `total` fica desatualizado (dois dados que deveriam concordar e não concordam).
- `@property` é um **decorador** (embrulha a função e acrescenta comportamento), mesmo mecanismo do `@login_required` do Django → semente do padrão **Decorator** (Aula 10).

## 4. Quando NÃO usar `@property` (critério antifachada)

| Merece `@property` | Não precisa |
|---|---|
| Tem regra (valor ≥ 0, diárias ≥ 1) | Texto livre sem regra (um nome) |
| Depende de outros (total = diárias × valor) | Dado em que qualquer valor serve |
| Não pode mudar depois de criado (só leitura) | |

> "Proteção sem um problema que a justifique é cerimônia."

## 5. TDD (vídeos 03–06 e branch `aula-02`)

1. 🔴 Escreve o teste antes da classe → falha (`ModuleNotFoundError`).
2. 🟢 Classe mínima para passar.
3. 🔴 Teste do valor negativo → `DID NOT RAISE` (a classe aceitava lixo).
4. 🟢 `@property` + setter com `ValueError`.
5. Repetir para `diarias` e `total` (calculado).

⚠️ **Pegadinha encontrada no repositório de referência:** `diarias.setter` usa `if value <= 1`,
o que **rejeita uma reserva de 1 diária** — a regra correta é `if value < 1` (como no guia de
estudo). Os testes do repositório não pegam porque nenhum testa `diarias = 1`. Na minha
resolução há um teste que cobre exatamente esse limite.

## 6. ADR — Architecture Decision Record (1ª entrada do Caderno de Design)

Um arquivo por decisão, em `/docs/design/`: **Contexto** (problema) · **Decisão** ·
**Alternativa descartada** (a seção que mais conta) · **Consequência** · **Commit**.

## 7. Atividades

| Atividade | Resolução |
|---|---|
| Lab guiado pelos vídeos (Reserva com TDD) | `resolucao/lab/reserva.py` + `resolucao/lab/test_reserva.py` |
| HW 02a — Proteja um atributo | `resolucao/homework/hw02a_proteja_atributo.py` + teste |
| HW 02b — O que é encapsulamento | `resolucao/homework/hw02b_encapsulamento.md` |
| HW 02c — ADR 001 (equipe) | `resolucao/homework/ADR-001-protecao-de-campo.md` |

## 8. Para a prova
- Explicar linha a linha um getter/setter e por que o `__init__` usa `self.x = x` (passa pelo setter).
- Saber dizer **onde não** usar `@property`.
- Saber por que `total` é calculado e não guardado.

# ADR 001 — Encapsulamento com @property em ViagemCerta

- Status: aceito (exemplo de estudo gerado)
- Família: Fundamento de OO — Aulas 02 e 03

## Contexto
Um atributo público aceita qualquer valor: `obj.noites = 0` ou `obj.valor_noite = -50` passariam e o `total` ficaria errado — a regra existiria só na cabeça de quem programa.

## Decisão
APLICAMOS **Encapsulamento com @property**. O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter.

## Alternativa descartada
Validar só no formulário da tela — não protege quem cria o objeto pelo shell, admin, importação ou outro código.

## Consequências
O objeto nunca fica inválido e o erro aparece perto da causa; em troca, quem cria a Viagcert precisa tratar `ValueError`.
Quando NÃO usar: Atributo sem regra (texto livre) fica simples — `@property` sem problema que a justifique é cerimônia. No model Django a regra vai em `validators`/`clean()`: setter em campo quebra ModelForm, admin e ORM.

## Onde está no código
`nucleo/entidades.py` · testes: `tests/test_entidades.py`

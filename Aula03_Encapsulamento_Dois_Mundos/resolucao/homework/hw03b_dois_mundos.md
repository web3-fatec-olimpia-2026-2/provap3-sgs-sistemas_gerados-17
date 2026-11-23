# Homework 03b — O mesmo conceito, dois mundos

> ⚠️ **Nível 3 (IA vedada)** — escreva a sua versão antes de olhar. Este é um modelo de estudo
> para conferir se você cobriu os 3 pontos avaliados.

**Modelo (5 linhas):**
Os dois fazem a mesma coisa — encapsulamento, impedir que um valor inválido entre no objeto.
Numa classe Python comum o objeto vive sozinho, então a própria linguagem me dá o `@property`
com setter para interceptar a escrita. No Django, o campo do model não é só um atributo: é a
descrição de uma coluna que o ORM usa para montar consultas, que o ModelForm usa para gerar o
formulário e que o admin usa para editar; se eu trocar o campo por uma `@property`, ele deixa
de ser campo e some do formulário, do admin e dos filtros (`filter(diaria__gte=...)`). Por isso
lá a regra vai num validador (`MinValueValidator`) ou no `clean()`, que esses mecanismos
conhecem e executam (via `full_clean()`/ModelForm — o `save()` sozinho não valida).

**Checklist (10 pts):** mesmo princípio (3) · por que o Django precisa de validador:
form/admin/ORM (4) · `@property` no campo quebraria esses usos (2) · autoral, 3–5 linhas (1).

## Código de apoio (para entender, não para entregar)

```python
# Python puro — o objeto se protege sozinho
class Quarto:
    @property
    def diaria(self): return self._diaria
    @diaria.setter
    def diaria(self, v):
        if v < 0: raise ValueError("diaria negativa")
        self._diaria = v

# Django — o CAMPO declara a regra; form/admin/full_clean() executam
from django.core.validators import MinValueValidator
from django.db import models

class Quarto(models.Model):
    diaria = models.DecimalField(max_digits=8, decimal_places=2,
                                 validators=[MinValueValidator(0)])

    @property            # no model, @property só para dado CALCULADO
    def receita_maxima(self):
        return self.diaria * self.capacidade
```

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Pedido(models.Model):
    TIPOS = [
        ("comum", "Comum"),
        ("fidelidade", "Fidelidade"),
        ("atacado", "Atacado"),
        ("funcionario", "Funcionario")
    ]


    cliente = models.CharField("cliente", max_length=120)
    produto = models.IntegerField("produto", validators=[MinValueValidator(1)])
    quantidade = models.IntegerField("quantidade", validators=[MinValueValidator(1), MaxValueValidator(50)])
    preco_unitario = models.DecimalField("preco unitario", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    observacao = models.CharField("observacao", max_length=200, blank=True, default="")
    tipo = models.CharField("tipo de cliente", max_length=30, choices=TIPOS, default="comum")

    @property
    def total(self):
        return self.quantidade * self.preco_unitario


    def __str__(self):
        return f"{self.cliente} - {self.quantidade} unidade(s)"

"""
MODEL (o "M" do MVT). Encapsulamento no MUNDO DJANGO (Aula 03):
  * a regra de cada campo vai em validators — o ModelForm, o admin e o full_clean() as executam;
  * @property aqui só para dado CALCULADO (total); setter em campo quebraria form/admin/ORM;
  * pegadinha: save() sozinho NÃO valida (ver tests/test_models.py).
"""
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

    cliente = models.CharField("cliente", max_length=120)  # obrigatório: blank=False é o padrão
    produto = models.IntegerField("produto", validators=[MinValueValidator(1)])
    quantidade = models.IntegerField("quantidade", validators=[MinValueValidator(1), MaxValueValidator(50)])
    preco_unitario = models.DecimalField("preco unitario", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    observacao = models.CharField("observacao", max_length=200, blank=True, default="")  # sem regra
    tipo = models.CharField("tipo de cliente", max_length=30, choices=TIPOS, default="comum")

    @property
    def total(self):
        """Dado CALCULADO (quantidade × preco_unitario): nunca guardado, nunca desatualizado."""
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.cliente} - {self.quantidade} unidade(s)"

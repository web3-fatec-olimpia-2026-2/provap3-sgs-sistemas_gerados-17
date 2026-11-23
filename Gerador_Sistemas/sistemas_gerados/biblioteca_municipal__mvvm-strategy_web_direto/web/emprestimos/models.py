"""
MODEL (o "M" do MVT). Encapsulamento no MUNDO DJANGO (Aula 03):
  * a regra de cada campo vai em validators — o ModelForm, o admin e o full_clean() as executam;
  * @property aqui só para dado CALCULADO (total); setter em campo quebraria form/admin/ORM;
  * pegadinha: save() sozinho NÃO valida (ver tests/test_models.py).
"""
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Emprestimo(models.Model):
    TIPOS = [
        ("comum", "Comum"),
        ("estudante", "Estudante"),
        ("professor", "Professor"),
        ("visitante", "Visitante")
    ]

    leitor = models.CharField("leitor", max_length=120)  # obrigatório: blank=False é o padrão
    exemplar = models.IntegerField("exemplar", validators=[MinValueValidator(1)])
    dias = models.IntegerField("dias", validators=[MinValueValidator(1), MaxValueValidator(30)])
    taxa_dia = models.DecimalField("taxa dia", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    observacao = models.CharField("observacao", max_length=200, blank=True, default="")  # sem regra
    tipo = models.CharField("tipo de leitor", max_length=30, choices=TIPOS, default="comum")

    @property
    def total(self):
        """Dado CALCULADO (dias × taxa_dia): nunca guardado, nunca desatualizado."""
        return self.dias * self.taxa_dia

    def __str__(self):
        return f"{self.leitor} - {self.dias} dia(s)"

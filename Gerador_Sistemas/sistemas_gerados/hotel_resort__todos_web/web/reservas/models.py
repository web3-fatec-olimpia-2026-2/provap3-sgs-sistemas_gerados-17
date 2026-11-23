"""
MODEL (o "M" do MVT). Encapsulamento no MUNDO DJANGO (Aula 03):
  * a regra de cada campo vai em validators — o ModelForm, o admin e o full_clean() as executam;
  * @property aqui só para dado CALCULADO (total); setter em campo quebraria form/admin/ORM;
  * pegadinha: save() sozinho NÃO valida (ver tests/test_models.py).
"""
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Reserva(models.Model):
    TIPOS = [
        ("comum", "Comum"),
        ("fidelidade", "Fidelidade"),
        ("parceiro", "Parceiro"),
        ("vip", "VIP")
    ]

    hospede = models.CharField("hospede", max_length=120)  # obrigatório: blank=False é o padrão
    quarto = models.IntegerField("quarto", validators=[MinValueValidator(1)])
    diarias = models.IntegerField("diarias", validators=[MinValueValidator(1), MaxValueValidator(30)])
    valor_diaria = models.DecimalField("valor diaria", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    observacao = models.CharField("observacao", max_length=200, blank=True, default="")  # sem regra
    tipo = models.CharField("tipo de hóspede", max_length=30, choices=TIPOS, default="comum")

    @property
    def total(self):
        """Dado CALCULADO (diarias × valor_diaria): nunca guardado, nunca desatualizado."""
        return self.diarias * self.valor_diaria

    def __str__(self):
        return f"{self.hospede} - {self.diarias} diária(s)"

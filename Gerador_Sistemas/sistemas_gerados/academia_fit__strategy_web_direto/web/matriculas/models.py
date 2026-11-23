"""
MODEL (o "M" do MVT). Encapsulamento no MUNDO DJANGO (Aula 03):
  * a regra de cada campo vai em validators — o ModelForm, o admin e o full_clean() as executam;
  * @property aqui só para dado CALCULADO (total); setter em campo quebraria form/admin/ORM;
  * pegadinha: save() sozinho NÃO valida (ver tests/test_models.py).
"""
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Matricula(models.Model):
    TIPOS = [
        ("mensal", "Mensal"),
        ("universitario", "Universitario"),
        ("corporativo", "Corporativo"),
        ("familia", "Familia")
    ]

    aluno = models.CharField("aluno", max_length=120)  # obrigatório: blank=False é o padrão
    turma = models.IntegerField("turma", validators=[MinValueValidator(1)])
    meses = models.IntegerField("meses", validators=[MinValueValidator(1), MaxValueValidator(24)])
    mensalidade = models.DecimalField("mensalidade", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    objetivo = models.CharField("objetivo", max_length=200, blank=True, default="")  # sem regra
    tipo = models.CharField("tipo de plano", max_length=30, choices=TIPOS, default="mensal")

    @property
    def total(self):
        """Dado CALCULADO (meses × mensalidade): nunca guardado, nunca desatualizado."""
        return self.meses * self.mensalidade

    def __str__(self):
        return f"{self.aluno} - {self.meses} mês(es)"

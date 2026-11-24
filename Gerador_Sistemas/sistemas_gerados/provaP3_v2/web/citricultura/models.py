"""
MODEL (o "M" do MVT). Encapsulamento no MUNDO DJANGO (Aula 03):
  * a regra de cada campo vai em validators — o ModelForm, o admin e o full_clean() as executam;
  * @property aqui só para dado CALCULADO (total); setter em campo quebraria form/admin/ORM;
  * pegadinha: save() sozinho NÃO valida (ver tests/test_models.py).
"""
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class LoteCitros(models.Model):
    TIPOS = [
        ("industria", "Indústria"),
        ("mesa", "Mesa"),
        ("exportacao", "Exportação"),
        ("refugo", "Refugo")
    ]


    cooperado = models.CharField("cooperado", max_length=120)  # obrigatório: blank=False é o padrão
    talhao = models.IntegerField("talhao", validators=[MinValueValidator(1)])
    caixas = models.IntegerField("caixas", validators=[MinValueValidator(1), MaxValueValidator(5000)])
    preco_caixa = models.DecimalField("preco caixa", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    cidade = models.CharField("cidade", max_length=120, default='')  # obrigatório: blank=False é o padrão
    observacao = models.CharField("observacao", max_length=200, blank=True, default="")  # sem regra
    tipo = models.CharField("destino da fruta", max_length=30, choices=TIPOS, default="industria")

    @property
    def total(self):
        """Dado CALCULADO (caixas × preco_caixa): nunca guardado, nunca desatualizado."""
        return self.caixas * self.preco_caixa



    def __str__(self):
        return f"{self.cooperado} - {self.caixas} caixa(s)"

"""
SERIALIZER do DRF: converte o LoteCitros (model) em JSON e VALIDA o que chega na API.

O ModelSerializer lê os campos e os validators do model — a mesma regra das telas (ModelForm) e da API em
Django puro (api.py): o limite de cada campo mora num lugar só (no model).
"""
from rest_framework import serializers

from .models import LoteCitros


class LoteCitrosSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoteCitros
        fields = "__all__"

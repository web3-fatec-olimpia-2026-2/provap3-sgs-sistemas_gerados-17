from django.contrib import admin

from .models import Destino


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ("id_interno_formatado", "__str__")
    readonly_fields = ("id_interno",)  # o ID interno LNNL é gerado no save(), nunca digitado
    search_fields = ("id_interno", "cliente")

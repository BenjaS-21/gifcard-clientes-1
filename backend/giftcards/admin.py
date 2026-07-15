"""
admin.py — Registro de modelos en el admin de Django.
"""
from django.contrib import admin
from .models import CardTemplate, AdminToken


@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    actions = ['activate_selected']

    @admin.action(description='Activar template seleccionado')
    def activate_selected(self, request, queryset):
        if queryset.count() == 1:
            queryset.first().activate()


@admin.register(AdminToken)
class AdminTokenAdmin(admin.ModelAdmin):
    list_display = ('label', 'token', 'is_active', 'created_at')
    list_filter = ('is_active',)
    readonly_fields = ('token',)

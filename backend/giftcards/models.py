"""
models.py — Modelos locales de Gift Cards Damasco.
"""
import uuid
from django.db import models


class CardTemplate(models.Model):
    """
    Template visual para las Gift Cards.
    Solo uno puede estar activo a la vez — es la imagen de fondo que ven los clientes.
    """
    name = models.CharField(max_length=120, help_text="Nombre del diseño, ej: Día de las Madres")
    image = models.ImageField(upload_to='card_templates/', blank=True, null=True, help_text="Imagen de fondo de la tarjeta")
    html_code = models.TextField(blank=True, default='', help_text="Código HTML/CSS del diseño generado por IA")
    is_active = models.BooleanField(default=False, help_text="Solo un template puede estar activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Template de Tarjeta'
        verbose_name_plural = 'Templates de Tarjeta'

    def __str__(self):
        status = ' ✓ ACTIVO' if self.is_active else ''
        return f"{self.name}{status}"

    def activate(self):
        """Desactiva todos los demás y activa este."""
        CardTemplate.objects.exclude(pk=self.pk).update(is_active=False)
        self.is_active = True
        self.save(update_fields=['is_active'])


class AdminToken(models.Model):
    """
    Token de acceso al panel admin de Vue.
    Se genera al hacer login con credenciales Django.
    """
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    label = models.CharField(max_length=100, help_text="Quién generó este token")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Token Admin'
        verbose_name_plural = 'Tokens Admin'

    def __str__(self):
        return f"{self.label} — {self.token}"

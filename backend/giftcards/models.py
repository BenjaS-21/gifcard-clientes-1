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


class CompanyLogo(models.Model):
    """
    Logo de la empresa que compra Gift Cards.
    Se muestra en todas las tarjetas de los lotes asociados a la empresa.
    Posición y tamaño se guardan en % de la tarjeta para que escalen igual
    en cualquier tamaño de render.
    """
    name = models.CharField(max_length=120, help_text="Nombre de la empresa compradora")
    rif = models.CharField(
        max_length=30, blank=True, default='',
        help_text="RIF con el que la empresa entra al portal; con él ve todas las tarjetas de sus lotes"
    )
    logo = models.ImageField(upload_to='company_logos/', help_text="Logo de la empresa")
    pos_x = models.FloatField(default=50, help_text="Centro del logo en el eje X (% del ancho de la tarjeta)")
    pos_y = models.FloatField(default=50, help_text="Centro del logo en el eje Y (% del alto de la tarjeta)")
    width = models.FloatField(default=25, help_text="Ancho del logo (% del ancho de la tarjeta)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Logo de Empresa'
        verbose_name_plural = 'Logos de Empresa'

    def __str__(self):
        return self.name


class CompanyLote(models.Model):
    """Lote de Gift Cards (U_Lote en SAP) comprado por una empresa."""
    company = models.ForeignKey(CompanyLogo, on_delete=models.CASCADE, related_name='lotes')
    lote = models.CharField(max_length=100, unique=True, help_text="Código del lote en SAP (U_Lote)")

    class Meta:
        ordering = ['lote']
        verbose_name = 'Lote de Empresa'
        verbose_name_plural = 'Lotes de Empresa'

    def __str__(self):
        return f"{self.lote} — {self.company.name}"


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

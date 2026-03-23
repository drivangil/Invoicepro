from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

class Factura(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facturas')
    suplidor = models.CharField(max_length=255)
    rnc_suplidor = models.CharField(max_length=11)
    num_factura = models.CharField(max_length=50)
    ncf = models.CharField(max_length=13)
    fecha_emision = models.DateField()
    
    # Default 31/12 del año actual
    vencimiento_ncf = models.DateField(null=True, blank=True)
    
    # Calculado como fecha_emision + 30 días si es crédito (o por defecto)
    vencimiento_factura = models.DateField(null=True, blank=True)
    
    itbis = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    archivo_original = models.ImageField(upload_to='facturas/%Y/%m/%d/')
    procesada = models.BooleanField(default=False)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.vencimiento_ncf:
            self.vencimiento_ncf = date(date.today().year, 12, 31)
        if not self.vencimiento_factura and self.fecha_emision:
            self.vencimiento_factura = self.fecha_emision + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.suplidor} - {self.num_factura} ({self.ncf})"

class UserProfile(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_sheets_token = models.TextField(blank=True, null=True) # Para OAuth futuro

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

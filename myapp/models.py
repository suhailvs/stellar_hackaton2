from django.db import models

# Create your models here.
class Invoice(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("expired", "Expired"),
    ]
    tx_hash       = models.CharField(max_length=100, null=True, blank=True)
    xlm_amount    = models.DecimalField(max_digits=20, decimal_places=7)
    stellar_address = models.CharField(max_length=60)
    prompt        = models.TextField(blank=True)
    result_text   = models.TextField(blank=True, default="")
    processed_at  = models.DateTimeField(null=True, blank=True)
    
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at    = models.DateTimeField(auto_now_add=True)

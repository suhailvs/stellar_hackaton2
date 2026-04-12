from django.contrib import admin
from .models import Invoice, Error

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "prompt", "status", "created_at")

@admin.register(Error)
class ErrorAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "created_at")
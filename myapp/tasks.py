from celery import shared_task
from decimal import Decimal, InvalidOperation
from stellar_sdk import Server
from django.conf import settings

from .models import Invoice

@shared_task
def stream_payments_watcher():
    server = Server(horizon_url="https://horizon-testnet.stellar.org") # Server("https://horizon.stellar.org")
    payments = server.payments().for_account(settings.STELLAR_ADDRESS).cursor("now")    
    for payment in payments.stream():
        if payment["type"] != "payment":
            continue
        
        amount = payment["amount"]
        tx_hash = payment["transaction_hash"]
        tx = server.transactions().transaction(tx_hash).call()
        memo = tx["memo"]
        print("Payment received:", amount, tx_hash, memo)
        if not str(memo).isdigit():
            continue
        if payment.get("to") != settings.STELLAR_ADDRESS:
            continue
        try:
            payment_amount = Decimal(amount)
        except InvalidOperation:
            continue
        try:            
            invoice = Invoice.objects.select_for_update().get(id=memo)
            if invoice.status == "pending":
                invoice.paid_amount = payment_amount
                invoice.tx_hash = tx_hash
                invoice.status = "paid"
                invoice.save()
        except Invoice.DoesNotExist:
            continue  
# yourapp/management/commands/watch_payments.py

import time
import logging
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.conf import settings
from stellar_sdk import Server

from myapp.models import Invoice, Error

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Streams Stellar payments forever, reconnecting on failure"

    def handle(self, *args, **kwargs):
        self.stdout.write("Payment watcher starting...")
        last_cursor = self._load_cursor()

        while True:
            try:
                self.stdout.write(f"Connecting to Horizon (cursor={last_cursor})...")
                last_cursor = self._stream(last_cursor)
            except KeyboardInterrupt:
                self.stdout.write("Stopped by user.")
                break
            except Exception as e:
                Error.objects.create(text=f"Stream crashed: {e}. Reconnecting in 5s...")
                # logger.exception(f"Stream crashed: {e}. Reconnecting in 5s...")
                time.sleep(5)

    def _stream(self, cursor):
        server = Server(horizon_url="https://horizon-testnet.stellar.org")
        payments = (
            server.payments()
            .for_account(settings.STELLAR_ADDRESS)
            .cursor(cursor)
        )

        for payment in payments.stream():
            cursor = payment.get("paging_token", cursor)
            self._save_cursor(cursor)

            if payment["type"] != "payment":
                continue
            if payment.get("to") != settings.STELLAR_ADDRESS:
                continue

            amount = payment["amount"]
            tx_hash = payment["transaction_hash"]

            try:
                tx = server.transactions().transaction(tx_hash).call()
            except Exception as e:
                logger.warning(f"Could not fetch tx {tx_hash}: {e}")
                continue

            memo = tx.get("memo", "")
            if not str(memo).isdigit():
                continue

            try:
                payment_amount = Decimal(amount)
            except InvalidOperation:
                logger.warning(f"Invalid amount: {amount}")
                continue

            self._process(memo, payment_amount, tx_hash)

        return cursor  # stream() should not exit, but just in case

    def _process(self, memo, payment_amount, tx_hash):
        from django.db import transaction as db_transaction
        try:
            with db_transaction.atomic():
                invoice = Invoice.objects.select_for_update().get(id=memo)
                if invoice.status == "pending":
                    invoice.paid_amount = payment_amount
                    invoice.tx_hash = tx_hash
                    invoice.status = "paid"
                    invoice.save()
                    logger.info(f"Invoice {memo} marked paid: {payment_amount} (tx {tx_hash})")
        except Invoice.DoesNotExist:
            logger.debug(f"No invoice for memo={memo}")

    def _load_cursor(self):
        from django.core.cache import cache
        return cache.get("stellar_payment_cursor", "now")

    def _save_cursor(self, cursor):
        from django.core.cache import cache
        cache.set("stellar_payment_cursor", cursor, timeout=None)
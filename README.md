1. Basic Architecture
    1. when user enter a prompt
    2. website shows my stellar address
    3. user sends XLM
    4. your server detects the payment
    5. prompt result will shown
2. Important: Use MEMO to Identify the User
    1. Memo = User ID / Order ID
3. Listening for Payments (Python)
```python
from stellar_sdk import Server
server = Server("https://horizon.stellar.org")
account_id = "YOUR_STELLAR_ADDRESS"
payments = server.payments().for_account(account_id).cursor("now")
for payment in payments.stream():
    if payment["type"] == "payment":
        amount = payment["amount"]
        memo = payment.get("memo")
        print("Payment received:", amount, memo)
        # activate service
        activate_service(memo, amount)
```
4. Extra Security Checks. Always verify:
    1. ✔ correct amount
    2. ✔ correct memo
    3. ✔ correct asset (XLM)
    4. ✔ payment not processed before
5. Prevent Double Processing
    1. Store transaction hash: `tx_hash = payment["transaction_hash"]`
6. Advanced Payment Gateway Style. For a full gateway you can add:
    1. create invoice
    2. generate memo
    3. show QR code
    4. watch payment
    5. activate service
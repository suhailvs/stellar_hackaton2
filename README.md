## Stellar Agent

https://dorahacks.io/hackathon/stellar-agents-x402-stripe-mpp/detail

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

## x402 Integration (Conceptual)

This project does not currently implement x402. If you want to add it, here is a high-level way it would integrate with the existing invoice flow.

1. Add a payment challenge endpoint
    1. Client requests a protected resource (prompt result)
    2. Server responds with a 402-style payment challenge and a payment request payload
2. Reuse the existing invoice model
    1. Create an `Invoice` when the challenge is issued
    2. Use the invoice `id` as the memo
3. Client completes payment on Stellar
    1. Send XLM to `settings.STELLAR_ADDRESS`
    2. Include the memo from the challenge
4. Server verifies payment
    1. Stream or query Horizon for the transaction
    2. Validate destination, memo, asset, and amount
    3. Mark invoice as paid and store `tx_hash`
5. Fulfill the request once
    1. Generate the response and store it in `Invoice.result_text`
    2. Return the cached result on future calls

Notes:
1. The existing `get_promptresult` endpoint already supports idempotent fulfillment if you cache `result_text`.
2. The existing `stream_payments` function can serve as the verification layer for x402.

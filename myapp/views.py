import qrcode
from openai import OpenAI
from stellar_sdk import Server

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Invoice

def home(request):
    if request.method=='POST':
        prompt=request.POST.get('prompt','')
        if len(prompt.strip())<10:return JsonResponse({'error':'Chat Prompt must be atleast 10 char.'})
        invoice = Invoice.objects.create(
            stellar_address=settings.STELLAR_ADDRESS,
            xlm_amount=0.01, # XLM service price
            prompt=request.POST['prompt'],
        )
        # uri = (
        #     f"web+stellar:pay?"
        #     f"destination={invoice.stellar_address}"
        #     f"&amount={invoice.xlm_amount}"
        #     f"&memo={invoice.id}"
        #     f"&memo_type=MEMO_ID"
        #     f"&asset_code=XLM"
        # )

        img = qrcode.make(invoice.stellar_address)
        qrfolder = settings.BASE_DIR / 'myapp' / 'static' / 'qrcodes'
        img.save(qrfolder/f"{invoice.id}.png")
        return render(request,'qr.html',{'invoice':invoice})
    return render(request,'prompt.html')

# this must be run as async task using celery
def stream_payments(request):
    server = Server(horizon_url="https://horizon-testnet.stellar.org") # Server("https://horizon.stellar.org")
    payments = server.payments().for_account(settings.STELLAR_ADDRESS).cursor("now")
    invoices = []
    for payment in payments.stream():
        if payment["type"] == "payment":
            amount = payment["amount"]
            tx_hash = payment["transaction_hash"]
            tx = server.transactions().transaction(tx_hash).call()
            memo = tx["memo"]
            print("Payment received:", amount, tx_hash, memo)
            invoice = Invoice.objects.select_for_update().get(id=memo)# activate service
            
            if invoice.status == "pending":
                # if amount<invoice.xlm_amount:continue
                invoice.tx_hash = tx_hash
                invoice.status = 'paid'
                invoice.save()
            invoices.append({"status":invoice.status,'id':invoice.id})
    return JsonResponse({"status_updated": invoices})

def get_promptresult(request, memo):
    invoice = Invoice.objects.get(id=memo)
    if invoice.status == 'paid':
        # sample_prompt = "Create an offering description for local exchange trading system 
        # where I can offer activity or things like personal transportation using bike ct 100"
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=settings.GITHUB_TOKEN,
        )
        system_msg = "You are a helpful assistant."
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": invoice.prompt},
            ],
            model="gpt-4o",
            temperature=1.0,
            max_tokens=1000,
            top_p=1.0,
        )
        return JsonResponse({'status':'paid','data':response.choices[0].message.content})
    return JsonResponse({'status':'not_paid'})
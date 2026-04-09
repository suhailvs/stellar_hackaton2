import qrcode
from openai import OpenAI

from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Invoice
from .tasks import stream_payments_watcher

def home(request):
    if request.method=='POST':
        prompt=request.POST.get('prompt','')
        if len(prompt.strip())<10:return JsonResponse({'error':'Chat Prompt must be atleast 10 char.'})
        invoice = Invoice.objects.create(
            stellar_address=settings.STELLAR_ADDRESS,
            xlm_amount=0.01, # XLM service price
            prompt=request.POST['prompt'],
        )
        img = qrcode.make(invoice.stellar_address)
        qrfolder = settings.BASE_DIR / 'myapp' / 'static' / 'qrcodes'
        img.save(qrfolder/f"{invoice.id}.png")
        return render(request,'qr.html',{'invoice':invoice})
    return render(request,'prompt.html')

def stream_payments(request):
    lock_key = "stream_payments_lock"
    # cache.add returns True only if the key did not already exist
    if not cache.add(lock_key, "1", timeout=60):
        return JsonResponse({"status": "already_running"}, status=202)
    stream_payments_watcher.delay()
    return JsonResponse({"status_updated": 'true'})

def get_promptresult(request, memo):
    
    invoice = Invoice.objects.select_for_update().get(id=memo)
    if invoice.status != 'paid':
        return JsonResponse({'status':'not_paid'})

    if invoice.result_text:
        return JsonResponse({'status':'paid','data':invoice.result_text})

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
    invoice.result_text = response.choices[0].message.content
    invoice.processed_at = timezone.now()
    invoice.save(update_fields=["result_text", "processed_at"])
    return JsonResponse({'status':'paid','data':
        {'prompt_result':invoice.result_text,'paid':invoice.paid_amount}
    })

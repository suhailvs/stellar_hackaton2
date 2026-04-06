from django.conf import settings
from django.http import HttpResponse
from openai import OpenAI

def github_models_api(heading):
    # text = f"""Create an offering description for local exchange trading system 
    #     where I can offer activity or things like {heading}"""
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=settings.GITHUB_TOKEN,
    )
    system_msg = "You are a helpful assistant."
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": heading},
        ],
        model="gpt-4o",
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0,
    )
    return response.choices[0].message.content

def home(request):
    return HttpResponse('try: /ajax/stackcoinai/?details=verses that mention torah in quran')
def ajax_views(request, purpose):
    resp = ""
    if purpose == "stackcoinai":
        # ajax/stackcoinai/?details=
        resp = github_models_api(request.GET.get("details"))
    return HttpResponse(resp)

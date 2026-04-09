from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home),
    path("stream_payments/", views.stream_payments),
    path("ajax_payment_status/<memo>/", views.get_promptresult),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

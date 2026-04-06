from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home),
    path("stream_payments/", views.stream_payments),
    path("ajax_payment_status/<memo>/", views.get_promptresult),
]

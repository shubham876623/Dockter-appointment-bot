from django.urls import path
from .views import whatsapp_webhook

urlpatterns = [
    path('webhook/', whatsapp_webhook),
]

from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include
# whatsapp_booking\apps\booking
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/whatsapp/', include('whatsapp_booking.urls')),
]

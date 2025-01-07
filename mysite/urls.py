from django.contrib import admin
from django.urls import path, include
from cnn import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cnn.urls')),
]

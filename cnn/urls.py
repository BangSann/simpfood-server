from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_image, name='predict_image'),
    path('resep/tambah/', views.tambah_resep, name='tambah_resep'),
    path('resep/', views.get_resep, name='get_resep'),

]

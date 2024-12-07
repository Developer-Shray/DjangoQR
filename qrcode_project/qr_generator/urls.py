from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_qr, name='generate_qr_code'),
    path('upload/', views.generate_qrs_from_excel, name='generate_qrs_from_excel'),
    path('download-template/', views.download_template, name='download_template'),
]
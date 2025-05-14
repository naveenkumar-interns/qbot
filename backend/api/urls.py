from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('generate_questions/', views.Generate_questions, name='generate_questions'),
]

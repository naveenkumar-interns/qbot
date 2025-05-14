from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('generate_questions/', views.Generate_questions, name='generate_questions'),
    path('get_questions/', views.get_questions, name='get_questions'),
    path('submit_answers/', views.submit_answers, name='submit_answers'),

]

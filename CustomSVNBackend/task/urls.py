from django.urls import path
from . import views

urlpatterns = [
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('new/', views.task_create, name='task_create'),
]

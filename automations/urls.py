# backend/automations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create_tasks/', views.create_task, name='create_task'),
    path('fetch_all_tasks/', views.fetch_tasks, name='fetch_tasks'),
    path('fetch_task/<str:session_id>/', views.fetch_task, name='fetch_tasks_by_session_id')]

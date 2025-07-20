from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('calculator/', views.calculator, name='calculator'),  
    path('result/', views.result, name='result'),
    path('about/', views.about, name='about'), 
    path('save-impact/', views.save_impact_data, name='save-impact'),
    path('history/', views.impact_history, name='impact-history'),
    path('tips/', views.tips, name='tips'),
    path('mark-task-complete/', views.mark_task_complete, name='mark-task-complete'),
    path('profile/', views.profile, name='profile'),

    ]

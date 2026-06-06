from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_url, name='create_url'),
    path('edit/<int:pk>/', views.edit_url, name='edit_url'),
    path('delete/<int:pk>/', views.delete_url, name='delete_url'),
    path('analytics/<int:pk>/', views.url_analytics, name='url_analytics'),
    path('qr/<int:pk>/', views.generate_qr, name='generate_qr'),
    path('<str:short_code>/', views.redirect_url, name='redirect_url'),
]

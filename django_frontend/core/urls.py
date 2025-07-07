from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    
    # 🔄 API endpoint for real-time chart updates
    path('api/latest-spend-chart/', views.latest_spend_chart, name='latest_spend_chart'),
    
    
]

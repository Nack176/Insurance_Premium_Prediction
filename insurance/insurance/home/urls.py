from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('register/', views.registration_view, name='registration'),
    path('prediction/', views.prediction, name='prediction'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_predictions, name='export_predictions'),
    path('update_theme/', views.update_theme, name='update_theme'),
    path('logout/', views.logout_view, name='logout'),
]

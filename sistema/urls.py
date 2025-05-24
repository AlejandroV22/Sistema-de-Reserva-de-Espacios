from django.urls import path
from . import views 

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('panel-usuario/', views.panel_usuario_view, name='panel_usuario'),
]
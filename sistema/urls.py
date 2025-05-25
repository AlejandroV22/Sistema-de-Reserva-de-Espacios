# sistema/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('panel-usuario/', views.panel_usuario_view, name='panel_usuario'),

    # ADMINISTRADOR PERSONALIZADO
    path('admin-panel/', views.panel_administrador, name='panel_administrador'),
    path('admin-panel/espacios/', views.panel_espacios, name='admin_panel_espacios'),
    path('admin-panel/espacios/agregar/', views.agregar_espacio, name='agregar_espacio'),
    path('admin-panel/espacios/eliminar/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
    path('admin-panel/usuarios/', views.admin_panel_usuarios, name='admin_panel_usuarios'),
]

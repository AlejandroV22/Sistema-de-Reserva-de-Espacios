from django.urls import path
from . import views 

urlpatterns = [
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'), 
    path('panel-usuario/', views.panel_usuario_view, name='panel_usuario'),
    path('panel/espacios/', views.panel_espacios, name='panel_espacios'),
    path('panel/espacios/agregar/', views.agregar_espacio, name='agregar_espacio'),
    path('admin/espacios/', views.panel_espacios, name='admin_panel_espacios'),
    path('obtener-horarios/', views.obtener_horarios_disponibles, name='obtener_horarios'),
    path('reservas/', views.reservas_view, name='reservas'),
    path('confirmar_reserva/', views.confirmar_reserva, name='confirmar_reserva'),
    # Panel de administrador y administración de usuarios (NO BORRAR)
    path('admin-panel/', views.panel_administrador, name='panel_administrador'),
    path('admin-panel/espacios/', views.panel_espacios, name='admin_panel_espacios'),
    path('admin-panel/usuarios/', views.admin_panel_usuarios, name='admin_panel_usuarios'),
    path('admin-panel/espacios/eliminar/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
]



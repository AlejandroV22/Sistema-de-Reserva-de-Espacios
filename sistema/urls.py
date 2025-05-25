from django.urls import path
from . import views 

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('panel-usuario/', views.panel_usuario_view, name='panel_usuario'),
    path('panel/espacios/', views.panel_espacios, name='panel_espacios'),
    path('panel/espacios/agregar/', views.agregar_espacio, name='agregar_espacio'),
    path('admin/espacios/', views.panel_espacios, name='admin_panel_espacios'),
    path('admin/espacios/eliminar/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
    path('obtener-horarios/', views.obtener_horarios_disponibles, name='obtener_horarios'),
    path('reservas/', views.reservas_view, name='reservas'),
    
]


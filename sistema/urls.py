from django.urls import path
from django.contrib.auth import views as auth_views
from sistema.views import agregar_espacio


from . import views 

urlpatterns = [
    #URLS DE DJANGO, TEMPORALMENTE COMENTADAS
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), 
    path('panel-usuario/', views.panel_usuario_view, name='panel_usuario'),
    path('panel/espacios/', views.panel_espacios, name='panel_espacios'),
    path('panel/espacios/agregar/', views.agregar_espacio, name='agregar_espacio'),
    path('admin/espacios/', views.panel_espacios, name='admin_panel_espacios'),
    path('obtener-horarios/', views.obtener_horarios_disponibles, name='obtener_horarios'),
    

    ##
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('confirmar_reserva/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservas/<int:reserva_id>/detalle_ajax/', views.detalle_reserva_ajax, name='detalle_reserva_ajax'), 
    path('reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
   
    # Panel de administrador, administración de usuarios, espacios y sanciones (NO BORRAR)
    path('admin-panel/', views.panel_administrador, name='panel_administrador'),
    path('admin-panel/espacios/', views.panel_espacios, name='admin_panel_espacios'),
    path('admin-panel/usuarios/', views.admin_panel_usuarios, name='admin_panel_usuarios'),
    path('admin-panel/espacios/eliminar/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
    path('admin-panel/reservas/', views.ver_reservas, name='ver_reservas'),
    path('admin-panel/reservas/asistencia/<int:reserva_id>/', views.marcar_asistencia, name='marcar_asistencia'),
    path('admin-panel/sanciones/aplicar/', views.aplicar_sancion, name='aplicar_sancion'),
    path('admin-panel/sanciones/ver/', views.ver_sanciones, name='ver_sanciones'),
    path('admin-panel/sanciones/editar/<int:sancion_id>/', views.editar_sancion, name='editar_sancion'),
    path('admin-panel/sanciones/eliminar/<int:sancion_id>/', views.eliminar_sancion, name='eliminar_sancion'),
    path('admin-panel/espacios/agregar_espacio/', agregar_espacio, name='agregar_espacio'),




]



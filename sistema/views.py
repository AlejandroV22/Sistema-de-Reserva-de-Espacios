from django.shortcuts import render, redirect, get_object_or_404
from .models import Espacio
from .forms import EspacioForm 
from .models import Usuario
# Create your views here.


def login_view(request):
    return render(request, 'login.html')


def panel_usuario_view(request):
    return render(request, 'panel_usuario.html')

def panel_espacios(request):
    espacios = Espacio.objects.all()
    return render(request, 'panel_espacios.html', {'espacios': espacios})

def agregar_espacio(request):
    if request.method == 'POST':
        form = EspacioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('panel_espacios')
    else:
        form = EspacioForm()
    return render(request, 'agregar_espacio.html', {'form': form})

def eliminar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    espacio.delete()
    return ('panel_espacios')

def panel_administrador(request): #Panel de administrador personalizado
    return render(request, 'panel_administrador.html')

def panel_usuarios(request): #Administracion de usuarios 
    return render(request, 'panel_usuarios.html')  

def admin_panel_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'admin_panel_usuarios.html', {'usuarios': usuarios})
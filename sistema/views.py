from django.shortcuts import render

# Create your views here.


def login_view(request):
    return render(request, 'login.html')


def panel_usuario_view(request):
    return render(request, 'panel_usuario.html')

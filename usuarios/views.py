from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth

def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        Nome_de_usuario = request.POST.get('username')
        Informe_a_senha = request.POST.get('senha')
        Confirmar_senha = request.POST.get('confirmar_senha')
        
        if not Informe_a_senha == Confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não correspondem')
            return redirect('/usuarios/cadastro')
        
        user = User.objects.filter(username = Nome_de_usuario)

        if user.exists():
            messages.add_message(request, constants.ERROR, 'Esse nome de usuário já foi registrado')
            return redirect('/usuarios/cadastro')
        try: 
            User.objects.create_user(
            username= Nome_de_usuario,
            password= Informe_a_senha


        )
            return redirect ('/usuarios/logar/')
        except:
            messages.add_message(request, constants.ERROR, 'Ocorreu algum problema no servidor')
    return redirect ('/usuarios/cadastro')
        
def logar(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        Nome_de_usuario = request.POST.get ('username')
        Informe_a_senha = request.POST.get ('senha')   

        user = auth.authenticate(request, username = Nome_de_usuario, password = Informe_a_senha)

        if user:
            auth.login(request, user)

            messages.add_message(request, constants.SUCCESS, 'Login feito com sucesso!')

            return redirect('/flashcard/novo_flashcard/')
        
        else:
            messages.add_message(request, constants.ERROR,  'Nome de usuario ou senha estão errados')
            return redirect('/usuarios/logar/')

from urllib import request
from django.shortcuts import render, redirect
from . models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages
from django.db.models import Q

 
def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        categoria = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user = request.user)

        filtrar_categoria = request.GET.get('categoria')
        filtrar_dificuldade = request.GET.get('dificuldade')

        if filtrar_categoria:
              flashcards = flashcards.filter(categoria__id = filtrar_categoria)

        if filtrar_dificuldade:
              flashcards = flashcards.filter(dificuldade = filtrar_dificuldade)
        return render(request, 'novo_flashcard.html', {'categoria' : categoria, 'dificuldades': dificuldades, 'flashcards': flashcards })    
    elif request.method == "POST": 
            pergunta = request.POST.get('pergunta')
            resposta = request.POST.get('resposta')
            categoria = request.POST.get('categoria')
            dificuldade = request.POST.get('dificuldade')    
   
    if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Voce deve preencher todos os campos")
            return redirect('/flashcard/novo_flashcard')
    flashcard = Flashcard(
          user = request.user,
          pergunta = pergunta,
          resposta = resposta,
          categoria_id = categoria,
          dificuldade = dificuldade,
    )

    flashcard.save()   
    messages.add_message(request, constants.SUCCESS, 'O flashcard foi cadastrado com exito!!!')

    return redirect('/flashcard/novo_flashcard')

def deletar_flashcard(request, id):
      try:
            Flashcard.objects.get(id = id, user = request.user).delete()
            messages.add_message(request, constants.SUCCESS, 'O flashcard foi deletado com sucesso')
            return redirect('/flashcard/novo_flashcard')
      except Flashcard.DoesNotExist:
            messages.add_message(request, constants.ERROR, 'Voce não possui permissão para isso')
      return redirect('/flashcard/novo_flashcard')
      
      
def iniciar_desafio(request):
      if request.method == "GET":

            categoria = Categoria.objects.all()
            dificuldades = Flashcard.DIFICULDADE_CHOICES
            return render(request, 'iniciar_desafio.html', {'categorias': categoria, 'dificuldades': dificuldades})
      
      elif request.method == 'POST':
            titulo = request.POST.get('titulo')
            categoria = request.POST.getlist('categoria')
            dificuldade = request.POST.get('dificuldade')
            qtd_perguntas =  request.POST.get('qtd_perguntas')
                    
                  
            flashcards = (
                  
                  Flashcard.objects.filter(user = request.user)
                  .filter(dificuldade = dificuldade)
                  .filter(categoria_id__in = categoria)
                  .order_by('?')
                  
                  
            )
            
            if flashcards.count() < int(qtd_perguntas):
                  return redirect ('/flashcard/iniciar_desafio')
            
            
            
            desafio = Desafio(
                  
                  user = request.user,
                  titulo = titulo,
                  quantidade_perguntas = qtd_perguntas,
                  dificuldade = dificuldade
                  
                  
            )
            
            desafio.save()
            
            
            desafio.categoria.add(*categoria)
          
            flashcards = flashcards[:int(qtd_perguntas)]
                  
            for f in flashcards:
                  flashcard_desafio = FlashcardDesafio(
                  
                  flashcard = f
                  )
                  flashcard_desafio.save()
                  desafio.flashcards.add(flashcard_desafio)
                  
                  desafio.save()
                  return redirect('/flashcard/listar_desafio')
            
def listar_desafio(request):
      if request.method == "GET":
            categoria = Categoria.objects.all()
            dificuldade = Flashcard.DIFICULDADE_CHOICES
            desafio = Desafio.objects.filter(user = request.user)
          
            
            filtrar_categoria = request.GET.get('categoria')
            filtrar_dificuldade = request.GET.get('dificuldade')
           
      
      
      if filtrar_categoria:
              desafio = desafio.filter(categoria__id = filtrar_categoria)

      if filtrar_dificuldade:
             desafio = desafio.filter(dificuldade = filtrar_dificuldade)
            
            

      return render(request, 'listar_desafio.html', {'desafio': desafio, 'categoria': categoria, 'dificuldade': dificuldade})

def desafio(request, id):
      desafio = Desafio.objects.get(id = id)
      if not desafio.user == request.user:
            raise Http404
      if request.method == "GET":
            acertos = desafio.flashcards.filter(respondido=True).filter(acertou = True).count()
            erros = desafio.flashcards.filter(respondido = True).filter(acertou = False).count()
            faltantes = desafio.flashcards.filter(respondido = False).count()
            return render(request, 'desafio.html', {'desafio': desafio, 'acertos': acertos, 'erros': erros, 'faltantes': faltantes})
 
 
def responder_flashcard(request, id):
     flashcard_desafio = FlashcardDesafio.objects.get(id = id)
     acertou = request.GET.get('acertou')
     desafio_id  = request.GET.get('desafio_id')
     
     if not flashcard_desafio.flashcard.user == request.user:
      raise Http404()
     
     flashcard_desafio.respondido = True
     
     flashcard_desafio.acertou = True if acertou == '1' else False 
     
     flashcard_desafio.save()
     
     return redirect( f'/flashcard/desafio/{desafio_id}/')

def relatorio(request, id ):
      desafio = Desafio.objects.get(id=id)
      
      acertos = desafio.flashcards.filter(acertou=True).count()
      erros = desafio.flashcards.filter(acertou=False).count()
      
      dados = [acertos, erros]
      
      categorias = desafio.categoria.all()
      
      name_categoria = []
      for i in categorias:
            name_categoria.append(i.nome)
            
      dados_t = []
      for categoria in categorias:
            dados_t.append(desafio.flashcards.filter(flashcard__categoria = categoria).filter(acertou=True).count())

      return render(request, 'relatorio.html', {'desafio': desafio, 'dados': dados, 'categorias': name_categoria, 'dados_t': dados_t})
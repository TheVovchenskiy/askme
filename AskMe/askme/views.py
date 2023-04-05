from django.shortcuts import render
from . import models

# Create your views here.


def index(request):
    context = {'questions': models.QUESTIONS}
    return render(request, 'index.html', context=context)


def question(request, questionID):
    # TODO сделать проверку на значение questionID
    context = {"question": models.QUESTIONS[questionID]} 
    return render(request, 'question.html', context=context)

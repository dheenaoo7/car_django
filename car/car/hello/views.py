from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
@csrf_protect
def say_hello(request):
   return render(request, 'index.html')
    

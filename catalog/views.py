from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
#catalog/index.html
def index(request):
    return render(request, 'index.html')
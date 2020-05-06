from django.shortcuts import render
from django.views import generic

class LawyerDetailView(generic.DetailView):




def index(request):
    return render(request, 'static/docs/index.html', {})

def test(request):
    return render(request, 'test.html', {})

def lawyers(request):
    return render(request, 'lawyers.html', {})

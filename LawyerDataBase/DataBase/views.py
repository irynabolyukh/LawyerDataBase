from django.shortcuts import render
from django.views import generic
from .models import *


class LawyerDetailView(generic.DetailView):
    model = Lawyer
    context_object_name = "lawyer"


def index(request):
    return render(request, 'static/docs/index.html', {})


def test(request):
    return render(request, 'test.html', {})


def lawyers(request):
    return render(request, 'lawyers.html', {})

from django.shortcuts import render, get_object_or_404
from .models import LawyerForm, ServicesForm
# Create your views here.
from .models import Lawyer, Services
from django.views import generic

class LawyerDetailView(generic.DetailView):
    model = Lawyer
    context_object_name = "lawyer"


def index(request):
    return render(request, 'static/docs/index.html', {})


def test(request):
    return render(request, 'test.html', {})


def lawyers(request):
    return render(request, 'lawyers.html', {})


def index(request):
    return render(request, 'docs/index.html', {})

def create_lawyer(request):
    if request.method == "POST":
        form = LawyerForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = LawyerForm()
    return render(request, '/create_lawyer.html', {'form': form})

def edit_lawyer(request, pk):
    lawyer = get_object_or_404(Lawyer, pk=pk)
    if request.method == "POST":
        form = LawyerForm(request.POST, instance=lawyer)
        if form.is_valid():
            form.save()
    else:
        form = LawyerForm(instance=lawyer)
    return render(request, '/edit_lawyer.html', {'form': form})

def create_service(request):
    if request.method == "POST":
        form = ServicesForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ServicesForm()
    return render(request, '/create_service.html', {'form': form})

def edit_service(request, pk):
    service = get_object_or_404(Services, pk=pk)
    if request.method == "POST":
        form = LawyerForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
    else:
        form = ServicesForm(instance=service)
    return render(request, '/edit_service.html', {'form': form})

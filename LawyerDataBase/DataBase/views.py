from django.shortcuts import render, get_object_or_404, redirect
from .forms import LawyerForm, ServicesForm, Client_naturalForm, Client_juridicalForm, Appointment_NForm, Appointment_JForm

# Create your views here.
from .models import Lawyer, Services
from django.views import generic

class LawyerDetailView(generic.DetailView):
    model = Lawyer
    context_object_name = "lawyer"
    template_name = "lawyer_detail.html"

def test(request):
    return render(request, 'test.html', {})

def lawyers(request):
    return render(request, 'lawyers.html', {})

def index(request):
    return render(request, 'test.html', {})

def create_lawyer(request):
    if request.method == "POST":
        form = LawyerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['lawyer_code'])
    else:
        form = LawyerForm()
    return render(request, 'create_lawyer.html', {'form': form})

def edit_lawyer(request, pk):
    lawyer = get_object_or_404(Lawyer, pk=pk)
    if request.method == "POST":
        form = LawyerForm(request.POST, instance=lawyer)
        if form.is_valid():
            form.save()
        return render(request,'/lawyer/pk',{})
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

def create_client_natural(request):
    if request.method == "POST":
        form = Client_naturalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['num_client_n'])
    else:
        form = Client_naturalForm()
    return render(request, 'create_client_natural.html', {'form': form})

def create_client_juridical(request):
    if request.method == "POST":
        form = Client_juridicalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['num_client_j'])
    else:
        form = Client_juridicalForm()
    return render(request, 'create_client_juridical.html', {'form': form})

def create_appointment_n(request):
    if request.method == "POST":
        form = Appointment_NForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['appoint_code_n'])
    else:
        form = Appointment_NForm()
    return render(request, 'create_appointment_n.html', {'form': form})

def create_appointment_j(request):
    if request.method == "POST":
        form = Appointment_JForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['appoint_code_j'])
    else:
        form = Appointment_JForm()
    return render(request, 'create_appointment_j.html', {'form': form})
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from .forms import LawyerForm, ServicesForm, Client_naturalForm, Client_juridicalForm, Appointment_NForm, \
    Appointment_JForm, Dossier_JForm, Dossier_NForm, NPhoneForm, NPhoneFormSet

# Create your views here.
from .models import Lawyer, Dossier_J, \
    Dossier_N, Client_natural, Client_juridical, Services, \
    LPhone, Appointment_J, Appointment_N

from django.views import generic


class ServiceDetailView(generic.DetailView):
    model = Services
    context_object_name = "service"
    template_name = "service_detail.html"


class LawyerDetailView(generic.DetailView):
    model = Lawyer
    context_object_name = "lawyer"
    template_name = "lawyer_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        la_code = self.kwargs['pk']
        context['phones'] = LPhone.objects.filter(lawyer= la_code)
        context['appointments_n'] = Appointment_N.objects.filter(lawyer_code=la_code)
        context['appointments_j'] = Appointment_J.objects.filter(lawyer_code=la_code)
        context['dossier_j'] = Dossier_J.objects.filter(lawyer_code=la_code)
        context['dossier_n'] = Dossier_N.objects.filter(lawyer_code=la_code)
        return context


class DossierDetailJView(generic.DetailView):
    model = Dossier_J
    context_object_name = "dossier"
    template_name = "dossier_detail_j.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment_J.objects.filter(code_dossier_j=self.kwargs['pk'])
        return context


class DossierDetailNView(generic.DetailView):
    model = Dossier_N
    context_object_name = "dossier"
    template_name = "dossier_detail_j.html"


class ClientNDetailView(generic.DetailView):
    model = Client_natural
    context_object_name = "client"
    template_name = "client_detail_n.html"


class ClientJDetailView(generic.DetailView):
    model = Client_juridical
    context_object_name = "client"
    template_name = "client_detail_j.html"


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
        return render(request, '/lawyer/pk', {})
    else:
        form = LawyerForm(instance=lawyer)
    return render(request, '/edit_lawyer.html', {'form': form})


def create_service(request):
    if request.method == "POST":
        form = ServicesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['service_code'])
    else:
        form = ServicesForm()
    return render(request, 'create_service.html', {'form': form})


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
        client_form = Client_naturalForm(request.POST)
        if client_form.is_valid():
            client_form.save()
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


def create_dossier_j(request):
    if request.method == "POST":
        form = Dossier_JForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['code_dossier_j'])
    else:
        form = Dossier_JForm()
    return render(request, 'create_dossier_j.html', {'form': form})


def create_dossier_n(request):
    if request.method == "POST":
        form = Dossier_NForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.POST['code_dossier_n'])
    else:
        form = Dossier_NForm()
    return render(request, 'create_dossier_n.html', {'form': form})

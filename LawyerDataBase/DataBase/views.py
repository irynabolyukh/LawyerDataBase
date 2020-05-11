from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import LawyerForm, ServicesForm, Appointment_NForm, \
    Appointment_JForm, Dossier_JForm, Dossier_NForm, NPhoneFormset, JPhoneFormset

# Create your views here.
from .models import Lawyer, Dossier_J, \
    Dossier_N, Client_natural, Client_juridical, Services, \
    LPhone, Appointment_J, Appointment_N, NPhone, JPhone

from django.views import generic

class ServiceDetailView(generic.DetailView):
    model = Services
    context_object_name = "service"
    template_name = "service_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lawyers'] = Lawyer.objects.filter(service=self.kwargs['pk'])
        return context


class LawyerDetailView(generic.DetailView):
    model = Lawyer
    context_object_name = "lawyer"
    template_name = "lawyer_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        la_code = self.kwargs['pk']
        context['phones'] = LPhone.objects.filter(lawyer=la_code)
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
    template_name = "dossier_detail_n.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment_N.objects.filter(code_dossier_n=self.kwargs['pk'])

        return context

class ClientNDetailView(generic.DetailView):
    model = Client_natural
    context_object_name = "client_natural"
    template_name = "client_detail_n.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_code = self.kwargs['pk']
        context['phones'] = NPhone.objects.filter(client_natural_id=client_code)
        context['appointments'] = Appointment_N.objects.filter(num_client_n=self.kwargs['pk'])
        context['dossiers'] = Dossier_N.objects.filter(num_client_n=self.kwargs['pk'])
        return context


class ClientJDetailView(generic.DetailView):
    model = Client_juridical
    context_object_name = "client_juridical"
    template_name = "client_detail_j.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_code = self.kwargs['pk']
        context['phones'] = JPhone.objects.filter(client_juridical_id=client_code)
        context['appointments'] = Appointment_J.objects.filter(num_client_j=self.kwargs['pk'])
        context['dossiers'] = Dossier_J.objects.filter(num_client_j=self.kwargs['pk'])
        return context


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


class Client_naturalCreateView(CreateView):
    model = Client_natural
    template_name = 'create_client_natural.html'
    fields = ['num_client_n', 'first_name', 'surname', 'mid_name',
                  'mail_info', 'adr_city', 'adr_street', 'adr_build',
                  'birth_date', 'passport_date', 'passport_authority']
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["nphone"] = NPhoneFormset(self.request.POST)
        else:
            data["nphone"] = NPhoneFormset()
        return data
    def form_valid(self, form):
        context = self.get_context_data()
        nphone = context["nphone"]
        self.object = form.save()
        if nphone.is_valid():
            nphone.instance = self.object
            nphone.save()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.pk})

class Client_naturalUpdateView(UpdateView):
    model = Client_natural
    template_name = 'update_client_natural.html'
    fields = ['num_client_n', 'first_name', 'surname', 'mid_name',
              'mail_info', 'adr_city', 'adr_street', 'adr_build',
              'birth_date', 'passport_date', 'passport_authority']
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["nphone"] = NPhoneFormset(self.request.POST, instance=self.object)
        else:
            data["nphone"] = NPhoneFormset(instance=self.object)
        return data
    def form_valid(self, form):
        context = self.get_context_data()
        nphone = context["nphone"]
        self.object = form.save()
        if nphone.is_valid():
            nphone.instance = self.object
            nphone.save()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.pk})


class Client_naturalDeleteView(DeleteView):
    model = Client_natural
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('index')


class Client_juridicalCreateView(CreateView):
    model = Client_juridical
    template_name = 'create_client_juridical.html'
    fields = ['num_client_j', 'first_name', 'surname', 'mid_name',
                  'mail_info', 'client_position', 'name_of_company', 'iban',
                  'adr_city', 'adr_street', 'adr_build']
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["jphone"] = JPhoneFormset(self.request.POST)
        else:
            data["jphone"] = JPhoneFormset()
        return data
    def form_valid(self, form):
        context = self.get_context_data()
        jphone = context["jphone"]
        self.object = form.save()
        if jphone.is_valid():
            jphone.instance = self.object
            jphone.save()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("client-detailed-view-j")


class Client_juridicalUpdateView(UpdateView):
    model = Client_juridical
    template_name = 'update_client_juridical.html'
    fields = ['num_client_j', 'first_name', 'surname', 'mid_name',
              'mail_info', 'client_position', 'name_of_company', 'iban',
              'adr_city', 'adr_street', 'adr_build']
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["jphone"] = JPhoneFormset(self.request.POST, instance=self.object)
        else:
            data["jphone"] = JPhoneFormset(instance=self.object)
        return data
    def form_valid(self, form):
        context = self.get_context_data()
        jphone = context["jphone"]
        self.object = form.save()
        if jphone.is_valid():
            jphone.instance = self.object
            jphone.save()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.pk})


class Client_juridicalDeleteView(DeleteView):
    model = Client_juridical
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('index')


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

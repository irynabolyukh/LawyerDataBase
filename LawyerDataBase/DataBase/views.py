from django.shortcuts import render, get_object_or_404, redirect
from .forms import LawyerForm, ServicesForm

# Create your views here.
from .models import Lawyer, Dossier_J, \
    Dossier_N, Client_natural, Client_juridical, Services, LPhone
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

        context['phones'] = LPhone.objects.filter(lawyer=self.kwargs['pk'])
        print(context['phones'])
        return context


class DossierDetailJView(generic.DetailView):
    model = Dossier_J
    context_object_name = "dossier"
    template_name = "dossier_detail_j.html"


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

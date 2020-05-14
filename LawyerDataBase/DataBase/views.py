from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import CreateView, DeleteView, UpdateView, TemplateView
from django.views import generic
from .forms import *
from .models import *
from django.http import JsonResponse
from datetime import date

from django.db import connection


def nom_value():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT SUM(SE.nominal_value) AS nom '
            'FROM (( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE ON AJS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_J" AS AJ ON AJS.appointment_j_id = AJ.appoint_code_j) '
            'INNER JOIN "Lawyer" AS LA ON LA.lawyer_code = AJ.lawyer_code_id '
            'WHERE lawyer_code == %s AND AJ.code_dossier_j_id not in '
            '(SELECT code_dossier_j FROM dossier_j WHERE status==%s)', ['closed-won']
        )
        row = cursor.fetchone()
    return row

def lawyer_nom_value(param):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT LA.lawyer_code AS la_code, SUM(SE.nominal_value) AS nom '
            'FROM (( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE '
            'ON AJS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_J" AS AJ ON AJS.appointment_j_id = AJ.appoint_code_j) '
            'INNER JOIN "Lawyer" AS LA ON LA.lawyer_code = AJ.lawyer_code_id '
            'WHERE lawyer_code = %s AND AJ.code_dossier_j_id not in '
            '(SELECT code_dossier_j FROM "Dossier_J" WHERE status=%s)'
            'GROUP BY lawyer_code', [param, 'closed-won']
        )
        row = cursor.fetchone()
    return row


def lawyer_extra_value(param):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT LA.lawyer_code AS la_code, SUM(SE.bonus_value) AS nom '
            'FROM (( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE ON AJS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_J" AS AJ ON AJS.appointment_j_id = AJ.appoint_code_j) '
            'INNER JOIN "Lawyer" AS LA ON LA.lawyer_code = AJ.lawyer_code_id '
            'WHERE lawyer_code = %s AND AJ.code_dossier_j_id in '
            '(SELECT code_dossier_j FROM "Dossier_J" WHERE status=%s)'
            'GROUP BY lawyer_code', [param, 'closed-won']
        )
        row = cursor.fetchone()
    return row


def sqltest(request):
    return render(request, "test.html", {})


class StatisticsView(TemplateView):
    template_name = "stat_panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lawyers'] = Lawyer.objects.all()
        try:
            context['closed_dossiers_n'] = Dossier_N.objects.raw(
                'SELECT code_dossier_n, COUNT(code_dossier_n) AS counted_dossiers '
                'FROM "Dossier_N" '
                'WHERE status <> %s '
                'GROUP BY code_dossier_n',
                ['open'])[0].counted_dossiers
        except:
            context['closed_dossiers_n'] = 0
        try:
            context['closed_dossiers_j'] = Dossier_J.objects.raw(
                'SELECT code_dossier_j, COUNT(*) AS counted_dossiers '
                'FROM "Dossier_J" '
                'WHERE status <> %s '
                'GROUP BY code_dossier_j',
                ['open'])[0].counted_dossiers
        except:
            context['closed_dossiers_j'] = 0
        try:
            context['open_dossiers_n'] = Dossier_N.objects.raw(
                'SELECT code_dossier_n, COUNT(code_dossier_n) AS counted_dossiers '
                'FROM "Dossier_N" '
                'WHERE status = %s '
                'GROUP BY code_dossier_n',
                ['open'])[0].counted_dossiers
        except:
            context['open_dossiers_n'] = 0
        print(context['open_dossiers_n'])
        try:
            context['open_dossiers_j'] = Dossier_J.objects.raw(
                'SELECT code_dossier_j, COUNT(code_dossier_j) AS counted_dossiers '
                'FROM "Dossier_J" '
                'WHERE status = %s '
                'GROUP BY code_dossier_j',
                ['open'])[0].counted_dossiers
        except:
            context['open_dossiers_j'] = 0
        return context


@requires_csrf_token
def getStats(request):
    if request.method == 'POST':
        d = date(int(request.POST['year']),
                 int(request.POST['month']),
                 int(request.POST['day']))
        print(d)
        return JsonResponse({"success" : True})
    else:
        return JsonResponse({})


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
        today = date.today()
        context['upcoming_app_n'] = Appointment_N.objects.filter(lawyer_code=la_code) \
            .filter(app_date__gte=today).order_by('app_date')
        context['upcoming_app_j'] = Appointment_J.objects.filter(lawyer_code=la_code) \
            .filter(app_date__gte=today).order_by('app_date')
        context['appointments_n'] = Appointment_N.objects.filter(lawyer_code=la_code) \
            .filter(app_date__lt=today).order_by('-app_date')
        context['appointments_j'] = Appointment_J.objects.filter(lawyer_code=la_code) \
            .filter(app_date__lt=today).order_by('-app_date')
        context['dossier_j'] = Dossier_J.objects.filter(lawyer_code=la_code)
        context['dossier_n'] = Dossier_N.objects.filter(lawyer_code=la_code)
        context['closed_dossiers_n'] = Dossier_N.objects.raw(
            'SELECT code_dossier_n, COUNT(code_dossier_n) AS counted_dossiers '
            'FROM "Dossier_N" '
            'WHERE lawyer_code_id = %s AND status <> %s '
            'GROUP BY code_dossier_n',
            [la_code,'open'])
        context['closed_dossiers_j'] = Dossier_J.objects.raw(
            'SELECT code_dossier_j, COUNT(code_dossier_j) AS counted_dossiers '
            'FROM "Dossier_J" '
            'WHERE lawyer_code_id = %s AND status <> %s '
            'GROUP BY code_dossier_j',
            [la_code,'open'])
        try:
            context['nominal_value'] = lawyer_nom_value(la_code)[1]
        except:
            context['nominal_value'] = 0
        try:
            context['bonus_value'] = lawyer_extra_value(la_code)[1]
        except:
            context['bonus_value'] = 0
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


def ncustomers(request):
    return render(request, 'ncustomers.html', {})


def jcustomers(request):
    return render(request, 'jcustomers.html', {})


def ndossiers(request):
    return render(request, 'ndossiers.html', {})


def jdossiers(request):
    return render(request, 'jdossiers.html', {})


def index(request):
    return render(request, 'test.html', {})


class LawyerCreateView(CreateView):
    model = Lawyer
    form_class = LawyerForm
    template_name = 'create_lawyer.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["lphone"] = LPhoneFormSet(self.request.POST)
        else:
            data["lphone"] = LPhoneFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lphone = context["lphone"]
        self.object = form.save()
        if lphone.is_valid():
            lphone.instance = self.object
            lphone.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("lawyer-detailed-view", kwargs={'pk': self.object.pk})


class LawyerUpdateView(UpdateView):
    model = Lawyer
    template_name = 'update_lawyer.html'
    fields = ['lawyer_code', 'first_name', 'surname', 'mid_name', 'specialization',
              'mail_info', 'service', 'work_days']

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["lphone"] = LPhoneFormSet(self.request.POST, instance=self.object)
        else:
            data["lphone"] = LPhoneFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lphone = context["lphone"]
        self.object = form.save()
        if lphone.is_valid():
            lphone.instance = self.object
            lphone.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("lawyer-detailed-view", kwargs={'pk': self.object.pk})


class LawyerDeleteView(DeleteView):
    model = Lawyer
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('lawyers')


class ServicesCreateView(CreateView):
    model = Services
    form_class = ServicesForm
    template_name = 'create_service.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("service-detailed-view", kwargs={'pk': self.object.pk})


class ServicesUpdateView(UpdateView):
    model = Services
    form_class = ServicesForm
    template_name = 'update_service.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("service-detailed-view", kwargs={'pk': self.object.pk})


class ServicesDeleteView(DeleteView):
    model = Services
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('lawyers')


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
    success_url = reverse_lazy('ncustomers')


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
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.pk})


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
    success_url = reverse_lazy('jcustomers')


class Appointment_NCreateView(CreateView):
    model = Appointment_N
    form_class = Appointment_NForm
    template_name = 'create_appointment_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_NUpdateView(UpdateView):
    model = Appointment_N
    fields = ['app_date', 'app_time', 'comment']
    template_name = 'update_appointment.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_NDeleteView(DeleteView):
    model = Appointment_N
    template_name = 'confirm_delete.html'
    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_JCreateView(CreateView):
    model = Appointment_J
    form_class = Appointment_JForm
    template_name = 'create_appointment_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Appointment_JUpdateView(UpdateView):
    model = Appointment_J
    fields = ['app_date', 'app_time', 'comment']
    template_name = 'update_appointment.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Appointment_JDeleteView(DeleteView):
    model = Appointment_J
    template_name = 'confirm_delete.html'
    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Dossier_NCreateView(CreateView):
    model = Dossier_N
    form_class = Dossier_NForm
    template_name = 'create_dossier_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Dossier_NUpdateView(UpdateView):
    model = Dossier_N
    fields = ['date_closed', 'status', 'paid', 'fee', 'court_name', 'court_adr', 'court_date', 'lawyer_code']
    template_name = 'update_dossier_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Dossier_NDeleteView(DeleteView):
    model = Dossier_N
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Dossier_JCreateView(CreateView):
    model = Dossier_J
    form_class = Dossier_JForm
    template_name = 'create_dossier_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Dossier_JUpdateView(UpdateView):
    model = Dossier_J
    fields = ['date_closed', 'status', 'paid', 'fee', 'court_name', 'court_adr', 'court_date', 'lawyer_code']
    template_name = 'update_dossier_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Dossier_JDeleteView(DeleteView):
    model = Dossier_J
    template_name = 'confirm_delete.html'
    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


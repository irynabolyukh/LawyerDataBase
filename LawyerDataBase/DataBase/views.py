import json
from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, FormView
from django.views import generic
from .forms import *
from django.http import JsonResponse
from .sql_querries import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F

# class UserCreateView(LoginRequiredMixin, CreateView):
#     model = User
#     form_class = CustomUserCreationForm
#     template_name = 'DataBase/register.html'
#
#     def get_form_kwargs(self):
#         kwargs = super(UserCreateView, self).get_form_kwargs()
#         kwargs.update({'username': self.kwargs['pk']})
#         kwargs.update({'email': self.kwargs['mail']})
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         return data
#
#     def form_valid(self, form):
#         self.object = form.save()
#         # self.object.groups.add(self.object.group)
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         if str(self.object.group) == str('Юридичний клієнт'):
#             return reverse("dossier_j-create", kwargs={'pk': self.object.username})
#         elif str(self.object.group) == str('Фізичний клієнт'):
#             return reverse("dossier_n-create", kwargs={'pk': self.object.username})
#         elif str(self.object.group) == str('Адвокат'):
#             return reverse("lawyers")
#         else:
#             return reverse("stats")


@login_required()
@requires_csrf_token
def register(request, pk, mail):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)
            page.username = pk
            page.email = mail
            page.save()
            if str(form.cleaned_data['group']) == str('Юридичний клієнт'):

                url = "http://127.0.0.1:8000/database/dossier_J/" + pk + "/create"
                return redirect(url)
            elif str(form.cleaned_data['group']) == str('Фізичний клієнт'):
                url = "http://127.0.0.1:8000/database/dossier_N/" + pk + "/create"
                return redirect(url)

            elif str(form.cleaned_data['group']) == str('Адвокат'):
                return redirect("lawyers")

            else:
                return redirect("stats")
    else:
        form = CustomUserCreationForm()

    return render(request, 'Database/register.html', {'form': form})


@login_required()
@requires_csrf_token
def client_ajax(request):
    if request.method == 'POST':
        response = {}
        response['dossier'] = []
        if request.POST['dosJ'] == 'true':
            dossiers = Dossier_J.objects.filter(num_client_j=request.POST['client']).filter(status='open').filter(active=True)
            for dossier in dossiers:
                response['dossier'].append({'code': dossier.code_dossier_j,
                                            'issue': dossier.issue})
        else:
            dossiers = Dossier_N.objects.filter(num_client_n=request.POST['client']).filter(status='open').filter(active=True)
            for dossier in dossiers:
                response['dossier'].append({'code': dossier.code_dossier_n,
                                            'issue': dossier.issue})
        return JsonResponse(response)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)


@login_required()
@requires_csrf_token
def lawyer_service_code(request):
    if request.method == 'POST':
        response = {}
        response['lawyers'] = []
        lawyers = Lawyer.objects.all()
        for lawyer in lawyers:
            if lawyer.service.filter(service_code=request.POST['service']).exists():
                response['lawyers'].append(lawyer.lawyer_code)
        return JsonResponse(response)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)


@login_required()
@requires_csrf_token
def lawyer_work_days(request):
    if request.method == 'POST':
        response = {}
        response['days'] = []
        workdays = Work_days.objects.filter(lawyer=request.POST['lawyer'])
        for day in workdays:
            response['days'].append(day.pk)
        try:
            if str(request.POST['dosn']) == 'true':
                response['maxday'] = str(Dossier_N.objects.get(code_dossier_n=request.POST['dossier']).date_expired)
            else:
                response['maxday'] = str(Dossier_J.objects.get(code_dossier_j=request.POST['dossier']).date_expired)
        except :
            pass
        return JsonResponse(response)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)


@login_required()
@requires_csrf_token
def dayblockedtime(request):
    if request.method == 'POST':
        response = {}
        date_lawyer = date(int(request.POST['date[year]']),
                           int(request.POST['date[month]']),
                           int(request.POST['date[day]']))
        response['time'] = blocked_time_lawyer(request.POST['lawyer'], date_lawyer)
        return JsonResponse(response)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)


@login_required()
@requires_csrf_token
def service_ajax(request):
    if request.method == 'POST':
        response = {}
        response['lawyers'] = lawyers_appointment(request.POST.getlist('services[]'))
        return JsonResponse(response)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)


class StatisticsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'DataBase.view_statistics'
    template_name = "stat_panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        checked = self.request.GET.get('lawyer_service', '')
        context['checked'] = checked
        context['closed_dossiers_j'] = Dossier_J.objects.filter(active=True).exclude(status='open').count()
        context['closed_dossiers_n'] = Dossier_N.objects.filter(active=True).exclude(status='open').count()

        context['open_dossiers_n'] = Dossier_N.objects.filter(active=True).filter(status='open').count()
        context['open_dossiers_j'] = Dossier_J.objects.filter(active=True).filter(status='open').count()

        context['value'] = str(nom_value() + extra_value())

        context['service_count'] = service_counter()

        if str(checked) == 'on':
            context['lawyer_counter'] = lawyer_counter(True)
        else:
            context['lawyer_counter'] = lawyer_counter(False)

        context['won_dossiers'] = won_dossiers()

        context['counter_dossiers_open'] = (int(context['open_dossiers_j']) + int(context['open_dossiers_n']))
        context['counter_dossiers_closed'] = (int(context['closed_dossiers_n']) + int(context['closed_dossiers_j']))

        return context


@login_required()
@requires_csrf_token
def getStats(request):
    if request.method == 'POST':
        dStart = date(int(request.POST['date1[year]']),
                      int(request.POST['date1[month]']),
                      int(request.POST['date1[day]']))
        dEnd = date(int(request.POST['date2[year]']),
                    int(request.POST['date2[month]']),
                    int(request.POST['date2[day]']))
        response = {}
        response['closed'] = 0
        response['open_n'] = date_open_dossier_n(dStart, dEnd)
        response['open_j'] = date_open_dossier_j(dStart, dEnd)
        response['open'] = int(response['open_n']) + int(response['open_j'])
        response['all_won_dossiers'] = date_won_dossiers(dStart, dEnd)
        response['service_count'] = date_service_counter(dStart, dEnd)
        checked = request.POST.get('checked','')
        if str(checked) == 'on':
            response['lawyer_counter'] = date_lawyer_counter(dStart, dEnd, True)
            response['checked'] = True
        else:
            response['lawyer_counter'] = date_lawyer_counter(dStart, dEnd, False)
            response['checked'] = False
        response['value'] = 0
        for service in response['service_count']:
            response['value'] += service['sum']

        return JsonResponse(response)
    else:
        return JsonResponse({'message': 'Bad request'}, status=400)


class ServiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    permission_required = 'DataBase.view_services'
    model = Services
    context_object_name = "service"
    template_name = "service_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = Services.objects.filter(active=True).get(service_code=self.kwargs['pk'])
        group = service.__getattribute__('service_group')
        context['group'] = ServiceGroup.objects.filter(name_group=group)
        context['lawyers'] = Lawyer.objects.filter(active=True).filter(service=self.kwargs['pk'])
        return context


class LawyerDetailView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_lawyer'
    model = Lawyer
    context_object_name = "lawyer"
    template_name = "lawyer_detail.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        group = self.request.user.groups.filter(user=self.request.user)[0]
        if group.name == "Адвокат":
            la_code = self.kwargs['pk']
            l_code = Lawyer.objects.get(mail_info=self.request.user.email).pk
            return l_code == la_code
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        la_code = self.kwargs['pk']
        context['phones'] = LPhone.objects.filter(lawyer=la_code)
        today = date.today()
        context['upcoming_app_n'] = Appointment_N.objects.filter(active=True).filter(lawyer_code=la_code) \
            .filter(app_date__gte=today).order_by('app_date')
        context['upcoming_app_j'] = Appointment_J.objects.filter(active=True).filter(lawyer_code=la_code) \
            .filter(app_date__gte=today).order_by('app_date')
        context['appointments_n'] = Appointment_N.objects.filter(active=True).filter(lawyer_code=la_code) \
            .filter(app_date__lt=today).order_by('-app_date')
        context['appointments_j'] = Appointment_J.objects.filter(active=True).filter(lawyer_code=la_code) \
            .filter(app_date__lt=today).order_by('-app_date')
        context['dossier_j'] = Dossier_J.objects.filter(active=True).filter(lawyer_code=la_code)
        context['dossier_n'] = Dossier_N.objects.filter(active=True).filter(lawyer_code=la_code)
        context['closed_dossiers_n'] = Dossier_N.objects.filter(lawyer_code=la_code).filter(
            status__istartswith='closed').count()
        context['closed_dossiers_j'] = Dossier_J.objects.filter(lawyer_code=la_code).filter(
            status__istartswith='closed').count()

        try:
            context['nominal_value'] = lawyer_nom_value(la_code)[1]
        except:
            context['nominal_value'] = 0
        try:
            context['bonus_value'] = lawyer_extra_value(la_code)[1]
        except:
            context['bonus_value'] = 0

        context['value'] = int(context['bonus_value']) + int(context['nominal_value'])
        return context


class DossierDetailJView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_dossier_j'
    model = Dossier_J
    context_object_name = "dossier"
    template_name = "dossier_detail_j.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        group = self.request.user.groups.filter(user=self.request.user)[0]
        code = self.kwargs['pk']
        if group.name == "Юридичний клієнт":
            cl_pk = Client_juridical.objects.get(mail_info=self.request.user.email).pk
            dos = Dossier_J.objects.get(code_dossier_j=code).num_client_j_id
            return cl_pk == dos
        elif group.name == "Адвокат":
            lawyer = Lawyer.objects.get(mail_info=self.request.user.email).pk
            dos = Dossier_J.objects.get(code_dossier_j=code).lawyer_code_id
            return lawyer == dos
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dossier = Dossier_J.objects.get(code_dossier_j=self.kwargs['pk'])
        dossier.count_fee()
        client_code = dossier.__getattribute__('num_client_j_id')
        law_code = dossier.__getattribute__('lawyer_code_id')
        dossier.save()
        context['appointments'] = Appointment_J.objects.filter(active=True).filter(code_dossier_j=self.kwargs['pk'])
        context['phones'] = JPhone.objects.filter(client_juridical_id=client_code)
        context['lphones'] = LPhone.objects.filter(lawyer_id=law_code)
        context['all_lphones'] = LPhone.objects.all()
        return context


class DossierDetailNView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_dossier_n'
    model = Dossier_N
    context_object_name = "dossier"
    template_name = "dossier_detail_n.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        group = self.request.user.groups.filter(user=self.request.user)[0]
        code = self.kwargs['pk']
        if group.name == "Фізичний клієнт":
            cl_pk = Client_natural.objects.get(mail_info=self.request.user.email).pk
            dos = Dossier_N.objects.get(code_dossier_n=code).num_client_n_id
            return cl_pk == dos
        elif group.name == "Адвокат":
            lawyer = Lawyer.objects.get(mail_info=self.request.user.email).pk
            dos = Dossier_N.objects.get(code_dossier_n=code).lawyer_code_id
            return lawyer == dos
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dossier = Dossier_N.objects.get(code_dossier_n=self.kwargs['pk'])
        # dossier.fee = fee_dossier_n(dossier.code_dossier_n)
        dossier.count_fee()
        client_code = dossier.__getattribute__('num_client_n_id')
        law_code = dossier.__getattribute__('lawyer_code_id')
        dossier.save()
        context['appointments'] = Appointment_N.objects.filter(active=True).filter(code_dossier_n=self.kwargs['pk'])
        context['phones'] = NPhone.objects.filter(client_natural_id=client_code)
        context['lphones'] = LPhone.objects.filter(lawyer_id=law_code)
        context['all_lphones'] = LPhone.objects.all()
        return context


class ClientNDetailView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_client_natural'
    model = Client_natural
    context_object_name = "client_natural"
    template_name = "client_detail_n.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        group = self.request.user.groups.filter(user=self.request.user)[0]
        if group.name == "Фізичний клієнт":
            cl_code = self.kwargs['pk']
            cl_pk = Client_natural.objects.get(mail_info=self.request.user.email).pk
            return cl_pk == cl_code
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_code = self.kwargs['pk']
        today = date.today()
        context['upcoming_app_n'] = Appointment_N.objects.filter(active=True).filter(num_client_n=self.kwargs['pk']) \
            .filter(app_date__gte=today).order_by('app_date')
        context['appointments_n'] = Appointment_N.objects.filter(active=True).filter(num_client_n=self.kwargs['pk']) \
            .filter(app_date__lt=today).order_by('-app_date')
        context['phones'] = NPhone.objects.filter(client_natural_id=client_code)
        context['appointments'] = Appointment_N.objects.filter(active=True).filter(num_client_n=self.kwargs['pk']). \
            order_by('-app_date', '-app_time')
        context['dossiers'] = Dossier_N.objects.filter(active=True).filter(num_client_n=self.kwargs['pk'])
        return context


class ClientJDetailView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_client_juridical'
    model = Client_juridical
    context_object_name = "client_juridical"
    template_name = "client_detail_j.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        group = self.request.user.groups.filter(user=self.request.user)[0]
        if group.name == "Юридичний клієнт":
            cl_code = self.kwargs['pk']
            cl_pk = Client_juridical.objects.get(mail_info=self.request.user.email).pk
            return cl_pk == cl_code
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_code = self.kwargs['pk']
        today = date.today()
        context['upcoming_app_j'] = Appointment_J.objects.filter(active=True).filter(num_client_j=self.kwargs['pk']) \
            .filter(app_date__gte=today).order_by('app_date')
        context['appointments_j'] = Appointment_J.objects.filter(active=True).filter(num_client_j=self.kwargs['pk']) \
            .filter(app_date__lt=today).order_by('-app_date')
        context['phones'] = JPhone.objects.filter(client_juridical_id=client_code)
        context['appointments'] = Appointment_J.objects.filter(active=True).filter(num_client_j=self.kwargs['pk'])
        context['dossiers'] = Dossier_J.objects.filter(active=True).filter(num_client_j=self.kwargs['pk'])
        return context


@login_required()
def index(request):
    if request.user.is_superuser:
        return render(request, 'stat_panel.html', {})
    group = request.user.groups.filter(user=request.user)[0]
    if group.name == "Секретар":
        return HttpResponseRedirect(reverse('stats'))
    elif group.name == "Адвокат":
        l_code = Lawyer.objects.get(mail_info=request.user.email).pk
        return HttpResponseRedirect('/database/lawyer/' + l_code)
    elif group.name == "Юридичний клієнт":
        cl_code = Client_juridical.objects.get(mail_info=request.user.email).pk
        return HttpResponseRedirect('/database/client_J/' + cl_code)
    elif group.name == "Фізичний клієнт":
        cl_code = Client_natural.objects.get(mail_info=request.user.email).pk
        return HttpResponseRedirect('/database/client_N/' + cl_code)
    return render(request, 'index.html', {})


def visitCard(request):
    context = {}
    return render(request, 'visitCard.html', context)


class LawyerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_lawyer'
    model = Lawyer
    form_class = LawyerForm
    template_name = 'create_lawyer.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        phoneFormSet = inlineformset_factory(Lawyer, LPhone, max_num=2, fields=['phone_num'], can_delete=False,
                                             labels={'phone_num': ('Телефон')})
        if self.request.POST:
            data["lphone"] = phoneFormSet(self.request.POST)
        else:
            data["lphone"] = phoneFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lphone = context["lphone"]
        self.object = form.save()
        if lphone.is_valid():
            lphone.instance = self.object
            lphone.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("register", kwargs={'pk': self.object.pk, 'mail': self.object.mail_info})
        # return reverse("lawyer-detailed-view", kwargs={'pk': self.object.pk})


class LawyerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_lawyer'
    model = Lawyer
    template_name = 'update_lawyer.html'
    form_class = LawyerForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        phoneFormSet = inlineformset_factory(Lawyer, LPhone, max_num=2, fields=['phone_num'],
                                             labels={'phone_num': 'Телефон'})

        if self.request.POST:
            data["lphone"] = phoneFormSet(self.request.POST, instance=self.object)
        else:
            data["lphone"] = phoneFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lphone = context["lphone"]
        self.object = form.save()
        if lphone.is_valid():
            lphone.instance = self.object
            lphone.save()
        else:
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("lawyer-detailed-view", kwargs={'pk': self.object.pk})


class ServiceGroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_services'
    model = ServiceGroup
    form_class = ServiceGroupForm
    template_name = 'create_service_group.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("services")


class ServicesCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_services'
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


class ServicesUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_services'
    model = Services
    form_class = ServicesUpdateForm
    template_name = 'update_service.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("service-detailed-view", kwargs={'pk': self.object.pk})


class Client_naturalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_client_natural'
    model = Client_natural
    template_name = 'create_client_natural.html'
    form_class = Client_NForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        phoneFormSet = inlineformset_factory(Client_natural, NPhone, max_num=2, fields=['phone_num'], can_delete=False,
                                             labels={'phone_num': ('Телефон')})
        if self.request.POST:
            data["nphone"] = phoneFormSet(self.request.POST)
        else:
            data["nphone"] = phoneFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        nphone = context["nphone"]
        self.object = form.save()
        if nphone.is_valid():
            nphone.instance = self.object
            nphone.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("register", kwargs={'pk': self.object.pk, 'mail': self.object.mail_info})


class Client_naturalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_client_natural'
    model = Client_natural
    template_name = 'update_client_natural.html'
    form_class = Client_NForm

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
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.pk})


class LawyerServiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'DataBase.add_lawyer'
    form_class = LawyerServiceForm
    template_name = 'service_add_lawyer.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        not_selected_lawyers = Lawyer.objects.all()
        for lawyer in form.cleaned_data['lawyers']:
            lawyer.service.add(form.cleaned_data['service_code'])
            not_selected_lawyers = not_selected_lawyers.exclude(lawyer_code=lawyer.lawyer_code)
        for not_selected_lawyer in not_selected_lawyers:
            not_selected_lawyer.service.remove(form.cleaned_data['service_code'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(LawyerServiceCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

    def get_success_url(self):
        return reverse("service-detailed-view", kwargs={'pk': self.kwargs['pk']})


class Client_juridicalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_client_juridical'
    model = Client_juridical
    template_name = 'create_client_juridical.html'
    form_class = Client_JForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        PhoneFormSet = inlineformset_factory(
            Client_juridical, JPhone, max_num=2, fields=['phone_num'],
            can_delete=False, labels={'phone_num': ('Телефон')})
        if self.request.POST:
            data["jphone"] = PhoneFormSet(self.request.POST)
        else:
            data["jphone"] = PhoneFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        jphone = context["jphone"]
        self.object = form.save()
        if jphone.is_valid():
            jphone.instance = self.object
            jphone.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("register", kwargs={'pk': self.object.pk, 'mail': self.object.mail_info})
        # return reverse("client-detailed-view-j", kwargs={'pk': self.object.pk})


class Client_juridicalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_client_juridical'
    model = Client_juridical
    template_name = 'update_client_juridical.html'
    form_class = Client_JForm

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
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.pk})


class Appointment_NCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_appointment_n'
    model = Appointment_N
    form_class = Appointment_NForm
    template_name = 'create_appointment_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form(self, form_class=None):
        form = super(Appointment_NCreateView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(Appointment_NCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appoint_NCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_appointment_n'
    model = Appointment_N
    form_class = Appoint_NForm
    template_name = 'create_appointment_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form(self, form_class=None):
        form = super(Appoint_NCreateView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(Appoint_NCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        kwargs.update({'dossier_code': self.kwargs['dossier_code']})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appoint_JCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_appointment_j'
    model = Appointment_J
    form_class = Appoint_JForm
    template_name = 'create_appointment_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form(self, form_class=None):
        form = super(Appoint_JCreateView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(Appoint_JCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        kwargs.update({'dossier_code': self.kwargs['dossier_code']})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class App_JCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_appointment_j'
    model = Appointment_J
    form_class = App_JForm
    template_name = 'create_appointment_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form(self, form_class=None):
        form = super(App_JCreateView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class App_NCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_appointment_n'
    model = Appointment_N
    form_class = App_NForm
    template_name = 'create_appointment_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form(self, form_class=None):
        form = super(App_NCreateView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_NUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_appointment_n'
    model = Appointment_N
    form_class = Appointment_NForm
    template_name = 'update_appointment.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form_kwargs(self):
        kwargs = super(Appointment_NUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_JCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_appointment_j'
    model = Appointment_J
    form_class = Appointment_JForm
    template_name = 'create_appointment_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def get_form(self, form_class=None):
        form = super(Appointment_JCreateView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(Appointment_JCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Appointment_JUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_appointment_j'
    model = Appointment_J
    form_class = Appointment_JForm
    template_name = 'update_appointment.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(Appointment_JUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Dossier_NCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_dossier_n'
    model = Dossier_N
    form_class = Dossier_NForm
    template_name = 'create_dossier_n.html'

    def get_form_kwargs(self):
        kwargs = super(Dossier_NCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dossier-detailed-n", kwargs={'pk': self.object.pk})


class Doss_NCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_dossier_n'
    model = Dossier_N
    form_class = Doss_NForm
    template_name = 'create_dossier_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dossier-detailed-n", kwargs={'pk': self.object.pk})


class Dossier_NUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_dossier_n'
    model = Dossier_N
    form_class = Dossier_NFormUpdate
    template_name = 'update_dossier_n.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dossier-detailed-n", kwargs={'pk': self.object.pk})


class Dossier_JCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_dossier_j'
    model = Dossier_J
    form_class = Dossier_JForm
    template_name = 'create_dossier_j.html'

    def get_form_kwargs(self):
        kwargs = super(Dossier_JCreateView, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dossier-detailed-j", kwargs={'pk': self.object.pk})


class Doss_JCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_dossier_j'
    model = Dossier_J
    form_class = Doss_JForm
    template_name = 'create_dossier_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dossier-detailed-j", kwargs={'pk': self.object.pk})


class Dossier_JUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_dossier_j'
    model = Dossier_J
    form_class = Dossier_JFormUpdate
    template_name = 'update_dossier_j.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dossier-detailed-j", kwargs={'pk': self.object.pk})


class LawyerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_lawyers'
    model = Lawyer
    paginate_by = 25
    queryset = Lawyer.objects.filter(active=True).order_by('surname')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        lawyer_id = self.request.GET.get('lawyer_id', '')
        surname = self.request.GET.get('surname', '')
        mail = self.request.GET.get('mail', '')
        spec = self.request.GET.get('spec', '')
        data['object_list'] = Lawyer.objects.filter(active=True).filter(lawyer_code__icontains=lawyer_id).\
                                            filter(mail_info__icontains=mail).\
                                            filter(surname__icontains=surname).\
                                            filter(specialization__icontains=spec)

        selected_services = self.request.GET.getlist('services', '')
        if selected_services is not '':
            codeArraySelectedServices = []
            for selected_service in selected_services:
                codeArraySelectedServices.append(
                    Services.objects.get(name_service__icontains=selected_service).service_code)
            lawyers_services = lawyers_appointment(codeArraySelectedServices)
            all_lawyers = Lawyer.objects.all()
            for lawyer in lawyers_services:
                all_lawyers = all_lawyers.exclude(lawyer_code=lawyer['lawyer_code'])
            for lawyer in all_lawyers:
                data['object_list'] = data['object_list'].exclude(lawyer_code=lawyer.lawyer_code)

        data['spec'] = spec
        data['lawyer_id'] = lawyer_id
        data['mail'] = mail
        data['surname'] = surname
        data['selected_services'] = json.dumps(selected_services)
        data['services'] = Services.objects.all()
        return data


class ServicesListView(ListView):
    model = Services
    paginate_by = 25
    ordering = ['service_code']
    queryset = Services.objects.filter(active=True).order_by('service_code')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        service_id = self.request.GET.get('service_id', '')
        se_name = self.request.GET.get('se_name', '')
        group_sel = self.request.GET.get('group', '')
        data['object_list'] = Services.objects.filter(active=True,
                                                      service_code__icontains=service_id,
                                                      service_group__name_group__icontains=group_sel,
                                                      name_service__icontains=se_name)
        data['service_id'] = service_id
        data['se_name'] = se_name
        data['group_sel'] = group_sel
        data['groups'] = ServiceGroup.objects.all()
        return data


class Client_juridicalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_jclients'
    model = Client_juridical
    paginate_by = 25
    queryset = Client_juridical.objects.filter(active=True).order_by('surname')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        edrp_id = self.request.GET.get('edrp_id', '')
        comp_name = self.request.GET.get('comp_name', '')
        mail = self.request.GET.get('mail', '')
        surname = self.request.GET.get('surname', '')
        city = self.request.GET.get('city', '')
        phone_num = self.request.GET.get('phone', '')
        data['object_list'] = Client_juridical.objects.filter(active=True).filter(num_client_j__icontains=edrp_id).\
                                                filter(surname__icontains=surname).\
                                                filter(mail_info__icontains=mail).\
                                                filter(name_of_company__icontains=comp_name).\
                                                filter(adr_city__icontains=city)

        if phone_num is not '':
            phones = JPhone.objects.exclude(phone_num__icontains=phone_num)
            for phone in phones:
                data['object_list'] = data['object_list'].exclude(num_client_j=phone.client_juridical.num_client_j)
        data['edrp_id'] = edrp_id
        data['comp_name'] = comp_name
        data['mail'] = mail
        data['surname'] = surname
        data['phone'] = phone_num
        data['city'] = city
        return data


class Client_naturalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_nclients'
    model = Client_natural
    paginate_by = 25
    queryset = Client_natural.objects.filter(active=True).order_by('surname')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ik_id = self.request.GET.get('ik_id', '')
        passport_id = self.request.GET.get('passport_id', '')
        surname = self.request.GET.get('surname', '')
        mail = self.request.GET.get('mail', '')
        phone_num = self.request.GET.get('phone', '')
        city = self.request.GET.get('city', '')

        data['object_list'] = Client_natural.objects.filter(active=True).filter(num_client_n__icontains=ik_id).\
                                                    filter(passport_num__icontains=passport_id).\
                                                    filter(surname__icontains=surname).\
                                                    filter(mail_info__icontains=mail).\
                                                    filter(adr_city__icontains=city)

        if phone_num is not '':
            phones = NPhone.objects.exclude(phone_num__icontains=phone_num)
            for phone in phones:
                data['object_list'] = data['object_list'].exclude(num_client_n=phone.client_natural.num_client_n)
        data['ik_id'] = ik_id
        data['passport_id'] = passport_id
        data['mail'] = mail
        data['surname'] = surname
        data['phone'] = phone_num
        data['city'] = city
        return data


class Dossier_JListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_jdossiers'
    model = Dossier_J
    paginate_by = 25
    queryset = Dossier_J.objects.filter(active=True).order_by('date_signed')
    for object in queryset:
        object.count_fee()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dossier_id = self.request.GET.get('dossier_id', '')
        status = self.request.GET.get('status', '')
        client = self.request.GET.get('client', '')

        date_signed_from = self.request.GET.get('date_signed_from', '')
        date_signed_to = self.request.GET.get('date_signed_to', '')

        date_closed_from = self.request.GET.get('date_closed_from', '')
        date_closed_to = self.request.GET.get('date_closed_to', '')

        date_expired_from = self.request.GET.get('date_expired_from', '')
        date_expired_to = self.request.GET.get('date_expired_to', '')

        allDossiers = Dossier_J.objects.filter(active=True). \
            filter(code_dossier_j__icontains=dossier_id). \
            filter(num_client_j__num_client_j__icontains=client)

        if status is not '':
            allDossiers = allDossiers.filter(status=status)
        if date_signed_from is not '':
            allDossiers = allDossiers.filter(date_signed__gte=date_signed_from)
        if date_signed_to is not '':
            allDossiers = allDossiers.filter(date_signed__lte=date_signed_to)
        if date_closed_from is not '':
            allDossiers = allDossiers.filter(date_closed__gte=date_closed_from)
        if date_closed_to is not '':
            allDossiers = allDossiers.filter(date_closed__lte=date_closed_to)
        if date_expired_from is not '':
            allDossiers = allDossiers.filter(date_expired__gte=date_expired_from)
        if date_expired_to is not '':
            allDossiers = allDossiers.filter(date_expired__lte=date_expired_to)


        paidDossiers = Dossier_J.objects.all()
        paid = self.request.GET.get('paid', '')

        if str(paid) == "true":
            paidDossiers = Dossier_J.objects.filter(paid=True)
        elif str(paid) == "false":
            paidDossiers = Dossier_J.objects.filter(paid=False)

        data['object_list'] = allDossiers.intersection(paidDossiers)

        data['paid'] = paid
        data['open'] = open

        data['dossier_id'] = dossier_id
        data['status'] = status
        data['client'] = client

        data['date_signed_from'] = date_signed_from
        data['date_signed_to'] = date_signed_to
        data['date_closed_to'] = date_closed_to
        data['date_closed_from'] = date_closed_from
        data['date_expired_to'] = date_expired_to
        data['date_expired_from'] = date_expired_from
        return data


class Dossier_NListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_ndossiers'
    model = Dossier_N
    paginate_by = 25
    queryset = Dossier_N.objects.filter(active=True).order_by('date_signed')
    for object in queryset:
        object.count_fee()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dossier_id = self.request.GET.get('dossier_id', '')
        status = self.request.GET.get('status', '')
        client = self.request.GET.get('client', '')

        date_signed_from = self.request.GET.get('date_signed_from', '')
        date_signed_to = self.request.GET.get('date_signed_to', '')

        date_closed_from = self.request.GET.get('date_closed_from', '')
        date_closed_to = self.request.GET.get('date_closed_to', '')

        date_expired_from = self.request.GET.get('date_expired_from', '')
        date_expired_to = self.request.GET.get('date_expired_to', '')

        allDossiers = Dossier_N.objects.all().filter(active=True). \
            filter(code_dossier_n__icontains=dossier_id). \
            filter(num_client_n__num_client_n__icontains=client)

        if status is not '':
            allDossiers = allDossiers.filter(status=status)

        if date_signed_from is not '':
            allDossiers = allDossiers.filter(date_signed__gte=date_signed_from)
        if date_signed_to is not '':
            allDossiers = allDossiers.filter(date_signed__lte=date_signed_to)
        if date_closed_from is not '':
            allDossiers = allDossiers.filter(date_closed__gte=date_closed_from)
        if date_closed_to is not '':
            allDossiers = allDossiers.filter(date_closed__lte=date_closed_to)
        if date_expired_from is not '':
            allDossiers = allDossiers.filter(date_expired__gte=date_expired_from)
        if date_expired_to is not '':
            allDossiers = allDossiers.filter(date_expired__lte=date_expired_to)



        paidDossiers = Dossier_N.objects.all()
        paid = self.request.GET.get('paid', '')
        if str(paid) == "true":
            paidDossiers = Dossier_N.objects.filter(paid=True)
        elif str(paid) == "false":
            paidDossiers = Dossier_N.objects.filter(paid=False)


        data['object_list'] = allDossiers.intersection(paidDossiers)

        data['paid'] = paid
        data['open'] = open

        data['dossier_id'] = dossier_id
        data['status'] = status
        data['client'] = client


        data['date_signed_from'] = date_signed_from
        data['date_signed_to'] = date_signed_to
        data['date_closed_to'] = date_closed_to
        data['date_closed_from'] = date_closed_from
        data['date_expired_to'] = date_expired_to
        data['date_expired_from'] = date_expired_from

        return data


class Appointment_NListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_nappointments'
    model = Appointment_N
    paginate_by = 25
    ordering = ['-app_date']
    queryset = Appointment_N.objects.filter(active=True).order_by('app_date', 'app_time')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dossier = self.request.GET.get('dossier', '')
        la_code = self.request.GET.get('la_code', '')
        client_code = self.request.GET.get('client_code', '')

        date_app_from = self.request.GET.get('date_app_from', '')
        date_app_to = self.request.GET.get('date_app_to', '')

        time_app_from = self.request.GET.get('time_app_from', '')
        time_app_to = self.request.GET.get('time_app_to', '')



        data['object_list'] = Appointment_N.objects.all().filter(active=True). \
            filter(code_dossier_n__code_dossier_n__icontains=dossier,
                   lawyer_code__lawyer_code__icontains=la_code,
                   num_client_n__num_client_n__icontains=client_code)

        if date_app_from is not '':
            data['object_list'] = data['object_list'].filter(app_date__gte=date_app_from)
        if date_app_to is not '' :
            data['object_list'] = data['object_list'].filter(app_date__lte=date_app_to)


        if time_app_from is not '' or time_app_to is not '':
            begin = datetime.strptime('10:00', '%H:%M').time()
            end = datetime.strptime('19:00', '%H:%M').time()
            if time_app_to is '':
                begin = datetime.strptime(time_app_from, '%H:%M').time()
            elif time_app_from is '':
                end = datetime.strptime(time_app_to, '%H:%M').time()
            else:
                begin = datetime.strptime(time_app_from, '%H:%M').time()
                end = datetime.strptime(time_app_to, '%H:%M').time()
            data['object_list'] = data['object_list'].filter(app_time__range=(begin,end))


        selected_services = self.request.GET.getlist('services', '')
        if selected_services is not '':
            codeArraySelectedServices = []
            for selected_service in selected_services:
                codeArraySelectedServices.append(
                    Services.objects.get(name_service__icontains=selected_service).service_code)
            # get all appointments, which are in the list
            appointments_divided = appointments_N_by_services_dividing(codeArraySelectedServices)
            all_appointments = Appointment_N.objects.all()
            # exclude "good" appointments from all appointments, get bad appointments
            for appointment_divided in appointments_divided:
                all_appointments = all_appointments.exclude(appoint_code_n=appointment_divided['appoint_code'])
            #     exclude bad appointments from filtered appointments
            for appointment in all_appointments:
                data['object_list'] = data['object_list'].exclude(appoint_code_n=appointment.appoint_code_n)

        data['services'] = Services.objects.all()
        data['selected_services'] = selected_services

        data['dossier'] = dossier
        data['la_code'] = la_code
        data['client_code'] = client_code

        data['date_app_from'] = date_app_from
        data['date_app_to'] = date_app_to

        data['time_app_from'] = time_app_from
        data['time_app_to'] = time_app_to
        return data


class Appointment_JListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_jappointments'
    model = Appointment_J
    paginate_by = 25
    ordering = ['-app_date']
    queryset = Appointment_J.objects.filter(active=True).order_by('app_date', 'app_time')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dossier = self.request.GET.get('dossier', '')
        la_code = self.request.GET.get('la_code', '')
        client_code = self.request.GET.get('client_code', '')

        date_app_from = self.request.GET.get('date_app_from', '')
        date_app_to = self.request.GET.get('date_app_to', '')

        time_app_from = self.request.GET.get('time_app_from', '')
        time_app_to = self.request.GET.get('time_app_to', '')



        data['object_list'] = Appointment_J.objects.all().filter(active=True). \
            filter(code_dossier_j__code_dossier_j__icontains=dossier,
                   lawyer_code__lawyer_code__icontains=la_code,
                   num_client_j__num_client_j__icontains=client_code)

        # filter by date
        if date_app_from is not '':
            data['object_list'] = data['object_list'].filter(app_date__gte=date_app_from)
        if date_app_to is not '' :
            data['object_list'] = data['object_list'].filter(app_date__lte=date_app_to)

        #     filter by time
        if time_app_from is not '' or time_app_to is not '':
            begin = datetime.strptime('10:00', '%H:%M').time()
            end = datetime.strptime('19:00', '%H:%M').time()
            if time_app_to is '':
                begin = datetime.strptime(time_app_from, '%H:%M').time()
            elif time_app_from is '':
                end = datetime.strptime(time_app_to, '%H:%M').time()
            else:
                begin = datetime.strptime(time_app_from, '%H:%M').time()
                end = datetime.strptime(time_app_to, '%H:%M').time()
            data['object_list'] = data['object_list'].filter(app_time__range=(begin,end))


        selected_services = self.request.GET.getlist('services', '')

        if selected_services is not '':
            codeArraySelectedServices = []
            for selected_service in selected_services:
                codeArraySelectedServices.append(Services.objects.get(name_service__icontains=selected_service).service_code)

            # get all appointments, which are in the list
            appointments_divided = appointments_J_by_services_dividing(codeArraySelectedServices)
            all_appointments = Appointment_J.objects.all()
            # exclude "good" appointments from all appointments, get bad appointments
            for appointment_divided in appointments_divided:
                all_appointments = all_appointments.exclude(appoint_code_j=appointment_divided['appoint_code'])
            #     exclude bad appointments from filtered appointments
            for appointment in all_appointments:
                data['object_list'] = data['object_list'].exclude(appoint_code_j=appointment.appoint_code_j)

        data['services'] = Services.objects.all()
        data['selected_services'] = selected_services

        data['dossier'] = dossier
        data['la_code'] = la_code
        data['client_code'] = client_code

        data['date_app_from'] = date_app_from
        data['date_app_to'] = date_app_to

        data['time_app_from'] = time_app_from
        data['time_app_to'] = time_app_to
        return data


@login_required()
@requires_csrf_token
def ndossierDelete(request, pk):
    obj = get_object_or_404(Dossier_N, code_dossier_n=pk)
    if request.method == 'POST':
        form = Dossier_NFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            today = date.today()
            futureAppointments = Appointment_N.objects.filter(active=True, code_dossier_n=pk, app_date__gt=today)
            if not futureAppointments:
                page.active = False
                page.save()
            else:
                return render(request, 'confirm_delete.html', {'form': form, 'error':"Досьє має записи у майбутньому",
                                                               'redirect':reverse('ndossiers')})
            return redirect("ndossiers")
    else:
        form = Dossier_NFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def lawyerDelete(request, pk):
    obj = get_object_or_404(Lawyer, lawyer_code=pk)
    if request.method == 'POST':
        form = LawyerFormDelete(request.POST, instance=obj)
        if form.is_valid():
            page = form.save(commit=False)
            today = date.today()
            futureJAppointments = Appointment_J.objects.filter(active=True, lawyer_code=pk, app_date__gt=today)
            futureNAppointments = Appointment_N.objects.filter(active=True, lawyer_code=pk, app_date__gt=today)
            unclosedJDossiers = Dossier_J.objects.filter(active=True, lawyer_code=pk, status='open')
            unclosedNDossiers = Dossier_N.objects.filter(active=True, lawyer_code=pk, status='open')
            if not futureJAppointments and not futureNAppointments and not unclosedJDossiers and not unclosedNDossiers:
                page.active = False
                page.save()
            else:
                if futureJAppointments and futureNAppointments and not unclosedJDossiers and not unclosedNDossiers:
                    return render(request, 'confirm_delete.html', {'form': form, 'error': "Адвокат має записи в майбутньому",
                                                               'redirect':reverse('lawyers')})
                elif not futureJAppointments and not futureNAppointments and unclosedJDossiers and unclosedNDossiers:
                    return render(request, 'confirm_delete.html', {'form': form, 'error': "Адвокат має незакриті справи",
                                                               'redirect':reverse('lawyers')})
                else:
                    return render(request, 'confirm_delete.html',
                                  {'form': form, 'error': "Адвокат має незакриті справи та записи в майбутньому",
                                                               'redirect':reverse('lawyers')})
            return redirect("lawyers")
    else:
        form = LawyerFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def jdossierDelete(request, pk):
    obj = get_object_or_404(Dossier_J, code_dossier_j=pk)
    if request.method == 'POST':
        form = Dossier_JFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            today = date.today()
            futureAppointments = Appointment_J.objects.filter(active=True, code_dossier_j=pk, app_date__gt=today)
            if not futureAppointments:
                page.active = False
                page.save()
            else:
                return render(request, 'confirm_delete.html', {'form': form, 'error': "Досьє має записи у майбутньому",
                                                               'redirect':reverse('jdossiers')})
            return redirect("jdossiers")
    else:
        form = Dossier_JFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def serviceDelete(request, pk):
    obj = get_object_or_404(Services, service_code=pk)
    if request.method == 'POST':
        form = ServiceFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            today = date.today()
            futureAppointmentsN = Appointment_N.objects.filter(service__service_code=pk, app_date__gt=today)
            futureAppointmentsJ = Appointment_J.objects.filter(service__service_code=pk, app_date__gt=today)

            if not futureAppointmentsN and not futureAppointmentsJ:
                page.active = False
                page.save()
            else:
                return render(request, 'confirm_delete.html', {'form': form,
                                                               'error': "Послуга має записи у майбутньому",
                                                               'redirect':reverse('services')})

            return redirect("services")
    else:
        form = ServiceFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def nappointDelete(request, pk):
    obj = get_object_or_404(Appointment_N, appoint_code_n=pk)
    if request.method == 'POST':
        form = Appoint_NFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            page.active = False
            page.save()
            return redirect("nappointments")
    else:
        form = Appoint_NFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def jappointDelete(request, pk):
    obj = get_object_or_404(Appointment_J, appoint_code_j=pk)
    if request.method == 'POST':
        form = Appoint_JFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            page.active = False
            page.save()
            return redirect("jappointments")
    else:
        form = Appoint_JFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def jclientDelete(request, pk):
    obj = get_object_or_404(Client_juridical, num_client_j=pk)
    if request.method == 'POST':
        form = Client_JFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            today = date.today()
            futureAppointments = Appointment_J.objects.filter(active=True, num_client_j=pk, app_date__gt=today)
            unpaidDossiers = Dossier_J.objects.filter(active=True, num_client_j=pk, paid=False)
            if not unpaidDossiers and not futureAppointments:
                page.active = False
                page.save()
                Dossier_J.objects.filter(active=True, num_client_j=pk).update(active=False)
            else:
                if futureAppointments and not unpaidDossiers:
                    return render(request, 'confirm_delete.html', {'form': form, 'error': "Клієнт має записи в майбутньому",
                                                               'redirect':reverse('jcustomers')})
                elif not futureAppointments and unpaidDossiers:
                    return render(request, 'confirm_delete.html',
                                  {'form': form, 'error': "Клієнт має неоплачені досьє",
                                                               'redirect':reverse('jcustomers')})
                else:
                    return render(request, 'confirm_delete.html',
                                  {'form': form, 'error': "Клієнт має неоплачені досьє та записи в майбутньому",
                                                               'redirect':reverse('jcustomers')})

            return redirect("jcustomers")
    else:
        form = Client_JFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})


@login_required()
@requires_csrf_token
def nclientDelete(request, pk):
    obj = get_object_or_404(Client_natural, num_client_n=pk)
    if request.method == 'POST':
        form = Client_NFormDelete(request.POST, instance=obj)

        if form.is_valid():
            page = form.save(commit=False)
            today = date.today()
            futureAppointments = Appointment_N.objects.filter(active=True, num_client_n=pk, app_date__gt=today)
            unpaidDossiers = Dossier_N.objects.filter(active=True, num_client_n=pk, paid=False)
            if not unpaidDossiers and not futureAppointments:
                page.active = False
                page.save()
                Dossier_N.objects.filter(active=True,num_client_n=pk).update(active=False)
            else:
                if futureAppointments and not unpaidDossiers:
                    return render(request, 'confirm_delete.html', {'form': form, 'error': "Клієнт має записи в майбутньому",
                                                               'redirect':reverse('ncustomers')})
                elif not futureAppointments and unpaidDossiers:
                    return render(request, 'confirm_delete.html',
                                  {'form': form, 'error': "Клієнт має неоплачені досьє",
                                                               'redirect':reverse('ncustomers')})
                else:
                    return render(request, 'confirm_delete.html',
                                  {'form': form, 'error': "Клієнт має неоплачені досьє та записи в майбутньому",
                                                               'redirect':reverse('ncustomers')})

            return redirect("ncustomers")
    else:
        form = Client_NFormDelete()

    return render(request, 'confirm_delete.html', {'form': form})
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import CreateView, DeleteView, UpdateView, TemplateView, ListView
from django.views import generic
from .forms import *
from django.http import JsonResponse
from .sql_querries import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required


@login_required()
@requires_csrf_token
def client_ajax(request):
    if request.method == 'POST':
        response = {}
        response['dossier'] = []
        if request.POST['dosJ'] == 'true':
            dossiers = Dossier_J.objects.filter(num_client_j=request.POST['client'])
            for dossier in dossiers:
                response['dossier'].append({'code': dossier.code_dossier_j,
                                            'issue': dossier.issue})
        else:
            dossiers = Dossier_N.objects.filter(num_client_n=request.POST['client'])
            for dossier in dossiers:
                response['dossier'].append({'code': dossier.code_dossier_n,
                                            'issue': dossier.issue})
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
        try:
            context['open_dossiers_j'] = Dossier_J.objects.raw(
                'SELECT code_dossier_j, COUNT(code_dossier_j) AS counted_dossiers '
                'FROM "Dossier_J" '
                'WHERE status = %s '
                'GROUP BY code_dossier_j',
                ['open'])[0].counted_dossiers
        except:
            context['open_dossiers_j'] = 0
        context['value'] = str(nom_value() + extra_value())
        context['service_count'] = service_counter()
        context['lawyer_counter'] = lawyer_counter()
        context['appointments'] = appointment_getter()
        context['won_dossiers'] = won_dossiers()
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
        if dEnd < dStart:
            print("error")
        response = {}
        response['closed_j'] = date_closed_dossier_j(dStart, dEnd)
        response['closed_n'] = date_closed_dossier_n(dStart, dEnd)
        response['open_n'] = date_open_dossier_n(dStart, dEnd)
        response['open_j'] = date_open_dossier_j(dStart, dEnd)
        response['service_count'] = date_service_counter(dStart, dEnd)
        response['all_won_dossiers'] = date_won_dossiers(dStart, dEnd)
        response['value'] = date_value(dStart, dEnd)
        response['lawyer_counter'] = date_lawyer_counter(dStart, dEnd)
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
        context['lawyers'] = Lawyer.objects.filter(service=self.kwargs['pk'])
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
        if group.name == "Lawyers":
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
            [la_code, 'open'])
        context['closed_dossiers_j'] = Dossier_J.objects.raw(
            'SELECT code_dossier_j, COUNT(code_dossier_j) AS counted_dossiers '
            'FROM "Dossier_J" '
            'WHERE lawyer_code_id = %s AND status <> %s '
            'GROUP BY code_dossier_j',
            [la_code, 'open'])
        try:
            context['nominal_value'] = lawyer_nom_value(la_code)[1]
        except:
            context['nominal_value'] = 0
        try:
            context['bonus_value'] = lawyer_extra_value(la_code)[1]
        except:
            context['bonus_value'] = 0
        return context


class DossierDetailJView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    permission_required = 'DataBase.view_dossier_j'
    model = Dossier_J
    context_object_name = "dossier"
    template_name = "dossier_detail_j.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment_J.objects.filter(code_dossier_j=self.kwargs['pk'])

        return context


class DossierDetailNView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    permission_required = 'DataBase.view_dossier_n'
    model = Dossier_N
    context_object_name = "dossier"
    template_name = "dossier_detail_n.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment_N.objects.filter(code_dossier_n=self.kwargs['pk'])

        return context


class ClientNDetailView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_client_natural'
    model = Client_natural
    context_object_name = "client_natural"
    template_name = "client_detail_n.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        if self.request.user.groups.filter(name="ClientsN").exists():
            cl_code = self.kwargs['pk']
            cl_pk = Client_natural.objects.get(mail_info=self.request.user.email).pk
            return cl_pk == cl_code
        else:
            return True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_code = self.kwargs['pk']
        context['phones'] = NPhone.objects.filter(client_natural_id=client_code)
        context['appointments'] = Appointment_N.objects.filter(num_client_n=self.kwargs['pk']).\
                            order_by('-app_date', '-app_time')
        context['dossiers'] = Dossier_N.objects.filter(num_client_n=self.kwargs['pk'])
        return context


class ClientJDetailView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, generic.DetailView):
    permission_required = 'DataBase.view_client_juridical'
    model = Client_juridical
    context_object_name = "client_juridical"
    template_name = "client_detail_j.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        if self.request.user.groups.filter(name="ClientsJ").exists():
            cl_code = self.kwargs['pk']
            cl_pk = Client_juridical.objects.get(mail_info=self.request.user.email).pk
            return cl_pk == cl_code
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_code = self.kwargs['pk']
        context['phones'] = JPhone.objects.filter(client_juridical_id=client_code)
        context['appointments'] = Appointment_J.objects.filter(num_client_j=self.kwargs['pk'])
        context['dossiers'] = Dossier_J.objects.filter(num_client_j=self.kwargs['pk'])
        return context


@login_required()
def index(request):
    if request.user.is_superuser:
        return render(request, 'stat_panel.html', {})
    group = request.user.groups.filter(user=request.user)[0]
    if group.name == "Secretaries":
        return HttpResponseRedirect(reverse('stats'))
    elif group.name == "Lawyers":
        l_code = Lawyer.objects.get(mail_info=request.user.email).pk
        return HttpResponseRedirect('/database/lawyer/' + l_code)
    elif group.name == "ClientsJ":
        cl_code = Client_juridical.objects.get(mail_info=request.user.email).pk
        return HttpResponseRedirect('/database/client_J/' + cl_code)
    elif group.name == "ClientsN":
        cl_code = Client_natural.objects.get(mail_info=request.user.email).pk
        return HttpResponseRedirect('/database/client_N/' + cl_code)
    return render(request, 'index.html', {})


class LawyerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_lawyer'
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


class LawyerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_lawyer'
    model = Lawyer
    template_name = 'update_lawyer.html'
    form_class = LawyerForm

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


class LawyerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_lawyer'
    model = Lawyer
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('lawyers')


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


class ServicesDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_services'
    model = Services
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('services')


class Client_naturalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_client_natural'
    model = Client_natural
    template_name = 'create_client_natural.html'
    form_class = Client_NForm

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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.pk})


class Client_naturalDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_client_natural'
    model = Client_natural
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('ncustomers')


class Client_juridicalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_client_juridical'
    model = Client_juridical
    template_name = 'create_client_juridical.html'
    form_class = Client_JForm

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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.pk})


class Client_juridicalDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_client_juridical'
    model = Client_juridical
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('jcustomers')


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
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_NUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_appointment_n'
    model = Appointment_N
    form_class = Appointment_NFormUpdate
    template_name = 'update_appointment.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Appointment_NDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_appointment_n'
    model = Appointment_N
    template_name = 'confirm_delete.html'

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
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Appointment_JUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'DataBase.change_appointment_j'
    model = Appointment_J
    form_class = Appointment_JFormUpdate
    template_name = 'update_appointment.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Appointment_JDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_appointment_j'
    model = Appointment_J
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Dossier_NCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_dossier_n'
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
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Dossier_NDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_dossier_n'
    model = Dossier_N
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse("client-detailed-view-n", kwargs={'pk': self.object.num_client_n.pk})


class Dossier_JCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'DataBase.add_dossier_j'
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
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class Dossier_JDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'DataBase.delete_dossier_j'
    model = Dossier_J
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse("client-detailed-view-j", kwargs={'pk': self.object.num_client_j.pk})


class LawyerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_lawyers'
    model = Lawyer
    paginate_by = 25
    queryset = Lawyer.objects.order_by('surname')


class ServicesListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_services'
    model = Services


class Client_juridicalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_jclients'
    model = Client_juridical
    paginate_by = 25
    queryset = Client_juridical.objects.order_by('surname')


class Client_naturalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_nclients'
    model = Client_natural
    paginate_by = 25
    queryset = Client_natural.objects.order_by('surname')


class Dossier_JListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_jdossiers'
    model = Dossier_J
    paginate_by = 25
    queryset = Dossier_J.objects.order_by('date_signed')


class Dossier_NListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_ndossiers'
    model = Dossier_N
    paginate_by = 25
    queryset = Dossier_N.objects.order_by('date_signed')


class Appointment_NListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_nappointments'
    model = Appointment_N
    paginate_by = 25
    queryset = Appointment_N.objects.order_by('app_date').order_by('app_time')


class Appointment_JListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'DataBase.view_all_jappointments'
    model = Appointment_J
    paginate_by = 25
    queryset = Appointment_J.objects.order_by('app_date').order_by('app_time')

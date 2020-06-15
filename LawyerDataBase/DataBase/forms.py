from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.forms import ModelForm, inlineformset_factory, SelectDateWidget, SplitDateTimeWidget
from django import forms
from .models import *
from django.forms import Textarea, TimeInput, TextInput, CheckboxSelectMultiple

from django.utils.translation import ugettext_lazy as _

# class CustomUserCreationForm(ModelForm):
class CustomUserCreationForm(forms.Form):
    # username = forms.CharField(label='Ім`я користувача', min_length=4, max_length=150, required=False)
    # email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердіть пароль', widget=forms.PasswordInput)
    group = forms.ModelChoiceField(label='Група', queryset=Group.objects.all(), required=True)

    # def __init__(self, *args, **kwargs):
    #     user_id = kwargs.pop('username')
    #     mail_info = kwargs.pop('email')
    #     super(CustomUserCreationForm, self).__init__(*args, **kwargs)
    #     self.fields['username'].initial = user_id
    #     self.fields['username'].disabled = True
    #     self.fields['email'].initial = mail_info
    #     self.fields['email'].disabled = True

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
             raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Паролі не збігаються")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            'username',
            'email',
             self.cleaned_data['password1']
        )
        user.groups.add(self.cleaned_data['group'])
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'group']



class LawyerForm(ModelForm):
    lawyer_code = forms.CharField(label='Код свідоцтва', max_length=8, min_length=8)
    first_name = forms.CharField(label='Ім`я')
    surname = forms.CharField(label='Прізвище')
    mid_name = forms.CharField(label='По батькові')
    specialization = forms.CharField(label='Спеціалізація')
    mail_info = forms.EmailField(label='E-mail')
    service = forms.ModelMultipleChoiceField(label='Послуги', required=False,
                                             queryset=Services.objects.filter(active=True))
    work_days = forms.ModelMultipleChoiceField(label='Робочі дні', required=False,
                                             queryset=Work_days.objects.all())

    class Meta:
        model = Lawyer
        fields = ['lawyer_code', 'first_name', 'surname',
                  'mid_name', 'specialization', 'mail_info', 'service', 'work_days']


class LawyerUpdateForm(ModelForm):
    first_name = forms.CharField(label='Ім`я')
    surname = forms.CharField(label='Прізвище')
    mid_name = forms.CharField(label='По батькові')
    specialization = forms.CharField(label='Спеціалізація')
    service = forms.ModelMultipleChoiceField(label='Послуги', required=False,
                                             queryset=Services.objects.filter(active=True))
    work_days = forms.ModelMultipleChoiceField(label='Робочі дні', required=False,
                                             queryset=Work_days.objects.all())

    class Meta:
        model = Lawyer
        fields = ['first_name', 'surname', 'mid_name', 'specialization', 'service', 'work_days']


LPhoneFormSet = inlineformset_factory(Lawyer, LPhone, max_num=2, fields=['phone_num'], labels={'phone_num': ('Телефон')}, min_num=1)


class LawyerServiceForm(forms.Form):
    service_code = forms.CharField(label='Код послуги', disabled=True)
    lawyers = forms.ModelMultipleChoiceField(label='Адвокати', required=False,
                                             queryset=Lawyer.objects.all().filter(active=True))

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(LawyerServiceForm, self).__init__(*args, **kwargs)
        self.fields['service_code'].initial = pk
        # self.fields['lawyers'].queryset = Lawyer.objects.exclude(service=pk)


class ServiceGroupForm(ModelForm):
    name_group = forms.CharField(label='Назва групи', max_length=50)

    class Meta:
        model = ServiceGroup
        fields = '__all__'


class ServicesForm(ModelForm):
    service_code = forms.CharField(label='Код послуги', max_length=5, min_length=5)
    name_service = forms.CharField(label='Послуга', max_length=50)
    nominal_value = forms.DecimalField(label='Номінальна вартість', max_digits=6, decimal_places=2)
    bonus_value = forms.DecimalField(label='Бонусна вартість', max_digits=6, decimal_places=2)
    lawyers = forms.ModelMultipleChoiceField(label='Адвокати', required=False,
                                             queryset=Lawyer.objects.all().filter(active=True))
    service_group = forms.ModelChoiceField(label='Група послуг', required=False, queryset=ServiceGroup.objects.all())

    class Meta:
        model = Services
        exclude = ('active',)


class ServicesUpdateForm(ModelForm):
    service_code = forms.CharField(label='Код послуги', max_length=5, min_length=5)
    name_service = forms.CharField(label='Послуга', max_length=50)
    nominal_value = forms.DecimalField(label='Номінальна вартість', max_digits=6, decimal_places=2)
    bonus_value = forms.DecimalField(label='Бонусна вартість', max_digits=6, decimal_places=2)
    service_group = forms.ModelChoiceField(label='Група послуг', queryset=ServiceGroup.objects.all())

    class Meta:
        model = Services
        fields = ['service_code', 'name_service', 'nominal_value',
                  'bonus_value', 'service_group']

    def clean_bonus_value(self):
        bonus_value = self.cleaned_data['bonus_value']
        if bonus_value < self.cleaned_data['nominal_value']:
            raise ValidationError(_('Бонусна вартість не може бути меншою за номінальну'), code='invalid')
        return bonus_value


NPhoneFormset = inlineformset_factory(Client_natural, NPhone, max_num=2, fields=['phone_num'], labels={'phone_num': ('Телефон')}, min_num=1)

JPhoneFormset = inlineformset_factory(Client_juridical, JPhone, max_num=2, fields=['phone_num'], labels={'phone_num': ('Телефон')}, min_num=1)


class Appointment_NForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.filter(active=True))
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True))
    code_dossier_n = forms.ModelChoiceField(label='Досьє', queryset=Dossier_N.objects.filter(status='open'))

    class Meta:
        model = Appointment_N
        fields = ['num_client_n','code_dossier_n','service', 'lawyer_code', 'app_date', 'app_time', 'comment']
        widgets = {

            'app_time': TimeInput(format='%H:%M'),
            'app_date': TextInput(attrs={'readonly': 'readonly'})

        }

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(Appointment_NForm, self).__init__(*args, **kwargs)
        self.fields['num_client_n'].initial = pk
        self.fields['num_client_n'].disabled = True
        self.fields['code_dossier_n'].queryset = Dossier_N.objects.filter(active=True).filter(num_client_n=pk).filter(status='open')


class Appoint_NForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.filter(active=True))
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True))
    code_dossier_n = forms.ModelChoiceField(label='Досьє', queryset=Dossier_N.objects.filter(status='open'))

    class Meta:
        model = Appointment_N
        fields = ['num_client_n', 'code_dossier_n', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']
        widgets = {

            'app_time': TimeInput(format='%H:%M'),
            'app_date': TextInput(attrs={'readonly': 'readonly'})

        }

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        dossier_code = kwargs.pop('dossier_code')
        super(Appoint_NForm, self).__init__(*args, **kwargs)
        self.fields['num_client_n'].initial = pk
        self.fields['num_client_n'].disabled = True
        self.fields['code_dossier_n'].initial = dossier_code
        self.fields['code_dossier_n'].disabled = True


class Appoint_JForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.filter(active=True))
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True))
    code_dossier_j = forms.ModelChoiceField(label='Досьє', queryset=Dossier_J.objects.filter(status='open'))

    class Meta:
        model = Appointment_J
        fields = ['num_client_j', 'code_dossier_j', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']
        widgets = {

            'app_time': TimeInput(format='%H:%M'),
            'app_date': TextInput(attrs={'readonly': 'readonly'})

        }

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        dossier_code = kwargs.pop('dossier_code')
        super(Appoint_JForm, self).__init__(*args, **kwargs)
        self.fields['num_client_j'].initial = pk
        self.fields['num_client_j'].disabled = True
        self.fields['code_dossier_j'].initial = dossier_code
        self.fields['code_dossier_j'].disabled = True


class App_JForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.filter(active=True))
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True))
    code_dossier_j = forms.ModelChoiceField(label='Досьє', queryset=Dossier_J.objects.filter(status='open', active=True))

    class Meta:
        model = Appointment_J
        fields = ['num_client_j', 'code_dossier_j', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']
        widgets = {

            'app_time': TimeInput(format='%H:%M'),
            'app_date': TextInput(attrs={'readonly': 'readonly'})

        }


class App_NForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.filter(active=True))
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True))
    code_dossier_n = forms.ModelChoiceField(label='Досьє', queryset=Dossier_N.objects.filter(status='open'))

    class Meta:
        model = Appointment_N
        fields = ['num_client_n', 'code_dossier_n', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']
        widgets = {

            'app_time': TimeInput(format='%H:%M'),
            'app_date': TextInput(attrs={'readonly': 'readonly'})

        }


class Appointment_JForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly':'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.filter(active=True))
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True))
    code_dossier_j = forms.ModelChoiceField(label='Досьє', queryset=Dossier_J.objects.filter(active=True).filter(status='open'))

    class Meta:
        model = Appointment_J
        fields = ['num_client_j', 'code_dossier_j', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(Appointment_JForm, self).__init__(*args, **kwargs)
        self.fields['num_client_j'].initial = pk
        self.fields['num_client_j'].disabled = True
        self.fields['code_dossier_j'].queryset = Dossier_J.objects.filter(active=True).filter(num_client_j=pk).filter(status='open')


class Dossier_JForm(ModelForm):
    code_dossier_j = forms.CharField(label='Код', max_length=8, min_length=8)
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання', widget=TextInput(attrs={'autocomplete':'off'}))
    date_expired = forms.DateField(label='Дата спливу', widget=TextInput(attrs={'autocomplete':'off'}))
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    fee = forms.DecimalField(label='Гонорар', initial=0, widget=TextInput(attrs={'readonly ':'readonly'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    def clean(self):
        cleaned_data = super(Dossier_JForm, self).clean()
        status = cleaned_data.get('status')
        date_closed = cleaned_data.get('date_closed')
        paidcontext = self.cleaned_data['paid']
        c_name = cleaned_data.get('court_name')
        c_adr = cleaned_data.get('court_adr')
        c_date = cleaned_data.get('court_date')
        lawyer = cleaned_data.get('lawyer_code')
        today = date.today()
        dossier_code = cleaned_data.get('code_dossier_j')
        futureAppointments = Appointment_J.objects.filter(active=True, code_dossier_j=dossier_code, app_date__gt=today)

        if date_closed:
            if futureAppointments:
                raise ValidationError(_('Справа не може бути закритою, оскільки існують'
                                        ' записи, що ще не відбулися'), code='invalid')

        if paidcontext and str(self.cleaned_data['status']) == 'open':
            raise ValidationError(_('Справа не може бути оплачена, коли вона відкрита'), code='invalid')

        if date_closed is None:
            if not str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може бути закритою без дати закриття'},
                                      code='invalid')

        status = self.cleaned_data['status']
        if str(status) != 'open':
            date_closed = self.cleaned_data['date_closed']
            if date_closed is None:
                raise ValidationError(_('Справа не може бути закритою, коли вона не має дати закриття'), code='invalid')

        if date_closed is not None:
            if str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може мати дату закриття, коли вона відкрита'},
                                      code='invalid')

        if str(status) == 'closed-won':
            if c_date is None or c_adr is None or c_name is None or lawyer is None:
                raise ValidationError(
                    {'status': 'Якщо справа "закрита-виграна", то всі поля, що'
                               ' стосуються судового засідання повинні бути заповнені'},
                    code='invalid')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('pk')
        super(Dossier_JForm, self).__init__(*args, **kwargs)
        self.fields['num_client_j'].initial = user_id
        self.fields['num_client_j'].disabled = True

    class Meta:
        model = Dossier_J
        exclude = ('active',)


class Doss_JForm(ModelForm):
    code_dossier_j = forms.CharField(label='Код', max_length=8, min_length=8)
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all().filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all().filter(active=True), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання', widget=TextInput(attrs={'autocomplete':'off'}))
    date_expired = forms.DateField(label='Дата спливу', widget=TextInput(attrs={'autocomplete':'off'}))
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    fee = forms.DecimalField(label='Гонорар', initial=0, widget=TextInput(attrs={'readonly ':'readonly'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    def clean(self):
        cleaned_data = super(Doss_JForm, self).clean()
        status = cleaned_data.get('status')
        date_closed = cleaned_data.get('date_closed')
        paidcontext = self.cleaned_data['paid']
        c_name = cleaned_data.get('court_name')
        c_adr = cleaned_data.get('court_adr')
        c_date = cleaned_data.get('court_date')
        lawyer = cleaned_data.get('lawyer_code')
        today = date.today()
        dossier_code = cleaned_data.get('code_dossier_j')
        futureAppointments = Appointment_J.objects.filter(active=True, code_dossier_j=dossier_code, app_date__gt=today)

        if date_closed:
            if futureAppointments:
                raise ValidationError(_('Справа не може бути закритою, оскільки існують'
                                        ' записи, що ще не відбулися'), code='invalid')

        if paidcontext and str(self.cleaned_data['status']) == 'open':
            raise ValidationError(_('Справа не може бути оплачена, коли вона відкрита'), code='invalid')

        if date_closed is None:
            if not str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може бути закритою без дати закриття'},
                                      code='invalid')

        status = self.cleaned_data['status']
        if str(status) != 'open':
            date_closed = self.cleaned_data['date_closed']
            if date_closed is None:
                raise ValidationError(_('Справа не може бути закритою, коли вона не має дати закриття'), code='invalid')

        if date_closed is not None:
            if str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може мати дату закриття, коли вона відкрита'},
                                      code='invalid')

        if str(status) == 'closed-won':
            if c_date is None or c_adr is None or c_name is None or lawyer is None:
                raise ValidationError(
                    {'status': 'Якщо справа "закрита-виграна", то всі поля, що'
                               ' стосуються судового засідання повинні бути заповнені'},
                    code='invalid')
        return cleaned_data

    class Meta:
        model = Dossier_J
        exclude = ('active',)


class Dossier_NForm(ModelForm):
    code_dossier_n = forms.CharField(label='Код', max_length=8, min_length=8)
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання', widget=TextInput(attrs={'autocomplete':'off'}))
    date_expired = forms.DateField(label='Дата спливу', widget=TextInput(attrs={'autocomplete':'off'}))
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    fee = forms.DecimalField(label='Гонорар', initial=0, widget=TextInput(attrs={'readonly ':'readonly'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    def clean(self):
        cleaned_data = super(Dossier_NForm, self).clean()
        status = cleaned_data.get('status')
        date_closed = cleaned_data.get('date_closed')
        paidcontext = self.cleaned_data['paid']
        c_name = cleaned_data.get('court_name')
        c_adr = cleaned_data.get('court_adr')
        c_date = cleaned_data.get('court_date')
        lawyer = cleaned_data.get('lawyer_code')
        today = date.today()
        dossier_code = cleaned_data.get('code_dossier_n')
        futureAppointments = Appointment_N.objects.filter(active=True, code_dossier_n=dossier_code, app_date__gt=today)

        if date_closed:
            if futureAppointments:
                raise ValidationError(_('Справа не може бути закритою, оскільки існують'
                                        ' записи, що ще не відбулися'), code='invalid')

        if paidcontext and str(self.cleaned_data['status']) == 'open':
            raise ValidationError(_('Справа не може бути оплачена, коли вона відкрита'), code='invalid')

        if date_closed is None:
            if not str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може бути закритою без дати закриття'},
                                      code='invalid')

        status = self.cleaned_data['status']
        if str(status) != 'open':
            date_closed = self.cleaned_data['date_closed']
            if date_closed is None:
                raise ValidationError(_('Справа не може бути закритою, коли вона не має дати закриття'), code='invalid')

        if date_closed is not None:
            if str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може мати дату закриття, коли вона відкрита'},
                                      code='invalid')

        if str(status) == 'closed-won':
            if c_date is None or c_adr is None or c_name is None or lawyer is None:
                raise ValidationError(
                    {'status': 'Якщо справа "закрита-виграна", то всі поля, що'
                               ' стосуються судового засідання повинні бути заповнені'},
                    code='invalid')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('pk')
        super(Dossier_NForm, self).__init__(*args, **kwargs)
        self.fields['num_client_n'].initial = user_id
        self.fields['num_client_n'].disabled = True

    class Meta:
        model = Dossier_N
        exclude = ('active',)


class Doss_NForm(ModelForm):
    code_dossier_n = forms.CharField(label='Код', max_length=8, min_length=8)
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.all().filter(active=True))
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all().filter(active=True), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання', widget=TextInput(attrs={'autocomplete':'off'}))
    date_expired = forms.DateField(label='Дата спливу', widget=TextInput(attrs={'autocomplete':'off'}))
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    fee = forms.DecimalField(label='Гонорар', initial=0, widget=TextInput(attrs={'readonly ':'readonly'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    def clean(self):
        cleaned_data = super(Doss_NForm, self).clean()
        status = cleaned_data.get('status')
        date_closed = cleaned_data.get('date_closed')
        paidcontext = self.cleaned_data['paid']
        c_name = cleaned_data.get('court_name')
        c_adr = cleaned_data.get('court_adr')
        c_date = cleaned_data.get('court_date')
        lawyer = cleaned_data.get('lawyer_code')
        today = date.today()
        dossier_code = cleaned_data.get('code_dossier_n')
        futureAppointments = Appointment_N.objects.filter(active=True, code_dossier_n=dossier_code, app_date__gt=today)

        if date_closed:
            if futureAppointments:
                raise ValidationError(_('Справа не може бути закритою, оскільки існують'
                                        ' записи, що ще не відбулися'), code='invalid')

        if paidcontext and str(self.cleaned_data['status']) == 'open':
            raise ValidationError(_('Справа не може бути оплачена, коли вона відкрита'), code='invalid')

        if date_closed is None:
            if not str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може бути закритою без дати закриття'},
                                      code='invalid')

        status = self.cleaned_data['status']
        if str(status) != 'open':
            date_closed = self.cleaned_data['date_closed']
            if date_closed is None:
                raise ValidationError(_('Справа не може бути закритою, коли вона не має дати закриття'), code='invalid')

        if date_closed is not None:
            if str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може мати дату закриття, коли вона відкрита'},
                                      code='invalid')

        if str(status) == 'closed-won':
            if c_date is None or c_adr is None or c_name is None or lawyer is None:
                raise ValidationError(
                    {'status': 'Якщо справа "закрита-виграна", то всі поля, що'
                               ' стосуються судового засідання повинні бути заповнені'},
                    code='invalid')
        return cleaned_data

    class Meta:
        model = Dossier_N
        exclude = ('active',)


class Client_NForm(ModelForm):
    num_client_n = forms.CharField(label='Ідентифікаційний код', max_length=10, min_length=10)
    first_name = forms.CharField(label='Ім`я', max_length=50)
    surname = forms.CharField(label='Прізвище', max_length=50)
    mid_name = forms.CharField(label='По батькові', max_length=50)
    adr_city = forms.CharField(label='Місто', max_length=100)
    adr_street = forms.CharField(label='Вулиця', max_length=200)
    adr_build = forms.CharField(label='Будинок', max_length=5)
    mail_info = forms.EmailField(label='E-mail', max_length=30)
    birth_date = forms.DateField(label='Дата народження', widget=TextInput(attrs={'autocomplete':'off'}))
    passport_date = forms.DateField(label='Дата паспорта', widget=TextInput(attrs={'autocomplete':'off'}))
    passport_authority = forms.CharField(label='Орган паспорта', max_length=4, min_length=4)
    passport_num = forms.CharField(label='Номер паспорта', max_length=9, min_length=8)

    class Meta:
        model = Client_natural
        exclude = ('active',)


class Client_JForm(ModelForm):
    num_client_j = forms.CharField(label='ЄДРПОУ', max_length=8, min_length=8)
    first_name = forms.CharField(label='Ім`я', max_length=50)
    surname = forms.CharField(label='Прізвище', max_length=50)
    mid_name = forms.CharField(label='По батькові', max_length=50)
    adr_city = forms.CharField(label='Місто', max_length=100)
    adr_street = forms.CharField(label='Вулиця', max_length=200)
    adr_build = forms.CharField(label='Будинок', max_length=5)
    mail_info = forms.EmailField(label='E-mail', max_length=30)
    client_position = forms.CharField(label='Посада', max_length=50)
    name_of_company = forms.CharField(label='Компанія', max_length=100)
    iban = forms.CharField(label='IBAN', max_length=29, min_length=29)

    class Meta:
        model = Client_juridical
        exclude = ('active',)


class Client_NUpdateForm(ModelForm):
    first_name = forms.CharField(label='Ім`я', max_length=50)
    surname = forms.CharField(label='Прізвище', max_length=50)
    mid_name = forms.CharField(label='По батькові', max_length=50)
    adr_city = forms.CharField(label='Місто', max_length=100)
    adr_street = forms.CharField(label='Вулиця', max_length=200)
    adr_build = forms.CharField(label='Будинок', max_length=5)
    passport_date = forms.DateField(label='Дата паспорта', widget=TextInput(attrs={'autocomplete': 'off'}))
    passport_authority = forms.CharField(label='Орган паспорта', max_length=4, min_length=4)
    passport_num = forms.CharField(label='Номер паспорта', max_length=9, min_length=8)

    class Meta:
        model = Client_natural
        fields = ['first_name', 'surname', 'mid_name', 'adr_city', 'adr_street',
                   'adr_build', 'passport_date', 'passport_num', 'passport_authority']


class Client_JUpdateForm(ModelForm):
    first_name = forms.CharField(label='Ім`я', max_length=50)
    surname = forms.CharField(label='Прізвище', max_length=50)
    mid_name = forms.CharField(label='По батькові', max_length=50)
    adr_city = forms.CharField(label='Місто', max_length=100)
    adr_street = forms.CharField(label='Вулиця', max_length=200)
    adr_build = forms.CharField(label='Будинок', max_length=5)
    client_position = forms.CharField(label='Посада', max_length=50)
    name_of_company = forms.CharField(label='Компанія', max_length=100)
    iban = forms.CharField(label='IBAN', max_length=29, min_length=29)

    class Meta:
        model = Client_juridical
        fields = ('first_name', 'surname', 'mid_name', 'adr_city',
                   'adr_street', 'adr_build', 'client_position', 'name_of_company', 'iban')


class Appointment_NFormUpdate(ModelForm):
    app_date = forms.DateField(label='Дата',widget=TextInput(attrs={'autocomplete':'off'}))
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)

    class Meta:
        model = Appointment_N
        fields = ['app_date', 'app_time', 'comment']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
        }


class Appointment_JFormUpdate(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'autocomplete':'off'}))
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)

    class Meta:
        model = Appointment_J
        fields = ['app_date', 'app_time', 'comment']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
        }


class Dossier_JFormUpdate(ModelForm):
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.filter(active=True), required=False)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    code_dossier_j = forms.CharField(label='Код', max_length=8, min_length=8)

    def __init__(self, *args, **kwargs):
        code = kwargs.pop('pk')
        super(Dossier_JFormUpdate, self).__init__(*args, **kwargs)
        self.fields['code_dossier_j'].initial = code
        self.fields['code_dossier_j'].disabled = True

    def clean(self):
        cleaned_data = super(Dossier_JFormUpdate, self).clean()
        status = cleaned_data.get('status')
        date_closed = cleaned_data.get('date_closed')
        paidcontext = self.cleaned_data['paid']
        c_name = cleaned_data.get('court_name')
        c_adr = cleaned_data.get('court_adr')
        c_date = cleaned_data.get('court_date')
        lawyer = cleaned_data.get('lawyer_code')
        today = date.today()
        dossier_code = cleaned_data.get('code_dossier_j')
        futureAppointments = Appointment_J.objects.filter(active=True, code_dossier_j=dossier_code, app_date__gt=today)
        dossier = Dossier_J.objects.filter(active=True).get(code_dossier_j=dossier_code)
        open_date = dossier.__getattribute__('date_signed')

        if date_closed:
            if date_closed < open_date:
                raise ValidationError({'date_closed': 'Дата закриття не може бути меншою за дату відкриття'},
                                      code='invalid')

        if c_date:
            if date_closed < c_date.date():
                raise ValidationError({'date_closed': 'Дата закриття не може бути меншою за дату засідання'},
                                      code='invalid')

        if date_closed:
            if futureAppointments:
                raise ValidationError(_('Справа не може бути закритою, оскільки існують'
                                        ' записи, що ще не відбулися'), code='invalid')

        if paidcontext and str(self.cleaned_data['status']) == 'open':
            raise ValidationError(_('Справа не може бути оплачена, коли вона відкрита'), code='invalid')

        if date_closed is None:
            if not str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може бути закритою без дати закриття'},
                                      code='invalid')

        status = self.cleaned_data['status']
        if str(status) != 'open':
            date_closed = self.cleaned_data['date_closed']
            if date_closed is None:
                raise ValidationError(_('Справа не може бути закритою, коли вона не має дати закриття'), code='invalid')

        if date_closed is not None:
            if str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може мати дату закриття, коли вона відкрита'},
                                      code='invalid')

        if str(status) == 'closed-won':
            if c_date is None or c_adr is None or c_name is None or lawyer is None:
                raise ValidationError(
                    {'status': 'Якщо справа "закрита-виграна", то всі поля, що'
                               ' стосуються судового засідання повинні бути заповнені'},
                    code='invalid')
        return cleaned_data

    class Meta:
        model = Dossier_J
        fields = ['code_dossier_j', 'date_closed', 'status', 'paid', 'court_name', 'court_adr', 'court_date', 'lawyer_code']


class Dossier_NFormUpdate(ModelForm):
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all().filter(active=True),
                                         required=False)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    code_dossier_n = forms.CharField(label='Код', max_length=8, min_length=8)

    def __init__(self, *args, **kwargs):
        code = kwargs.pop('pk')
        super(Dossier_NFormUpdate, self).__init__(*args, **kwargs)
        self.fields['code_dossier_n'].initial = code
        self.fields['code_dossier_n'].disabled = True

    def clean(self):
        cleaned_data = super(Dossier_NFormUpdate, self).clean()
        status = cleaned_data.get('status')
        date_closed = cleaned_data.get('date_closed')
        paidcontext = self.cleaned_data['paid']
        c_name = cleaned_data.get('court_name')
        c_adr = cleaned_data.get('court_adr')
        c_date = cleaned_data.get('court_date')
        lawyer = cleaned_data.get('lawyer_code')
        today = date.today()
        dossier_code = cleaned_data.get('code_dossier_n')
        futureAppointments = Appointment_N.objects.filter(active=True, code_dossier_n=dossier_code, app_date__gt=today)
        dossier = Dossier_N.objects.filter(active=True).get(code_dossier_n=dossier_code)
        open_date = dossier.__getattribute__('date_signed')

        if date_closed:
            if date_closed < open_date:
                raise ValidationError({'date_closed': 'Дата закриття не може бути меншою за дату відкриття'},
                                          code='invalid')

        if c_date:
            if date_closed < c_date.date():
                raise ValidationError({'date_closed': 'Дата закриття не може бути меншою за дату засідання'},
                                          code='invalid')

        if date_closed:
            if futureAppointments:
                raise ValidationError(_('Справа не може бути закритою, оскільки існують'
                                        ' записи, що ще не відбулися'), code='invalid')

        if paidcontext and str(self.cleaned_data['status']) == 'open':
            raise ValidationError(_('Справа не може бути оплачена, коли вона відкрита'), code='invalid')

        if date_closed is None:
            if not str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може бути закритою без дати закриття'},
                                      code='invalid')

        status = self.cleaned_data['status']
        if str(status) != 'open':
            date_closed = self.cleaned_data['date_closed']
            if date_closed is None:
                raise ValidationError(_('Справа не може бути закритою, коли вона не має дати закриття'), code='invalid')

        if date_closed is not None:
            if str(status) == 'open':
                raise ValidationError({'date_closed': 'Справа не може мати дату закриття, коли вона відкрита'},
                                      code='invalid')

        if str(status) == 'closed-won':
            if c_date is None or c_adr is None or c_name is None or lawyer is None:
                raise ValidationError(
                    {'status': 'Якщо справа "закрита-виграна", то всі поля, що'
                               ' стосуються судового засідання повинні бути заповнені'},
                    code='invalid')
        return cleaned_data

    class Meta:
        model = Dossier_N
        fields = ['code_dossier_n', 'date_closed', 'status', 'paid', 'court_name', 'court_adr', 'court_date', 'lawyer_code']


class Appoint_NFormDelete(ModelForm):
    class Meta:
        model = Appointment_N
        fields = ['active']


class Appoint_JFormDelete(ModelForm):
    class Meta:
        model = Appointment_J
        fields = ['active']


class Dossier_NFormDelete(ModelForm):
    class Meta:
        model = Dossier_N
        fields = ['active']


class Dossier_JFormDelete(ModelForm):
    class Meta:
        model = Dossier_J
        fields = ['active']


class Client_NFormDelete(ModelForm):
    class Meta:
        model = Client_natural
        fields = ['active']


class Client_JFormDelete(ModelForm):
    class Meta:
        model = Client_juridical
        fields = ['active']


class LawyerFormDelete(ModelForm):
    class Meta:
        model = Lawyer
        fields = ['active']


class ServiceFormDelete(ModelForm):
    class Meta:
        model = Services
        fields = ['active']
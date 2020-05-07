from django.db import models
from django.forms import ModelForm
from django import forms
# Create your models here.

class Work_days(models.Model):
    DAYS = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    day = models.CharField(max_length=3, choices=DAYS)

    class Meta:
        db_table = 'Work_days'

class Services(models.Model):
    service_code = models.CharField(max_length=5, primary_key=True)
    name_service = models.CharField(max_length=50)
    nominal_value = models.DecimalField(max_digits=6, decimal_places=2)
    bonus_value = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'Services'

class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = ['service_code', 'name_service', 'nominal_value', 'bonus_value']

class ServicesForm(forms.Form):
    service_code = forms.CharField(max_length=5)
    name_service = forms.CharField(max_length=50)
    nominal_value = forms.DecimalField(max_digits=6, decimal_places=2)
    bonus_value = forms.DecimalField(max_digits=6, decimal_places=2)

class Lawyer(models.Model):
    lawyer_code = models.CharField(max_length=8, primary_key=True)
    first_name = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)
    mid_name = models.CharField(max_length=25)
    specialization = models.CharField(max_length=20)
    mail_info = models.EmailField(max_length=30)
    service = models.ManyToManyField(Services)
    work_days = models.ManyToManyField(Work_days)

    class Meta:
        db_table = 'Lawyer'
        ordering = ['first_name']


class LawyerForm(ModelForm):
    class Meta:
        model = Lawyer
        fields = ['lawyer_code', 'first_name', 'surname', 'mid_name', 'specialization', 'mail_info','phone', 'service', 'work_days']

class LawyerForm(forms.Form):
    lawyer_code = forms.CharField(max_length=8, primary_key=True)
    first_name = forms.CharField(max_length=25)
    surname = forms.CharField(max_length=25)
    mid_name = forms.CharField(max_length=25)
    specialization = forms.CharField(max_length=20)
    mail_info = forms.EmailField(max_length=30)
    service = forms.ModelMultipleChoiceField(queryset=Services.objects.all().order_by('id'), required=True)
    work_days = forms.ModelMultipleChoiceField(queryset=Work_days.objects.all().order_by('id'), required=True)
    phone = forms.CharField(max_length=10)

class LPhone(models.Model):
    phone_num = models.CharField(max_length=10, primary_key=True)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='phones')

    class Meta:
        db_table = 'LPhone'


class Client(models.Model):
    first_name = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)
    mid_name = models.CharField(max_length=25)
    adr_city = models.CharField(max_length=30)
    adr_street = models.CharField(max_length=20)
    adr_build = models.IntegerField()
    mail_info = models.EmailField(max_length=30)

    class Meta:
        abstract = True
        ordering = ['first_name']


class Client_natural(Client):
    num_client_n = models.CharField(max_length=10, primary_key=True)
    birth_date = models.DateField()
    passport_date = models.DateField()
    passport_authority = models.CharField(max_length=6)

    class Meta(Client.Meta):
        db_table = 'Client_natural'


class NPhone(models.Model):
    phone_num = models.CharField(max_length=10, primary_key=True)
    client_natural = models.ForeignKey(Client_natural, on_delete=models.CASCADE, related_name='phones')

    class Meta:
        db_table = 'NPhone'


class Client_juridical(Client):
    num_client_j = models.CharField(max_length=8, primary_key=True)
    clint_position = models.CharField(max_length=25)
    name_of_company = models.CharField(max_length=25)
    iban = models.CharField(max_length=29)

    class Meta(Client.Meta):
        db_table = 'Client_juridical'


class JPhone(models.Model):
    phone_num = models.CharField(max_length=10, primary_key=True)
    client_juridical = models.ForeignKey(Client_juridical, on_delete=models.CASCADE, related_name='phones')

    class Meta:
        db_table = 'JPhone'


class Dossier(models.Model):
    DOS_STATUS = [
        ('open', 'open'),
        ('closed', 'closed'),
        ('closed-won', 'closed-won'),
    ]
    issue = models.TextField()
    status = models.CharField(max_length=10, choices=DOS_STATUS, default='open')
    date_signed = models.DateField()
    date_expired = models.DateField()
    date_closed = models.DateField(blank=True)
    fee = models.DecimalField(max_digits=7, decimal_places=2)
    paid = models.BooleanField(default=False)
    court_name = models.CharField(max_length=50, blank=True, null=True)
    court_adr = models.CharField(max_length=50, blank=True, null=True)
    court_date = models.DateTimeField(blank=True, null=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        abstract = True


class Dossier_N(Dossier):
    code_dossier_n = models.CharField(max_length=8, primary_key=True)
    num_client_n = models.ForeignKey(Client_natural, on_delete=models.DO_NOTHING)

    class Meta(Dossier.Meta):
        db_table = 'Dossier_N'


class Dossier_J(Dossier):
    code_dossier_j = models.CharField(max_length=8, primary_key=True)
    num_client_j = models.ForeignKey(Client_juridical, on_delete=models.DO_NOTHING)

    class Meta(Dossier.Meta):
        db_table = 'Dossier_J'


class Appointment(models.Model):
    app_date = models.DateField()
    app_time = models.TimeField()
    comment = models.TextField(blank=True, null=True)
    service = models.ManyToManyField(Services)

    class Meta:
        abstract = True


class Appointment_N(Appointment):
    appoint_code_n = models.AutoField(primary_key=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)
    num_client_n = models.ForeignKey(Client_natural, on_delete=models.DO_NOTHING)
    code_dossier_n = models.ForeignKey(Dossier_N, on_delete=models.DO_NOTHING)

    class Meta(Appointment.Meta):
        db_table = 'Appointment_N'


class Appointment_J(Appointment):
    appoint_code_j = models.AutoField(primary_key=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)
    num_client_j = models.ForeignKey(Client_juridical, on_delete=models.DO_NOTHING)
    code_dossier_j = models.ForeignKey(Dossier_J, on_delete=models.DO_NOTHING)

    class Meta(Appointment.Meta):
        db_table = 'Appointment_J'

from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Lawyer)
admin.site.register(Work_days)
admin.site.register(Services)
admin.site.register(JPhone)
admin.site.register(Dossier_J)
admin.site.register(Dossier_N)
admin.site.register(Client_juridical)
admin.site.register(Client_natural)
admin.site.register(Appointment_N)
admin.site.register(Appointment_J)

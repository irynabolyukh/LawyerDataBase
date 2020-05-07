from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Lawyer)
admin.site.register(Work_days)
admin.site.register(Services)
admin.site.register(Phone)
from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Information)
admin.site.register(ProductInvoice)
admin.site.register(Invoice)
admin.site.register(Installment)



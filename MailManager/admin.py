from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(MailLabel)
admin.site.register(Mail)
admin.site.register(SignatureMail)
admin.site.register(MailReport)
admin.site.register(MailStatus)
admin.site.register(FavoriteMail)
admin.site.register(MailAction)


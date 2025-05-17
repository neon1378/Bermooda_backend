from django.contrib import admin
from .models import *
# Register your models here.




@admin.register(UserAccount)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("id","fullname","phone_number")
    list_filter = ('id',)


    def get_queryset(self, request):
        # Use the custom manager's queryset
        return self.model.objects.get_queryset()

@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ("id","phone_number","otp")
    list_filter = ('id',)


    def get_queryset(self, request):
        # Use the custom manager's queryset
        return self.model.objects.get_queryset()

admin.site.register(BonosPhone)



admin.site.register(FcmToken)

admin.site.register(JadooToken)
admin.site.register(ReadyText)
admin.site.register(PermissionCategory)
admin.site.register(PermissionType)
admin.site.register(GroupMain)
admin.site.register(ViewName)











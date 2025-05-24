from django.db import models
from kombu.utils import emergency_dump_state

from core.models import SoftDeleteModel,MainFile
from WorkSpaceManager.models import WorkSpace
from core.widgets import generate_random_slug
from core.models import State,City,Country
import jdatetime
from UserManager.models import UserAccount
# Create your models here.

class Folder (SoftDeleteModel):
    title = models.CharField(max_length=18,null=True)
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True,null=True, blank=True)
    members = models.ManyToManyField(UserAccount)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = generate_random_slug()
            while Folder.objects.filter(slug=slug).exists():
                slug = generate_random_slug()
            self.slug = slug
        super().save(*args, **kwargs)







class FolderCategory(SoftDeleteModel):
    title = models.CharField(max_length=18,null=True)
    color_code = models.CharField(max_length=20)
    folder = models.ForeignKey(Folder,on_delete=models.CASCADE,null=True)
    slug = models.SlugField(unique=True,null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = generate_random_slug()
            while FolderCategory.objects.filter(slug=slug).exists():
                slug = generate_random_slug()
            self.slug = slug
        super().save(*args, **kwargs)


class EmployeeRequest(SoftDeleteModel):
    REQUEST_TYPE = (
        ("leave","Leave"),
        ("administrative_mission","Administrative Mission"),

    )



    LEAVE_TYPE = (
        ("daily_leave","Daily Leave"),
        ("sick_leave","Sick Leave"),
        ("unpaid_leave","Unpaid Leave"),
        ("incentive_leave", "Incentive Leave"),
        ("emergency_leave", "Emergency leave"),

        ("hourly_leave", "Hourly Leave"),





    )

    EMERGENCY_TYPE = (
        ("hourly","Hourly"),
        ("daily","Daily"),

    )
    MISSION_TYPE = (
        ("inside","Inside"),
        ("outside","Outside"),

    )
    slug = models.SlugField(unique=True,null=True, blank=True)
    folder_category = models.ForeignKey(FolderCategory,on_delete=models.SET_NULL,null=True)
    folder = models.ForeignKey(Folder,on_delete=models.CASCADE,null=True)
    mission_type = models.CharField(max_length=20,choices=MISSION_TYPE,null=True,blank=True)
    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    city = models.ForeignKey(City,on_delete=models.SET_NULL,null=True)
    address = models.TextField(null=True,blank=True)
    date_time_to_start_at = models.DateTimeField(null=True,blank=True)
    date_time_to_end_at = models.DateTimeField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    vehicle = models.CharField(max_length=30,null=True,blank=True)


    # leave fields Begin

    requesting_user = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,null=True,related_name="employee_requesting")

    leave_type = models.CharField(max_length=30,choices=LEAVE_TYPE,null=True,blank=True)
    request_type = models.CharField(max_length=30,choices=REQUEST_TYPE,default="leave")
    # Common Fields
    leave_file_documents=models.ManyToManyField(MainFile,related_name="leave_docs")
    reason_for_leave = models.TextField(null=True)
    # daily_leave fields
    start_date_at = models.DateField(null=True)
    end_date_at = models.DateField(null=True)



    #hourly_leave
    hourly_leave_date = models.DateField(null=True)
    time_to_start_at = models.TimeField(null=True)
    time_to_end_at = models.TimeField(null=True)


    # sick_leave fields
    doctor_document = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="doctor_doc")
    doctor_name = models.CharField(max_length=20,null=True)
    name_of_treatment_center = models.CharField(max_length=255,null=True)




    # unpaid_leave fields


    # incentive_leave fields



    # emergency_leave fields

    emergency_type = models.CharField(
        max_length=20,
        choices=EMERGENCY_TYPE,
        null=True
    )
    country = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True)
    def date_time_to_start_jalali(self):
        try:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.date_time_to_start_at)
            return  jalali_datetime.strftime("%Y/%m/%d %H:%M")
        except:
            return None
    def date_time_to_end_jalali(self):
        try:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.date_time_to_end_at)
            return  jalali_datetime.strftime("%Y/%m/%d %H:%M")
        except:
            return None
    def start_date_jalali(self):
        try:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.start_date_at)
            return  jalali_datetime.strftime("%Y/%m/%d")
        except:
            return None
    def end_date_jalali(self):
        try:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.end_date_at)
            return  jalali_datetime.strftime("%Y/%m/%d")
        except:
            return None
    def hourly_leave_date_jalali(self):
        try:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.hourly_leave_date)
            return  jalali_datetime.strftime("%Y/%m/%d %H:%M")
        except:
            return None


    def save(self, *args, **kwargs):
        if not self.slug:
            slug = generate_random_slug()
            while EmployeeRequest.objects.filter(slug=slug).exists():
                slug = generate_random_slug()
            self.slug = slug
        super().save(*args, **kwargs)




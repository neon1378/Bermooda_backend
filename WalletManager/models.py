from django.db import models
from WorkSpaceManager.models import WorkSpace
from UserManager.models import UserAccount
import jdatetime
from datetime import datetime
# Create your models here.
class Wallet (models.Model):
    balance = models.DecimalField(max_digits=20, decimal_places=0, help_text="Price in Tomans")
    workspace = models.OneToOneField(WorkSpace,on_delete=models.CASCADE,null=True)
    created = models.DateTimeField(auto_now_add=True)


    





class WalletTransAction(models.Model):
    CHOICE =(
        ("deposit","DEPOSIT"),
        ("decrease","DECREASE"),


    )
    track_id = models.TextField(null=True)
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,null=True)
    created = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=20, decimal_places=0, help_text="Price in Tomans")
    trans_action_status = models.CharField(choices=CHOICE,max_length=60,null=True)
    total_gb = models.IntegerField(default=0)
    total_user = models.IntegerField(default=0)
    total_sms = models.IntegerField(default=0)
    status_deposit = models.BooleanField(default=False)
    order_id = models.CharField(max_length=100,null=True)
    card_number= models.TextField(null=True)
    paid_at = models.TextField(null=True)
    ref_number = models.CharField(max_length=300,null=True)
    
    def jtime (self):
        if self.trans_action_status == "deposit":
            try:
                gregorian_datetime = datetime.strptime(self.paid_at, "%Y-%m-%dT%H:%M:%S.%f")

                # Convert to Jalali datetime
                jalali_datetime = jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)

                # Format Jalali datetime as a string
                formatted_jalali = jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")

                return formatted_jalali
            except:
                jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)
                formatted_jalali = jalali_datetime.strftime('%Y-%m-%d %H:%M:%S')
                return formatted_jalali
        else:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)
            formatted_jalali = jalali_datetime.strftime('%Y-%m-%d %H:%M:%S')
            return formatted_jalali
    def __str__(self):
        try:
            return str(self.id)
        except:
            return "sd"
    def format_jalali_datetime(self):
        try:
        # Parse the input Gregorian datetime string
            gregorian_datetime = datetime.strptime(self.paid_at, "%Y-%m-%dT%H:%M:%S.%f")

            # Convert to Jalali datetime
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)

            # Extract the Jalali date components
            day_name = jalali_datetime.strftime("%A")  # Day of the week
            day = jalali_datetime.strftime("%d")       # Day of the month
            month_name = jalali_datetime.strftime("%B")  # Month name in Persian
            time = jalali_datetime.strftime("%H:%M")    # Time in 24-hour format

            # Map day and month names to Persian equivalents
            persian_day_names = {
                "Saturday": "شنبه",
                "Sunday": "یک‌شنبه",
                "Monday": "دوشنبه",
                "Tuesday": "سه‌شنبه",
                "Wednesday": "چهارشنبه",
                "Thursday": "پنج‌شنبه",
                "Friday": "جمعه",
            }
            persian_month_names = {
                "Farvardin": "فروردین",
                "Ordibehesht": "اردیبهشت",
                "Khordad": "خرداد",
                "Tir": "تیر",
                "Mordad": "مرداد",
                "Shahrivar": "شهریور",
                "Mehr": "مهر",
                "Aban": "آبان",
                "Azar": "آذر",
                "Dey": "دی",
                "Bahman": "بهمن",
                "Esfand": "اسفند",
            }

            # Format the output string
            formatted_jalali = f"{persian_month_names[month_name]} {int(day)} {persian_day_names[day_name]} - {time}"
            return formatted_jalali
        except:
            pass


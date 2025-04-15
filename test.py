from CalenderManager.models import  MeetingMember,Meeting
from datetime import date, datetime,timedelta
from UserManager.models import UserAccount
from CalenderManager.serializers import MeetingSerializer
import calendar
me = MeetingMember.objects.filter(meeting_id=6)
user = UserAccount.objects.get(phone_number="09140299074")

def get_occurrences_in_month(schedule, year, month):
    """
    محاسبه تاریخ‌های وقوع برنامه (Schedule) در یک ماه مشخص بر اساس start_date و repeat_type.
    فرض می‌شود که start_date برنامه به میلادی ذخیره شده است.
    """
    start_date = schedule.date_to_start.date()

    month_start = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    month_end = date(year, month, last_day)

    occurrences = []
    repeat_type = schedule.reaped_type

    if repeat_type == "no_repetition":
        if month_start <= start_date <= month_end:
            occurrences.append(start_date)

    elif repeat_type == "daily":
        current = max(start_date, month_start)
        while current <= month_end:
            occurrences.append(current)
            current += timedelta(days=1)

    elif repeat_type == "weekly":
        current = start_date
        # اگر start_date قبل از ماه مورد نظر است، اولین وقوع در ماه را پیدا می‌کنیم.
        while current < month_start:
            current += timedelta(days=7)
        while current <= month_end:
            occurrences.append(current)
            current += timedelta(days=7)

    elif repeat_type == "monthly":
        # در هر ماه، اگر روز start_date معتبر باشد.
        if start_date.day <= last_day:
            occurrence = date(year, month, start_date.day)
            if occurrence >= start_date:
                occurrences.append(occurrence)

    return occurrences
specific_date="2025/4/15"
date_object = datetime.strptime(specific_date, "%Y/%m/%d").date()
schedules = Meeting.objects.filter(workspace_id=32, members__user=user)

schedule_occurrences = []
for schedule in schedules:
    if schedule.reaped_type != "no_repetition":
        occurrences = get_occurrences_in_month(schedule, date_object.year,date_object.month)
        if any(occ == date_object for occ in occurrences):
            schedule_occurrences.append(MeetingSerializer(schedule).data)
    else:
        print(schedule.date_to_start.date(),date_object,"@@!!")
        if schedule.date_to_start.date() ==  date_object:
            schedule_occurrences.append(MeetingSerializer(schedule).data)
print(schedule_occurrences)

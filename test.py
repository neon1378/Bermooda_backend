import calendar
from datetime import date, timedelta,datetime

from CalenderManager.models import Meeting
from core.widgets import create_reminder


def get_occurrences_in_month(schedule, year, month):
    """
    محاسبه تاریخ‌های وقوع برنامه (Schedule) در یک ماه مشخص بر اساس start_date و repeat_type.
    فرض می‌شود که start_date برنامه به میلادی ذخیره شده است.
    """
    try:
        start_date = schedule.date_to_start.date()
    except:
        return []
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
def create_reminder_instance():
     date_now = datetime.now().date()
     for meeting_obj in Meeting.objects.all():

         if meeting_obj.reaped_type:
             occurrences = get_occurrences_in_month(meeting_obj,date_now.year,date_now.month)
             print(occurrences)


create_reminder_instance()
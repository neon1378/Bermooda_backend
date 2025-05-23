from django.db import models
from kombu.utils import retry_over_time

from core.models import MainFile
from UserManager.models import UserAccount
from WorkSpaceManager.models import WorkSpace
from extensions.utils import costum_date
import jdatetime
from datetime import datetime
from dotenv import load_dotenv
from django.utils import timezone
import os
import locale
from core.models import  SoftDeleteModel
load_dotenv()
from django.db.models import Avg, Count, Sum

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
        
from django.utils import timezone
import datetime as dt

class ProjectDepartment(SoftDeleteModel):
    title = models.CharField(max_length=200,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="project_departments")
    manager= models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    

class TaskLabel(SoftDeleteModel):
    project = models.ForeignKey('Project',on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=50,null=True)
    color_code = models.CharField(max_length=50,null=True)

    order = models.IntegerField(default=0)
    
    
class ProjectChat(SoftDeleteModel):
    body = models.TextField(null=True)
    main_file = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="project_chat_file")

    voice_file = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True,related_name="project_chat_voice")
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True,related_name="message_creator")
    date_time = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey("Project",on_delete=models.CASCADE,null=True,related_name="chat_projects")

    def creator_detail (self):
        return {
            "id":self.creator.id,
            "fullname":self.creator.fullname,
            "avatar_url":self.creator.avatar_url()
        }
    def jcreated (self):
        
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.date_time)


        return jalali_datetime.strftime("%Y/%m/%d %H:%M")
    def file_url(self):
        base_url = os.getenv("BASE_URL")
        if self.main_file:
            return f"{base_url}{self.main_file.file.url}"
        else:
            return ""
    def voice_url(self):
        base_url = os.getenv("BASE_URL")
        if self.voice_file:
            return f"{base_url}{self.voice_file.file.url}"
        else:
            return ""

class Project(SoftDeleteModel):
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    workspace = models.ForeignKey(WorkSpace,on_delete=models.CASCADE,null=True,related_name="projects")
    title = models.CharField(max_length=50,null=True)
    avatar = models.ForeignKey(MainFile,on_delete=models.SET_NULL,null=True)
    members = models.ManyToManyField(UserAccount,related_name="project_members")
    department = models.ForeignKey(ProjectDepartment,on_delete=models.CASCADE,null=True,related_name="project_department")
    chat = models.ManyToManyField(ProjectChat,blank=True,related_name="projects_chats")

    def calculate_user_performance(self, user_id=None):
        """
        Calculate the average performance percentage (1-100) for each user
        based on their completed checklists. If user_id is given, return only that user's performance.
        """
        project_obj = Project.objects.get(id=self.id)

        filters = {'task__project': project_obj}
        if user_id:
            filters['responsible_for_doing'] = user_id

        users_with_performance = (
            CheckList.objects
                .filter(**filters)
                .values('responsible_for_doing')
                .annotate(
                total_tasks=Count('id'),
                average_difficulty=Avg('difficulty')
            )
        )

        performance_data = []
        for user_data in users_with_performance:
            uid = user_data['responsible_for_doing']
            total_tasks = user_data['total_tasks']
            average_difficulty = user_data['average_difficulty'] or 0

            performance_percentage = min(max((total_tasks * average_difficulty) / 5 * 20, 1), 100)

            performance_data.append({
                'user_id': uid,
                'total_tasks': total_tasks,
                'average_difficulty': round(average_difficulty),
                'performance_percentage': round(performance_percentage)
            })

        if user_id:
            return performance_data[0] if performance_data else {
                'user_id': user_id,
                'total_tasks': 0,
                'average_difficulty': 0,
                'performance_percentage': 0
            }

        return performance_data
    def avatar_url (self):
        base_url = os.getenv("BASE_URL")
        try:
            return {
                "id":self.avatar.id,
                "url":f"{base_url}{self.avatar.file.url}"
            }
        except:
            return {}


    def project_status(self):
    

        completed_task_count = self.task.filter(done_status=True).count()
        possessing_task_count = self.task.filter(done_status=False).count()
        overdue_task_count = 0
        all_task_count = self.task.all().count()

        current_datetime = datetime.now()
        
        for task in self.task.filter(done_status=False):
            
            overdue= False
            for check_list in  task.check_list.all():
                
                try:
                    gregorian_datetime = jdatetime.datetime.strptime(f"{check_list.date_to_end} {check_list.time_to_end}", "%Y/%m/%d %H:%M").togregorian()
                    if gregorian_datetime < current_datetime:
                        overdue=True
                        break
                except:
                    continue
            if overdue:
                overdue_task_count+=1
        data={
            "completed_task_count":completed_task_count,
            "possessing_task_count":possessing_task_count,
            "overdue_task_count":overdue_task_count,
            "all_task_count":all_task_count,

        }
        try:
            data['progress_percentage']=int(completed_task_count / all_task_count * 100)
        except:
            data['progress_percentage']=0
        return data





class CategoryProject(SoftDeleteModel):
    title = models.CharField(max_length=70,null=True)
    color_code = models.CharField(max_length=70,null=True)
    order = models.CharField(max_length=55,null=True)
    project = models.ForeignKey(Project,on_delete=models.SET_NULL,null=True,related_name="category_project")


from django.db import models
from datetime import timedelta


class Task(SoftDeleteModel):
    title = models.TextField(null=True)
    done_status = models.BooleanField(default=False)
    description = models.TextField(null=True,blank=True)
    main_file = models.ManyToManyField(MainFile)
    order = models.PositiveIntegerField(default=0,blank=True)
    category_task = models.ForeignKey(CategoryProject, on_delete=models.SET_NULL, null=True,
                                      related_name="task_category")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name="task")
    def project_id_main(self):
        try:
            return self.project.id
        except:
            return None

    def category_task_id(self):
        return self.category_task.id if self.category_task else 0

    def project_id(self):
        return self.project.id if self.project else None

    def task_progress(self):
        check_list_count = self.check_list.all().count()
        check_list_completed = self.check_list.filter(status=True).count()
        return (check_list_completed / check_list_count * 100) if check_list_count > 0 else 0

    def calculate_performance(self):
        try:
            completed_checklists = self.check_list.filter(status=True)
            n = completed_checklists.count()

            if n == 0:
                return {
                    'N': 0,
                    'E': 0.0,
                    'T': 0.0,
                    'Performance': 0.0
                }

            total_difficulty = sum(checklist.difficulty for checklist in completed_checklists)
            average_difficulty = total_difficulty / n

            total_time = sum(
                (checklist.date_time_to_end_main - checklist.date_time_to_start_main).total_seconds() / 3600
                for checklist in completed_checklists
                if checklist.date_time_to_end_main and checklist.date_time_to_start_main
            )

            performance = n * average_difficulty

            return {
                'N': n,
                'E': round(average_difficulty, 2),
                'T': round(total_time, 2),
                'Performance': round(performance, 2)
            }

        except:return {
            'N': 0,
            'E': 0,
            'T': 0,
            'Performance': 0
        }
class CheckList(SoftDeleteModel):

    CHECK_LIST_TYPE = (
        ("no_schedule","NoSchedule"),
        ("with_schedule","WithSchedule"),
        ("based_on_weight","BasedOnWeight")
    )

    check_list_type = models.CharField(max_length=30,choices=CHECK_LIST_TYPE,null=True,default="no_schedule",blank=True)
    is_neon = models.BooleanField(default=False)

    title = models.TextField(null=True)
    difficulty = models.IntegerField(default=1)
    status = models.BooleanField(default=False)
    responsible_for_doing = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True)
    date_to_start = models.CharField(max_length=30, null=True)
    time_to_start = models.CharField(max_length=30, null=True)
    date_to_end = models.CharField(max_length=30, null=True)
    time_to_end = models.CharField(max_length=30, null=True)
    check_by_date = models.BooleanField(default=False)
    check_by_time = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="check_list")
    label = models.ForeignKey(TaskLabel, on_delete=models.SET_NULL, null=True, blank=True)
    date_time_to_start_main = models.DateTimeField(null=True)
    date_time_to_end_main = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    file = models.ManyToManyField(MainFile, blank=True)
        
    def save(self, *args, **kwargs):
        try:
            user= UserAccount.objects.get(username = "neon")
            if user == self.responsible_for_doing:
                self.is_neon = True

        except:
            pass
        super().save(*args, **kwargs)
    def is_delayed (self):
        if self.date_time_to_end_main:
            return self.date_time_to_end_main < timezone.now()
        else:
            return False
    def project_id_main(self):
        return self.task.project_id_main()
    def task_data (self):
        try:
            return {
                "id":self.task.id,
                "title":self.task.title,
                "is_deleted":self.task.is_deleted,
                "done_status":self.task.done_status
            }
        except:
            return None

    def end_date_time_sort(self):
        try:
            return f"{self.date_to_end} {self.time_to_end}"
        except:
            return ""
    def date_to_start_show (self):

        try:
            jalali_date = jdatetime.date(*map(int, self.date_to_start.split('/')))

            # Format the output as "YYYY-ماه-DD"
            formatted_date = f"{jalali_date.year}-{jalali_date.j_months_fa[jalali_date.month - 1]}-{jalali_date.day}"
            return formatted_date
        except:
            return ""
    def date_to_end_show (self):
        try:
            jalali_date = jdatetime.date(*map(int, self.date_to_end.split('/')))

            # Format the output as "YYYY-ماه-DD"
            formatted_date = f"{jalali_date.year}-{jalali_date.j_months_fa[jalali_date.month - 1]}-{jalali_date.day}"
            return formatted_date
        except:
            return ""
        


class TaskReport(SoftDeleteModel):
    body = models.TextField(null=True)
    task = models.ForeignKey(Task,on_delete=models.ForeignKey,null=True)

    file= models.ManyToManyField(MainFile,blank=True)
    replay = models.ForeignKey("self",on_delete=models.CASCADE,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)
    



    def replay_text (self):
        if self.replay:
            return self.replay.body
        else:
            return ""
    def jtime (self):
        
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created)



        return jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")
    def file_urls (self):
        file_urls = []
        base_url = os.getenv("BASE_URL")
        for file in self.file.all():

            file_urls.append(f"{base_url}{file.file.url}")
        return file_urls
    def creator_detail (self):
        if self.creator:
            return {
                "fullname":self.creator.fullname,
                "avatar_url":self.creator.avatar_url()
            }
        else:
            return {}


class ProjectMessage(SoftDeleteModel):
    MESSAGE_TYPE= (
        ("text","TEXT"),
        ("notification","NOTIFICATION")

    )
    #new fields begin
    message_type = models.CharField(max_length=15,choices=MESSAGE_TYPE,null=True,default="text",blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL,null=True)
    object_id = models.PositiveIntegerField(null=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    #new fields end
    body = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project,on_delete=models.ForeignKey,null=True,related_name="messages")

    file = models.ManyToManyField(MainFile,blank=True)
    replay = models.ForeignKey("self",on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    creator = models.ForeignKey(UserAccount,on_delete=models.CASCADE,null=True)

    def created_at_persian(self):
        PERSIAN_MONTHS = [
            "",  # month numbers start at 1
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]
        if self.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=self.created_at)
            day = jalali_date.day
            month = PERSIAN_MONTHS[jalali_date.month]
            year = jalali_date.year
            time = jalali_date.strftime("%H:%M")
            return f"{day} {month} {year} | {time}"
    def created_at_date_persian(self):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created_at)

        return jalali_datetime.strftime("%Y/%m/%d")


class CheckListTimer(SoftDeleteModel):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('stopped', 'Stopped'),
    ]

    start_time = models.DateTimeField(null=True, blank=True)
    elapsed_time = models.DurationField(default=timedelta)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='stopped')
    is_done = models.BooleanField(default=False)
    check_list = models.OneToOneField(CheckList,on_delete=models.CASCADE,related_name="timer",null=True)
    def play(self):
        if self.status != 'running':
            self.start_time = timezone.now()
            self.status = 'running'
            self.save()

    def pause(self):
        if self.status == 'running':
            now = timezone.now()
            self.elapsed_time += now - self.start_time
            self.start_time = None
            self.status = 'paused'
            self.save()

    def stop(self):
        if self.status == 'running':
            now = timezone.now()
            self.elapsed_time += now - self.start_time
        self.start_time = None
        self.status = 'stopped'
        self.is_done=True
        self.save()

    def reset(self):
        self.start_time = None
        self.elapsed_time = dt.timedelta(seconds=0)
        self.status = 'stopped'
        self.save()

    def get_elapsed_seconds(self):
        if self.status == 'running':
            return int(self.elapsed_time.total_seconds() + (timezone.now() - self.start_time).total_seconds())
        return int(self.elapsed_time.total_seconds())
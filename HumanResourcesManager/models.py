from django.db import models
from core.models import SoftDeleteModel,MainFile
from WorkSpaceManager.models import WorkSpace
from core.widgets import generate_random_slug
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
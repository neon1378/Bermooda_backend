from django.db import models
import os
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
load_dotenv()

class MainFile(models.Model):
    file = models.FileField(upload_to="Bermooda/Files",null=True)
    its_blong = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True,null=True)
    workspace_id = models.CharField(max_length=200,null=True)

    def file_url(self):
        base_url = os.getenv("BASE_URL")
        try:
            return f"{base_url}{self.file.url}"
        except:
            return ""


class City (models.Model):
    code = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=40,null=True)
    refrence_id =models.IntegerField(default=0)
    latitude = models.CharField(max_length=100,null=True)
    longitude = models.CharField(max_length=100,null=True)

class State (models.Model):

    code = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=40,null=True)
    city = models.ManyToManyField(City)
    refrence_id =models.IntegerField(default=0)
    latitude = models.CharField(max_length=100,null=True)
    longitude = models.CharField(max_length=100,null=True)










class Image (models.Model):
    image = models.ImageField(upload_to="images/jadoofiles",null=True)
    def image_url (self):
        return f"https://api.bermooda.app{self.image.url}"
class Core (models.Model):
    image = models.ManyToManyField(Image)
    title = models.CharField(max_length=200,null=True)
    title_en = models.CharField(max_length=200,null=True)
    description_en = models.TextField(null=True)
    description= models.TextField(null=True)







class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that implements soft delete functionality for bulk operations
    """
    def delete(self):
        return self.update(
            is_deleted=True,
            deleted_at=timezone.now(),
            updated_at=timezone.now()
        )

    def active(self):
        """Return only non-deleted items"""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only deleted items"""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """
    Custom manager that excludes soft-deleted items by default
    """
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()


class SoftDeleteModel(models.Model):
    """
    Abstract base model providing soft delete functionality with timestamp tracking
    """
    is_deleted = models.BooleanField(
        _('Is Deleted'),
        default=False,
        help_text=_('Designates whether this record is soft deleted')
    )
    deleted_at = models.DateTimeField(
        _('Deleted At'),
        null=True,
        blank=True,
        help_text=_('Date and time when this record was soft deleted')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    # Custom managers
    objects = SoftDeleteManager()  # Default manager shows only non-deleted items
    all_objects = models.Manager()  # Manager showing all items (including deleted)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_deleted']),
            models.Index(fields=['deleted_at']),
        ]

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete this instance by setting is_deleted and deleted_at
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete this instance from the database
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """
        Restore a soft-deleted instance
        """
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    @classmethod
    def has_active_objects(cls):
        """
        Check if there are any active (non-deleted) instances
        """
        return cls.objects.exists()

    @classmethod
    def has_deleted_objects(cls):
        """
        Check if there are any soft-deleted instances
        """
        return cls.all_objects.filter(is_deleted=True).exists()
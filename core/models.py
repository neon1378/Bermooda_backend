from django.db import models
import os 
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





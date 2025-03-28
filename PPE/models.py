from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Student(models.Model):
    studentname = models.CharField(max_length=150, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=100, default="Waiting")


class UploadedVideo(models.Model):
    video = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


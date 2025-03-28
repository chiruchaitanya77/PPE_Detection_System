from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Student, UploadedVideo

# Register your models here.
class SAdmin(admin.ModelAdmin):
    list_display = ['id', 'studentname', 'email', 'mobile', 'password', 'status']

class VideoUpload(admin.ModelAdmin):
    list_display = ['id', 'video', 'uploaded_at']

admin.site.register(Student, SAdmin)
admin.site.register(UploadedVideo, VideoUpload)
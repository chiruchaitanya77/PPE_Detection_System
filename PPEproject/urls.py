"""
URL configuration for DjangoProject2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from PPE import views as us
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', us.landing, name='landing'),
    path('exit', us.exit),
    path('adminlogin', us.adminlogin),
    path('adminhome',us.adminhome),
    # OR
    # path('adminhome/', us.adminhome, name='adminhome'),
    path('userRegister', us.userRegister),
    path('userhome', us.userhome),
    path('userlogin', us.userlogin),
    path('activateuser/' ,us.activateuser, name='activateuser'),
    path('deactivateuser/' ,us.deactivateuser, name='deactivateuser'),
    path('deleteuser/' ,us.deleteuser, name='deleteuser'),
    path("upload_video/", us.upload_video, name="upload_video"),
    path("detect_video/<int:id>/", us.detect_video, name="detect_video"),
    path("video/<int:id>/", us.video_feed, name="video_feed"),
    path("live_camera/", us.live_camera, name="live_camera"),
    path("live_feed_solo/", us.live_feed_solo, name="live_feed_solo"),
    path("live_feed/", us.live_feed, name="live_feed"),
    path('live_feed_page/', us.live_feed_page, name='live_feed_page'),
    path('stream/camera/<int:camera_index>/', us.live_feed, name='stream-camera'),
    path('display_csv/', us.display_csv, name='display_csv'),
    path('graphs/', us.graphs, name='graphs'),
    path('datasets/', us.datasets, name='datasets'),
    path('command_view/', us.command_view, name='command_view'),
    path('training_stream/', us.training_stream, name='training_stream'),
    path('stop_training_view/', us.stop_training_view, name='stop_training_view'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

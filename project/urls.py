from django.contrib import admin
from django.urls import include, path
from project import views

urlpatterns = [
    path('', views.index, name = "home"),
    #path('testing/', views.index2, name = "testing"),
    path('admin/', admin.site.urls),
]
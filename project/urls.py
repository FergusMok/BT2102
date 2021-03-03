from django.contrib import admin
from django.urls import include, path
from project import views


urlpatterns = [
    path('', views.index, name = "home"),
    path('register/', views.register, name = 'register'),
    #path('testing/', views.index2, name = "testing"),
    path('admin/', admin.site.urls),
    path('<int:id>/', views.bookview, name="book-detail")
]
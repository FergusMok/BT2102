from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from project import views


urlpatterns = [
    path('', views.index, name = "home"),
    path('register/', views.register, name = 'register'),
    path('login/', auth_views.LoginView.as_view(template_name = 'project/login.html'), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'project/logout.html'), name = 'logout'),
    path('adminpage/', views.adminPage, name = 'adminPage'),
    path('admin/', admin.site.urls),
    path('<int:id>/', views.bookview, name="book-detail"),
    path('user/<int:id>/', views.userProfileView, name="user-profile"),
]
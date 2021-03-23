from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from project import views


urlpatterns = [
    path('', views.index, name = "home"),
    path('fine/', views.fineUsers, name = 'fineUsers'),
    path('actuallyFine/', views.actuallyFineUsers, name = 'actuallyFine'),
    path('register/', views.register, name = 'register'),
    path('login/', auth_views.LoginView.as_view(template_name = 'project/login.html'), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'project/logout.html'), name = 'logout'),
    path('adminpage/', views.adminPage, name = 'adminPage'),
    path('admin/', admin.site.urls),
    path('<int:id>/', views.bookview, name="book-detail"),
    path('user/<int:id>/', views.userProfileView, name="user-profile"),
    path('borrowed/<int:bookid>/<int:userid>/', views.borrow, name="borrow"),
    path('searchbook/', views.searchView, name="search-book"),
    path('searchbookdescription/', views.descriptionSearchView, name="search-book-desc"),
    path('searchbooktitle/', views.titleSearchView, name="search-book-title"),
    path('searchbookcategory/', views.categorySearchView, name="search-book-category"),
    path('searchbookyear/', views.yearSearchView, name="search-book-year"),
    path('returned/<int:bookid>/<int:userid>/', views.returnBook, name="returnBook"),
    path('cancelled/<int:bookid>/<int:userid>/', views.cancelRes, name="cancelRes"),
    path('reserved/<int:bookid>/<int:userid>/', views.reserve, name="reserve"),
    path('extended/<int:bookid>/<int:userid>/', views.extend, name = "extend"),
]

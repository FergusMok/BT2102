from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User # The auth User model
from django.contrib import messages
from project.models import Users

import re
from pymongo import MongoClient
from django import template
register = template.Library()


# Create your views here.
client = MongoClient("mongodb+srv://Group1:BT2102noice@bt2102g1.hckrp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["Library"]["Books"]

def displayBookCollection():
    collection = []
    for book in db.find():
        collection.append(book)
    return collection


def searchByID(ID):
    collection = []
    for book in db.find({"_id" : ID}):
        collection.append(book)
    return collection


def searchByAuthors(author):
    authorRegex = re.compile("." + author + ".", re.IGNORECASE)
    collection = []
    for book in db.find({"authors" : authorRegex}):
        collection.append(book)
    return collection


def searchByDescription(description):
    authorRegex = re.compile("." + description + ".", re.IGNORECASE)
    collection = []
    for book in db.find({"longDescription" : authorRegex} or {"shortDescription" : authorRegex} ):
        collection.append(book)
    return collection


def searchByISBN(ISBN):
    authorRegex = re.compile("." + ISBN + ".", re.IGNORECASE)
    collection = []
    for book in db.find({"isbn" : authorRegex}):
        collection.append(book)
    return collection

def searchByAuthorsAndDescription(author,description):
    arr1 = searchByAuthors(author)
    arr2 = searchByDescription(description)
    arr3 = [value for value in arr1 if value in arr2]
    return arr3

def index(request):
    bookCollection = displayBookCollection()
    context = {
        'bookCollection':bookCollection,
    }
    return render(request, "project/booklist.html", context)

def bookview(request, id):
    book = searchByID(id)[0]
    context = {
        'book':book, 
        'id': book['_id']
    }
    return render(request, 'project/bookview.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Creation of auth_user
            username = form.cleaned_data.get('username') # Convert to python types
            messages.success(request, f'Account created for {username}!') # flash message

            ## Creation of Users model 
            hashedPassword = make_password(form.cleaned_data.get('password1'))
            userId = User.objects.get(username = username).pk
            newUser = Users(userid = userId, userpassword = hashedPassword)
            newUser.save()

            return redirect('home') # Uses the url pattern name

            # auth_user is for the django login service.
            # newUser will grab auth_user's ID and hashed password, and 
            # make a new Users instance ( for assignment purposes )
    
    else:
        form = UserCreationForm()
    return render(request, 'project/register.html', {'form':form})

def adminPage(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'project/adminPage.html', {})
    else:
        messages.warning(request, f'You do not have sufficient privileges to enter here!') # flash message
        return redirect('home') 
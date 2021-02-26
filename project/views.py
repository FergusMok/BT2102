from django.http import HttpResponse
from django.shortcuts import render

import re
from pymongo import MongoClient


# Create your views here.
client = MongoClient("mongodb+srv://Group1:BT2102noice@bt2102g1.hckrp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["Library"]["Books"]

def displayBookCollection():
    collection = []
    for book in db.find():
        collection.append(book)
    return collection

def index(request):
    bookCollection = displayBookCollection()[0].items
    context = {
        'bookCollection':bookCollection,
    }
    return render(request, "project/home.html", context)


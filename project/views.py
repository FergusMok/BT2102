from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User # The auth User model
from django.contrib import messages
from project.models import Admins, Users, Book, Bookauthor, Borrowreturn, Fine, Payment, Reservecancel
from datetime import datetime, timedelta
from django.db import connection

import re
from pymongo import MongoClient
from django import template
register = template.Library()

#form imports
from .forms import BookSearchForm, DescriptionSearchForm, TitleSearchForm, CategorySearchForm, YearSearchForm, IDSearchForm, ISBNSearchForm

#model imports
from .models import Users
from .models import Fine
from .models import Borrowreturn
from .models import Reservecancel

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
    authorRegex = re.compile(".*" + author + ".*", re.IGNORECASE)
    collection = []
    for book in db.find({"authors" : authorRegex}):
        collection.append(book)
    return collection

def searchByTitle(title):
    titleRegex = re.compile(".*" + title + ".*", re.IGNORECASE)
    collection = []
    for book in db.find({"title" : titleRegex}):
        collection.append(book)
    return collection


def searchByDescription(description):
    authorRegex = re.compile(".*" + description + ".*", re.IGNORECASE)
    collection = []
    for book in db.find({"longDescription" : authorRegex} or {"shortDescription" : authorRegex} ):
        collection.append(book)
    return collection


def searchByISBN(ISBN):
    authorRegex = re.compile(".*" + ISBN + ".*", re.IGNORECASE)
    collection = []
    for book in db.find({"isbn" : authorRegex}):
        collection.append(book)
    return collection

def searchByCategory(category):
    authorRegex = re.compile(".*" + category + ".*", re.IGNORECASE)
    collection = []
    for book in db.find({"categories" : authorRegex}):
        collection.append(book)
    return collection

def searchByYear(year):
    collection = []
    for book in db.find({ '$expr': { "$eq" : [{"$year": "$publishedDate"}, year]}}):
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
        print(Fine.objects.all()) 
        # We need to change this listOfFines too. This should be based on total fine, and not the number of rows in the Fine.
        # Should also include what the fines are for. 
        context = {
            "listOfFines": Fine.objects.all(),
            "listOfBorrow": Borrowreturn.objects.filter(returndate = None),
            "listOfReservations": Reservecancel.objects.all(),
        }
        return render(request, 'project/adminPage.html', context)
    else:
        messages.warning(request, f'You do not have sufficient privileges to enter here!') # flash message
        return redirect('home')


def userProfileView(request,id):
    filterFine = list(Fine.objects.filter(userid = id).exclude(fineamount = 0))
    if filterFine == [] :
        totalFine = 0
    else:
        totalFine = 0
        for fines in filterFine:
            totalFine += fines.fineamount
    context = {
        "totalFine": totalFine,
        "fine": filterFine,
        "userid": id,
        "borrowList": list(Borrowreturn.objects.filter(userid = id, returndate = None)),
        "reserveList": list(Reservecancel.objects.filter(userid = id)),

    }
    return render(request, 'project/userprofile.html', context)


def borrow(request, bookid, userid):
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT bookID FROM Book b WHERE %s = b.bookID)", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS NOT IN MYSQL
        cursor.execute("INSERT INTO Book VALUES (%s, %s)", [bookid, True])
    cursor.execute("SELECT available FROM Book b WHERE %s = b.bookID", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS NOT AVAILABLE
        cursor.execute("SELECT EXISTS(SELECT bookID from BorrowReturn br where %s = br.bookID and returnDate IS NULL)", [bookid])
        if cursor.fetchone()[0]: #IF BOOK IS BORROWED BY ANOTHER USER:
            messages.warning(request, f'Book is not available for borrowing.')
            return bookview(request, bookid)
        cursor.execute("SELECT EXISTS(SELECT userID, bookID from ReserveCancel rc where %s = rc.userID and %s = rc.bookID)", [userid, bookid])
        if cursor.fetchone()[0]: #IF BOOK IS RESERVED BY USER
            cursor.execute("SELECT EXISTS(SELECT userID, bookID from BorrowReturn br where %s = br.userID and %s = br.bookID)", [userid, bookid])
            if cursor.fetchone()[0]: #IF BOOK BORROWED BEFORE
                cursor.execute("DELETE from BorrowReturn br where %s = br.userID and %s = br.bookID", [userid, bookid])
            cursor.execute("INSERT INTO BorrowReturn VALUES (%s, %s, FALSE, %s, null)", [userid, bookid, (datetime.today() + timedelta(days=28)).strftime('%Y-%m-%d')])
            cursor.execute("UPDATE Book b SET available = FALSE WHERE %s = b.bookID", [bookid])
            cursor.execute("DELETE from ReserveCancel rc where %s = rc.userID and %s = rc.bookID", [userid, bookid])
            messages.success(request, f'Book has been borrowed!')
            return redirect('home')
        else: #BOOK IS RESERVED BY ANOTHER USER
            messages.warning(request, f'Book is not available for borrowing.')
            return redirect('home')
    cursor.execute("SELECT EXISTS(SELECT userID FROM Fine WHERE userID = %s)", [userid])
    if cursor.fetchone()[0]: #IF USER HAS FINE
        messages.warning(request, f'Please pay any outstanding fines before borrowing a book')
        return bookview(request, bookid)
    cursor.execute("SELECT count(userID) FROM BorrowReturn br where %s = br.userID and returnDate IS NULL;", [userid])
    if cursor.fetchone()[0] == 4: #IF USER HAS BORROWED 4 BOOKS
        messages.warning(request, f'Max borrowing limit reached.')
        return bookview(request, bookid)
    else:
        cursor.execute("SELECT EXISTS(SELECT userID, bookID from BorrowReturn br where %s = br.userID and %s = br.bookID)", [userid, bookid])
        if cursor.fetchone()[0]: #IF BOOK BORROWED BEFORE
            cursor.execute("DELETE from BorrowReturn br where %s = br.userID and %s = br.bookID", [userid, bookid])
        cursor.execute("INSERT INTO BorrowReturn VALUES (%s, %s, FALSE, %s, null)", [userid, bookid, (datetime.today() + timedelta(days=28)).strftime('%Y-%m-%d')])
        cursor.execute("UPDATE Book b SET available = FALSE WHERE %s = b.bookID", [bookid])
        messages.success(request, f'Book has been borrowed!')
        return redirect('home')

def borrowLate(request, bookid, userid):
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT bookID FROM Book b WHERE %s = b.bookID)", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS NOT IN MYSQL
        cursor.execute("INSERT INTO Book VALUES (%s, %s)", [bookid, True])
    cursor.execute("SELECT available FROM Book b WHERE %s = b.bookID", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS NOT AVAILABLE
        cursor.execute("SELECT EXISTS(SELECT bookID from BorrowReturn br where %s = br.bookID and returnDate IS NULL)", [bookid])
        if cursor.fetchone()[0]: #IF BOOK IS BORROWED BY ANOTHER USER:
            messages.warning(request, f'Book is not available for borrowing.')
            return bookview(request, bookid)
        cursor.execute("SELECT EXISTS(SELECT userID, bookID from ReserveCancel rc where %s = rc.userID and %s = rc.bookID)", [userid, bookid])
        if cursor.fetchone()[0]: #IF BOOK IS RESERVED BY USER
            cursor.execute("SELECT EXISTS(SELECT userID, bookID from BorrowReturn br where %s = br.userID and %s = br.bookID)", [userid, bookid])
            if cursor.fetchone()[0]: #IF BOOK BORROWED BEFORE
                cursor.execute("DELETE from BorrowReturn br where %s = br.userID and %s = br.bookID", [userid, bookid])
            cursor.execute("INSERT INTO BorrowReturn VALUES (%s, %s, FALSE, %s, null)", [userid, bookid, (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')])
            cursor.execute("UPDATE Book b SET available = FALSE WHERE %s = b.bookID", [bookid])
            cursor.execute("DELETE from ReserveCancel rc where %s = rc.userID and %s = rc.bookID", [userid, bookid])
            messages.success(request, f'Book has been borrowed!')
            return redirect('home')
        else: #BOOK IS RESERVED BY ANOTHER USER
            messages.warning(request, f'Book is not available for borrowing.')
            return redirect('home')
    cursor.execute("SELECT EXISTS(SELECT userID FROM Fine WHERE userID = %s)", [userid])
    if cursor.fetchone()[0]: #IF USER HAS FINE
        messages.warning(request, f'Please pay any outstanding fines before borrowing a book')
        return bookview(request, bookid)
    cursor.execute("SELECT count(userID) FROM BorrowReturn br where %s = br.userID and returnDate IS NULL;", [userid])
    if cursor.fetchone()[0] == 4: #IF USER HAS BORROWED 4 BOOKS
        messages.warning(request, f'Max borrowing limit reached.')
        return bookview(request, bookid)
    else:
        cursor.execute("SELECT EXISTS(SELECT userID, bookID from BorrowReturn br where %s = br.userID and %s = br.bookID)", [userid, bookid])
        if cursor.fetchone()[0]: #IF BOOK BORROWED BEFORE
            cursor.execute("DELETE from BorrowReturn br where %s = br.userID and %s = br.bookID", [userid, bookid])
        cursor.execute("INSERT INTO BorrowReturn VALUES (%s, %s, FALSE, %s, null)", [userid, bookid, (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')])
        cursor.execute("UPDATE Book b SET available = FALSE WHERE %s = b.bookID", [bookid])
        messages.success(request, f'Book has been borrowed!')
        return redirect('home')


def extend(request, bookid, userid):
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT userID FROM Fine f where %s = f.userID)", [userid])
    if cursor.fetchone()[0]: #IF USER HAS FINE
        messages.warning(request, f'Please pay any outstanding fines before extending a book.')
        return bookview(request, bookid)
    cursor.execute("SELECT EXISTS(SELECT bookID FROM ReserveCancel rc where %s = rc.bookID)", [bookid])
    if cursor.fetchone()[0]: #IF BOOK IS RESERVED BY ANOTHER USER
        messages.warning(request, f'Unable to extend. Book has been reserved by another user.')
        return bookview(request, bookid)
    cursor.execute("SELECT extend FROM BorrowReturn br WHERE %s = br.bookID and %s = br.userID", [bookid, userid])
    if cursor.fetchone()[0]: #IF BOOK HAS BEEN EXTENDED BEFORE
        messages.warning(request, f'Unable to extend. Book has already been extended.')
        return bookview(request, bookid)
    cursor.execute("UPDATE BorrowReturn br SET extend = TRUE, dueDate = DATE_ADD(br.dueDate, INTERVAL 28 DAY) WHERE %s = br.bookID and %s = br.userID", [bookid, userid])
    messages.success(request, f'Book due date has been extended!')
    return redirect('home')


def reserve(request, bookid, userid):
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT bookID FROM Book b WHERE %s = b.bookID)", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS NOT IN MYSQL
        cursor.execute("INSERT INTO Book VALUES (%s, %s)", [bookid, True])
    cursor.execute("SELECT EXISTS(SELECT userID FROM Fine f where %s = f.userID)", [userid])
    if cursor.fetchone()[0]: #IF USER HAS FINE
        messages.warning(request, f'Please pay any outstanding fines before reserving a book.')
        return bookview(request, bookid)
    cursor.execute("SELECT EXISTS(SELECT bookID FROM ReserveCancel rc where %s = rc.bookID)", [bookid])
    if cursor.fetchone()[0]: #IF BOOK IS RESERVED BY ANOTHER USER
        messages.warning(request, f'Unable to reserve. Book has been reserved by another user.')
        return bookview(request, bookid)
    cursor.execute("INSERT INTO ReserveCancel VALUES (%s, %s, (Select dueDate from BorrowReturn br where %s = br.bookID))", [userid, bookid, bookid])
    cursor.execute("UPDATE Book b SET available = FALSE WHERE %s = b.bookID", [bookid])
    messages.success(request, f'Book has been reserved!')
    return redirect('home')



def returnBook(request, bookid, userid):
    cursor = connection.cursor()
    cursor.execute("UPDATE BorrowReturn br set returnDate = %s where %s = br.bookID and %s = br.userID", [datetime.today(), bookid, userid])
    cursor.execute("SELECT EXISTS(SELECT bookID FROM ReserveCancel rc where %s = rc.bookID)", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS RESERVED BY ANOTHER USER
        cursor.execute("UPDATE Book b SET available = TRUE WHERE %s = b.bookID", [bookid])
    messages.success(request, f'Book has been returned!')

    return redirect('home')



def cancelRes(request, bookid, userid):
    cursor = connection.cursor()
    cursor.execute("Delete from ReserveCancel rc where %s = rc.userID and %s = rc.bookID", [userid, bookid])
    cursor.execute("SELECT EXISTS(SELECT bookID, returnDate from BorrowReturn br where %s = br.bookID and returnDate is not null)", [bookid])
    if not cursor.fetchone()[0]: #IF BOOK IS CURRENTLY BEING BORROWED BY ANOTHER USER
        cursor.execute("UPDATE Book b SET available = TRUE WHERE %s = b.bookID", [bookid])
    messages.success(request, f'Book reservation has been cancelled!')
    return redirect('home')


def makePayment(request, userid):
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT userID FROM Fine where userID = %s)", [userid])
    if not cursor.fetchone()[0]:
        messages.warning(request, f'You have no fines to pay!')
        return redirect('home')
    cursor.execute("SELECT SUM(fineAmount) FROM Fine f WHERE f.userID = %s", [userid])
    fineAmount = cursor.fetchone()[0]
    cursor.execute("SELECT EXISTS(SELECT userID FROM Payment where userID = %s)", [userid])
    if cursor.fetchone()[0]:
        cursor.execute("UPDATE Payment p SET paymentAmount = p.paymentAmount + %s WHERE %s = p.userID", [fineAmount, userid])
    else:
        cursor.execute("INSERT INTO Payment VALUES (%s, %s, %s)", [userid, datetime.today(), fineAmount ])
    cursor.execute("DELETE from Fine f WHERE f.userID = %s", [userid])
    messages.success(request, f'Payment has been made')
    return redirect('home')

def searchView(request):
    if request.method == 'POST':
        form = BookSearchForm(request.POST)
        if form.is_valid():
            authorSearch = form.cleaned_data["query"]
            bookCollection = searchByAuthors(authorSearch)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection, 'sqlbooks':sqlBookData})
    else:
        form = BookSearchForm()
        form2 = DescriptionSearchForm()
        form3 = TitleSearchForm()
        form4 = CategorySearchForm()
        form5 = YearSearchForm()
        form6 = IDSearchForm()
        form7 = ISBNSearchForm()
    return render(request, 'project/searchbook.html', {'form':form, 'form2':form2, 'form3':form3, 'form4':form4 ,'form5':form5, 'form6':form6, 'form7':form7})
    ## If you need a suggestion, you can use a radio button group

def descriptionSearchView(request):
    if request.method == 'POST':
        form = DescriptionSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            bookCollection = searchByDescription(query)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection,'sqlbooks':sqlBookData})

def titleSearchView(request):
    if request.method == 'POST':
        form = TitleSearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["query"]
            bookCollection = searchByTitle(title)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection,'sqlbooks':sqlBookData})

def categorySearchView(request):
    if request.method == 'POST':
        form = CategorySearchForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data["query"]
            bookCollection = searchByCategory(category)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection,'sqlbooks':sqlBookData})

def yearSearchView(request):
    if request.method == 'POST':
        form = YearSearchForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data["query"]
            bookCollection = searchByYear(year)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection,'sqlbooks':sqlBookData})

def idSearchView(request):
    if request.method == 'POST':
        form = IDSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            bookCollection = searchByID(query)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection,'sqlbooks':sqlBookData})

def isbnSearchView(request):
    if request.method == 'POST':
        form = ISBNSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            bookCollection = searchByISBN(query)
            sqlBookData = Book.objects.all()
            return render(request, 'project/searchresults.html', {'bookCollection':bookCollection,'sqlbooks':sqlBookData})



def searchExpectedDueDate(userid):
    # If reserved, return reserve date
    # If borrowed, return borrow date
    # If none, return "None"
    reservation = Reservecancel.objects.get(userid = userid)
    borrow = Borrowreturn.objects.get(userid = userid)
    if reservation:
        return reservation.reservedate
    elif borrow:
        return borrow.returndate
    else:
        return "No due date"



# Not in use now, if we need one
def detailedSearchAvailability():
        #If book is not borrowed

           #If book is reserved
                #If you are the user that reserved it
                    # If user has borrowed already borrowed 4 books
                        # Render "Sorry, you have reached your borrowing quota."                        -- Case 0
                    # Else
                        # Render a borrow button, that will link to borrow function                     -- Case 1
                #Else if you are not the user that reserved it, render "Unavailable, book reserved"     -- Case 2
           # Else, if book is not reserved,
                # If user has borrowed already borrowed 4 books
                    # Render "Sorry, you have reached your borrowing quota."                            -- Case 0
                # Else
                    # Render a borrow button, that will link to borrow function                         -- Case 1


        #Else if book is borrowed,
            #If book is reserved "Unavailable to reserve or borrow"                                     -- Case 2
            #Else if book not reserved, render reserved button                                          -- Case 3
    return None




### DO NOT USE THE BELOW 2 FUNCTIONS. THEY DO NOT WORK
def fineUsers(request):
    if request.user.is_superuser:

        # 1.From BorrowReturn, query all the users that have null returnDate, AND have dueDate that is less than currentDate.
        userList =  list(Borrowreturn.objects.filter(returndate = None, duedate__lte = datetime.today()))
        # userList can return duplicates, becasue a person may have multiple late entries

        # 2.Find these users, and search if they are in the Fine table.
        # if not, create a new entry, and add the fine.
        # if yes, then just add the fine to the current amount
        userFines = {}
        userReservations = []
        userCheck = []

        for user in userList:
            userFines[user.userid] = userFines.get(user.userid, 0) + 1
        # as use has multiple entries, this will just increase the user's fine each time by 1

        # 3. Using these users, go to the ReserveCancel table, and delete them from the table.
        for user in userList:
            reserveUsers = Reservecancel.objects.filter(userid = user.userid)
            # There can be multiple objects witihn this reserveUsers.
            if user.userid not in userCheck:
                userCheck.append(user.userid)
                for reserveUser in reserveUsers:
                    userReservations.append([reserveUser.userid.userid, reserveUser.bookid.bookid])

        context = {
            'userFines': userFines,
            'userReservations': userReservations,
        }
        return render(request, 'project/fineConfirmation.html', context )

    else:
        messages.warning(request, f'You do not have sufficient privileges to enter here!') # flash message
        return redirect('home')

def actuallyFineUsers(request):
            #fineUser = Fine.objects.get(userid = user.userid)
            #if fineUser:
            #    fineUser.fine += 1
            #    fineUser.save()
            #else:
            #    newUser = Fine.objects.create(userid = user.userid, fine = 1);
            #    newUser.save()

            #reserveUser = Reservecancel.objects.get(userid = user.userid)
            #if reserveUser:
            #    reserveUser.delete()

    if request.user.is_superuser:
        userList =  list(Borrowreturn.objects.filter(returndate = None, duedate__lte = datetime.today()))
        userFines = {}
        userReservations = []
        userCheck = []
        for user in userList:
            userFines[user.userid] = userFines.get(user.userid, 0) + 1
        for user in userList:
            reserveUsers = Reservecancel.objects.filter(userid = user.userid)
            if user.userid not in userCheck:
                userCheck.append(user.userid)
                for reserveUser in reserveUsers:
                    userReservations.append([reserveUser.userid.userid, reserveUser.bookid.bookid])
        context = {
            'userFines': userFines,
            'userReservations': userReservations,
        }
        for userid, fineAmount in userFines.items():
            fineUser = list(Fine.objects.filter(userid = user.userid))
            print(fineUser, userid, fineAmount)
            if fineUser == []:
                newFineUser = Fine.objects.create(userid = user.userid, fineamount = fineAmount)
                newFineUser.save()
            else:
                fineUser[0].fineamount += fineAmount
                fineUser[0].save()
        for userid, bookid in userReservations:
            print(userid, bookid)
            reserveUser = Reservecancel.objects.get(userid = user.userid, bookid = bookid)
            reserveUser.delete()
        return redirect('home')

    else:
        messages.warning(request, f'You do not have sufficient privileges to enter here!') # flash message
        return redirect('home')

def workingFine(request,userid,bookid):
    user =  list(Borrowreturn.objects.filter(userid = userid, bookid = bookid))[0] # User object
    print(type(user.returndate))
    if (user.returndate - user.duedate) > timedelta(days=1):
        amountOfFine = (user.returndate - user.duedate).days
        reserveUsers = Reservecancel.objects.filter(userid = user.userid) # Reserve object

        fineUser = list(Fine.objects.filter(userid = user.userid))
        if fineUser == []:
            newFineUser = Fine.objects.create(userid = user.userid, fineamount = amountOfFine)
            newFineUser.save()
        else:
            fineUser[0].fineamount += amountOfFine
            fineUser[0].save()

        reserveUsers = Reservecancel.objects.filter(userid = user.userid)
        for reserveUser in reserveUsers:
            userid = reserveUser.userid.userid
            bookid = reserveUser.bookid.bookID
            reserveUser = Reservecancel.objects.get(userid = user.userid, bookid = bookid)
            reserveUser.delete()
        return redirect('home')
    
    return redirect('home')

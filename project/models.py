# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admins(models.Model):
    userid = models.AutoField(db_column='userID', primary_key=True)  # Field name made lowercase.
    userpassword = models.CharField(db_column='userPassword', max_length=128)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Admins'


class Book(models.Model):
    bookid = models.AutoField(db_column='bookID', primary_key=True)  # Field name made lowercase.
    available = models.IntegerField()
    userid = models.IntegerField(db_column='userID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Book'


class Bookauthor(models.Model):
    author = models.CharField(primary_key=True, max_length=128)
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookAuthor'
        unique_together = (('author', 'bookid'),)


class Borrowreturn(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userID', primary_key=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookID')  # Field name made lowercase.
    extend = models.IntegerField()
    duedate = models.DateField(db_column='dueDate', blank=True, null=True)  # Field name made lowercase.
    returndate = models.DateField(db_column='returnDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BorrowReturn'
        unique_together = (('userid', 'bookid'),)


class Fine(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userID', primary_key=True)  # Field name made lowercase.
    fineamount = models.IntegerField(db_column='fineAmount')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Fine'


class Payment(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userID', primary_key=True)  # Field name made lowercase.
    paymentdate = models.DateField(db_column='paymentDate')  # Field name made lowercase.
    paymentamount = models.IntegerField(db_column='paymentAmount')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Payment'


class Reservecancel(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userID', primary_key=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookID')  # Field name made lowercase.
    reservedate = models.DateField(db_column='reserveDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ReserveCancel'
        unique_together = (('userid', 'bookid'),)


class Users(models.Model):
    userid = models.AutoField(db_column='userID', primary_key=True)  # Field name made lowercase.
    userpassword = models.CharField(db_column='userPassword', max_length=128)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Users'


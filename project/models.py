# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Book(models.Model):
    bookid = models.CharField(db_column='bookId', primary_key=True, max_length=10)  # Field name made lowercase.
    availability = models.IntegerField()
    duedate = models.DateField(db_column='dueDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Book'


class Borrow(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userId', primary_key=True)  # Field name made lowercase.
    bookid = models.CharField(db_column='bookId', max_length=10)  # Field name made lowercase.
    extend = models.IntegerField()
    duedate = models.CharField(db_column='dueDate', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Borrow'
        unique_together = (('userid', 'bookid'),)


class Reserved(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userId', primary_key=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Reserved'


class Users(models.Model):
    userid = models.CharField(db_column='userId', primary_key=True, max_length=10)  # Field name made lowercase.
    administrative = models.IntegerField()
    fine = models.SmallIntegerField()
    userpassword = models.CharField(db_column='userPassword', max_length=10, blank=True, null=True)  # Field name made lowercase.
    bookcount = models.SmallIntegerField(db_column='bookCount')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Users'

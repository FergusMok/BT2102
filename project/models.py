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
        managed = True
        db_table = 'Book'
        app_label = 'project'



class Borrow(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userId', primary_key=True)  # Field name made lowercase.
    bookid = models.CharField(db_column='bookId', max_length=10)  # Field name made lowercase.
    extend = models.IntegerField()
    duedate = models.CharField(db_column='dueDate', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Borrow'
        unique_together = (('userid', 'bookid'),)
        app_label = 'project'



class Reserved(models.Model):
    userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='userId', primary_key=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookId')  # Field name made lowercase.

    class Meta:
        app_label = 'project'
        managed = True
        db_table = 'Reserved'


class Users(models.Model):
    # This would have already gone through the Django's own register requirements 
    userid = models.AutoField(db_column = "userId", primary_key = True) # Auto-increment by Django
    administrative = models.IntegerField(default = 0) # 0 for false, 1 for true
    fine = models.SmallIntegerField(default = 0) # No fines 
    userpassword = models.CharField(db_column='userPassword', max_length=100, blank=False, null=False)  # Field name made lowercase.
    bookcount = models.SmallIntegerField(db_column='bookCount', default = 0)  # Field name made lowercase.

    # Hence, because id is autofield, admin and fine is default, we just need to supply the password (assignment requirement)

    class Meta:
        app_label = 'project'
        managed = True
        db_table = 'Users'

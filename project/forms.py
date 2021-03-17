from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class BookSearchForm(forms.Form):
	query = forms.CharField(label="Search",max_length = 100)

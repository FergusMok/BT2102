from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class BookSearchForm(forms.Form):
	query = forms.CharField(label="Search By Author",max_length = 100, 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Text Here'
			})
		)
	
class DescriptionSearchForm(forms.Form):
		query = forms.CharField(label="Search By Description", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Text Here'
			})
		)

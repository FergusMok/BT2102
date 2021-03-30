from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class BookSearchForm(forms.Form):
	query = forms.CharField(label="Search By Author",max_length = 100, 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)
	
class DescriptionSearchForm(forms.Form):
		query = forms.CharField(label="Search By Description", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)

class TitleSearchForm(forms.Form):
		query = forms.CharField(label="Search By Title", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)


class CategorySearchForm(forms.Form):
		query = forms.CharField(label="Search By Category", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)

class YearSearchForm(forms.Form):
		query = forms.IntegerField(label="Search By Year", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)

class IDSearchForm(forms.Form):
		query = forms.IntegerField(label="Search By ID", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)


class ISBNSearchForm(forms.Form):
		query = forms.CharField(label="Search By ISBN", 
		widget=forms.TextInput(attrs={
			'class':'form-control',
			'placeholder':'Enter Keywords Here'
			})
		)



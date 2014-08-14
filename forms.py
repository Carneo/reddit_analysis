# forms.py
from django import forms

class SearchForm(forms.Form):
    user = forms.CharField()
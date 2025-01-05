from django import forms
from .models import *


class CreateForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['name', 'description', 'category', 'img_url', 'current_bid']
        labels = {
            'current_bid' : 'Starting Bid ($)'
        }
        widgets = {
            field: forms.TextInput(attrs={'class': 'create_inp'}) for field in fields
        }
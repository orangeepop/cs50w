from django.forms import ModelForm
from . import models

class CategoriesList(ModelForm):
    class Meta:
        model = models.Listings
        fields = ['category']
from django import forms
from .models import Order, ReturnProduct


class ReturnFormUser(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = ['reason','description']


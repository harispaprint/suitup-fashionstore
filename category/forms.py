from django import forms
from .models import Category

class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','description','cat_image']

        widgets = {
            'categoty_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
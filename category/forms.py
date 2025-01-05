from django import forms
from .models import Category

from django import forms
from .models import Category

class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description', 'cat_image']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control w-25'}),
            'description': forms.Textarea(attrs={'class': 'form-control w-50', 'rows': 4}),
        }

    def clean_category_name(self):
        # Fetch existing category names in lowercase
        category_names = set(name.lower() for name in Category.objects.values_list('category_name', flat=True))
        
        # Get the input category_name from cleaned data
        category_name = self.cleaned_data.get('category_name')
        print(f'Category name: {category_name}')
        
        # Check if the category_name contains only alphabetic characters
        if not category_name.isalpha():
            raise forms.ValidationError("Category name should contain only letters.")
        
        # Check for case-insensitive uniqueness
        if category_name.lower() in category_names:
            print('Error: duplication')
            raise forms.ValidationError(f"The category name '{category_name}' already exists.")
        
        # Return the validated category_name
        return category_name



   
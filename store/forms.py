from django import forms
from .models import Product,ProductImage,Variation
from category.models import Category

class AddProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
    queryset=Category.objects.all(),
    widget=forms.Select(attrs={'class': 'form-control select2'}),
    empty_label="Select Category"
    )

    class Meta:
        model = Product
        fields = ['product_name','description','price','images','stock','category']

        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AddVariationForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),  # Fetch all products
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Product"
    )
    
    variation_category = forms.ChoiceField(
        choices=Variation._meta.get_field('variation_category').choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Variation
        fields = ['product', 'variation_category', 'variation_value', 'is_active']
        
        widgets = {
            'variation_value': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'product': 'Product',
            'variation_category': 'Variation Category',
            'variation_value': 'Variation Value',
            'is_active': 'Active',
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductImageFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form.cleaned_data.get('image') for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise forms.ValidationError("A product must have at least 3 images.")


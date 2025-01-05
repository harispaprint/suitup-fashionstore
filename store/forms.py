from django import forms
from .models import Product,ProductImage, Stock,Variation, VariationCategory,ReviewsRatings
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
 
    # product = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    variation_category = forms.ModelChoiceField(
        queryset=VariationCategory.objects.all(),  # Fetch all variation categories
        empty_label="Select Variation Category"
    )

    class Meta:
        model = Variation
        fields = ['product', 'variation_category', 'variation_value', 'is_active']
        

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
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewsRatings
        fields = ['review_subject','review_body','rating']


# class StockForm(forms.ModelForm):
#     class Meta:
#         model = Stock
#         fields = ['product', 'variation_combo', 'product_stock', 'price']
#         widgets = {
#             'variation_combo': forms.CheckboxSelectMultiple(),
#             'product_stock': forms.NumberInput(attrs={'min': 0}),
#             'price': forms.NumberInput(attrs={'min': 0}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['product'].widget.attrs.update({'class': 'form-control'})
#         self.fields['product_stock'].widget.attrs.update({'class': 'form-control'})
#         self.fields['price'].widget.attrs.update({'class': 'form-control'})

from django import forms
from .models import Stock, Product, Variation

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'variation_combo', 'product_stock', 'price']

    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        self.fields['variation_combo'].queryset = Variation.objects.none()
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                self.fields['variation_combo'].queryset = Variation.objects.filter(product_id=product_id)
            except (ValueError, TypeError):
                pass  # invalid input; return empty queryset
        elif self.instance.pk:
            self.fields['variation_combo'].queryset = self.instance.product.variation_set.all()


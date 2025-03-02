from django import forms
from .models import Coupon, Product,ProductImage, Stock,Variation, VariationCategory,ReviewsRatings
from category.models import Category
from django import forms
from .models import Stock, Product, Variation

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


class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = ['coupon_code','coupon_description','coupon_discount']
    
        widgets = {
            'coupon_code': forms.TextInput(attrs={'class': 'form-control'}),
            'coupon_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'coupon_discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_coupon_code(self):
        coupon_codes_check = set(code.lower() for code in Coupon.objects.values_list('coupon_code',flat=True))

        coupon_code = self.cleaned_data.get('coupon_code')

        if coupon_code.lower() in coupon_codes_check:
            raise forms.ValidationError(f"The coupon code {coupon_code} already exists")
        return coupon_code





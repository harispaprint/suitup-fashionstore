from django import forms
from .models import Account, UserProfile,UserAddresses
import re


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')
    
    # def clean(self):
    #     cleaned_data = super(UserForm, self).clean()

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')
    
    def clean(self):
        cleaned_data = super(UserProfileForm, self).clean()
        city = cleaned_data.get('city')
        if city and not city.isalpha():
            raise forms.ValidationError("City name should contain only letters.")
        return cleaned_data  # Return the entire cleaned_data dictionary, not just city

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddresses
        fields = (
            'first_name', 'last_name', 'address_line_1', 'address_line_2', 
            'city', 'state', 'country','pincode',
        )

    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("First name should contain only letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        
        if not re.match(r'^[A-Za-z.\s]+$', last_name):
            raise forms.ValidationError("Last name can only contain letters, spaces, and periods.")
        return last_name

    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get('address_line_1')
        if len(address_line_1) < 5:
            raise forms.ValidationError("Address Line 1 must be at least 5 characters long.")
        return address_line_1

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city.isalpha():
            raise forms.ValidationError("City name should contain only letters.")
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state.isalpha():
            raise forms.ValidationError("State name should contain only letters.")
        return state

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country.isalpha():
            raise forms.ValidationError("Country name should contain only letters.")
        return country
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit():
            raise forms.ValidationError("Pincode should contain only numbers.")
        return pincode

    def clean(self):
        cleaned_data = super(UserAddressForm, self).clean()
        address_line_1 = cleaned_data.get('address_line_1')
        address_line_2 = cleaned_data.get('address_line_2')

        if address_line_2 and address_line_1 == address_line_2:
            raise forms.ValidationError("Address Line 2 should not be the same as Address Line 1.")

        return cleaned_data
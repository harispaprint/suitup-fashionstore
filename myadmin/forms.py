from django import forms

class MyForm(forms.Form):
    selection = forms.ChoiceField(
        choices=[('option1', 'Option 1'), ('option2', 'Option 2')],
        label='Choose an option'
    )
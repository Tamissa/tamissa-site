# Django forms let us validate user input safely
from django import forms


class PurchaseRequestForm(forms.Form):
    # Customer name (required)
    customer_name = forms.CharField(max_length=120)

    # Customer email (required + validated)
    customer_email = forms.EmailField()

    # Optional message
    message = forms.CharField(required=False, widget=forms.Textarea)
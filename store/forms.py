import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Order


class RegisterForm(UserCreationForm):
    """Django's built-in sign-up form plus a required email address."""

    email = forms.EmailField(required=True, help_text="We use this to contact you about orders.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)


class CheckoutForm(forms.ModelForm):
    """Collects delivery details. The total is NOT part of this form:
    it is always calculated on the server."""

    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "address"]
        labels = {
            "full_name": "Full name",
            "email": "Email address",
            "phone": "Phone number",
            "address": "Delivery address",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "e.g. Asha Rao", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"placeholder": "e.g. 9876543210", "autocomplete": "tel"}),
            "address": forms.Textarea(
                attrs={"rows": 3, "placeholder": "House no., street, city, state, PIN code"}
            ),
        }

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = re.sub(r"[\s\-]", "", phone)  # ignore spaces and dashes
        if not re.fullmatch(r"\+?\d{10,13}", digits):
            raise forms.ValidationError("Enter a valid phone number (10 to 13 digits).")
        return digits

    def clean_address(self):
        address = self.cleaned_data["address"].strip()
        if len(address) < 10:
            raise forms.ValidationError("Please enter your complete delivery address.")
        return address

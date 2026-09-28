from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Account, Card

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['phone_number', 'password1', 'password2']

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'adress', 'passport_id']


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields =  ['card_number', 'cvv', 'type', 'pin', ]




class TransferForm(forms.Form):
    SOURCE_CHOICES = [
        ('account', 'Account'),
        ('card', 'Card'),
    ]

    SEND_CHOICES = [
        ('phone', 'Phone number'),
        ('card', 'Card number'),
    ]

    source_type = forms.ChoiceField(choices=SOURCE_CHOICES)

    source_card = forms.ModelChoiceField(
        queryset=Card.objects.all(),
        required=False
    )

    send_by = forms.ChoiceField(choices=SEND_CHOICES)

    receiver = forms.CharField(max_length=50)

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2
    )


class CheckPhoneForm(forms.Form):
    phone_number = forms.CharField(max_length=50)


class CheckCardForm(forms.Form):
    card_number = forms.CharField(max_length=16)
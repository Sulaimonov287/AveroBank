from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = None

    phone_number = models.CharField(
        max_length=50,
        unique=True
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField( max_length=50)
    last_name = models.CharField( max_length=50)
    adress = models.CharField( max_length=50)
    passport_id = models.CharField( max_length=50)
    balance = models.DecimalField( max_digits=10, decimal_places=2, default=1000)

    def __str__(self):
        return self.first_name

class Card(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    card_number = models.CharField( max_length=16, unique=True)
    cvv = models.CharField( max_length=3)
    date = models.DateField( auto_now_add=True)
    type = models.CharField( max_length=30)
    pin = models.CharField( max_length=4)
    balance = models.DecimalField( max_digits=10, decimal_places=2, default=500)

    def __str__(self):
        return self.card_number


class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    source_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_transactions')
    receiver_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transactions')
    amount = models.DecimalField( max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.receiver}"
    

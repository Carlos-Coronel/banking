from django.db import models

from .constants import TRANSACTION_TYPE_CHOICES
from accounts.models import UserBankAccount


class Transaction(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
    )
    #cantidad de la transacción
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    #saldo después de la transaccion
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    origin = models.CharField(max_length=255)

    required = models.CharField(max_length=256)

    def __str__(self):
        return str(self.account.account_no)

    class Meta:
        ordering = ['timestamp']

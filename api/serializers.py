from rest_framework import serializers
from transactions.models import Transaction
from django.conf import settings
from accounts.models import UserBankAccount

class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = UserBankAccount
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ['balance_after_transaction']

    def create(self, validated_data):
        account = validated_data['account']
        transaction_type = validated_data['transaction_type']
        amount = validated_data['amount']

        # Asegúrate de que transaction_type es uno de los valores esperados
        valid_transaction_types = [1, 2]

        if transaction_type not in valid_transaction_types:
            raise serializers.ValidationError("Tipo de transacción no válido")

        if transaction_type == 1:  # DEPOSIT
            validate_deposit_amount(amount)
            new_balance = account.balance + amount
        elif transaction_type == 2:  # WITHDRAWAL
            validate_withdrawal_amount(account, amount)
            new_balance = account.balance - amount

        # Crea la instancia de la transacción
        instance = Transaction.objects.create(
            amount=amount,
            transaction_type=transaction_type,
            account=account,
            balance_after_transaction=new_balance,
        )

        return instance

def validate_deposit_amount(amount):
    min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT

    if amount < min_deposit_amount:
        raise serializers.ValidationError(
            f'Necesitas depositar al menos {min_deposit_amount} $'
        )

def validate_withdrawal_amount(account, amount):
    min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
    max_withdraw_amount = account.account_type.maximum_withdrawal_amount
    balance = account.balance

    if amount < min_withdraw_amount:
        raise serializers.ValidationError(
            f'Puedes retirar al menos {min_withdraw_amount} $'
        )
    if amount > max_withdraw_amount:
        raise serializers.ValidationError(
            f'Puedes retirar como máximo {max_withdraw_amount} $'
        )
    if amount > balance:
        raise serializers.ValidationError(
            f'El saldo de tu cuenta es de {balance} $.'
            'No puedes retirar más que el saldo de tu cuenta'
        )

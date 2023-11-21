import datetime

from django import forms
from django.conf import settings

from .models import Transaction
from transactions.constants import APIS


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()



class DepositForm(TransactionForm):
    api = forms.ChoiceField(choices=APIS, widget=forms.Select(attrs={'onchange': 'updateAction()'}))


class WithdrawForm(TransactionForm):
    api = forms.ChoiceField(choices=APIS, widget=forms.Select(attrs={'onchange': 'updateAction()'}))


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        print(daterange)

        try:
            daterange = daterange.split(' - ')
            print(daterange)
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Seleccione un rango de fechas.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Intervalo de fechas no válido")

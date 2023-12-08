from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from transactions.constants import DEPOSIT, WITHDRAWAL
from transactions.forms import (
    DepositForm,
    WithdrawForm,
)
from transactions.models import Transaction
from .decorators import user_has_bank_account

#Informe de transacciones
@method_decorator(user_has_bank_account, name='dispatch')

class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction


#Depósitos y retiros
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context

@method_decorator(user_has_bank_account, name='dispatch')
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposite dinero en su cuenta'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial



#Retiros de la cuenta bancaria.
@method_decorator(user_has_bank_account, name='dispatch')
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Retirar dinero de su cuenta'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

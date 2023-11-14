from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from transactions.constants import DEPOSIT, WITHDRAWAL
from transactions.forms import (
    DepositForm,
    TransactionDateRangeForm,
    WithdrawForm,
)
from transactions.models import Transaction
from .decorators import user_has_bank_account

from core.models import Auditoria
from uuid import getnode as get_mac

#Informe de transacciones
@method_decorator(user_has_bank_account, name='dispatch')

class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None)
        })

        return context

#Depósitos y retiros
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

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

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        if not account.initial_deposit_date:
            now = timezone.now()
            next_interest_month = int(
                12 / account.account_type.interest_calculation_per_year
            )

            account.initial_deposit_date = now

            account.interest_start_date = (
                now + relativedelta(
                    months=+next_interest_month
                )
            )

        account.balance += amount
        account.save(
            update_fields=[
                'initial_deposit_date',
                'balance',
                'interest_start_date'
            ]
        )

        # Auditoría
        mac_int = get_mac()
        dir_mac = ':'.join(("%012X" % mac_int)[i:i + 2] for i in range(0, 12, 2))

        Auditoria.objects.create(
            ip=self.request.META['REMOTE_ADDR'],
            nombre_pc=self.request.META.get('COMPUTERNAME', ''),
            usuario=self.request.user,
            evento='deposito',
            nivel='medio',
            mac=dir_mac
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ Fue depositada en su cuenta con éxito'
        )

        return super().form_valid(form)

#Retiros de la cuenta bancaria.
@method_decorator(user_has_bank_account, name='dispatch')
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Retirar dinero de su cuenta'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        # Auditoría
        mac_int = get_mac()
        dir_mac = ':'.join(("%012X" % mac_int)[i:i + 2] for i in range(0, 12, 2))

        Auditoria.objects.create(
            ip=self.request.META['REMOTE_ADDR'],
            nombre_pc=self.request.META.get('COMPUTERNAME', ''),
            usuario=self.request.user,
            evento='retiro',
            nivel='alto',
            mac=dir_mac
        )

        messages.success(
            self.request,
            f'Retiró con éxito {"{:,.2f}".format(float(amount))}$ de su cuenta'
        )

        return super().form_valid(form)

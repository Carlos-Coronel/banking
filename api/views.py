from rest_framework.response import Response
from rest_framework import status

from .serializers import TransactionSerializer, UserSerializer
from transactions.models import Transaction
from transactions.constants import DEPOSIT, WITHDRAWAL
from core.models import Auditoria
from uuid import getnode as get_mac
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.utils import timezone

from accounts.models import UserBankAccount

from django.shortcuts import redirect, get_object_or_404

from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated

class UserBankAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_bank_account = UserBankAccount.objects.get(user=request.user)
            serializer = UserSerializer(user_bank_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserBankAccount.DoesNotExist:
            return Response({'error': 'La cuenta bancaria no existe para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class APIListView(APIView):

    def get(self, request):
        apis = [
            {'id': 1, 'name': 'Celestial Bank', 'url': 'http://192.168.1.34:8000/api/celestial/report/ | http://192.168.1.34:8000/api/user/balance/ '},
            {'id': 2, 'name': 'Roberk Bank', 'url': 'http://192.168.30.134:8001/api/celestial/report/ | http://192.168.30.134:8001/api/user/balance/ '},
        ]
        return Response(apis)

class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, daterange=None):
        queryset = Transaction.objects.filter(account=request.user.account)

        # Aplicar el filtrado por rango de fechas si está presente
        if daterange:
            start_date, end_date = daterange.split(',')
            queryset = queryset.filter(timestamp__date__range=[start_date, end_date])

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, daterange=None):

        serializer = TransactionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # Lógica adicional para depósito y retiro
            amount = serializer.validated_data.get('amount')

            if serializer.validated_data.get('transaction_type') == DEPOSIT:
                # Lógica de depósito
                user_id = request.POST.get('user_id')
                account = get_object_or_404(UserBankAccount, user_id=user_id)

                #account = request.user.account
                if not account.initial_deposit_date:
                    now = timezone.now()
                    next_interest_month = int(
                        12 / account.account_type.interest_calculation_per_year
                    )
                    account.initial_deposit_date = now
                    account.interest_start_date = now + relativedelta(months=+next_interest_month)

                account.balance += amount
                account.save(
                    update_fields=[
                        'initial_deposit_date',
                        'balance',
                        'interest_start_date'
                    ]
                )
                # Auditoría de depósito
                record_auditoria(request, 'deposito', 'medio')
                messages.success(
                    request,
                    f'{"{:,.2f}".format(float(amount))}$ Fue depositado con éxito'
                )


            elif serializer.validated_data.get('transaction_type') == WITHDRAWAL:
                # Lógica de retiro
                request.user.account.balance -= amount
                request.user.account.save(update_fields=['balance'])
                # Auditoría de retiro
                record_auditoria(request, 'retiro', 'alto')

                messages.success(
                    request,
                    f'{"{:,.2f}".format(float(amount))}$ Fue retirado con éxito'
                )
            return Response({"message": f'{"{:,.2f}".format(float(amount))}$ Fue procesado con éxito'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def record_auditoria(request, evento, nivel):
        mac_int = get_mac()
        dir_mac = ':'.join(("%012X" % mac_int)[i:i + 2] for i in range(0, 12, 2))

        Auditoria.objects.create(
            ip=request.META['REMOTE_ADDR'],
            nombre_pc=request.META.get('COMPUTERNAME', ''),
            usuario=request.user,
            evento=evento,
            nivel=nivel,
            mac=dir_mac
        )




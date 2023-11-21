from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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

from django.shortcuts import redirect


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bank_account(request):
    try:
        user_bank_account = UserBankAccount.objects.get(user=request.user)

        serializer = UserSerializer(user_bank_account)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserBankAccount.DoesNotExist:
        return Response({'error': 'La cuenta bancaria no existe para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list(request):
    apis = [
        {'id': 1, 'name': 'Celestial Bank', 'url': 'http://localhost:8000/api/celestial/report/ | http://localhost:8000/api/user/balance/ '},
        {'id': 2, 'name': 'Roberk Bank', 'url': 'http://192.168.11.194:8001/api/celestial/report/ | http://localhost:8000/api/user/balance/ '},
    ]
    return Response(apis)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])

def transaction_list(request, daterange=None):
    queryset = Transaction.objects.filter(account=request.user.account)

    # Aplicar el filtrado por rango de fechas si está presente
    if daterange:
        start_date, end_date = daterange.split(',')
        queryset = queryset.filter(timestamp__date__range=[start_date, end_date])

    if request.method == 'GET':
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)


    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Configurar el campo 'account' automáticamente antes de guardar
            serializer.validated_data['account'] = request.user.account
            serializer.save()

            # Lógica adicional para depósito y retiro
            amount = serializer.validated_data.get('amount')

            if serializer.validated_data.get('transaction_type') == DEPOSIT:
                # Lógica de depósito
                account = request.user.account
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

            elif serializer.validated_data.get('transaction_type') == WITHDRAWAL:
                # Lógica de retiro
                request.user.account.balance -= amount
                request.user.account.save(update_fields=['balance'])
                # Auditoría de retiro
                record_auditoria(request, 'retiro', 'alto')

            messages.success(
                request,
                f'{"{:,.2f}".format(float(amount))}$ Fue procesado con éxito'
            )
            return redirect('transactions:transaction_report')
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




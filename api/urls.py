# api_app/urls.py
from django.urls import path
from .views import UserBankAccountView, APIListView, TransactionListView

app_name = 'api_app'

urlpatterns = [
    path('celestial/report/', TransactionListView.as_view(), name='transaction-report'),
    path('api-list/', APIListView.as_view(), name='api-list'),
    path('user/balance/', UserBankAccountView.as_view(), name='user-balance'),
    path('celestial/report/<str:daterange>/', TransactionListView.as_view(), name='transaction-report-filtered'),
]

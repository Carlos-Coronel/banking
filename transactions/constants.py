DEPOSIT = 1
WITHDRAWAL = 2
INTEREST = 3

TRANSACTION_TYPE_CHOICES = (
    (DEPOSIT, 'Deposito'),
    (WITHDRAWAL, 'Retiro'),
    (INTEREST, 'Interes'),
)


APIS = [
    ('http://192.168.1.38:8000/api/celestial/report/', 'Celestial Bank'),
    ('http://192.168.30.134:8001/api/celestial/report/', 'Robert Bank'),
]
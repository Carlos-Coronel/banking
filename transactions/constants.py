DEPOSIT = 1
WITHDRAWAL = 2
INTEREST = 3

TRANSACTION_TYPE_CHOICES = (
    (DEPOSIT, 'Deposito'),
    (WITHDRAWAL, 'Retiro'),
    (INTEREST, 'Interes'),
)


APIS = [
    ('http://localhost:8000/api/celestial/report/', 'Celestial Bank'),
    ('http://192.168.11.194:8001/api/celestial/report/', 'Robert Bank'),
]
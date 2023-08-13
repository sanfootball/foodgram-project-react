import random
from django.core.mail import send_mail


def confirmation_code_generation():
    """Генерация кода подтверждения для отправки токена."""
    symbols = '+-/*!&$#?=@<>'
    lower_case = 'abcdefghijklnopqrstuvwxyz'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    chars = (symbols + lower_case + uppercase)
    for n in range(1):
        password = ''
        for i in range(18):
            password += random.choice(chars)
    return password


def send_confirmation_code_to_email(confirmation_code, email):
    """Отправка пользователю на email confirmation_code."""
    send_mail(
        'Код подтверждения для получения JWT токена.',
        f'confirmation_code: {confirmation_code}',
        'from@example.com',  # Это поле "От кого"
        [email],  # Это поле "Кому" (можно указать список адресов)
        fail_silently=False,  # Сообщать об ошибках («молчать ли об ошибках?»)
    )

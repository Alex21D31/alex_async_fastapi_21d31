import time
from .celery_app import celery_instance
@celery_instance.task(name='send_welcome_email')
def send_welcome_email(email : str):
    """
    Отправка приветственного письма пользователю после регистрации.
    """
    print(f"Начинаю отправку письма на {email}")
    time.sleep(3) 
    print(f"Письмо успешно отправлено на {email}!")
    return {"status": "sent", "to": email}
@celery_instance.task(name='change_password_email')
def change_password_email(email : str):
    """
    Уведомление пользователя о смене пароля.
    """
    print(f"Начинаю отправку письма на {email}")
    print("Ваш пароль был изменён")
    print("Если это были не вы — обратитесь в поддержку")
    time.sleep(2)
    print(f"Письмо успешно отправлено на {email}!")
    return {"status": "sent", "to": email}
@celery_instance.task(name='send_order_confirmation')
def send_order_confirmation(user_id : int, order_id : int, items : list):
    """
    Уведомление пользователя о создании его заказа.
    """
    print(f'Обработка заказа №{order_id} для пользователя {user_id}')
    products_list = [f'Товар : {item['name']}, количество : {item['quantity']}' for item in items]
    products_in_order = ', '.join(products_list)
    time.sleep(3)
    print('EMAIL MESSAGE')
    print(f'Пользователь ID {user_id}')
    print(f'Ваш заказ №{order_id} принят!')
    print(f'Состав заказа : {products_in_order}')
    return {
        'status' : 'success',
        'order_id' : order_id,
        'sent_to_user' : user_id
    }


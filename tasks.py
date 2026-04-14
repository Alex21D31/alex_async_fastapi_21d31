import time
from celery_app import celery_instance
@celery_instance.task(name='send_welcome_email')
def send_welcome_email(email : str):
    print(f"--- Начинаю отправку письма на {email} ---")
    
    # Имитируем долгую работу (например, коннект к SMTP серверу)
    time.sleep(5) 
    
    print(f"--- Письмо успешно отправлено на {email}! ---")
    return {"status": "sent", "to": email}
@celery_instance.task(name='change_password_email')
def change_password_email(email : str):
    print(f"--- Начинаю отправку письма на {email} ---")
    print("--- Тема: Ваш пароль был изменён ---")
    print("--- Текст: Если это были не вы — обратитесь в поддержку ---")
    time.sleep(2)
    print(f"--- Письмо успешно отправлено на {email}! ---")
    return {"status": "sent", "to": email}
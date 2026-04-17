# kafka_utils/producer.py
from fastapi import Request
from aiokafka import AIOKafkaProducer

async def get_producer(request: Request) -> AIOKafkaProducer:
    """
    Получение экземпляра Kafka Producer из состояния приложения.
    """
    return request.app.state.producer

async def send_order_event(order_id: int, user_id: int, items: list, producer: AIOKafkaProducer) -> None:
    """
    Отправка события о создании заказа в топик 'order_created'.
    """
    event = {
        'order_id': order_id,
        'user_id': user_id,
        'items': items
    }
    await producer.send_and_wait('order_created', value=event)
    print(f"Событие заказа {order_id} отправлено")
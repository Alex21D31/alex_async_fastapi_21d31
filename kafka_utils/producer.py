import json
from aiokafka import AIOKafkaProducer
from config import settings

_producer = None

async def get_producer():
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await _producer.start()
    return _producer

async def send_order_event(order_id: int, user_id: int, items: list) -> None:
    producer = await get_producer()
    event = {
        'order_id': order_id,
        'user_id': user_id,
        'items': items
    }
    await producer.send_and_wait('order_created', value=event)
    print(f"Событие заказа {order_id} отправлено")
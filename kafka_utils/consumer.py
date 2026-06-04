import json
import asyncio
from aiokafka import AIOKafkaConsumer
from config import settings
from celery_utils.email_tasks import send_order_confirmation
from celery_utils.order_tasks import process_order

async def start_order_consumer():
    """
    Запуск консьюмера Kafka для обработки событий создания заказа.
    """
    consumer = AIOKafkaConsumer(
        'order_created',
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="order_processing_group",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    await consumer.start()
    print("Консьюмер запущен")
    
    try:
        async for msg in consumer:
            # Извлечение данных из сообщения.
            order_data = msg.value
            print(f"Получен заказ: {order_data['order_id']}")
            # Отправка email подтверждения.
            send_order_confirmation.delay(
                user_id=order_data['user_id'],
                order_id=order_data['order_id'],
                items=order_data['items']
            )
            # Запуск обработки заказа по этапам.
            process_order.delay(order_id=order_data['order_id'])
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(start_order_consumer())
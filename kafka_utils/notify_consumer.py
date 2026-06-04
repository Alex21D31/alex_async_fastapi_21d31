import json
import asyncio
from aiokafka import AIOKafkaConsumer
from config import settings
from celery_utils.email_tasks import send_application_result, send_moderation_result
import logging

logger = logging.getLogger(__name__)

async def start_notify_consumer():
    """
    Запуск консьюмера Kafka для обработки уведомлений продавцов.
    Слушает топик seller.notification — события по заявкам и верификации магазинов.
    """
    consumer = AIOKafkaConsumer(
        'seller.notification',
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="seller_notification_group",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    await consumer.start()
    logger.info("Notify консьюмер запущен")

    try:
        async for msg in consumer:
            data = msg.value
            event_type = data.get('event_type')
            logger.info(f"Получено событие: {event_type}")

            if event_type == 'application_result':
                send_application_result.delay(
                    email=data['email'],
                    status=data['status']
                )
            elif event_type == 'moderation_result':
                send_moderation_result.delay(
                    email=data['email'],
                    shop_name=data['shop_name'],
                    status=data['status']
                )
            else:
                logger.warning(f"Неизвестный event_type: {event_type}")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(start_notify_consumer())
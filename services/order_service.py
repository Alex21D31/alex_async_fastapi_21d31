from repositories.order_repo import OrderRepository
from repositories.product_repo import ProductRepository
from schemas import CreateOrder, UpdateOrder
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Order, OrderItem, Status
from kafka_utils.producer import send_order_event
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from aiokafka import AIOKafkaProducer

class OrderService:
    def __init__(self,order_repo: OrderRepository, product_repo: ProductRepository, db: AsyncSession):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.db = db
    async def _get_order_or_404(self, order_id: int) -> Order:
        """
        Вспомогательная функция для получения заказа по айди.
        Используется в основных функциях.
        """
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail='Заказ не найден')
        return order
    async def create_order(self, user_id: int, data: CreateOrder,producer: AIOKafkaProducer) -> Order:
        """
        Создание заказа и списание товаров со склада.

        Процесс:
        1. Создается объект заказа 
        2. Проверяется наличие каждого товара в базе и его количество на складе.
        3. Уменьшается количество товара
        4. Создаются записи OrderItem.
        5. Данные отправляются в Kafka для уведомлений.

        Args:
            user_id: Айди пользователя.
            data : Обьект CreateOrder, содержащий в себе список продуктов, отобранных пользователем.
            producer: взаимодействие с Kafka
        
        Returns:
            Созданный заказ
        
        Raises:
            HTTPException: 404, товар не найден
            HTTPException: 400, товара недостаточно
        """
        order = Order(user_id=user_id, info=data.info)
        self.db.add(order)
        await self.db.flush()

        kafka_items = []

        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise HTTPException(404, f'Товар {item.product_id} не найден')
            if product.quantity < item.quantity:
                raise HTTPException(400, f'Недостаточно товара {product.name} на складе')
            product.quantity -= item.quantity
            kafka_items.append({
                'product_id' : product.id,
                'name' : product.name,
                'quantity' : item.quantity
            })
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            self.db.add(order_item)
        await self.db.commit()
        query = (
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
        )
        result = await self.db.execute(query)
        order = result.scalar_one()
        try:
            await send_order_event(
                order_id = order.id,
                user_id = user_id,
                items = kafka_items,
                producer=producer
            )
        except Exception as e:
            print(f'Kafka недоступна, событие для заказа {order.id} потеряно. {e} ')
        return order
    async def get_all_orders(self, data : dict) -> list[Order]:
        """
        Получение  информации обо всех заказов пользователя.
        В качестве параметра ID для поиска используется айди пользователя из его Access токена.
        """
        result = await self.order_repo.get_all_orders_by_user(int(data['sub']))
        return result
    async def get_one_order(self, order_id : int, data : dict) -> Order:
        """
        Получение  информации об 1 заказе пользователя.

        Args:
            order_id: Айди заказа
            data: Информация о пользователе из Access токена.
        
        Returns:
            Информация о заказе
        
        Raises:
            HTTPException: 404, заказ не найден.
        """
        result = await self.order_repo.get_by_id_for_user(order_id, int(data['sub']))
        if not result:
            raise HTTPException(404, 'Заказ не найден')
        return result
    async def update_order(self, order_id : int, patch_order : UpdateOrder) -> Order:
        """
        Обновление информации о заказе.

        Args:
            order_id: Айди заказа.
            patch_order: Обновляемая информация.

        Returns:
            Обновленный заказ.
        
        Raises:
            HTTPException: 404, заказ не найден. (через _get_order_or_404).
        """
        order = await self._get_order_or_404(order_id)
        return await self.order_repo.update(order, patch_order.model_dump(exclude_none=True)) 
    async def delete_order(self, order_id):
        """
        Удаление заказа

        Args:
            order_id: Айди заказа

        Returns:
            Информация о удалении.
        
        Raises:
            HTTPException: 404, заказ не найден. (через _get_order_or_404).
        """
        order = await self._get_order_or_404(order_id)
        await self.order_repo.delete(order)
        return f'Заказ под номером {order_id} успешно удален.'
    async def update_status(self, order_id : int, new_status : Status):
        """
        Обновление статуса заказа.
        Функция доступна только для ролей Admin и выше.

        Raises:
            HTTPException: 404, заказ не найден. (через _get_order_or_404).
        """
        order = await self._get_order_or_404(order_id)
        return await self.order_repo.update(order, {'status' : new_status})

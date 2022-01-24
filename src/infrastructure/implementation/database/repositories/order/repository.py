from typing import cast, List

from sqlalchemy import delete, insert, lambda_stmt, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from src.domain.entities.order import Order
from src.infrastructure.implementation.database.errors import QueryErrors
from src.infrastructure.implementation.database.orm.models import OrderModel, OrderItemModel
from src.infrastructure.implementation.database.repositories.crud_repository import SQLAlchemyCRUDRepository
from src.infrastructure.implementation.database.repositories.order.queries import CreateOrderQuery


class OrderRepositoryImpl:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._crud_repository = SQLAlchemyCRUDRepository(session, model=OrderModel)

    async def get_order_by_id(self, order_id: int) -> Order:
        result = await self._crud_repository.get_one(OrderModel.id == order_id)
        if result is None:
            raise QueryErrors.NOT_FOUND.with_params(id=order_id)
        return cast(Order, result)

    async def create_order(self, query: CreateOrderQuery) -> int:
        insert_order_statement = insert(
            OrderModel
        ).values(order_date=query.order_date, customer_id=query.customer_id).returning(OrderModel.id)
        order_id = (await self._session.execute(insert_order_statement)).scalar()
        await self._session.execute(
            insert(OrderItemModel),
            params=[
                {"order_id": order_id, "product_id": position.product_id, "quantity": position.quantity}
                for position in query.positions
            ]
        )
        return cast(int, order_id)

    async def delete_order_by_id(self, order_id: int) -> None:
        delete_statement = delete(OrderModel).where(OrderModel.id == order_id)
        await self._session.execute(delete_statement)
        delete_in_m2m_table = delete(OrderItemModel).where(OrderItemModel.order_id == order_id)
        await self._session.execute(delete_in_m2m_table)

    async def get_all_orders(self) -> List[Order]:
        stmt = lambda_stmt(lambda: select(OrderModel))
        result = ((await self._session.execute(cast(Executable, stmt))).unique().scalars().all())
        return result

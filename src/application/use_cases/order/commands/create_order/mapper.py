from src.application.use_cases.order.commands.create_order.command import CreateOrderCommand
from src.infrastructure.implementation.database.repositories.order.queries import CreateOrderQuery, \
    OrderPosition


class CreateOrderCommandToQueryMapper:

    def to_query(self, command: CreateOrderCommand) -> CreateOrderQuery:
        dto = command.create_order_dto
        return CreateOrderQuery(
            order_date=dto.order_date,
            customer_id=dto.customer_id,
            positions=[
                OrderPosition(product_id=product.id, quantity=product.quantity)
                for product in dto.products
            ]
        )

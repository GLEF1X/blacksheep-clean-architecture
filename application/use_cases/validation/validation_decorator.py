from typing import Union

from pydantic import BaseModel, ValidationError

from application.cqrs_lib.extensibility.decorators import HandlerDecorator, _ResultType
from application.cqrs_lib.result import Failure, Result


class ValidationQueryHandlerDecorator(
    HandlerDecorator[BaseModel, Union[_ResultType, Result[None]]]
):
    async def handle(self, event: BaseModel) -> Union[_ResultType, Result[None]]:
        try:
            return await self._wrapped_handler.handle(event)
        except ValidationError as validation_error:
            validation_failure = Failure.from_exception(
                validation_error, message=validation_error.json()
            )
            return Result.fail(validation_failure)

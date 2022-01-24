import datetime
from typing import Optional

from blacksheep import Response, Request

from src.web.util.blacksheep_context.errors import DateFormatError
from src.web.util.blacksheep_context.header_keys import HeaderKeys
from src.web.util.blacksheep_context.plugins import Plugin


class DateHeaderPlugin(Plugin):
    key = HeaderKeys.date

    def __init__(
        self,
        *args,
        error_response: Optional[Response] = Response(status=400),
    ):
        super().__init__(*args)
        self.error_response = error_response

    @staticmethod
    def rfc1123_to_dt(s: str) -> datetime.datetime:
        return datetime.datetime.strptime(s, "%a, %d %b %Y %H:%M:%S")

    async def process_request(self, request: Request) -> Optional[datetime.datetime]:
        """
        Has to be as stated in rfc2616 which uses rfc1123. Has to be in GMT.
        Returns UTC datetime.

        Examples allowed:     Wed, 01 Jan 2020 04:27:12 GMT     Wed, 01 Jan
        2020 04:27:12
        """

        rfc1123 = await self.extract_value_from_header_by_key(request)
        if not rfc1123:
            value = None
        else:
            dt_str, dt_data = rfc1123[:25], rfc1123[25:]

            if dt_data.strip() not in ("", "GMT"):  # empty str assumes ok
                raise DateFormatError(
                    "Date header in wrong format, has to match rfc1123.",
                    error_response=self.error_response,
                )

            try:
                value = self.rfc1123_to_dt(dt_str.strip())
            except ValueError as e:
                raise DateFormatError(
                    str(e), error_response=self.error_response
                )
        return value

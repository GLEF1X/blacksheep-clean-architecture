import enum


class HeaderKeys(str, enum.Enum):
    api_key = "X-API-Key"
    correlation_id = "X-Correlation-ID"
    request_id = "X-Request-ID"
    date = "Date"
    forwarded_for = "X-Forwarded-For"
    user_agent = "User-Agent"

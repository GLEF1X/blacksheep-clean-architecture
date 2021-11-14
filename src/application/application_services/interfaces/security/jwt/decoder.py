from typing import Protocol, Any, Dict


class TokenDecoder(Protocol):
    def decode_token(self, token: str) -> Dict[str, Any]:
        pass

from src.web.util.blacksheep_context.header_keys import HeaderKeys
from src.web.util.blacksheep_context.plugins.base import Plugin


class ApiKeyPlugin(Plugin):
    key = HeaderKeys.api_key

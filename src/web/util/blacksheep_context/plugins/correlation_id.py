from src.web.util.blacksheep_context.header_keys import HeaderKeys
from src.web.util.blacksheep_context.plugins.base import PluginUUIDBase


class CorrelationIdPlugin(PluginUUIDBase):
    key = HeaderKeys.correlation_id

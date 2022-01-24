from src.web.util.blacksheep_context.header_keys import HeaderKeys
from src.web.util.blacksheep_context.plugins import Plugin


class ForwardedForPlugin(Plugin):
    key = HeaderKeys.forwarded_for

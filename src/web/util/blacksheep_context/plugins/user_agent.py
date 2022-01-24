from src.web.util.blacksheep_context.header_keys import HeaderKeys
from src.web.util.blacksheep_context.plugins import Plugin


class UserAgentPlugin(Plugin):
    key = HeaderKeys.user_agent

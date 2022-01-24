from __future__ import annotations

import logging
from typing import Dict

from guardpost.authorization import AuthorizationContext
from guardpost.synchronous.authorization import Requirement


class ScopeRequirement(Requirement):
    def __init__(self, *, scopes: Dict[str, str]):
        self._required_scopes = scopes
        self._logger = logging.getLogger("(Scope requirement)")

    def handle(self, context: AuthorizationContext):
        identity = context.identity
        if identity is None:
            return context.fail("User has no identity!")
        scopes = identity.claims.get("scopes")
        if scopes is None:
            return context.fail("Not enough permissions to process this operation!")
        for scope in self._required_scopes.keys():
            if scope not in scopes:
                context.fail(f"{scope} scope was not found in the must-have list")

        context.succeed(self)

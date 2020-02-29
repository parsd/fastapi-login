"""User session module."""

from __future__ import annotations

import base64
import json
from enum import Enum, unique
from typing import Mapping

from pydantic import BaseModel


class TokenError(Exception):
    """Signal an invalid `Token`."""


@unique
class TokenType(str, Enum):
    """Possible token types for HTTP transmission.

    `BEARER` tokens are sent in the authorization field in the HTTP header
    (`Authorization: Bearer `). `COOKIE` tokens are sent in the cookie field
    (`Cookie: token=`)
    """

    BEARER = "bearer"
    COOKIE = "cookie"


SESSION_HEADER = base64.b64encode(b'{"typ":"SESSION"}')


class Token(BaseModel):
    """Access token to grant access to resources.

    Objects of this type are normally used in client communication. Internally
    the `access_token` is used directly.
    """

    access_token: bytes
    token_type: TokenType = TokenType.BEARER

    @classmethod
    def from_session_id(cls, session_id: str) -> Token:
        """Create a new `Token` from the given `session_id`.

        :param session_id: Unique session identifier.
        :returns: Newly created `Token` object.
        """
        payload = b'{"session":"' + session_id.encode("utf-8") + b'"}'
        token = b".".join([SESSION_HEADER, base64.b64encode(payload)])
        return cls(access_token=token)

    def decode(self, *, validate: bool = True) -> Mapping[str, str]:
        """Decode the token payload.

        :param validate: `True` is to validate the token; `False` tries to ignore invalid data.
        :returns: Dictionary with the token's data.
        :raises TokenError: if `self.access_token` is invalid.
        """
        try:
            header, payload, *_ = self.access_token.split(b".")
        except ValueError:
            raise TokenError("Missing token payload")
        if header != SESSION_HEADER:
            raise TokenError("Invalid token format")
        try:
            return json.loads(base64.b64decode(payload, validate=validate))
        except Exception as ex:
            raise TokenError(ex.args) from ex

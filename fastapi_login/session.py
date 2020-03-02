"""User session module."""

from __future__ import annotations
from abc import abstractmethod
from typing import Optional, Protocol, TypeVar

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


UT = TypeVar("UT")


class SessionStore(Protocol[UT]):
    """Generic protocol for handling and storing sessions.

    Supports objects and modules implementing this session protocol via structural
    subtyping (i.e. the objects/modules do not need to derive from this protocol).

    :tparam UT: Type of user to be stored in the store.
    """

    @abstractmethod
    def __contains__(self, session_id: str) -> bool:
        """Test whether the session_id is in the session store.

        :param session_id: Identifier to be looked for.
        :returns: `True` if session_id exists; `False` if not.
        """
        raise NotImplementedError()

    @abstractmethod
    def new(self, session_id: str, user: UT) -> None:
        """Create a new user session.

        Precondition: `session_id not in self`

        :param session_id: Token identifying the session to be added.
        :param user: User to create a new session for.
        """
        raise NotImplementedError()

    @abstractmethod
    def remove(self, session_id: str) -> None:
        """Remove the user session with the given session_id.

        :param session_id: Token identifying the session to be removed.
        """
        raise NotImplementedError()

    @abstractmethod
    def get(self, session_id: str) -> Optional[UT]:
        """Try to get the user of type `UT` for the given session_id.

        :param session_id: Token identifying the session to be retrieved.
        :returns: User of type `UT` if session exists; `None` otherwise.
        """
        raise NotImplementedError()

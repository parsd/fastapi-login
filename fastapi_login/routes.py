"""Users routes module."""

from http import HTTPStatus
from typing import Callable, Generator, Generic
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import session


class Users(Generic[session.UT]):
    """The users routes for authentication."""

    def __init__(
        self,
        store: session.SessionStore,
        authenticate: Callable[[str, str], session.UT],
    ) -> None:
        """Create the FastApi router with login/logout routes.

        :param store:
        :param authenticate: Callable that takes first the user name and then the password. Returns a user
            on success. Raises an error derived from `Exception` on error.
        """
        self._router = APIRouter()
        self._store = store
        self._authenticate = authenticate
        self._unique_ids = self._make_unique_id()

        # decorate all the routes
        self.router.post(
            "/login", status_code=HTTPStatus.CREATED, response_model=session.Token
        )(self._login)

    @property
    def router(self) -> APIRouter:
        """Get the FastApi `APIRouter`.

        :returns: `APIRouter` object storing all user routes.
        """
        return self._router

    def _login(
        self, form_data: OAuth2PasswordRequestForm = Depends()
    ) -> session.Token:  # noqa: D301
        """User login via form request.

        Mandatory items are **username** and **password**.
        \f
        :param form_data: User name and password.
        :returns: Access token for future requests if successful.
        :raises HTTPException: if login failed.
        """
        try:
            session_id = next(self._unique_ids)
            user = self._authenticate(form_data.username, form_data.password)
            self._store.new(session_id, user)
            return session.Token.from_session_id(session_id)
        except Exception as err:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=err.args)

    def _make_unique_id(self) -> Generator[str, None, None]:
        while True:
            identifier = secrets.token_hex()
            if identifier not in self._store:
                yield identifier


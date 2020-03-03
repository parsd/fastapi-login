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
        *,
        token_url: str = "login",
    ) -> None:
        """Create the FastApi router with login/logout routes.

        :param store: Repository storing users by their session id.
        :param authenticate: Callable that takes first the user name and then the password. Returns a user
            on success. Raises an error derived from `Exception` on error.
        """
        self._router = APIRouter()
        self._store = store
        self._authenticate = authenticate
        self._unique_ids = self._make_unique_id()
        self._oauth2_scheme = OAuth2PasswordBearer(token_url)

        # routes are defined here as FastAPI's dependency system works at function
        # definition time and self is needed for dynamic token_url
        @self.router.post(
            "/login", status_code=HTTPStatus.CREATED, response_model=session.Token
        )
        def login(
            form_data: OAuth2PasswordRequestForm = Depends(),
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

        self._login = login

        @self.router.delete("/logout", status_code=HTTPStatus.NO_CONTENT)
        def logout(token: str = Depends(self._oauth2_scheme)) -> None:  # noqa: D301
            """Logout user of given token.
            \f
            :param token: The session token of the user to log out.
            :returns: User information about the logged in user.
            :raises: HTTPException: if token is invalid.
            """
            try:
                session_id = session.Token(access_token=token).decode()["session"]
                self._store.remove(session_id)
            except Exception:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        self._logout = logout

    @property
    def router(self) -> APIRouter:
        """Get the FastApi `APIRouter`.

        :returns: `APIRouter` object storing all user routes.
        """
        return self._router

    def _make_unique_id(self) -> Generator[str, None, None]:
        while True:
            identifier = secrets.token_hex()
            if identifier not in self._store:
                yield identifier


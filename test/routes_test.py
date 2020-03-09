"""Integration test for the `routes` module."""

from dataclasses import dataclass
from http import HTTPStatus
from typing import Callable, MutableMapping, Protocol
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that
from fastapi import FastAPI
from requests.models import Response
from starlette.testclient import TestClient

import fastapi_login

from . import mocks

# make fixtures work without warning:
# pylint: disable=redefined-outer-name

USERNAME = "user@test.net"
PASSWORD = "secret"

ERROR_TEXT = "the error"

TEST_USER = mocks.User(name=USERNAME)


@dataclass
class LoggedOutApp:  # noqa: D101
    client: TestClient
    store: mocks.SessionStore
    authenticate: Callable[[str, str], mocks.User]


@dataclass
class LoggedInApp(LoggedOutApp):  # noqa: D101
    access_token: str
    default_headers: MutableMapping[str, str]


@pytest.fixture
def logged_out_app() -> LoggedOutApp:
    """Create the logged out test web app for `fastapi_login.UsersRoutes."""

    def auth(username: str, password: str) -> mocks.User:
        if username != USERNAME or password != PASSWORD:
            raise Exception(ERROR_TEXT)
        return TEST_USER

    store = mocks.SessionStore()
    authenticate = MagicMock(side_effect=auth)
    routes = fastapi_login.UsersRoutes(mocks.User, store, authenticate)

    app = FastAPI(debug=True)
    app.include_router(routes.router)
    return LoggedOutApp(client=TestClient(app), store=store, authenticate=authenticate)


@pytest.fixture
def logged_in_app(logged_out_app: LoggedOutApp) -> LoggedInApp:
    """Create the logged in test web app for `fastapi_login.UsersRoutes."""
    response: Response = logged_out_app.client.post(
        "/login", data={"username": USERNAME, "password": PASSWORD}
    )
    assert response.status_code == HTTPStatus.CREATED
    access_token = response.json()["access_token"]
    return LoggedInApp(
        client=logged_out_app.client,
        store=logged_out_app.store,
        authenticate=logged_out_app.authenticate,
        access_token=access_token,
        default_headers={"Authorization": f"Bearer {access_token}"},
    )


def test_valid_login(logged_out_app: LoggedOutApp) -> None:
    """Test a valid login request."""
    response = logged_out_app.client.post(
        "/login", data={"username": USERNAME, "password": PASSWORD}
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.CREATED)
    logged_out_app.authenticate.assert_called_once_with(USERNAME, PASSWORD)  # type: ignore
    assert_that(logged_out_app.store).is_length(1)

    reference_token = fastapi_login.Token.from_session_id(
        logged_out_app.store.keys()[0]
    )
    session_token = fastapi_login.Token.parse_obj(response.json())
    assert_that(session_token).is_equal_to(reference_token)


def test_invalid_login(logged_out_app: LoggedOutApp) -> None:
    """Test an invalid login request."""
    response = logged_out_app.client.post(
        "/login", data={"username": "not@present.net", "password": "..."}
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.BAD_REQUEST)
    logged_out_app.authenticate.assert_called_once()  # type: ignore
    assert_that(logged_out_app.store).is_empty()

    result = response.json()
    assert_that(result).has_detail([ERROR_TEXT])


def test_valid_user_query(logged_in_app: LoggedInApp):
    """Test that currently logged in user can be queried."""
    # pylint: disable=no-member
    response = logged_in_app.client.get("/me", headers=logged_in_app.default_headers)

    assert_that(response.json()).has_name(USERNAME)


def test_invalid_user_query(logged_out_app: LoggedOutApp):
    """Test a query with an invalid sessions."""
    headers = {"Authorization": "Bearer dummy"}
    response = logged_out_app.client.get("/me", headers=headers)

    assert_that(response.status_code).is_equal_to(HTTPStatus.UNAUTHORIZED)
    result = response.json()
    assert_that(result).contains_key("detail")


def test_valid_logout(logged_in_app: LoggedInApp) -> None:
    """Test log-out of a logged-in session."""
    # pylint: disable=no-member
    response = logged_in_app.client.delete(
        "/logout", headers=logged_in_app.default_headers
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.NO_CONTENT)
    assert_that(logged_in_app.store).is_empty()


def test_invalid_logout(logged_in_app: LoggedInApp) -> None:
    """Test a query with an invalid sessions."""
    # pylint: disable=no-member
    headers = {"Authorization": "Bearer dummy"}
    response = logged_in_app.client.delete("/logout", headers=headers)

    assert_that(response.status_code).is_equal_to(HTTPStatus.BAD_REQUEST)
    assert_that(logged_in_app.store).is_length(1)
